# Query Draft — AI SQL generator

Describe what you want in plain English, get back a runnable SQL query.
Runs on **Google Gemini's free API tier** — no paid account needed.

## Option A: a single app you just double-click (recommended)

This turns everything into one file — `QueryDraft.exe` on Windows — so after
a one-time build, you never touch Python, a terminal, or this folder again.

**One-time setup (needs Python + internet, only ever done once):**

- **Windows**: double-click `build_exe.bat`
- **Mac/Linux**: run `./build_exe.sh` in a terminal

This creates a `dist` folder containing a single file: `QueryDraft.exe`
(Windows) or `QueryDraft` (Mac/Linux). Move that one file wherever you
want — Desktop, a USB stick, another computer entirely. You can delete
everything else in this repo after that if you want; it's no longer needed.

**From then on:** just double-click that file. First run, it asks for a
free Gemini API key once (get one at https://aistudio.google.com/apikey —
no credit card required) and remembers it after that. Your browser opens
automatically. That's the whole experience — no terminal, no scripts, no
setup.

## Option B: run it straight from source (no build step)

If you'd rather skip building an exe:

- **Mac/Linux**: double-click `start.sh` (or run `./start.sh`)
- **Windows**: double-click `start.bat`

Same first-run API key prompt, same auto-opening browser — this just runs
directly from the Python files each time instead of a single packaged app.

(Requires Python 3.9+ installed — check with `python3 --version` or
`python --version`.)

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

## If you want to deploy this publicly instead of running it locally

Both options above are built for "run it on your own machine." If you want
a real hosted link you can share (so people don't need to download or run
anything at all), that's a different setup — deploying `app.py` to a host
like Render or Fly.io with the API key set as an environment variable there.
Ask and I'll walk through it.
