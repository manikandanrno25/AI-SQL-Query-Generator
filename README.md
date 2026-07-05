# Query Draft — AI SQL generator

Describe what you want in plain English, get back a runnable SQL query.
Runs on **Google Gemini's free API tier** — no paid account needed.

## 🚀 Getting Started

1. Download and extract **query-draft-gemini.zip**.
2. Double-click **build_exe.bat** (only the first time). This will create **QueryDraft.exe** inside the **dist** folder.
3. Open the **dist** folder and double-click **QueryDraft.exe**.
4. When prompted, enter your **Google Gemini API key** (only the first time).
   - Get a free API key from Google AI Studio: https://aistudio.google.com/apikey
5. Your API key will be saved locally, and the application will automatically open in your browser.
6. From then on, simply double-click **QueryDraft.exe** to launch the application.
## Getting a free Gemini API key

1. Go to https://aistudio.google.com/apikey
2. Sign in with any Google account.
3. Click "Create API key." No credit card, no payment info.
4. Paste that key into the app when it asks.

Gemini's free tier (unlike Anthropic's, which is a one-time trial credit)
is an ongoing free allowance with daily limits, not a balance that runs
out. Google does adjust free-tier limits and model availability over
time — if the app ever stops working, check
https://ai.google.dev/gemini-api/docs/pricing for the current free model
name, and update `GEMINI_MODEL` near the top of `app.py` if it's changed.

## What's actually happening

- `app.py` is the whole app: one small server that serves the page you see
  in the browser *and* calls Gemini to generate the SQL.
- Your API key lives only in a local `.env` file created on first run
  (next to `QueryDraft.exe` if you built it, or in this folder if you're
  running from source). It's never sent anywhere except to Google's API.
- To stop it, close its window or press `Ctrl+C`.
- To switch to a different key later, delete `.env` and run it again — it'll
  ask for a new one.

## Project structure

```
query-draft/
├── app.py              the whole backend + static file server
├── requirements.txt
├── build_exe.bat        one-time build → single .exe, Windows
├── build_exe.sh          one-time build → single app, Mac/Linux
├── start.bat             run from source directly, Windows
├── start.sh              run from source directly, Mac/Linux
├── frontend/
│   └── index.html       the page itself
└── .gitignore
```
<img width="1191" height="626" alt="Screenshot 2026-07-05 130701" src="https://github.com/user-attachments/assets/881b989b-d0b7-4146-b003-c0ff89324f78" />

