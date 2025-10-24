"""
Transaction API endpoints for 7tỷ.vn system
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from pydantic import BaseModel, validator
from datetime import datetime, date
from decimal import Decimal

from ..database import get_db
from ..models.users import User
from ..models.transactions import Transaction
from ..models.customers import Customer
from ..models.agents import Agent
from ..models.bills import Bill
from ..auth.dependencies import get_current_user

router = APIRouter()

# Pydantic models
class TransactionCreate(BaseModel):
    khach_hang_id: Optional[str] = None
    dai_ly_id: Optional[str] = None
    hoa_don_id: Optional[str] = None
    loai_giao_dich: str
    so_tien: Decimal
    phuong_thuc_thanh_toan: str
    ghi_chu: Optional[str] = None
    
    @validator('so_tien')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Số tiền phải lớn hơn 0')
        return v

class TransactionUpdate(BaseModel):
    trang_thai: Optional[str] = None
    ghi_chu: Optional[str] = None

class TransactionStats(BaseModel):
    total_transactions: int
    successful_transactions: int
    failed_transactions: int
    pending_transactions: int
    total_amount: Decimal
    today_transactions: int
    today_amount: Decimal

@router.get("/stats", response_model=TransactionStats)
async def get_transaction_stats(
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy thống kê giao dịch"""
    try:
        query = db.query(Transaction)
        
        if from_date:
            query = query.filter(func.date(Transaction.thoi_gian_tao) >= from_date)
        
        if to_date:
            query = query.filter(func.date(Transaction.thoi_gian_tao) <= to_date)
        
        # Thống kê tổng quan
        total_transactions = query.count()
        successful_transactions = query.filter(Transaction.trang_thai == 'thanh_cong').count()
        failed_transactions = query.filter(Transaction.trang_thai == 'that_bai').count()
        pending_transactions = query.filter(Transaction.trang_thai == 'dang_xu_ly').count()
        
        total_amount = query.filter(Transaction.trang_thai == 'thanh_cong').with_entities(
            func.sum(Transaction.so_tien)
        ).scalar() or Decimal('0')
        
        # Thống kê hôm nay
        today = date.today()
        today_query = query.filter(func.date(Transaction.thoi_gian_tao) == today)
        today_transactions = today_query.count()
        today_amount = today_query.filter(Transaction.trang_thai == 'thanh_cong').with_entities(
            func.sum(Transaction.so_tien)
        ).scalar() or Decimal('0')
        
        return TransactionStats(
            total_transactions=total_transactions,
            successful_transactions=successful_transactions,
            failed_transactions=failed_transactions,
            pending_transactions=pending_transactions,
            total_amount=total_amount,
            today_transactions=today_transactions,
            today_amount=today_amount
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi lấy thống kê giao dịch: {str(e)}"
        )

@router.get("/")
async def get_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    customer_id: Optional[str] = Query(None),
    agent_id: Optional[str] = Query(None),
    transaction_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy danh sách giao dịch với bộ lọc"""
    try:
        query = db.query(Transaction)
        
        # Áp dụng bộ lọc
        if customer_id:
            query = query.filter(Transaction.khach_hang_id == customer_id)
        
        if agent_id:
            query = query.filter(Transaction.dai_ly_id == agent_id)
        
        if transaction_type:
            query = query.filter(Transaction.loai_giao_dich == transaction_type)
        
        if status:
            query = query.filter(Transaction.trang_thai == status)
        
        if from_date:
            query = query.filter(func.date(Transaction.thoi_gian_tao) >= from_date)
        
        if to_date:
            query = query.filter(func.date(Transaction.thoi_gian_tao) <= to_date)
        
        # Phân quyền: chỉ admin mới xem được tất cả giao dịch
        if current_user.vai_tro not in ['admin', 'quan_ly']:
            if current_user.vai_tro == 'dai_ly':
                # Đại lý chỉ xem giao dịch của mình
                agent = db.query(Agent).filter(Agent.nguoi_dung_id == current_user.id).first()
                if agent:
                    query = query.filter(Transaction.dai_ly_id == agent.id)
                else:
                    query = query.filter(Transaction.id == None)  # Không có giao dịch nào
            elif current_user.vai_tro == 'khach_hang':
                # Khách hàng chỉ xem giao dịch của mình
                customer = db.query(Customer).filter(Customer.nguoi_dung_id == current_user.id).first()
                if customer:
                    query = query.filter(Transaction.khach_hang_id == customer.id)
                else:
                    query = query.filter(Transaction.id == None)  # Không có giao dịch nào
        
        total = query.count()
        transactions = query.order_by(Transaction.thoi_gian_tao.desc()).offset(skip).limit(limit).all()
        
        return {
            "total": total,
            "transactions": transactions,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi lấy danh sách giao dịch: {str(e)}"
        )

@router.get("/{transaction_id}")
async def get_transaction_detail(
    transaction_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy chi tiết giao dịch"""
    try:
        query = db.query(Transaction).filter(Transaction.id == transaction_id)
        
        # Phân quyền
        if current_user.vai_tro not in ['admin', 'quan_ly']:
            if current_user.vai_tro == 'dai_ly':
                agent = db.query(Agent).filter(Agent.nguoi_dung_id == current_user.id).first()
                if agent:
                    query = query.filter(Transaction.dai_ly_id == agent.id)
            elif current_user.vai_tro == 'khach_hang':
                customer = db.query(Customer).filter(Customer.nguoi_dung_id == current_user.id).first()
                if customer:
                    query = query.filter(Transaction.khach_hang_id == customer.id)
        
        transaction = query.first()
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy giao dịch"
            )
        
        return transaction
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi lấy chi tiết giao dịch: {str(e)}"
        )

@router.post("/")
async def create_transaction(
    transaction_data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Tạo giao dịch mới"""
    try:
        # Kiểm tra quyền tạo giao dịch
        if current_user.vai_tro not in ['admin', 'quan_ly', 'dai_ly']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Không có quyền tạo giao dịch"
            )
        
        # Tạo mã giao dịch
        ma_giao_dich = f"{transaction_data.loai_giao_dich.upper()}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{current_user.id}"
        
        # Tạo giao dịch mới
        new_transaction = Transaction(
            khach_hang_id=transaction_data.khach_hang_id,
            dai_ly_id=transaction_data.dai_ly_id,
            hoa_don_id=transaction_data.hoa_don_id,
            loai_giao_dich=transaction_data.loai_giao_dich,
            so_tien=transaction_data.so_tien,
            phuong_thuc_thanh_toan=transaction_data.phuong_thuc_thanh_toan,
            trang_thai='dang_xu_ly',
            ghi_chu=transaction_data.ghi_chu,
            ma_giao_dich=ma_giao_dich,
            nguoi_tao_id=current_user.id
        )
        
        db.add(new_transaction)
        db.commit()
        db.refresh(new_transaction)
        
        return {
            "message": "Tạo giao dịch thành công",
            "transaction_id": new_transaction.id,
            "transaction_code": ma_giao_dich
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi tạo giao dịch: {str(e)}"
        )

@router.put("/{transaction_id}")
async def update_transaction(
    transaction_id: str,
    transaction_data: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cập nhật giao dịch"""
    try:
        # Chỉ admin và quản lý mới được cập nhật giao dịch
        if current_user.vai_tro not in ['admin', 'quan_ly']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Không có quyền cập nhật giao dịch"
            )
        
        transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy giao dịch"
            )
        
        # Cập nhật thông tin
        update_data = transaction_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(transaction, field, value)
        
        transaction.thoi_gian_cap_nhat = datetime.utcnow()
        transaction.nguoi_cap_nhat_id = current_user.id
        
        db.commit()
        
        return {"message": "Cập nhật giao dịch thành công"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cập nhật giao dịch: {str(e)}"
        )

@router.post("/{transaction_id}/confirm")
async def confirm_transaction(
    transaction_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Xác nhận giao dịch thành công"""
    try:
        if current_user.vai_tro not in ['admin', 'quan_ly']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Không có quyền xác nhận giao dịch"
            )
        
        transaction = db.query(Transaction).filter(
            and_(
                Transaction.id == transaction_id,
                Transaction.trang_thai == 'dang_xu_ly'
            )
        ).first()
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy giao dịch hoặc giao dịch không ở trạng thái chờ xử lý"
            )
        
        # Cập nhật trạng thái
        transaction.trang_thai = 'thanh_cong'
        transaction.thoi_gian_hoan_thanh = datetime.utcnow()
        transaction.nguoi_cap_nhat_id = current_user.id
        
        # Cập nhật hóa đơn nếu có
        if transaction.hoa_don_id:
            bill = db.query(Bill).filter(Bill.id == transaction.hoa_don_id).first()
            if bill:
                bill.trang_thai = 'da_thanh_toan'
                bill.thoi_gian_thanh_toan = datetime.utcnow()
        
        db.commit()
        
        return {"message": "Xác nhận giao dịch thành công"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi xác nhận giao dịch: {str(e)}"
        )

@router.post("/{transaction_id}/cancel")
async def cancel_transaction(
    transaction_id: str,
    reason: str = Query(..., description="Lý do hủy giao dịch"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Hủy giao dịch"""
    try:
        if current_user.vai_tro not in ['admin', 'quan_ly']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Không có quyền hủy giao dịch"
            )
        
        transaction = db.query(Transaction).filter(
            and_(
                Transaction.id == transaction_id,
                Transaction.trang_thai.in_(['dang_xu_ly', 'cho_duyet'])
            )
        ).first()
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy giao dịch hoặc giao dịch không thể hủy"
            )
        
        # Cập nhật trạng thái
        transaction.trang_thai = 'da_huy'
        transaction.thoi_gian_cap_nhat = datetime.utcnow()
        transaction.nguoi_cap_nhat_id = current_user.id
        transaction.ghi_chu = f"{transaction.ghi_chu or ''}\nLý do hủy: {reason}"
        
        db.commit()
        
        return {"message": "Hủy giao dịch thành công"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hủy giao dịch: {str(e)}"
        )

@router.get("/export/csv")
async def export_transactions_csv(
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Xuất danh sách giao dịch ra CSV"""
    try:
        if current_user.vai_tro not in ['admin', 'quan_ly']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Không có quyền xuất báo cáo"
            )
        
        query = db.query(Transaction)
        
        if from_date:
            query = query.filter(func.date(Transaction.thoi_gian_tao) >= from_date)
        
        if to_date:
            query = query.filter(func.date(Transaction.thoi_gian_tao) <= to_date)
        
        if status:
            query = query.filter(Transaction.trang_thai == status)
        
        transactions = query.order_by(Transaction.thoi_gian_tao.desc()).all()
        
        # Tạo CSV data
        csv_data = []
        csv_data.append([
            "Mã giao dịch", "Loại giao dịch", "Số tiền", "Trạng thái",
            "Phương thức thanh toán", "Thời gian tạo", "Ghi chú"
        ])
        
        for transaction in transactions:
            csv_data.append([
                transaction.ma_giao_dich,
                transaction.loai_giao_dich,
                str(transaction.so_tien),
                transaction.trang_thai,
                transaction.phuong_thuc_thanh_toan,
                transaction.thoi_gian_tao.strftime("%Y-%m-%d %H:%M:%S"),
                transaction.ghi_chu or ""
            ])
        
        return {
            "message": "Xuất CSV thành công",
            "data": csv_data,
            "total_records": len(transactions)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi xuất CSV: {str(e)}"
        )