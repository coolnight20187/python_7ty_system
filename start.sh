#!/bin/bash
# 7tỷ.vn System Startup Script
# Quick start for development and testing

set -e

echo "🚀 Starting 7tỷ.vn System..."
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create environment file if not exists
if [ ! -f .env ]; then
    print_info "Creating .env file..."
    cat > .env << EOF
# 7tỷ.vn Environment Configuration
DATABASE_URL=postgresql://ty7user:ty7password@postgres:5432/ty7_db
REDIS_URL=redis://:ty7redis@redis:6379/0
SECRET_KEY=ty7-super-secret-key-2024-production
CORS_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
DEBUG=true
LOG_LEVEL=info

# Database Configuration
POSTGRES_DB=ty7_db
POSTGRES_USER=ty7user
POSTGRES_PASSWORD=ty7password

# Redis Configuration
REDIS_PASSWORD=ty7redis
EOF
    print_status ".env file created"
fi

# Stop any existing containers
print_info "Stopping existing containers..."
docker-compose down --remove-orphans 2>/dev/null || true

# Pull latest images
print_info "Pulling Docker images..."
docker-compose pull

# Build and start services
print_info "Building and starting services..."
docker-compose up -d --build

# Wait for services to be ready
print_info "Waiting for services to start..."
sleep 10

# Check service health
print_info "Checking service health..."

# Check PostgreSQL
if docker-compose exec -T postgres pg_isready -U ty7user -d ty7_db >/dev/null 2>&1; then
    print_status "PostgreSQL is ready"
else
    print_warning "PostgreSQL is not ready yet, waiting..."
    sleep 5
fi

# Check Redis
if docker-compose exec -T redis redis-cli -a ty7redis ping >/dev/null 2>&1; then
    print_status "Redis is ready"
else
    print_warning "Redis is not ready yet, waiting..."
    sleep 5
fi

# Check FastAPI backend
print_info "Waiting for FastAPI backend..."
for i in {1..30}; do
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        print_status "FastAPI backend is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "FastAPI backend failed to start"
        docker-compose logs backend
        exit 1
    fi
    sleep 2
done

# Show service status
echo ""
echo "🎉 7tỷ.vn System Started Successfully!"
echo "====================================="
echo ""
print_info "Service URLs:"
echo "  🌐 Main Portal:    http://localhost:8000/"
echo "  🏢 Admin Panel:    http://localhost:8000/admin"
echo "  📱 Agent App:      http://localhost:8000/agent"
echo "  👤 Customer App:   http://localhost:8000/customer"
echo "  📖 API Docs:       http://localhost:8000/docs"
echo ""
print_info "Demo Accounts:"
echo "  👑 Admin:     admin / admin123"
echo "  🤝 Agent:     demo / 123456 (5M VND wallet)"
echo "  📞 Test Phones: 0123456789, 0987654321"
echo ""
print_info "Database Access:"
echo "  🐘 PostgreSQL: localhost:5432 (ty7user/ty7password)"
echo "  🔴 Redis:      localhost:6379 (password: ty7redis)"
echo ""

# Show container status
print_info "Container Status:"
docker-compose ps

echo ""
print_info "Useful Commands:"
echo "  📊 View logs:      docker-compose logs -f"
echo "  🔄 Restart:        docker-compose restart"
echo "  🛑 Stop:           docker-compose down"
echo "  🗑️  Clean up:       docker-compose down -v --remove-orphans"
echo ""

# Check if all services are running
if [ "$(docker-compose ps -q | wc -l)" -eq 3 ]; then
    print_status "All services are running successfully!"
    echo ""
    print_info "🎯 Ready for testing! Visit http://localhost:8000/ to get started."
else
    print_warning "Some services may not be running properly. Check logs with: docker-compose logs"
fi

echo ""
print_info "Press Ctrl+C to view logs in real-time, or run 'docker-compose logs -f' in another terminal"
echo ""

# Follow logs (optional)
read -p "Do you want to follow logs? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose logs -f
fi