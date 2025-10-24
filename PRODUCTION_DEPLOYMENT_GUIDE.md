# 🚀 Hướng Dẫn Deploy Production - Hệ Thống 7tỷ.vn

## 📋 Mục Lục
1. [Yêu Cầu Hệ Thống](#yêu-cầu-hệ-thống)
2. [Chuẩn Bị Server](#chuẩn-bị-server)
3. [Cài Đặt Dependencies](#cài-đặt-dependencies)
4. [Cấu Hình Database](#cấu-hình-database)
5. [Deploy Backend](#deploy-backend)
6. [Cấu Hình Nginx](#cấu-hình-nginx)
7. [SSL Certificate](#ssl-certificate)
8. [Monitoring & Logging](#monitoring--logging)
9. [Backup & Recovery](#backup--recovery)
10. [Troubleshooting](#troubleshooting)

---

## 🖥️ Yêu Cầu Hệ Thống

### Minimum Requirements
- **CPU:** 2 cores (4 cores recommended)
- **RAM:** 4GB (8GB recommended)
- **Storage:** 50GB SSD (100GB recommended)
- **OS:** Ubuntu 22.04 LTS
- **Network:** 1Gbps connection

### Recommended Production Setup
- **CPU:** 4-8 cores
- **RAM:** 16GB
- **Storage:** 200GB NVMe SSD
- **Load Balancer:** Nginx
- **CDN:** CloudFlare (optional)

---

## 🛠️ Option 1: VPS Deployment (Ubuntu 22.04)

### Bước 1: Chuẩn Bị Server

```bash
# Cập nhật hệ thống
sudo apt update && sudo apt upgrade -y

# Cài đặt các package cần thiết
sudo apt install -y curl wget git vim htop unzip software-properties-common

# Tạo user cho application
sudo adduser ty7app
sudo usermod -aG sudo ty7app
sudo su - ty7app
```

### Bước 2: Cài Đặt Python 3.11+

```bash
# Thêm repository Python
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# Cài đặt Python 3.11
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Tạo symlink
sudo ln -sf /usr/bin/python3.11 /usr/bin/python3
sudo ln -sf /usr/bin/pip3 /usr/bin/pip

# Kiểm tra version
python3 --version  # Should show 3.11.x
```

### Bước 3: Cài Đặt PostgreSQL 15

```bash
# Thêm repository PostgreSQL
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" | sudo tee /etc/apt/sources.list.d/pgdg.list

# Cài đặt PostgreSQL
sudo apt update
sudo apt install -y postgresql-15 postgresql-client-15 postgresql-contrib-15

# Khởi động và enable service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Tạo database và user
sudo -u postgres psql << EOF
CREATE DATABASE ty7_db;
CREATE USER ty7user WITH ENCRYPTED PASSWORD 'SecurePassword123!';
GRANT ALL PRIVILEGES ON DATABASE ty7_db TO ty7user;
ALTER USER ty7user CREATEDB;
\q
EOF
```

### Bước 4: Cài Đặt Redis

```bash
# Cài đặt Redis
sudo apt install -y redis-server

# Cấu hình Redis
sudo nano /etc/redis/redis.conf
# Uncomment và sửa:
# bind 127.0.0.1
# requirepass YourRedisPassword123

# Khởi động Redis
sudo systemctl restart redis-server
sudo systemctl enable redis-server
```

### Bước 5: Cài Đặt Nginx

```bash
# Cài đặt Nginx
sudo apt install -y nginx

# Khởi động Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Kiểm tra status
sudo systemctl status nginx
```

### Bước 6: Deploy Application

```bash
# Tạo thư mục project
mkdir -p /home/ty7app/ty7_production
cd /home/ty7app/ty7_production

# Clone source code (hoặc upload files)
git clone https://github.com/your-repo/ty7-system.git .
# Hoặc upload files từ /workspace/python_7ty_system/

# Tạo virtual environment
python3 -m venv venv
source venv/bin/activate

# Cài đặt dependencies
pip install -r backend/requirements.txt
pip install gunicorn

# Tạo file environment
cat > .env << EOF
# Database
DATABASE_URL=postgresql://ty7user:SecurePassword123!@localhost:5432/ty7_db

# Redis
REDIS_URL=redis://:YourRedisPassword123@localhost:6379

# JWT
SECRET_KEY=your-super-secret-jwt-key-here-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Application
DEBUG=False
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000
EOF

# Set permissions
chmod 600 .env
```

### Bước 7: Tạo Systemd Service

```bash
# Tạo service file
sudo nano /etc/systemd/system/ty7-api.service
```

```ini
[Unit]
Description=7ty.vn FastAPI Application
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=ty7app
Group=ty7app
WorkingDirectory=/home/ty7app/ty7_production
Environment=PATH=/home/ty7app/ty7_production/venv/bin
EnvironmentFile=/home/ty7app/ty7_production/.env
ExecStart=/home/ty7app/ty7_production/venv/bin/gunicorn -c gunicorn.conf.py backend.main:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### Bước 8: Cấu Hình Gunicorn

```bash
# Tạo file cấu hình Gunicorn
cat > gunicorn.conf.py << EOF
import multiprocessing
import os

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# Logging
accesslog = "/var/log/ty7/access.log"
errorlog = "/var/log/ty7/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "ty7-api"

# Server mechanics
daemon = False
pidfile = "/tmp/ty7-api.pid"
user = "ty7app"
group = "ty7app"
tmp_upload_dir = None

# SSL (if needed)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"
EOF

# Tạo thư mục log
sudo mkdir -p /var/log/ty7
sudo chown ty7app:ty7app /var/log/ty7
```

### Bước 9: Cấu Hình Nginx

```bash
# Tạo cấu hình site
sudo nano /etc/nginx/sites-available/ty7.vn
```

```nginx
# Rate limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

# Upstream backend
upstream ty7_backend {
    server 127.0.0.1:8000;
    keepalive 32;
}

# HTTP to HTTPS redirect
server {
    listen 80;
    server_name ty7.vn www.ty7.vn;
    return 301 https://$server_name$request_uri;
}

# Main HTTPS server
server {
    listen 443 ssl http2;
    server_name ty7.vn www.ty7.vn;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/ty7.vn/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ty7.vn/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;";

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # Client settings
    client_max_body_size 10M;
    client_body_timeout 60s;
    client_header_timeout 60s;

    # Static files
    location /static/ {
        alias /home/ty7app/ty7_production/frontend/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # API endpoints with rate limiting
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://ty7_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Login endpoint with stricter rate limiting
    location /api/auth/login {
        limit_req zone=login burst=3 nodelay;
        
        proxy_pass http://ty7_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket
    location /ws/ {
        proxy_pass http://ty7_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }

    # Frontend applications
    location / {
        proxy_pass http://ty7_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/ty7.vn /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test cấu hình
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### Bước 10: SSL Certificate với Let's Encrypt

```bash
# Cài đặt Certbot
sudo apt install -y certbot python3-certbot-nginx

# Tạo certificate (thay ty7.vn bằng domain của bạn)
sudo certbot --nginx -d ty7.vn -d www.ty7.vn

# Tự động renew
sudo crontab -e
# Thêm dòng:
0 12 * * * /usr/bin/certbot renew --quiet
```

### Bước 11: Khởi Động Services

```bash
# Reload systemd
sudo systemctl daemon-reload

# Khởi động ty7-api service
sudo systemctl start ty7-api
sudo systemctl enable ty7-api

# Kiểm tra status
sudo systemctl status ty7-api
sudo systemctl status nginx
sudo systemctl status postgresql
sudo systemctl status redis-server

# Kiểm tra logs
sudo journalctl -u ty7-api -f
```

---

## ☁️ Option 2: AWS EC2 Deployment

### Bước 1: Tạo EC2 Instance

```bash
# Launch EC2 instance
# - AMI: Ubuntu 22.04 LTS
# - Instance Type: t3.medium (2 vCPU, 4GB RAM)
# - Security Group: HTTP (80), HTTPS (443), SSH (22)
# - Storage: 50GB gp3

# Connect via SSH
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### Bước 2: Setup RDS PostgreSQL

```bash
# Tạo RDS instance qua AWS Console:
# - Engine: PostgreSQL 15.x
# - Instance Class: db.t3.micro (for testing) hoặc db.t3.small (production)
# - Storage: 50GB gp3
# - Multi-AZ: Yes (for production)
# - Security Group: Allow port 5432 from EC2 security group

# Cập nhật DATABASE_URL trong .env
DATABASE_URL=postgresql://username:password@your-rds-endpoint:5432/ty7_db
```

### Bước 3: Setup ElastiCache Redis

```bash
# Tạo ElastiCache Redis cluster:
# - Engine: Redis 7.x
# - Node Type: cache.t3.micro
# - Security Group: Allow port 6379 from EC2

# Cập nhật REDIS_URL trong .env
REDIS_URL=redis://your-elasticache-endpoint:6379
```

### Bước 4: Load Balancer Setup

```bash
# Tạo Application Load Balancer:
# - Scheme: Internet-facing
# - IP address type: IPv4
# - Listeners: HTTP (80) và HTTPS (443)
# - Target Group: EC2 instances port 80
# - Health Check: /health

# Cấu hình SSL certificate qua AWS Certificate Manager
```

---

## 🌊 Option 3: DigitalOcean Deployment

### Bước 1: Tạo Droplet

```bash
# Tạo Droplet:
# - Image: Ubuntu 22.04 LTS
# - Plan: Basic $24/month (2 vCPU, 4GB RAM, 80GB SSD)
# - Datacenter: Singapore/US based on target users
# - Authentication: SSH Key

# Connect
ssh root@your-droplet-ip
```

### Bước 2: Managed Database

```bash
# Tạo Managed PostgreSQL Database:
# - Engine: PostgreSQL 15
# - Plan: Basic $15/month (1 vCPU, 1GB RAM, 10GB SSD)
# - Datacenter: Same as Droplet

# Tạo Managed Redis:
# - Plan: Basic $15/month
# - Datacenter: Same as Droplet

# Cập nhật connection strings trong .env
```

---

## 🐳 Option 4: Docker Production Setup

### Bước 1: Tạo Production Docker Files

```bash
# Tạo docker-compose.prod.yml
cat > docker-compose.prod.yml << EOF
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/sites-enabled:/etc/nginx/sites-enabled
      - ./ssl:/etc/ssl/certs
      - static_volume:/app/static
    depends_on:
      - api
    networks:
      - ty7_network

  api:
    build:
      context: .
      dockerfile: Dockerfile.prod
    environment:
      - DATABASE_URL=postgresql://ty7user:${DB_PASSWORD}@db:5432/ty7_db
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - static_volume:/app/static
    depends_on:
      - db
      - redis
    networks:
      - ty7_network
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=ty7_db
      - POSTGRES_USER=ty7user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - ty7_network
    deploy:
      restart_policy:
        condition: on-failure

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    networks:
      - ty7_network

  pgadmin:
    image: dpage/pgadmin4
    environment:
      - PGADMIN_DEFAULT_EMAIL=${PGADMIN_EMAIL}
      - PGADMIN_DEFAULT_PASSWORD=${PGADMIN_PASSWORD}
    ports:
      - "5050:80"
    depends_on:
      - db
    networks:
      - ty7_network

volumes:
  postgres_data:
  redis_data:
  static_volume:

networks:
  ty7_network:
    driver: bridge
EOF
```

### Bước 2: Production Dockerfile

```bash
# Tạo Dockerfile.prod
cat > Dockerfile.prod << EOF
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN addgroup --system app && adduser --system --group app

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy project
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Change ownership
RUN chown -R app:app /app

# Switch to app user
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run gunicorn
CMD ["gunicorn", "-c", "gunicorn.conf.py", "backend.main:app"]
EOF
```

### Bước 3: Environment File

```bash
# Tạo .env.prod
cat > .env.prod << EOF
# Database
DB_PASSWORD=SecureDbPassword123!

# Redis
REDIS_PASSWORD=SecureRedisPassword123!

# JWT
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production

# pgAdmin
PGADMIN_EMAIL=admin@ty7.vn
PGADMIN_PASSWORD=SecurePgAdminPassword123!

# Application
ENVIRONMENT=production
DEBUG=False
EOF
```

### Bước 4: Deploy với Docker

```bash
# Build và start services
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --build

# Kiểm tra logs
docker-compose -f docker-compose.prod.yml logs -f api

# Scale API service
docker-compose -f docker-compose.prod.yml up -d --scale api=3
```

---

## 📊 Monitoring & Logging

### Bước 1: Setup Monitoring với Prometheus

```bash
# Cài đặt Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.40.0/prometheus-2.40.0.linux-amd64.tar.gz
tar xvfz prometheus-*.tar.gz
sudo mv prometheus-2.40.0.linux-amd64 /opt/prometheus
sudo useradd --no-create-home --shell /bin/false prometheus
sudo chown -R prometheus:prometheus /opt/prometheus

# Tạo systemd service
sudo nano /etc/systemd/system/prometheus.service
```

```ini
[Unit]
Description=Prometheus
Wants=network-online.target
After=network-online.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/opt/prometheus/prometheus \
    --config.file /opt/prometheus/prometheus.yml \
    --storage.tsdb.path /opt/prometheus/data \
    --web.console.templates=/opt/prometheus/consoles \
    --web.console.libraries=/opt/prometheus/console_libraries \
    --web.listen-address=0.0.0.0:9090

[Install]
WantedBy=multi-user.target
```

### Bước 2: Setup Grafana

```bash
# Cài đặt Grafana
sudo apt-get install -y software-properties-common
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo apt-get update
sudo apt-get install grafana

# Khởi động Grafana
sudo systemctl start grafana-server
sudo systemctl enable grafana-server

# Access: http://your-server:3000 (admin/admin)
```

### Bước 3: Log Management

```bash
# Cấu hình logrotate
sudo nano /etc/logrotate.d/ty7
```

```
/var/log/ty7/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 ty7app ty7app
    postrotate
        systemctl reload ty7-api
    endscript
}
```

---

## 💾 Backup & Recovery

### Bước 1: Database Backup Script

```bash
# Tạo backup script
cat > /home/ty7app/backup_db.sh << EOF
#!/bin/bash

# Configuration
DB_NAME="ty7_db"
DB_USER="ty7user"
DB_HOST="localhost"
BACKUP_DIR="/home/ty7app/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/ty7_db_$DATE.sql"

# Create backup directory
mkdir -p $BACKUP_DIR

# Create backup
PGPASSWORD="SecurePassword123!" pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > $BACKUP_FILE

# Compress backup
gzip $BACKUP_FILE

# Remove backups older than 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

# Upload to S3 (optional)
# aws s3 cp $BACKUP_FILE.gz s3://your-backup-bucket/database/

echo "Backup completed: $BACKUP_FILE.gz"
EOF

chmod +x /home/ty7app/backup_db.sh

# Thêm vào crontab
crontab -e
# Thêm dòng: 0 2 * * * /home/ty7app/backup_db.sh
```

### Bước 2: Application Backup

```bash
# Tạo application backup script
cat > /home/ty7app/backup_app.sh << EOF
#!/bin/bash

BACKUP_DIR="/home/ty7app/backups"
DATE=$(date +%Y%m%d_%H%M%S)
APP_DIR="/home/ty7app/ty7_production"

# Create backup
tar -czf $BACKUP_DIR/ty7_app_$DATE.tar.gz -C $APP_DIR .

# Remove old backups
find $BACKUP_DIR -name "ty7_app_*.tar.gz" -mtime +7 -delete

echo "Application backup completed: ty7_app_$DATE.tar.gz"
EOF

chmod +x /home/ty7app/backup_app.sh
```

### Bước 3: Recovery Procedures

```bash
# Database Recovery
# 1. Stop application
sudo systemctl stop ty7-api

# 2. Restore database
PGPASSWORD="SecurePassword123!" psql -h localhost -U ty7user -d ty7_db < backup_file.sql

# 3. Start application
sudo systemctl start ty7-api

# Application Recovery
# 1. Stop services
sudo systemctl stop ty7-api nginx

# 2. Restore files
cd /home/ty7app
tar -xzf backups/ty7_app_YYYYMMDD_HHMMSS.tar.gz -C ty7_production/

# 3. Start services
sudo systemctl start ty7-api nginx
```

---

## 🔒 Security Best Practices

### Bước 1: Firewall Configuration

```bash
# Cấu hình UFW
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Kiểm tra status
sudo ufw status verbose
```

### Bước 2: SSH Hardening

```bash
# Cấu hình SSH
sudo nano /etc/ssh/sshd_config

# Thêm/sửa các dòng sau:
Port 2222  # Change default port
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 2

# Restart SSH
sudo systemctl restart ssh
```

### Bước 3: Fail2Ban

```bash
# Cài đặt Fail2Ban
sudo apt install -y fail2ban

# Cấu hình
sudo nano /etc/fail2ban/jail.local
```

```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = 2222

[nginx-http-auth]
enabled = true

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
logpath = /var/log/nginx/error.log
```

```bash
# Khởi động Fail2Ban
sudo systemctl start fail2ban
sudo systemctl enable fail2ban
```

---

## 🚀 Performance Optimization

### Bước 1: PostgreSQL Tuning

```bash
# Chỉnh sửa postgresql.conf
sudo nano /etc/postgresql/15/main/postgresql.conf
```

```ini
# Memory settings
shared_buffers = 256MB                 # 25% of RAM
effective_cache_size = 1GB             # 75% of RAM
work_mem = 4MB
maintenance_work_mem = 64MB

# Checkpoint settings
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100

# Connection settings
max_connections = 200

# Logging
log_statement = 'mod'
log_min_duration_statement = 1000
log_line_prefix = '%t [%p-%l] %q%u@%d '
```

### Bước 2: Redis Optimization

```bash
# Chỉnh sửa redis.conf
sudo nano /etc/redis/redis.conf
```

```ini
# Memory management
maxmemory 512mb
maxmemory-policy allkeys-lru

# Persistence
save 900 1
save 300 10
save 60 10000

# Network
tcp-keepalive 300
timeout 0
```

### Bước 3: Nginx Optimization

```bash
# Chỉnh sửa nginx.conf
sudo nano /etc/nginx/nginx.conf
```

```nginx
worker_processes auto;
worker_rlimit_nofile 65535;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    # Basic settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    
    # Buffer settings
    client_body_buffer_size 128k;
    client_max_body_size 10m;
    client_header_buffer_size 1k;
    large_client_header_buffers 4 4k;
    output_buffers 1 32k;
    postpone_output 1460;
    
    # Gzip settings
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json;
}
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Service Won't Start

```bash
# Kiểm tra logs
sudo journalctl -u ty7-api -f

# Kiểm tra cấu hình
python3 -m py_compile backend/main.py

# Kiểm tra dependencies
source venv/bin/activate
pip check
```

#### 2. Database Connection Issues

```bash
# Test connection
psql -h localhost -U ty7user -d ty7_db

# Kiểm tra PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-15-main.log

# Kiểm tra firewall
sudo ufw status
```

#### 3. High Memory Usage

```bash
# Kiểm tra memory usage
free -h
htop

# Kiểm tra PostgreSQL connections
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"

# Restart services
sudo systemctl restart ty7-api
```

#### 4. SSL Certificate Issues

```bash
# Kiểm tra certificate
sudo certbot certificates

# Renew certificate
sudo certbot renew --dry-run

# Test SSL
openssl s_client -connect ty7.vn:443
```

### Performance Monitoring

```bash
# Kiểm tra system resources
htop
iotop
nethogs

# Kiểm tra database performance
sudo -u postgres psql -d ty7_db -c "SELECT query, calls, total_time, mean_time FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"

# Kiểm tra Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## 📞 Support & Maintenance

### Daily Tasks
- [ ] Kiểm tra system resources (CPU, RAM, Disk)
- [ ] Kiểm tra application logs
- [ ] Kiểm tra database connections
- [ ] Backup verification

### Weekly Tasks
- [ ] Update system packages
- [ ] Review security logs
- [ ] Performance analysis
- [ ] SSL certificate check

### Monthly Tasks
- [ ] Full system backup
- [ ] Security audit
- [ ] Performance optimization
- [ ] Capacity planning

---

## 📧 Contact

Nếu gặp vấn đề trong quá trình deploy, vui lòng liên hệ:

- **Email:** support@ty7.vn
- **Hotline:** 1900-7777
- **Documentation:** https://docs.ty7.vn

---

**🎉 Chúc mừng! Hệ thống 7tỷ.vn đã sẵn sàng phục vụ production!**

> **Lưu ý:** Hãy thay đổi tất cả passwords mặc định và cấu hình domain name thực tế trước khi đưa vào sử dụng.