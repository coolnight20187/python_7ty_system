"""
Admin API endpoints for 7tỷ.vn system
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from pydantic import BaseModel
from datetime import datetime, date

from ..database import get_db
from ..models.users import User
from ..models.agents import Agent
from ..models.customers import Customer
from ..models.transactions import Transaction
from ..models.bills import Bill
from ..models.audit import AuditLog
from ..auth.dependencies import get_current_admin_user
from ..auth.password import get_password_hash

router = APIRouter()

# Pydantic models
class AdminStats(BaseModel):
    total_users: int
    total_agents: int
    total_customers: int
    total_transactions: int
    total_bills: int
    today_transactions: int
    today_revenue: float

class UserCreate(BaseModel):
    ten_dang_nhap: str
    email: str
    ho_ten: str
    so_dien_thoai: str
    vai_tro: str
    mat_khau: str

class UserUpdate(BaseModel):
    email: Optional[str] = None
    ho_ten: Optional[str] = None
    so_dien_thoai: Optional[str] = None
    trang_thai: Optional[str] = None

@router.get("/stats", response_model=AdminStats)
async def get_admin_stats(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Lấy thống kê tổng quan hệ thống"""
    try:
        today = date.today()
        
        stats = AdminStats(
            total_users=db.query(User).count(),
            total_agents=db.query(Agent).count(),
            total_customers=db.query(Customer).count(),
            total_transactions=db.query(Transaction).count(),
            total_bills=db.query(Bill).count(),
            today_transactions=db.query(Transaction).filter(
                func.date(Transaction.thoi_gian_tao) == today
            ).count(),
            today_revenue=db.query(func.sum(Transaction.so_tien)).filter(
                and_(
                    func.date(Transaction.thoi_gian_tao) == today,
                    Transaction.trang_thai == 'thanh_cong'
                )
            ).scalar() or 0.0
        )
        
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi lấy thống kê: {str(e)}"
        )

@router.get("/users")
async def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Lấy danh sách tất cả người dùng"""
    try:
        query = db.query(User)
        
        if search:
            query = query.filter(
                or_(
                    User.ho_ten.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%"),
                    User.ten_dang_nhap.ilike(f"%{search}%")
                )
            )
        
        if role:
            query = query.filter(User.vai_tro == role)
        
        total = query.count()
        users = query.offset(skip).limit(limit).all()
        
        return {
            "total": total,
            "users": users,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi lấy danh sách người dùng: {str(e)}"
        )

@router.post("/users")
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Tạo người dùng mới"""
    try:
        # Kiểm tra trùng lặp
        existing_user = db.query(User).filter(
            or_(
                User.ten_dang_nhap == user_data.ten_dang_nhap,
                User.email == user_data.email
            )
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tên đăng nhập hoặc email đã tồn tại"
            )
        
        # Tạo người dùng mới
        new_user = User(
            ten_dang_nhap=user_data.ten_dang_nhap,
            email=user_data.email,
            ho_ten=user_data.ho_ten,
            so_dien_thoai=user_data.so_dien_thoai,
            vai_tro=user_data.vai_tro,
            mat_khau_hash=get_password_hash(user_data.mat_khau),
            trang_thai='hoat_dong'
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {"message": "Tạo người dùng thành công", "user_id": new_user.id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi tạo người dùng: {str(e)}"
        )

@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Cập nhật thông tin người dùng"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy người dùng"
            )
        
        # Cập nhật thông tin
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        
        return {"message": "Cập nhật người dùng thành công"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cập nhật người dùng: {str(e)}"
        )

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Xóa người dùng"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy người dùng"
            )
        
        # Soft delete
        user.trang_thai = 'da_xoa'
        user.thoi_gian_cap_nhat = datetime.utcnow()
        
        db.commit()
        
        return {"message": "Xóa người dùng thành công"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi xóa người dùng: {str(e)}"
        )

@router.get("/audit-logs")
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_id: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Lấy nhật ký audit"""
    try:
        query = db.query(AuditLog)
        
        if user_id:
            query = query.filter(AuditLog.nguoi_dung_id == user_id)
        
        if action:
            query = query.filter(AuditLog.hanh_dong.ilike(f"%{action}%"))
        
        if from_date:
            query = query.filter(func.date(AuditLog.thoi_gian) >= from_date)
        
        if to_date:
            query = query.filter(func.date(AuditLog.thoi_gian) <= to_date)
        
        total = query.count()
        logs = query.order_by(AuditLog.thoi_gian.desc()).offset(skip).limit(limit).all()
        
        return {
            "total": total,
            "logs": logs,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi lấy nhật ký audit: {str(e)}"
        )

@router.get("/system-health")
async def get_system_health(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Kiểm tra tình trạng hệ thống"""
    try:
        # Kiểm tra database
        db_status = "healthy"
        try:
            db.execute("SELECT 1")
        except:
            db_status = "unhealthy"
        
        # Thống kê nhanh
        pending_approvals = db.query(func.count()).filter(
            # Add appropriate filter for pending approvals
        ).scalar() or 0
        
        failed_transactions = db.query(func.count(Transaction.id)).filter(
            and_(
                Transaction.trang_thai == 'that_bai',
                func.date(Transaction.thoi_gian_tao) == date.today()
            )
        ).scalar() or 0
        
        return {
            "database": db_status,
            "pending_approvals": pending_approvals,
            "failed_transactions_today": failed_transactions,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi kiểm tra tình trạng hệ thống: {str(e)}"
        )