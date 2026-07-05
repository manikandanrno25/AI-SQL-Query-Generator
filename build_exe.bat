@echo off
cd /d "%~dp0"

echo This builds QueryDraft.exe -- a single file you can double-click from now on.
echo This step only needs to run once, and needs Python + internet access.
echo.

python -m venv build_venv
build_venv\Scripts\pip install --quiet -r requirements.txt pyinstaller

echo.
echo Building QueryDraft.exe (this can take a minute)...
build_venv\Scripts\pyinstaller --onefile --name QueryDraft --add-data "frontend;frontend" app.py

echo.
echo Done. Your app is at: dist\QueryDraft.exe
echo Move or copy that one file anywhere you like -- Desktop, a folder, wherever.
echo From now on, just double-click QueryDraft.exe. You don't need this folder,
echo Python, or anything else after that.
echo.
pause
