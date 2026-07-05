import json
import os
import sys
import threading
import time
import webbrowser
from pathlib import Path

import requests
from dotenv import load_dotenv, set_key
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import uvicorn

if getattr(sys, "frozen", False):
    # Running as a built .exe: bundled files (like frontend/) are extracted
    # to a temp folder at sys._MEIPASS, but .env must live next to the real
    # exe so the saved API key survives between runs.
    BASE_DIR = Path(sys.executable).resolve().parent
    FRONTEND_DIR = Path(sys._MEIPASS) / "frontend"
else:
    BASE_DIR = Path(__file__).resolve().parent
    FRONTEND_DIR = BASE_DIR / "frontend"

ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)

# gemini-flash-latest always points at Google's current default Flash model,
# which is the model family covered by Gemini's free tier as of mid-2026.
# Google does change model names and free-tier limits over time -- if this
# ever stops working, check https://ai.google.dev/gemini-api/docs/pricing
# for the current free model name and swap it in below.
GEMINI_MODEL = "gemini-flash-latest"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"


def get_or_ask_for_api_key() -> str:
    """Use the key from .env / the environment if present, otherwise ask
    once in the terminal and save it to .env so this never happens again."""
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key

    print("\nFirst-time setup: Query Draft needs a free Gemini API key.")
    print("Get one at https://aistudio.google.com/apikey (no credit card needed).")
    key = input("Paste your API key here and press Enter: ").strip()

    if not key:
        raise RuntimeError("No API key entered. Restart and paste a valid key.")

    if not ENV_PATH.exists():
        ENV_PATH.touch()
    set_key(str(ENV_PATH), "GEMINI_API_KEY", key)
    os.environ["GEMINI_API_KEY"] = key
    print("Saved. You won't be asked again on this machine.\n")
    return key


API_KEY = get_or_ask_for_api_key()

DIALECT_NAMES = {
    "postgres": "PostgreSQL",
    "mysql": "MySQL",
    "sqlite": "SQLite",
    "sqlserver": "SQL Server (T-SQL)",
    "bigquery": "Google BigQuery",
    "snowflake": "Snowflake",
}

app = FastAPI(title="Query Draft")


class GenerateRequest(BaseModel):
    schema_text: str = Field(default="", max_length=8000, alias="schema")
    dialect: str = Field(default="postgres")
    request: str = Field(..., min_length=1, max_length=2000)

    class Config:
        populate_by_name = True


class GenerateResponse(BaseModel):
    sql: str
    explanation: str = ""
    assumptions: str = ""


def build_prompt(dialect_name: str, schema_text: str, user_request: str) -> str:
    schema_part = f"Schema:\n{schema_text}\n\n" if schema_text.strip() else "No schema was provided.\n\n"
    return f"""You are a SQL generation engine. Given an optional schema description and a \
natural-language request, produce a single SQL query in the {dialect_name} dialect.

Respond with ONLY a raw JSON object, no markdown fences, no preamble, in exactly this shape:
{{"sql": "the query, formatted with newlines and indentation", "explanation": "2-3 sentences \
in plain language explaining what the query does and any assumptions you made about the \
schema", "assumptions": "short note on any table/column names you had to guess, or empty \
string if a schema was fully provided"}}

Rules:
- If no schema is given, infer reasonable, commonly-used table and column names and state \
that clearly in "assumptions".
- Prefer explicit column lists over SELECT *.
- Use the specific syntax and functions idiomatic to {dialect_name} (e.g. date functions, \
LIMIT vs TOP, quoting).
- Keep the query correct and runnable, not just illustrative.

{schema_part}Request: {user_request}"""


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/generate-sql", response_model=GenerateResponse)
def generate_sql(payload: GenerateRequest):
    dialect_name = DIALECT_NAMES.get(payload.dialect, "PostgreSQL")
    prompt = build_prompt(dialect_name, payload.schema_text, payload.request)

    try:
        response = requests.post(
            GEMINI_URL,
            params={"key": API_KEY},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"maxOutputTokens": 1000},
            },
            timeout=30,
        )
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Could not reach Gemini API: {exc}") from exc

    if response.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Gemini API error ({response.status_code}): {response.text[:300]}")

    data = response.json()
    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise HTTPException(status_code=502, detail="No text content in Gemini response")

    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned[cleaned.find("{"):]

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        parsed = {"sql": cleaned, "explanation": "", "assumptions": ""}

    return GenerateResponse(
        sql=parsed.get("sql", ""),
        explanation=parsed.get("explanation", ""),
        assumptions=parsed.get("assumptions", ""),
    )


@app.get("/")
def serve_index():
    return FileResponse(FRONTEND_DIR / "index.html")


app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


def open_browser_when_ready():
    time.sleep(1.2)
    webbrowser.open("http://localhost:8000")


if __name__ == "__main__":
    try:
        threading.Thread(target=open_browser_when_ready, daemon=True).start()
        print("Starting Query Draft at http://localhost:8000 (opening in your browser...)")
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
    except Exception as exc:
        print(f"\nSomething went wrong: {exc}")
        input("Press Enter to close this window...")
