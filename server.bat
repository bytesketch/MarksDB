@echo off
setlocal enabledelayedexpansion

set arg1=%1
set arg2=%2

if "%arg1%"=="--inject-mysql" (
    if not exist "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" (
        if not exist "C:\Program Files (x86)\MySQL\MySQL Server 8.0\bin\mysql.exe" (
            echo MySQL is not installed. We can't inject SQL for the server.
            echo Please set-up MySQL first.
            exit /b 404
        )
    )

    echo You need to enter password of the root.
    mysql -u root -p < .cache\mysql.user-root.sql
    exit /b 0
)

if "%arg1%"=="--start" (
    set port=%arg2%

    if "%port%"=="" (
        set port=8080
    )

    if not exist ".\.env\Scripts\python.exe" (
        echo Environment not created.
        echo Create it by
        echo   server.bat --init
        exit /b 404
    )

    ".\.env\Scripts\python.exe" server.py %port%
    exit /b 0
)

if "%arg1%"=="--init" (
    where python >nul 2>nul
    if errorlevel 1 (
        echo Python is not installed. We can't run the server for you.
        echo Please install python first.
        exit /b 404
    )

    python -m venv .env
    ".\.env\Scripts\python" -m pip install --upgrade pip
    ".\.env\Scripts\python" -m pip install -r requirements.txt
    exit /b 0
)

if "%arg1%"=="--configure" (
    if not exist ".\.env\Scripts\python.exe" (
        echo Environment not created.
        echo Create it by
        echo   server.bat --init
        exit /b 404
    )

    if not exists ".cache" (
        mkdir .cache
    )
    ".\.env\Scripts\python.exe" configure.py
    exit /b 0
)

echo Usage:
echo "  ./server --init              # Setup environment"
echo "  ./server --start [port]      # Start server (default: 8080)"
echo "  ./server --configure         # Run configuration"
echo "  ./server --inject-mysql      # Inject MySQL schema"
exit /b 1
