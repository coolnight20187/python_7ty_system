"""
7tỷ.vn FastAPI Backend Application
Complete Vietnamese bill payment system
"""

import os
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from contextlib import asynccontextmanager

# Import routers
from routers import (
    auth_router,
    admin_router,
    agent_router,
    customer_router,
    bill_router,
    transaction_router,
    approval_router,
    file_router
)

# Import database
from database import init_database

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting 7tỷ.vn Backend System...")
    init_database()
    print("✅ Database initialized")
    yield
    # Shutdown
    print("🛑 Shutting down 7tỷ.vn Backend System...")

# FastAPI application
app = FastAPI(
    title="7tỷ.vn API",
    description="Hệ thống thanh toán hóa đơn điện 7tỷ.vn - Complete Vietnamese Bill Payment System",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth_router, prefix="/api/auth", tags=["🔐 Xác thực"])
app.include_router(admin_router, prefix="/api/admin", tags=["👑 Quản trị"])
app.include_router(agent_router, prefix="/api/agent", tags=["🏢 Đại lý"])
app.include_router(customer_router, prefix="/api/customer", tags=["👤 Khách hàng"])
app.include_router(bill_router, prefix="/api/bills", tags=["⚡ Hóa đơn điện"])
app.include_router(transaction_router, prefix="/api/transactions", tags=["💰 Giao dịch"])
app.include_router(approval_router, prefix="/api/approvals", tags=["✅ Phê duyệt"])
app.include_router(file_router, prefix="/api/files", tags=["📁 Tệp tin"])

# Health check endpoint
@app.get("/health")
async def health_check():
    """Kiểm tra tình trạng hệ thống"""
    return {
        "status": "healthy",
        "message": "Hệ thống 7tỷ.vn đang hoạt động bình thường",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    """Trang chủ API"""
    return {
        "message": "🏠 Chào mừng đến với API 7tỷ.vn",
        "description": "Hệ thống thanh toán hóa đơn điện hoàn chỉnh",
        "version": "2.0.0",
        "docs": "/docs",
        "endpoints": {
            "admin": "/admin",
            "agent": "/agent", 
            "customer": "/customer",
            "api_docs": "/docs"
        }
    }

# Static files (if needed)
if os.path.exists("../frontend"):
    app.mount("/static", StaticFiles(directory="../frontend"), name="static")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Không tìm thấy",
            "message": "Endpoint không tồn tại",
            "path": str(request.url.path)
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Lỗi hệ thống",
            "message": "Đã xảy ra lỗi không mong muốn",
            "detail": str(exc) if os.getenv("DEBUG") else "Vui lòng liên hệ quản trị viên"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )