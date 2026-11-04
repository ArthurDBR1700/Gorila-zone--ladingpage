@echo off
setlocal
cd /d "%~dp0"
if not exist "backend_gorila\.venv\Scripts\python.exe" goto instalar
if not exist "frontend\node_modules" goto instalar
start "GorilaZone API" /D "%~dp0backend_gorila" cmd /k ".venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
start "GorilaZone Frontend" /D "%~dp0frontend" cmd /k "npm.cmd run dev"
echo Abra http://127.0.0.1:5173 apos os dois servidores iniciarem.
echo Deixe as duas janelas abertas. Para parar, use Ctrl+C em cada uma.
pause
exit /b 0
:instalar
echo Execute INSTALAR_WINDOWS.bat primeiro.
pause
exit /b 1
