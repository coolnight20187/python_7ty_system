@echo off
REM 7ty.vn System Reset Script for Windows 11

title 7ty.vn System Reset
color 0C

echo.
echo ========================================
echo 🔄 7ty.vn System Reset
echo ========================================
echo.
echo ⚠️ WARNING: This will delete all data!
echo.

REM Change to script directory
cd /d "%~dp0"

REM Confirmation
set /p confirm="Are you sure you want to reset the system? (yes/no): "
if /i not "%confirm%"=="yes" (
    echo Reset cancelled.
    pause
    exit /b 0
)

echo.
echo 🛑 Stopping all services...
docker-compose down

echo 🗑️ Removing containers and volumes...
docker-compose down -v --remove-orphans

echo 🧹 Cleaning up Docker system...
docker system prune -f

echo 📥 Pulling fresh images...
docker-compose pull

echo 🏗️ Rebuilding and starting services...
docker-compose up -d --build

echo ⏳ Waiting for services to initialize...
timeout /t 20 /nobreak >nul

echo.
echo 🎉 System Reset Complete!
echo =========================
echo.
echo 🔑 Demo Accounts Restored:
echo   Admin: admin / admin123
echo   Agent: demo / 123456 (5M VND wallet)
echo.
echo 🌐 Access URLs:
echo   Main Portal: http://localhost:8000/
echo   Admin Panel: http://localhost:8000/admin
echo   Agent App:   http://localhost:8000/agent
echo   Customer:    http://localhost:8000/customer
echo.

pause