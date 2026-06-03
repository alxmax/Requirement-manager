@echo off
rem Launch the Requirement Manager app (Vite dev server) and open it in the browser.
cd /d "%~dp0..\..\app"
if not exist node_modules call npm install
start "Requirement Manager dev server" cmd /k npm run dev
timeout /t 4 /nobreak >nul
start "" http://localhost:5173/
exit
