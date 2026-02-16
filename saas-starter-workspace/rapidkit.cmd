@echo off
setlocal

set "SCRIPT_DIR=%~dp0"

if exist "%SCRIPT_DIR%\.venv\Scripts\rapidkit.exe" (
  "%SCRIPT_DIR%\.venv\Scripts\rapidkit.exe" %*
  exit /b %ERRORLEVEL%
)

where poetry >nul 2>nul
if %ERRORLEVEL%==0 if exist "%SCRIPT_DIR%\pyproject.toml" (
  poetry run rapidkit %*
  exit /b %ERRORLEVEL%
)

echo RapidKit launcher could not find a local Python CLI. 1>&2
echo Tip: run .venv\Scripts\rapidkit.exe --help 1>&2
exit /b 1
