# 🏦 7tỷ.vn - Hệ Thống Thu Hộ Tiền Điện

## 📖 Giới Thiệu

7tỷ.vn là hệ thống thu hộ tiền điện toàn diện được xây dựng với Python FastAPI và PostgreSQL. Hệ thống cung cấp 3 ứng dụng web đồng bộ cho Admin, Đại lý và Khách hàng với tính năng real-time synchronization.

### ✨ Tính Năng Chính

- **🔐 Xác thực JWT** với role-based access control
- **⚡ Real-time Updates** qua WebSocket
- **📱 3 Web Applications** đồng bộ hoàn toàn
- **💳 Multi-payment Gateway** integration
- **📊 Dashboard & Analytics** real-time
- **🌐 100% Vietnamese** interface
- **🐳 Docker Ready** cho development và production

---

## 🏗️ Kiến Trúc Hệ Thống

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Admin Panel   │    │   Agent PWA     │    │  Customer App   │
│   (Quản trị)    │    │   (Đại lý)      │    │  (Khách hàng)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  FastAPI Server │
                    │  (WebSocket +   │
                    │   REST APIs)    │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │   PostgreSQL    │
                    │   + Redis       │
                    │   + pgAdmin     │
                    └─────────────────┘
```

---

## 🚀 Quick Start

### Yêu Cầu Hệ Thống

- **Docker** 20.10+
- **Docker Compose** 2.0+
- **Git** 2.30+

### Bước 1: Clone Repository

```bash
git clone https://github.com/your-repo/7ty-system.git
cd 7ty-system
```

### Bước 2: Khởi Động Development Environment

```bash
# Khởi động tất cả services
docker-compose up -d

# Xem logs
docker-compose logs -f api

# Kiểm tra status
docker-compose ps
```

### Bước 3: Truy Cập Ứng Dụng

| Service | URL | Credentials |
|---------|-----|-------------|
| **Main Portal** | http://localhost | N/A |
| **Admin Panel** | http://localhost/admin | admin / admin123 |
| **Agent App** | http://localhost/agent | demo / 123456 |
| **Customer App** | http://localhost/customer | N/A |
| **pgAdmin** | http://localhost:5050 | admin@ty7.vn / ty7admin123 |
| **Redis Commander** | http://localhost:8081 | admin / ty7redis123 |

---

## 📁 Cấu Trúc Project

```
python_7ty_system/
├── backend/                    # FastAPI Backend
│   ├── main.py                # Main application file
│   └── requirements.txt       # Python dependencies
├── frontend/                  # Frontend Applications
│   ├── admin/                 # Admin Panel
│   ├── agent/                 # Agent PWA App
│   └── customer/              # Customer App
├── database/                  # Database Setup
│   ├── init.sql              # Database initialization
│   └── pgadmin_servers.json  # pgAdmin configuration
├── nginx/                     # Nginx Configuration
│   └── nginx.conf            # Reverse proxy config
├── docker/                    # Docker Files
├── docs/                      # Documentation
├── docker-compose.yml         # Development setup
├── Dockerfile                 # API container
└── README.md                  # This file
```

---

## 🎯 Tính Năng Chi Tiết

### 👑 Admin Panel Features

- **📊 Dashboard**: Real-time statistics và analytics
- **📦 Warehouse Management**: Quản lý kho hóa đơn
- **👥 Agent Management**: Quản lý đại lý và hoa hồng
- **👤 Customer Management**: Quản lý khách hàng
- **💳 Transaction Monitoring**: Theo dõi giao dịch real-time
- **📈 Reports & Analytics**: Báo cáo doanh thu chi tiết
- **⚙️ System Settings**: Cấu hình hệ thống

### 📱 Agent PWA Features

- **💰 Wallet Management**: Quản lý ví điện tử
- **🔍 Bill Lookup**: Tra cứu hóa đơn điện
- **💳 Payment Processing**: Xử lý thanh toán
- **📊 Performance Dashboard**: Thống kê hiệu suất
- **📋 Transaction History**: Lịch sử giao dịch
- **🖨️ Receipt Printing**: In hóa đơn Bluetooth
- **📱 PWA Support**: Cài đặt như app mobile

### 🛒 Customer App Features

- **⏱️ 5-Minute Timer**: Session timeout security
- **🔍 Bill Lookup**: Tra cứu hóa đơn nhanh
- **💳 Multi-Payment**: MoMo, Banking, ZaloPay, QR
- **📄 Receipt Download**: Tải hóa đơn PDF
- **🔒 Secure Payment**: Bảo mật cao
- **📱 Mobile Optimized**: Tối ưu cho mobile

---

## 🔧 Development

### Local Development Setup

```bash
# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Cài đặt dependencies
cd backend
pip install -r requirements.txt

# Chạy development server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Database Management

```bash
# Kết nối PostgreSQL
docker exec -it ty7_postgres psql -U ty7user -d ty7_db

# Backup database
docker exec ty7_postgres pg_dump -U ty7user ty7_db > backup.sql

# Restore database
docker exec -i ty7_postgres psql -U ty7user ty7_db < backup.sql

# View logs
docker-compose logs -f db
```

### API Testing

```bash
# Health check
curl http://localhost:8000/health

# Login API
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Get dashboard stats (với JWT token)
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:8000/api/dashboard/stats
```

---

## 🐳 Production Deployment

### Option 1: VPS Deployment

Chi tiết trong [PRODUCTION_DEPLOYMENT_GUIDE.md](PRODUCTION_DEPLOYMENT_GUIDE.md)

### Option 2: Docker Production

```bash
# Tạo production environment file
cp .env.example .env.prod
# Chỉnh sửa .env.prod với production values

# Deploy với production config
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# Scale API service
docker-compose -f docker-compose.prod.yml up -d --scale api=3
```

### Option 3: Cloud Deployment

- **AWS**: EC2 + RDS + ElastiCache + ALB
- **DigitalOcean**: Droplet + Managed Database
- **Google Cloud**: Compute Engine + Cloud SQL
- **Azure**: VM + Azure Database for PostgreSQL

---

## 📊 API Documentation

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | User login |
| GET | `/api/auth/me` | Get current user info |

### Core Business Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard/stats` | Dashboard statistics |
| GET/POST | `/api/bills` | Bills management |
| GET/POST | `/api/agents` | Agents management |
| GET/POST | `/api/customers` | Customers management |
| GET/POST | `/api/transactions` | Transactions management |
| POST | `/api/bills/lookup` | Bill lookup from DailyShopee |

### WebSocket Endpoints

| Endpoint | Description |
|----------|-------------|
| `/ws/admin` | Admin real-time updates |
| `/ws/agent` | Agent real-time updates |
| `/ws/customer` | Customer real-time updates |

---

## 🔒 Security

### Authentication & Authorization

- **JWT Tokens** với 24h expiration
- **Role-based Access Control** (Admin, Agent, Customer)
- **bcrypt Password Hashing**
- **Rate Limiting** trên API endpoints

### Security Headers

- **CORS Protection**
- **XSS Protection**
- **CSRF Protection**
- **Content Security Policy**
- **HTTPS Enforcement** (production)

### Data Protection

- **Input Validation** với Pydantic
- **SQL Injection Protection** với SQLAlchemy
- **Environment Variables** cho sensitive data
- **Database Encryption** at rest

---

## 📈 Performance

### Optimization Features

- **Connection Pooling** cho PostgreSQL
- **Redis Caching** cho session và data
- **Nginx Reverse Proxy** với load balancing
- **Gzip Compression** cho static files
- **Database Indexing** cho query optimization

### Monitoring

- **Health Check Endpoints**
- **Application Metrics** với Prometheus
- **Database Performance** monitoring
- **Real-time Logging** với structured logs

---

## 🧪 Testing

### Unit Tests

```bash
cd backend
python -m pytest tests/ -v
```

### Integration Tests

```bash
# Test API endpoints
python -m pytest tests/test_api.py -v

# Test WebSocket connections
python -m pytest tests/test_websocket.py -v
```

### Load Testing

```bash
# Cài đặt artillery
npm install -g artillery

# Chạy load test
artillery run tests/load-test.yml
```

---

## 📝 Environment Variables

### Development (.env)

```env
DATABASE_URL=postgresql://ty7user:ty7password123@localhost:5432/ty7_db
REDIS_URL=redis://:ty7redis123@localhost:6379
SECRET_KEY=ty7-development-secret-key
DEBUG=True
ENVIRONMENT=development
```

### Production (.env.prod)

```env
DATABASE_URL=postgresql://user:password@prod-db:5432/ty7_db
REDIS_URL=redis://:password@prod-redis:6379
SECRET_KEY=your-super-secure-production-secret-key
DEBUG=False
ENVIRONMENT=production
ALLOWED_HOSTS=ty7.vn,www.ty7.vn
```

---

## 🤝 Contributing

### Development Workflow

1. Fork repository
2. Tạo feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push branch: `git push origin feature/amazing-feature`
5. Tạo Pull Request

### Code Standards

- **Python**: PEP 8 compliance
- **JavaScript**: ES6+ standards
- **SQL**: PostgreSQL best practices
- **Documentation**: Vietnamese comments

---

## 📞 Support

### Liên Hệ

- **Email**: support@7ty.vn
- **Hotline**: 1900-7777
- **Website**: https://7ty.vn
- **Documentation**: https://docs.7ty.vn

### Bug Reports

Tạo issue trên GitHub với thông tin:
- Mô tả chi tiết lỗi
- Steps to reproduce
- Expected vs actual behavior
- Screenshots (nếu có)
- Environment information

---

## 📄 License

Copyright © 2024 7tỷ.vn. All rights reserved.

---

## 🎉 Acknowledgments

- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Powerful relational database
- **Redis** - In-memory data structure store
- **Docker** - Containerization platform
- **Nginx** - High-performance web server

---

**🚀 Happy Coding with 7tỷ.vn System!**