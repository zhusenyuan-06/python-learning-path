@echo off
chcp 65001 >nul
cd /d "%~dp0"

set "PY=<Python安装目录>\python.exe"
if not exist "%PY%" (
    echo [error] Python not found: %PY%
    echo Please check the path in run.bat
    pause
    exit /b 1
)

echo.
echo ==========================================
echo   Kindergarten Meal Delivery - Report
echo ==========================================
echo.

"%PY%" src\run.py report %1
set "RC=%ERRORLEVEL%"

echo.
if not "%RC%"=="0" (
    echo [FAILED] exit code: %RC%
) else (
    echo [DONE] Check the output folder.
)
echo.
pause
