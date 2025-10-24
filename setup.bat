@echo off
REM 7ty.vn System Initial Setup Script for Windows 11

title 7ty.vn System Setup
color 0B

echo.
echo ========================================
echo ⚙️ 7ty.vn System Initial Setup
echo ========================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check Windows version
echo 🔍 Checking Windows version...
for /f "tokens=4-5 delims=. " %%i in ('ver') do set VERSION=%%i.%%j
echo Windows version: %VERSION%

REM Check if Windows 11 (build 22000+)
if "%VERSION%" lss "10.0" (
    echo ⚠️ Warning: Windows 10 or older detected. Windows 11 recommended.
)

REM Check Docker Desktop installation
echo 🐳 Checking Docker Desktop...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Desktop is not installed or not running!
    echo.
    echo Please install Docker Desktop:
    echo 1. Download from: https://www.docker.com/products/docker-desktop/
    echo 2. Install with default settings
    echo 3. Enable WSL2 integration
    echo 4. Restart Docker Desktop
    echo 5. Run this setup again
    echo.
    pause
    exit /b 1
) else (
    echo ✅ Docker Desktop is available
    docker --version
)

REM Check Docker Compose
echo 🔧 Checking Docker Compose...
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose not found!
    echo Please update Docker Desktop to the latest version.
    pause
    exit /b 1
) else (
    echo ✅ Docker Compose is available
    docker-compose --version
)

REM Check WSL2
echo 🐧 Checking WSL2...
wsl --status >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ WSL2 may not be properly configured.
    echo To enable WSL2, run as Administrator:
    echo   wsl --install
    echo Then restart your computer.
)

REM Check required ports
echo 🔌 Checking required ports...
set "ports=8000 5432 6379"
for %%p in (%ports%) do (
    netstat -an | findstr :%%p >nul 2>&1
    if %errorlevel% equ 0 (
        echo ⚠️ Port %%p is in use
        echo To free port %%p:
        echo   netstat -ano ^| findstr :%%p
        echo   taskkill /PID ^<PID^> /F
    ) else (
        echo ✅ Port %%p is available
    )
)

REM Create directories if needed
echo 📁 Creating directories...
if not exist "logs" mkdir logs
if not exist "backups" mkdir backups
echo ✅ Directories created

REM Create environment file
echo 🔐 Creating environment configuration...
if exist ".env" (
    echo ⚠️ .env file already exists, backing up...
    copy .env .env.backup >nul
)

(
    echo # 7ty.vn Environment Configuration for Windows 11
    echo # Generated on %date% %time%
    echo.
    echo # FastAPI Backend
    echo DATABASE_URL=postgresql://ty7user:ty7password@postgres:5432/ty7_db
    echo REDIS_URL=redis://:ty7redis@redis:6379/0
    echo SECRET_KEY=ty7-super-secret-key-2024-production-%random%
    echo CORS_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
    echo DEBUG=true
    echo LOG_LEVEL=info
    echo.
    echo # Database Configuration
    echo POSTGRES_DB=ty7_db
    echo POSTGRES_USER=ty7user
    echo POSTGRES_PASSWORD=ty7password
    echo POSTGRES_INITDB_ARGS=--encoding=UTF-8 --locale=C
    echo.
    echo # Redis Configuration
    echo REDIS_PASSWORD=ty7redis
    echo.
    echo # Windows Specific
    echo COMPOSE_CONVERT_WINDOWS_PATHS=1
    echo DOCKER_BUILDKIT=1
) > .env

echo ✅ Environment file created

REM Download/pull Docker images
echo 📥 Downloading Docker images...
echo This may take a few minutes on first run...

docker pull postgres:15-alpine
docker pull redis:7-alpine
docker pull python:3.11-slim

if %errorlevel% neq 0 (
    echo ⚠️ Failed to download some images. Check internet connection.
) else (
    echo ✅ Docker images downloaded
)

REM Test Docker Compose configuration
echo 🧪 Testing Docker Compose configuration...
docker-compose config >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose configuration has errors!
    docker-compose config
    pause
    exit /b 1
) else (
    echo ✅ Docker Compose configuration is valid
)

REM Create Windows firewall rules
echo 🔥 Configuring Windows Firewall...
echo This requires Administrator privileges...

powershell -Command "& {
    try {
        New-NetFirewallRule -DisplayName '7ty-FastAPI' -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow -ErrorAction SilentlyContinue
        New-NetFirewallRule -DisplayName '7ty-PostgreSQL' -Direction Inbound -Protocol TCP -LocalPort 5432 -Action Allow -ErrorAction SilentlyContinue
        New-NetFirewallRule -DisplayName '7ty-Redis' -Direction Inbound -Protocol TCP -LocalPort 6379 -Action Allow -ErrorAction SilentlyContinue
        Write-Host '✅ Firewall rules configured'
    } catch {
        Write-Host '⚠️ Could not configure firewall (run as Administrator for automatic setup)'
    }
}"

REM Create desktop shortcuts
echo 🖥️ Creating desktop shortcuts...
set "desktop=%USERPROFILE%\Desktop"
set "current_dir=%~dp0"

REM Start shortcut
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%temp%\shortcut.vbs"
echo sLinkFile = "%desktop%\Start 7ty System.lnk" >> "%temp%\shortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%temp%\shortcut.vbs"
echo oLink.TargetPath = "%current_dir%start.bat" >> "%temp%\shortcut.vbs"
echo oLink.WorkingDirectory = "%current_dir%" >> "%temp%\shortcut.vbs"
echo oLink.Description = "Start 7ty.vn System" >> "%temp%\shortcut.vbs"
echo oLink.Save >> "%temp%\shortcut.vbs"
cscript "%temp%\shortcut.vbs" >nul 2>&1

REM Stop shortcut
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%temp%\shortcut.vbs"
echo sLinkFile = "%desktop%\Stop 7ty System.lnk" >> "%temp%\shortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%temp%\shortcut.vbs"
echo oLink.TargetPath = "%current_dir%stop.bat" >> "%temp%\shortcut.vbs"
echo oLink.WorkingDirectory = "%current_dir%" >> "%temp%\shortcut.vbs"
echo oLink.Description = "Stop 7ty.vn System" >> "%temp%\shortcut.vbs"
echo oLink.Save >> "%temp%\shortcut.vbs"
cscript "%temp%\shortcut.vbs" >nul 2>&1

del "%temp%\shortcut.vbs" >nul 2>&1
echo ✅ Desktop shortcuts created

REM System information
echo.
echo 📊 System Information:
echo =====================
systeminfo | findstr /C:"Total Physical Memory"
systeminfo | findstr /C:"Available Physical Memory"
wmic cpu get name /format:list | findstr Name=
echo Docker Desktop: %docker_version%

echo.
echo 🎉 Setup Complete!
echo ==================
echo.
echo ✅ Environment configured
echo ✅ Docker images downloaded  
echo ✅ Firewall rules configured
echo ✅ Desktop shortcuts created
echo.
echo 🚀 Next Steps:
echo 1. Run 'start.bat' to start the system
echo 2. Visit http://localhost:8000/ to test
echo 3. Use demo accounts: admin/admin123, demo/123456
echo.
echo 💡 Useful Files:
echo   start.bat  - Start the system
echo   stop.bat   - Stop the system
echo   logs.bat   - View system logs
echo   reset.bat  - Reset database
echo.

set /p start_now="🚀 Start the system now? (Y/N): "
if /i "%start_now%"=="Y" (
    echo.
    echo Starting system...
    call start.bat
) else (
    echo.
    echo Setup complete! Run 'start.bat' when ready.
)

pause