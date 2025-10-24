@echo off
REM 7ty.vn System Startup Script for Windows 11
REM Quick start for development and testing

title 7ty.vn System Startup
color 0A

echo.
echo ========================================
echo 🚀 Starting 7ty.vn System...
echo ========================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if Docker Desktop is running
echo ⏳ Checking Docker Desktop...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Desktop is not running!
    echo Please start Docker Desktop and try again.
    echo.
    pause
    exit /b 1
)
echo ✅ Docker Desktop is running

REM Check if docker-compose exists
if not exist "docker-compose.yml" (
    echo ❌ docker-compose.yml not found!
    echo Please make sure you're in the correct directory.
    echo.
    pause
    exit /b 1
)

REM Create .env file if not exists
if not exist ".env" (
    echo ⚙️ Creating .env file...
    (
        echo # 7ty.vn Environment Configuration
        echo DATABASE_URL=postgresql://ty7user:ty7password@postgres:5432/ty7_db
        echo REDIS_URL=redis://:ty7redis@redis:6379/0
        echo SECRET_KEY=ty7-super-secret-key-2024-production
        echo CORS_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
        echo DEBUG=true
        echo LOG_LEVEL=info
        echo.
        echo # Database Configuration
        echo POSTGRES_DB=ty7_db
        echo POSTGRES_USER=ty7user
        echo POSTGRES_PASSWORD=ty7password
        echo.
        echo # Redis Configuration
        echo REDIS_PASSWORD=ty7redis
    ) > .env
    echo ✅ .env file created
)

REM Stop any existing containers
echo 🛑 Stopping existing containers...
docker-compose down --remove-orphans >nul 2>&1

REM Pull latest images
echo 📥 Pulling Docker images...
docker-compose pull

REM Build and start services
echo 🏗️ Building and starting services...
docker-compose up -d --build

if %errorlevel% neq 0 (
    echo ❌ Failed to start services!
    echo Check the error messages above.
    echo.
    pause
    exit /b 1
)

REM Wait for services to be ready
echo ⏳ Waiting for services to start...
timeout /t 15 /nobreak >nul

REM Check service health
echo 🔍 Checking service health...

REM Check PostgreSQL
docker-compose exec -T postgres pg_isready -U ty7user -d ty7_db >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ PostgreSQL is ready
) else (
    echo ⚠️ PostgreSQL is not ready yet, waiting...
    timeout /t 5 /nobreak >nul
)

REM Check Redis
docker-compose exec -T redis redis-cli -a ty7redis ping >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Redis is ready
) else (
    echo ⚠️ Redis is not ready yet, waiting...
    timeout /t 5 /nobreak >nul
)

REM Check FastAPI backend
echo ⏳ Waiting for FastAPI backend...
set /a counter=0
:check_backend
set /a counter+=1
curl -f http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ FastAPI backend is ready
    goto backend_ready
)
if %counter% geq 30 (
    echo ❌ FastAPI backend failed to start
    echo Showing backend logs:
    docker-compose logs backend
    pause
    exit /b 1
)
timeout /t 2 /nobreak >nul
goto check_backend

:backend_ready

REM Show service status
echo.
echo 🎉 7ty.vn System Started Successfully!
echo =====================================
echo.
echo 🌐 Service URLs:
echo   Main Portal:    http://localhost:8000/
echo   Admin Panel:    http://localhost:8000/admin
echo   Agent App:      http://localhost:8000/agent
echo   Customer App:   http://localhost:8000/customer
echo   API Docs:       http://localhost:8000/docs
echo.
echo 👤 Demo Accounts:
echo   Admin:     admin / admin123
echo   Agent:     demo / 123456 (5M VND wallet)
echo   Test Phones: 0123456789, 0987654321
echo.
echo 🗄️ Database Access:
echo   PostgreSQL: localhost:5432 (ty7user/ty7password)
echo   Redis:      localhost:6379 (password: ty7redis)
echo.

REM Show container status
echo 📊 Container Status:
docker-compose ps

echo.
echo 💡 Useful Commands:
echo   View logs:      logs.bat
echo   Restart:        docker-compose restart
echo   Stop:           stop.bat
echo   Reset:          reset.bat
echo.

REM Check if all services are running
for /f %%i in ('docker-compose ps -q ^| find /c /v ""') do set container_count=%%i
if %container_count% geq 3 (
    echo ✅ All services are running successfully!
    echo.
    echo 🎯 Ready for testing! Visit http://localhost:8000/ to get started.
    
    REM Open browser automatically
    set /p open_browser="🌐 Open browser automatically? (Y/N): "
    if /i "%open_browser%"=="Y" (
        start http://localhost:8000/
    )
) else (
    echo ⚠️ Some services may not be running properly.
    echo Run 'logs.bat' to check for errors.
)

echo.
echo 📋 Press any key to view logs, or close this window to continue...
pause >nul

REM Follow logs
docker-compose logs -f