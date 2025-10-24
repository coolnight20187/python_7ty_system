"""
7tỷ.vn FastAPI Backend Application (SQLite Version)
Complete backend server for bill payment system
"""

import os
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
from pydantic import BaseModel
import jwt
import bcrypt
import json
import uuid
from pathlib import Path

# Configuration
DATABASE_PATH = "/workspace/python_7ty_system/ty7_system.db"
SECRET_KEY = os.getenv("SECRET_KEY", "ty7-super-secret-key-2024-production")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000").split(",")

# FastAPI app instance
app = FastAPI(
    title="7tỷ.vn API",
    description="Complete bill payment system API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS + ["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Pydantic models
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user_id: str
    role: str

class BillLookupRequest(BaseModel):
    customer_code: str
    provider_id: str

class BulkLookupRequest(BaseModel):
    customer_codes: List[str]
    provider_id: str

class PaymentRequest(BaseModel):
    bill_id: str
    payment_method: str
    amount: float

class User(BaseModel):
    id: str
    username: str
    role: str
    is_active: bool

# Database connection
def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# JWT token functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "database": "connected"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

# Authentication endpoints
@app.post("/api/auth/login", response_model=LoginResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """User authentication"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user from database
        cursor.execute(
            "SELECT id, username, password_hash, role, is_active FROM users WHERE username = ?",
            (form_data.username,)
        )
        user = cursor.fetchone()
        conn.close()
        
        if not user or not user['is_active']:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Verify password
        if not bcrypt.checkpw(form_data.password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Create access token
        access_token = create_access_token(
            data={"sub": str(user['id']), "username": user['username'], "role": user['role']}
        )
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=86400,  # 24 hours
            user_id=str(user['id']),
            role=user['role']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@app.get("/api/auth/me")
async def get_current_user(token_data: dict = Depends(verify_token)):
    """Get current user information"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, role, is_active, created_at FROM users WHERE id = ?",
            (token_data["sub"],)
        )
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        return {
            "id": str(user['id']),
            "username": user['username'],
            "role": user['role'],
            "is_active": bool(user['is_active']),
            "created_at": user['created_at']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user: {str(e)}")

# Dashboard endpoints
@app.get("/api/dashboard/stats")
async def get_dashboard_stats(token_data: dict = Depends(verify_token)):
    """Get dashboard statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get various statistics
        cursor.execute("SELECT COUNT(*) as count FROM users")
        total_users = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM agents")
        total_agents = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM customers")
        total_customers = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM transactions")
        total_transactions = cursor.fetchone()['count']
        
        cursor.execute("SELECT COALESCE(SUM(amount), 0) as revenue FROM transactions WHERE status = 'completed'")
        total_revenue = cursor.fetchone()['revenue'] or 0
        
        conn.close()
        
        return {
            "total_users": total_users,
            "total_agents": total_agents,
            "total_customers": total_customers,
            "total_transactions": total_transactions,
            "total_revenue": float(total_revenue),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

# Bill management endpoints
@app.post("/api/bills/lookup")
async def lookup_bill(request: BillLookupRequest):
    """Lookup bill by customer code and provider"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM bills 
            WHERE customer_code = ? AND provider_id = ? AND status = 'available'
            LIMIT 1
        """, (request.customer_code, request.provider_id))
        
        bill = cursor.fetchone()
        conn.close()
        
        if not bill:
            raise HTTPException(status_code=404, detail="Bill not found")
        
        return {
            "id": str(bill['id']),
            "customer_code": bill['customer_code'],
            "customer_name": bill['customer_name'],
            "customer_address": bill['customer_address'],
            "total_amount": float(bill['total_amount']),
            "due_date": bill['due_date'],
            "provider_name": bill['provider_name'],
            "status": bill['status'],
            "created_at": bill['created_at']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bill lookup failed: {str(e)}")

@app.post("/api/bills/bulk-lookup")
async def bulk_lookup_bills(request: BulkLookupRequest):
    """Bulk lookup bills by customer codes and provider"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        results = []
        
        for customer_code in request.customer_codes:
            try:
                # Try to find existing bill first
                cursor.execute("""
                    SELECT * FROM bills 
                    WHERE customer_code = ? AND provider_id = ?
                    LIMIT 1
                """, (customer_code.strip(), request.provider_id))
                
                bill = cursor.fetchone()
                
                if bill:
                    results.append({
                        "id": str(bill['id']),
                        "customer_code": bill['customer_code'],
                        "customer_name": bill['customer_name'],
                        "customer_address": bill['customer_address'],
                        "amount_previous": float(bill['previous_amount']) / 100,
                        "amount_current": float(bill['current_amount']) / 100,
                        "total_amount": float(bill['total_amount']) / 100,
                        "period": bill['period'],
                        "provider_name": bill['provider_name'],
                        "status": bill['status'],
                        "success": True
                    })
                else:
                    # Generate mock data for demo (in production, call external API)
                    mock_data = {
                        "customer_code": customer_code.strip(),
                        "customer_name": f"Khách hàng {customer_code[-4:]}",
                        "customer_address": f"Địa chỉ {customer_code[-4:]}",
                        "amount_previous": 0,
                        "amount_current": 150000 + (hash(customer_code) % 500000),
                        "period": "11/2024",
                        "provider_name": "Điện Miền Nam",
                        "status": "available",
                        "success": True
                    }
                    mock_data["total_amount"] = mock_data["amount_previous"] + mock_data["amount_current"]
                    results.append(mock_data)
                    
            except Exception as e:
                results.append({
                    "customer_code": customer_code.strip(),
                    "customer_name": "Lỗi tra cứu",
                    "customer_address": f"Error: {str(e)}",
                    "amount_previous": 0,
                    "amount_current": 0,
                    "total_amount": 0,
                    "period": "N/A",
                    "provider_name": "N/A",
                    "status": "error",
                    "success": False,
                    "error": str(e)
                })
        
        conn.close()
        
        return {
            "results": results,
            "total_found": len([r for r in results if r["success"]]),
            "total_requested": len(request.customer_codes),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk lookup failed: {str(e)}")

@app.get("/api/bills")
async def get_bills(skip: int = 0, limit: int = 50, token_data: dict = Depends(verify_token)):
    """Get bills list"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM bills 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        """, (limit, skip))
        
        bills = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": str(bill['id']),
                "customer_code": bill['customer_code'],
                "customer_name": bill['customer_name'],
                "customer_address": bill['customer_address'],
                "provider_name": bill['provider_name'],
                "period": bill['period'],
                "previous_amount": bill['previous_amount'],
                "current_amount": bill['current_amount'],
                "total_amount": bill['total_amount'],
                "status": bill['status'],
                "created_at": bill['created_at']
            }
            for bill in bills
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get bills: {str(e)}")

@app.post("/api/bills")
async def create_bill(bill_data: dict, token_data: dict = Depends(verify_token)):
    """Create new bill"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        bill_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO bills (id, customer_code, customer_name, customer_address, 
                             provider_id, provider_name, period, previous_amount, 
                             current_amount, total_amount, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            bill_id,
            bill_data['customer_code'],
            bill_data['customer_name'],
            bill_data['address'],
            bill_data['provider_id'],
            bill_data['provider_name'],
            bill_data['period'],
            bill_data['previous_amount'],
            bill_data['current_amount'],
            bill_data['total_amount'],
            'available'
        ))
        
        conn.commit()
        conn.close()
        
        return {"id": bill_id, "status": "created"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create bill: {str(e)}")

# Agent endpoints
@app.get("/api/agents")
async def get_agents(token_data: dict = Depends(verify_token)):
    """Get agents list (admin only)"""
    try:
        if token_data.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Access denied")
            
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.*, u.username 
            FROM agents a 
            LEFT JOIN users u ON a.user_id = u.id 
            ORDER BY a.created_at DESC
        """)
        
        agents = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": str(agent['id']),
                "code": agent['code'],
                "name": agent['name'],
                "phone": agent['phone'],
                "wallet_balance": agent['wallet_balance'],
                "commission_rate": agent['commission_rate'],
                "status": agent['status'],
                "username": agent['username'] or 'N/A',
                "created_at": agent['created_at']
            }
            for agent in agents
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agents: {str(e)}")

# Transaction endpoints
@app.get("/api/transactions")
async def get_transactions(skip: int = 0, limit: int = 50, token_data: dict = Depends(verify_token)):
    """Get transactions list"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Admin can see all, agents only their own
        if token_data.get("role") == "admin":
            cursor.execute("""
                SELECT * FROM transactions
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (limit, skip))
        else:
            cursor.execute("""
                SELECT * FROM transactions
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (token_data["sub"], limit, skip))
        
        transactions = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": str(txn['id']),
                "transaction_code": txn['transaction_code'],
                "type": txn['type'],
                "amount": txn['amount'],
                "payment_method": txn['payment_method'],
                "status": txn['status'],
                "username": txn['username'],
                "customer_name": txn['customer_name'],
                "customer_code": txn['customer_code'],
                "created_at": txn['created_at']
            }
            for txn in transactions
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get transactions: {str(e)}")

# Provider endpoints
@app.get("/api/providers")
async def get_providers():
    """Get providers list"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, code, type, status FROM providers WHERE status = 'active' ORDER BY name"
        )
        
        providers = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": str(provider['id']),
                "name": provider['name'],
                "code": provider['code'],
                "type": provider['type'],
                "status": provider['status']
            }
            for provider in providers
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get providers: {str(e)}")

# Static file serving for frontend applications
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Frontend routes
@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Main portal page"""
    try:
        with open("frontend/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="""
        <html>
        <head><title>7tỷ.vn - Bill Payment System</title></head>
        <body>
            <h1>🏠 7tỷ.vn - Hệ thống thanh toán hóa đơn</h1>
            <p>Chào mừng đến với hệ thống thanh toán hóa đơn 7tỷ.vn</p>
            <ul>
                <li><a href="/admin">🏢 Admin Panel</a></li>
                <li><a href="/agent">📱 Agent App</a></li>
                <li><a href="/customer">👤 Customer App</a></li>
                <li><a href="/docs">📖 API Documentation</a></li>
            </ul>
        </body>
        </html>
        """)

@app.get("/admin/")
async def admin_panel_redirect():
    """Redirect /admin/ to /admin"""
    return RedirectResponse(url="/admin", status_code=301)

@app.get("/admin")
async def admin_panel():
    """Admin panel"""
    try:
        with open("frontend/admin/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Admin Panel - File not found</h1>")

@app.get("/agent", response_class=HTMLResponse)
async def agent_app():
    """Agent PWA"""
    try:
        with open("frontend/agent/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Agent App - File not found</h1>")

@app.get("/customer", response_class=HTMLResponse)
async def customer_app():
    """Customer app"""
    try:
        with open("frontend/customer/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Customer App - File not found</h1>")

# Catch-all route for SPA routing
@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    """Catch-all route for frontend routing"""
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    # Handle admin routes properly
    if full_path.startswith("admin"):
        return RedirectResponse(url="/admin", status_code=301)
    
    # Try to serve static files
    file_path = Path(f"frontend/{full_path}")
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    
    # Default to main page
    return await read_root()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)