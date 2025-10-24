@echo off
REM 7ty.vn System Logs Viewer for Windows 11

title 7ty.vn System Logs
color 0E

echo.
echo ========================================
echo 📋 7ty.vn System Logs
echo ========================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if Docker Desktop is running
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Desktop is not running!
    echo Cannot view logs without Docker.
    echo.
    pause
    exit /b 1
)

REM Show menu
:menu
echo.
echo 📊 Log Viewer Options:
echo =====================
echo 1. All services (live)
echo 2. Backend logs only
echo 3. Database logs only  
echo 4. Redis logs only
echo 5. Container status
echo 6. System health check
echo 7. Error logs only
echo 8. Last 50 lines (all)
echo 9. Export logs to file
echo 0. Exit
echo.

set /p choice="Select option (0-9): "

if "%choice%"=="1" goto all_live
if "%choice%"=="2" goto backend_logs
if "%choice%"=="3" goto database_logs
if "%choice%"=="4" goto redis_logs
if "%choice%"=="5" goto container_status
if "%choice%"=="6" goto health_check
if "%choice%"=="7" goto error_logs
if "%choice%"=="8" goto last_lines
if "%choice%"=="9" goto export_logs
if "%choice%"=="0" goto exit
goto menu

:all_live
echo.
echo 📺 Showing live logs from all services...
echo Press Ctrl+C to stop and return to menu
echo.
docker-compose logs -f
goto menu

:backend_logs
echo.
echo 🐍 Backend (FastAPI) Logs:
echo ==========================
docker-compose logs backend
echo.
pause
goto menu

:database_logs
echo.
echo 🗄️ Database (PostgreSQL) Logs:
echo ==============================
docker-compose logs postgres
echo.
pause
goto menu

:redis_logs
echo.
echo 🔴 Redis Cache Logs:
echo ===================
docker-compose logs redis
echo.
pause
goto menu

:container_status
echo.
echo 📊 Container Status:
echo ===================
docker-compose ps
echo.
echo 💾 Resource Usage:
docker stats --no-stream
echo.
pause
goto menu

:health_check
echo.
echo 🏥 System Health Check:
echo =======================

REM Check API health
echo ⏳ Checking API health...
curl -s http://localhost:8000/health
if %errorlevel% equ 0 (
    echo ✅ API is responding
) else (
    echo ❌ API is not responding
)

REM Check database
echo ⏳ Checking database...
docker-compose exec -T postgres pg_isready -U ty7user -d ty7_db >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Database is ready
) else (
    echo ❌ Database is not ready
)

REM Check Redis
echo ⏳ Checking Redis...
docker-compose exec -T redis redis-cli -a ty7redis ping >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Redis is ready
) else (
    echo ❌ Redis is not ready
)

REM Check ports
echo ⏳ Checking ports...
netstat -an | findstr :8000 >nul && echo ✅ Port 8000 is open || echo ❌ Port 8000 is closed
netstat -an | findstr :5432 >nul && echo ✅ Port 5432 is open || echo ❌ Port 5432 is closed
netstat -an | findstr :6379 >nul && echo ✅ Port 6379 is open || echo ❌ Port 6379 is closed

echo.
pause
goto menu

:error_logs
echo.
echo ❌ Error Logs (Last 100 lines):
echo ===============================
docker-compose logs --tail=100 | findstr /i "error\|exception\|failed\|fatal"
echo.
pause
goto menu

:last_lines
echo.
echo 📄 Last 50 Lines (All Services):
echo ================================
docker-compose logs --tail=50
echo.
pause
goto menu

:export_logs
echo.
echo 💾 Exporting logs to file...
set "timestamp=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "timestamp=%timestamp: =0%"
set "logfile=logs\7ty_logs_%timestamp%.txt"

if not exist "logs" mkdir logs

echo 7ty.vn System Logs > "%logfile%"
echo Generated: %date% %time% >> "%logfile%"
echo ================================ >> "%logfile%"
echo. >> "%logfile%"

echo Container Status: >> "%logfile%"
docker-compose ps >> "%logfile%"
echo. >> "%logfile%"

echo All Service Logs: >> "%logfile%"
docker-compose logs >> "%logfile%"

echo ✅ Logs exported to: %logfile%
echo.
pause
goto menu

:exit
echo.
echo 👋 Goodbye!
exit /b 0