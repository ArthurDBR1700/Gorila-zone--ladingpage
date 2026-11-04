@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (set "GORILA_PY=python") else (set "GORILA_PY=py -3")
%GORILA_PY% --version
if errorlevel 1 goto erro
where npm.cmd >nul 2>nul
if errorlevel 1 goto erro
if not exist "backend_gorila\.venv\Scripts\python.exe" %GORILA_PY% -m venv "backend_gorila\.venv"
if errorlevel 1 goto erro
"backend_gorila\.venv\Scripts\python.exe" -m pip install -r "backend_gorila\requirements.txt"
if errorlevel 1 goto erro
pushd frontend
call npm.cmd ci --no-audit --no-fund
if errorlevel 1 goto erro
call npm.cmd run build
if errorlevel 1 goto erro
popd
echo.
echo Instalacao concluida. Execute INICIAR_WINDOWS.bat.
pause
exit /b 0
:erro
echo.
echo Falha na instalacao. Confira a mensagem acima.
echo Necessario: Python 3.11 a 3.14 estavel e Node.js 20.19 ou superior.
pause
exit /b 1
