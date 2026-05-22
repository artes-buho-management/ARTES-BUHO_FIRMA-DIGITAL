@echo off
REM Arranque en modo desarrollo - el navegador lo abre index.js
cd /d "%~dp0"
start /min "" cmd /c "node src/index.js"
