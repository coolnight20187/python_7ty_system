# 🪟 7tỷ.vn - Windows 11 Setup Guide

## 📋 Prerequisites

### Required Software:
- ✅ **Windows 11** (Build 19041 or higher)
- ✅ **Docker Desktop** (Latest version)
- ✅ **pgAdmin 4** (Optional, for database management)
- ✅ **Git** (Optional, for version control)

## 🚀 Quick Start (5 Minutes)

### Step 1: Enable WSL2
```powershell
# Run as Administrator in PowerShell
wsl --install
# Restart computer if prompted
```

### Step 2: Install Docker Desktop
1. Download from: https://www.docker.com/products/docker-desktop/
2. Install with default settings
3. Enable WSL2 integration
4. Restart Docker Desktop

### Step 3: Clone/Download Project
```cmd
cd C:\
git clone <repository-url> 7ty-system
# OR download and extract to C:\7ty-system
```

### Step 4: Start System
```cmd
cd C:\7ty-system\python_7ty_system
start.bat
```

## 🔧 Detailed Setup Instructions

### 1. Docker Desktop Configuration

#### Enable Required Features:
1. Open Docker Desktop
2. Go to Settings → General
3. ✅ Enable "Use WSL 2 based engine"
4. ✅ Enable "Expose daemon on tcp://localhost:2375"

#### Resource Allocation:
1. Settings → Resources → Advanced
2. **Memory:** 4GB minimum (8GB recommended)
3. **CPUs:** 2 minimum (4 recommended)
4. **Disk:** 20GB minimum

#### WSL Integration:
1. Settings → Resources → WSL Integration
2. ✅ Enable integration with default WSL distro
3. ✅ Enable Ubuntu (if installed)

### 2. Port Configuration

#### Required Ports:
- **8000** - FastAPI Backend
- **5432** - PostgreSQL Database
- **6379** - Redis Cache
- **80/443** - Nginx (if used)

#### Check Port Availability:
```cmd
netstat -an | findstr :8000
netstat -an | findstr :5432
netstat -an | findstr :6379
```

#### Free Ports if Needed:
```cmd
# Kill process using port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### 3. Windows Firewall Configuration

#### Allow Docker Ports:
```powershell
# Run as Administrator
New-NetFirewallRule -DisplayName "Docker-8000" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
New-NetFirewallRule -DisplayName "Docker-5432" -Direction Inbound -Protocol TCP -LocalPort 5432 -Action Allow
New-NetFirewallRule -DisplayName "Docker-6379" -Direction Inbound -Protocol TCP -LocalPort 6379 -Action Allow
```

## 🗄️ pgAdmin 4 Setup

### Installation:
1. Download from: https://www.pgadmin.org/download/pgadmin-4-windows/
2. Install with default settings
3. Launch pgAdmin 4

### Server Connection:
1. Right-click "Servers" → Create → Server
2. **General Tab:**
   - Name: `7ty-PostgreSQL`
3. **Connection Tab:**
   - Host: `localhost`
   - Port: `5432`
   - Database: `ty7_db`
   - Username: `ty7user`
   - Password: `ty7password`
4. Click "Save"

### Test Connection:
```sql
-- Run in pgAdmin Query Tool
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY tablename;
```

## 📁 Project Structure

```
python_7ty_system/
├── 📄 start.bat              # 🚀 Start system
├── 📄 stop.bat               # 🛑 Stop system
├── 📄 setup.bat              # ⚙️ Initial setup
├── 📄 logs.bat               # 📋 View logs
├── 📄 reset.bat              # 🔄 Reset database
├── 📄 docker-compose.yml     # 🐳 Docker configuration
├── 📄 .env                   # 🔐 Environment variables
├── 📂 backend/               # 🐍 FastAPI backend
├── 📂 frontend/              # 🌐 Web applications
├── 📂 database/              # 🗄️ Database files
└── 📂 docs/                  # 📖 Documentation
```

## 🎯 Testing Procedures

### 1. Pre-Deployment Check
```cmd
# Run setup.bat first
setup.bat

# Check Docker status
docker --version
docker-compose --version
docker ps
```

### 2. System Startup
```cmd
# Start all services
start.bat

# Verify services are running
docker-compose ps
```

### 3. Application Testing

#### Access URLs:
- **🏠 Main Portal:** http://localhost:8000/
- **🏢 Admin Panel:** http://localhost:8000/admin
- **📱 Agent PWA:** http://localhost:8000/agent
- **👤 Customer App:** http://localhost:8000/customer
- **📖 API Docs:** http://localhost:8000/docs

#### Test Accounts:
- **👑 Admin:** `admin` / `admin123`
- **🤝 Agent:** `demo` / `123456` (5M VND wallet)
- **📞 Customer Phones:** `0123456789`, `0987654321`

### 4. API Testing

#### Health Check:
```cmd
curl http://localhost:8000/health
```

#### Login Test:
```cmd
curl -X POST "http://localhost:8000/api/auth/login" ^
     -H "Content-Type: application/json" ^
     -d "{\"username\":\"demo\",\"password\":\"123456\"}"
```

## 🔧 Troubleshooting

### Common Issues:

#### 1. Docker Desktop Not Starting
**Solution:**
```cmd
# Restart Docker service
net stop com.docker.service
net start com.docker.service

# Reset Docker Desktop
"C:\Program Files\Docker\Docker\Docker Desktop.exe" --reset-to-factory
```

#### 2. Port Already in Use
**Solution:**
```cmd
# Find process using port
netstat -ano | findstr :8000
# Kill the process
taskkill /PID <PID> /F
```

#### 3. WSL2 Issues
**Solution:**
```powershell
# Update WSL
wsl --update
# Set default version
wsl --set-default-version 2
# Restart Docker Desktop
```

#### 4. Permission Denied
**Solution:**
```cmd
# Run as Administrator
# OR add user to docker-users group
net localgroup docker-users "%USERNAME%" /add
```

#### 5. Database Connection Failed
**Solution:**
```cmd
# Reset database
reset.bat
# Check database logs
docker-compose logs postgres
```

### Performance Optimization:

#### 1. Docker Settings:
- Increase memory allocation to 8GB
- Enable file sharing for project directory
- Disable unnecessary startup programs

#### 2. Windows Settings:
```cmd
# Disable Windows Defender real-time scanning for project folder
# Add exclusion: C:\path\to\python_7ty_system
```

#### 3. Network Optimization:
```cmd
# Flush DNS
ipconfig /flushdns
# Reset network stack
netsh winsock reset
```

## 📊 System Monitoring

### Resource Usage:
```cmd
# Check Docker resource usage
docker stats

# Check system resources
tasklist /svc | findstr docker
```

### Log Monitoring:
```cmd
# View all logs
logs.bat

# View specific service logs
docker-compose logs backend
docker-compose logs postgres
docker-compose logs redis
```

## 🔒 Security Considerations

### 1. Change Default Passwords:
Edit `.env` file:
```env
POSTGRES_PASSWORD=your-secure-password
REDIS_PASSWORD=your-redis-password
SECRET_KEY=your-secret-key
```

### 2. Firewall Rules:
- Only allow necessary ports
- Restrict access to localhost for development

### 3. Docker Security:
```cmd
# Scan for vulnerabilities
docker scout cves
```

## 📞 Support

### Getting Help:
1. **Documentation:** Check `/docs` folder
2. **Logs:** Run `logs.bat` for error details
3. **Reset:** Use `reset.bat` to start fresh
4. **Community:** Check GitHub issues

### System Requirements Met? ✅
- [ ] Windows 11 Build 19041+
- [ ] Docker Desktop installed & running
- [ ] WSL2 enabled
- [ ] 8GB RAM available
- [ ] 20GB disk space
- [ ] Ports 8000, 5432, 6379 free
- [ ] Internet connection for Docker images

---

**🎉 Ready to start? Run `setup.bat` then `start.bat`!**