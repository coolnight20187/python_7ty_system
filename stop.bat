@echo off
REM 7ty.vn System Stop Script for Windows 11

title 7ty.vn System Stop
color 0C

echo.
echo ========================================
echo 🛑 Stopping 7ty.vn System...
echo ========================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if Docker Desktop is running
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Desktop is not running!
    echo System may already be stopped.
    echo.
    pause
    exit /b 0
)

REM Show current running containers
echo 📊 Current running containers:
docker-compose ps

echo.
echo ⏳ Stopping all services...

REM Stop and remove containers
docker-compose down

if %errorlevel% equ 0 (
    echo ✅ All services stopped successfully!
) else (
    echo ⚠️ Some services may not have stopped properly.
    echo Forcing stop...
    docker-compose down --remove-orphans
)

echo.
echo 🧹 Cleaning up...

REM Remove unused networks
docker network prune -f >nul 2>&1

echo ✅ System stopped and cleaned up!
echo.
echo 💡 To start again, run: start.bat
echo 🔄 To reset database, run: reset.bat
echo.

pause