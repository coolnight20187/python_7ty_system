"""
Agent API endpoints for 7tỷ.vn system
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal

from ..database import get_db
from ..models.users import User
from ..models.agents import Agent
from ..models.customers import Customer
from ..models.transactions import Transaction
from ..models.bills import Bill
from ..auth.dependencies import get_current_agent_user

router = APIRouter()

# Pydantic models
class AgentProfile(BaseModel):
    ho_ten: str
    so_dien_thoai: str
    dia_chi: str
    tinh_thanh: str
    quan_huyen: str
    phuong_xa: str
    so_du_hien_tai: Optional[Decimal] = None

class AgentStats(BaseModel):
    total_customers: int
    total_transactions: int
    total_commission: Decimal
    monthly_revenue: Decimal
    pending_bills: int

class CustomerRegistration(BaseModel):
    ho_ten: str
    so_dien_thoai: str
    email: Optional[str] = None
    dia_chi: str
    so_cong_to: str
    ma_khach_hang_dien: str

@router.get("/profile")
async def get_agent_profile(
    current_user: User = Depends(get_current_agent_user),
    db: Session = Depends(get_db)
):
    """Lấy thông tin hồ sơ đại lý"""
    try:
        agent = db.query(Agent).filter(Agent.nguoi_dung_id == current_user.id).first()
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy thông tin đại lý"
            )
        
        return {
            "user_info": current_user,
            "agent_info": agent
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi lấy thông tin hồ sơ: {str(e)}"
        )

@router.put("/profile")
async def update_agent_profile(
    profile_data: AgentProfile,
    current_user: User = Depends(get_current_agent_user),
    db: Session = Depends(get_db)
):
    """Cập nhật thông tin hồ sơ đại lý"""
    try:
        agent = db.query(Agent).filter(Agent.nguoi_dung_id == current_user.id).first()
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy thông tin đại lý"
            )
        
        # Cập nhật thông tin user
        current_user.ho_ten = profile_data.ho_ten
        current_user.so_dien_thoai = profile_data.so_dien_thoai
        
        # Cập nhật thông tin agent
        agent.dia_chi = profile_data.dia_chi
        agent.tinh_thanh = profile_data.tinh_thanh
        agent.quan_huyen = profile_data.quan_huyen
        agent.phuong_xa = profile_data.phuong_xa
        agent.thoi_gian_cap_nhat = datetime.utcnow()
        
        db.commit()
        
        return {"message": "Cập nhật hồ sơ thành công"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cập nhật hồ sơ: {str(e)}"
        )

@router.get("/stats", response_model=AgentStats)
async def get_agent_stats(
    current_user: User = Depends(get_current_agent_user),
    db: Session = Depends(get_db)
):
    """Lấy thống kê của đại lý"""
    try:
        agent = db.query(Agent).filter(Agent.nguoi_dung_id == current_user.id).first()
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy thông tin đại lý"
            )
        
        # Thống kê khách hàng
        total_customers = db.query(Customer).filter(Customer.dai_ly_id == agent.id).count()
        
        # Thống kê giao dịch
        total_transactions = db.query(Transaction).filter(
            Transaction.dai_ly_id == agent.id
        ).count()
        
        # Tổng hoa hồng
        total_commission = db.query(func.sum(Transaction.hoa_hong)).filter(
            and_(
                Transaction.dai_ly_id == agent.id,
                Transaction.trang_thai == 'thanh_cong'
            )
        ).scalar() or Decimal('0')
        
        # Doanh thu tháng này
        current_month = datetime.now().replace(day=1)
        monthly_revenue = db.query(func.sum(Transaction.so_tien)).filter(
            and_(
                Transaction.dai_ly_id == agent.id,
                Transaction.trang_thai == 'thanh_cong',
                Transaction.thoi_gian_tao >= current_month
            )
        ).scalar() or Decimal('0')
        
        # Hóa đơn chờ xử lý
        pending_bills = db.query(Bill).join(Customer).filter(
            and_(
                Customer.dai_ly_id == agent.id,
                Bill.trang_thai == 'chua_thanh_toan'
            )
        ).count()
        
        return AgentStats(
            total_customers=total_customers,
            total_transactions=total_transactions,
            total_commission=total_commission,
            monthly_revenue=monthly_revenue,
            pending_bills=pending_bills
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi lấy thống kê: {str(e)}"
        )

@router.get("/customers")
async def get_agent_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_agent_user),
    db: Session = Depends(get_db)
):
    """Lấy danh sách khách hàng của đại lý"""
    try:
        agent = db.query(Agent).filter(Agent.nguoi_dung_id == current_user.id).first()
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy thông tin đại lý"
            )
        
        query = db.query(Customer).filter(Customer.dai_ly_id == agent.id)
        
        if search:
            query = query.filter(
                or_(
                    Customer.ho_ten.ilike(f"%{search}%"),
                    Customer.so_dien_thoai.ilike(f"%{search}%"),
                    Customer.ma_khach_hang_dien.ilike(f"%{search}%")
                )
            )
        
        total = query.count()
        customers = query.offset(skip).limit(limit).all()
        
        return {
            "total": total,
            "customers": customers,
            "skip": skip,
            "limit": limit
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi lấy danh sách khách hàng: {str(e)}"
        )

@router.post("/customers")
async def register_customer(
    customer_data: CustomerRegistration,
    current_user: User = Depends(get_current_agent_user),
    db: Session = Depends(get_db)
):
    """Đăng ký khách hàng mới"""
    try:
        agent = db.query(Agent).filter(Agent.nguoi_dung_id == current_user.id).first()
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy thông tin đại lý"
            )
        
        # Kiểm tra trùng lặp
        existing_customer = db.query(Customer).filter(
            or_(
                Customer.so_dien_thoai == customer_data.so_dien_thoai,
                Customer.ma_khach_hang_dien == customer_data.ma_khach_hang_dien
            )
        ).first()
        
        if existing_customer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Khách hàng đã tồn tại với số điện thoại hoặc mã khách hàng điện này"
            )
        
        # Tạo khách hàng mới
        new_customer = Customer(
            ho_ten=customer_data.ho_ten,
            so_dien_thoai=customer_data.so_dien_thoai,
            email=customer_data.email,
            dia_chi=customer_data.dia_chi,
            so_cong_to=customer_data.so_cong_to,
            ma_khach_hang_dien=customer_data.ma_khach_hang_dien,
            dai_ly_id=agent.id,
            trang_thai='hoat_dong'
        )
        
        db.add(new_customer)
        db.commit()
        db.refresh(new_customer)
        
        return {
            "message": "Đăng ký khách hàng thành công",
            "customer_id": new_customer.id
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi đăng ký khách hàng: {str(e)}"
        )

@router.get("/transactions")
async def get_agent_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_agent_user),
    db: Session = Depends(get_db)
):
    """Lấy danh sách giao dịch của đại lý"""
    try:
        agent = db.query(Agent).filter(Agent.nguoi_dung_id == current_user.id).first()
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy thông tin đại lý"
            )
        
        query = db.query(Transaction).filter(Transaction.dai_ly_id == agent.id)
        
        if from_date:
            query = query.filter(func.date(Transaction.thoi_gian_tao) >= from_date)
        
        if to_date:
            query = query.filter(func.date(Transaction.thoi_gian_tao) <= to_date)
        
        if status:
            query = query.filter(Transaction.trang_thai == status)
        
        total = query.count()
        transactions = query.order_by(Transaction.thoi_gian_tao.desc()).offset(skip).limit(limit).all()
        
        return {
            "total": total,
            "transactions": transactions,
            "skip": skip,
            "limit": limit
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi lấy danh sách giao dịch: {str(e)}"
        )

@router.get("/wallet")
async def get_wallet_info(
    current_user: User = Depends(get_current_agent_user),
    db: Session = Depends(get_db)
):
    """Lấy thông tin ví của đại lý"""
    try:
        agent = db.query(Agent).filter(Agent.nguoi_dung_id == current_user.id).first()
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy thông tin đại lý"
            )
        
        # Tính toán số dư hiện tại
        total_income = db.query(func.sum(Transaction.hoa_hong)).filter(
            and_(
                Transaction.dai_ly_id == agent.id,
                Transaction.trang_thai == 'thanh_cong',
                Transaction.loai_giao_dich.in_(['hoa_hong', 'nap_tien'])
            )
        ).scalar() or Decimal('0')
        
        total_expense = db.query(func.sum(Transaction.so_tien)).filter(
            and_(
                Transaction.dai_ly_id == agent.id,
                Transaction.trang_thai == 'thanh_cong',
                Transaction.loai_giao_dich.in_(['rut_tien', 'thanh_toan'])
            )
        ).scalar() or Decimal('0')
        
        current_balance = total_income - total_expense
        
        # Cập nhật số dư trong database
        agent.so_du_hien_tai = current_balance
        db.commit()
        
        return {
            "current_balance": current_balance,
            "total_income": total_income,
            "total_expense": total_expense,
            "last_updated": datetime.utcnow()
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi lấy thông tin ví: {str(e)}"
        )

@router.get("/commission-report")
async def get_commission_report(
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_agent_user),
    db: Session = Depends(get_db)
):
    """Lấy báo cáo hoa hồng"""
    try:
        agent = db.query(Agent).filter(Agent.nguoi_dung_id == current_user.id).first()
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy thông tin đại lý"
            )
        
        query = db.query(Transaction).filter(
            and_(
                Transaction.dai_ly_id == agent.id,
                Transaction.trang_thai == 'thanh_cong',
                Transaction.hoa_hong > 0
            )
        )
        
        if from_date:
            query = query.filter(func.date(Transaction.thoi_gian_tao) >= from_date)
        
        if to_date:
            query = query.filter(func.date(Transaction.thoi_gian_tao) <= to_date)
        
        transactions = query.order_by(Transaction.thoi_gian_tao.desc()).all()
        
        total_commission = sum(t.hoa_hong for t in transactions)
        total_transactions = len(transactions)
        
        return {
            "total_commission": total_commission,
            "total_transactions": total_transactions,
            "transactions": transactions,
            "from_date": from_date,
            "to_date": to_date
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi lấy báo cáo hoa hồng: {str(e)}"
        )