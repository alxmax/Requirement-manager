@echo off
rem Launch the Requirement Manager app (Vite dev server) and open it in the browser.
cd /d "%~dp0..\..\app"
rem Free port 5173 if a stale dev server is still holding it, so the link below always matches.
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":5173 " ^| findstr LISTENING') do taskkill /f /pid %%p >nul 2>&1
if not exist node_modules call npm install
start "Requirement Manager dev server" cmd /k npm run dev
timeout /t 4 /nobreak >nul
start "" http://localhost:5173/
exit
