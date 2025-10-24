"""
Customer API endpoints for 7tỷ.vn system
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
from ..models.customers import Customer
from ..models.transactions import Transaction
from ..models.bills import Bill
from ..auth.dependencies import get_current_customer_user

router = APIRouter()

# Pydantic models
class CustomerProfile(BaseModel):
    ho_ten: str
    so_dien_thoai: str
    email: Optional[str] = None
    dia_chi: str
    so_cong_to: str
    ma_khach_hang_dien: str

class BillPayment(BaseModel):
    bill_id: str
    so_tien: Decimal
    phuong_thuc_thanh_toan: str
    ghi_chu: Optional[str] = None

class WalletTopUp(BaseModel):
    so_tien: Decimal
    phuong_thuc_nap: str
    
    @validator('so_tien')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Số tiền phải lớn hơn 0')
        if v > 10000000:  # 10 triệu VND
            raise ValueError('Số tiền nạp không được vượt quá 10,000,000 VND')
        return v

class CustomerStats(BaseModel):
    total_bills: int
    paid_bills: int
    unpaid_bills: int
    total_paid_amount: Decimal
    wallet_balance: Decimal

@router.get("/profile")
async def get_customer_profile(
    current_user: User = Depends(get_current_customer_user),
    db: Session = Depends(get_db)
):
    """Lấy thông tin hồ sơ khách hàng"""
    try:
        customer = db.query(Customer).filter(Customer.nguoi_dung_id == current_user.id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy thông tin khách hàng"
            )
        
        return {
            "user_info": current_user,
            "customer_info": customer
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi lấy thông tin hồ sơ: {str(e)}"
        )

@router.put("/profile")
async def update_customer_profile(
    profile_data: CustomerProfile,
    current_user: User = Depends(get_current_customer_user),
    db: Session = Depends(get_db)
):
    """Cập nhật thông tin hồ sơ khách hàng"""
    try:
        customer = db.query(Customer).filter(Customer.nguoi_dung_id == current_user.id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy thông tin khách hàng"
            )
        
        # Kiểm tra trùng lặp mã khách hàng điện
        if profile_data.ma_khach_hang_dien != customer.ma_khach_hang_dien:
            existing_customer = db.query(Customer).filter(
                and_(
                    Customer.ma_khach_hang_dien == profile_data.ma_khach_hang_dien,
                    Customer.id != customer.id
                )
            ).first()
            
            if existing_customer:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Mã khách hàng điện đã tồn tại"
                )
        
        # Cập nhật thông tin user
        current_user.ho_ten = profile_data.ho_ten
        current_user.so_dien_thoai = profile_data.so_dien_thoai
        current_user.email = profile_data.email
        
        # Cập nhật thông tin customer
        customer.ho_ten = profile_data.ho_ten
        customer.so_dien_thoai = profile_data.so_dien_thoai
        customer.email = profile_data.email
        customer.dia_chi = profile_data.dia_chi
        customer.so_cong_to = profile_data.so_cong_to
        customer.ma_khach_hang_dien = profile_data.ma_khach_hang_dien
        customer.thoi_gian_cap_nhat = datetime.utcnow()
        
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

@router.get("/stats", response_model=CustomerStats)
async def get_customer_stats(
    current_user: User = Depends(get_current_customer_user),
    db: Session = Depends(get_db)
):
    """Lấy thống kê của khách hàng"""
    try:
        customer = db.query(Customer).filter(Customer.nguoi_dung_id == current_user.id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy thông tin khách hàng"
            )
        
        # Thống kê hóa đơn
        total_bills = db.query(Bill).filter(Bill.khach_hang_id == customer.id).count()
        paid_bills = db.query(Bill).filter(
            and_(
                Bill.khach_hang_id == customer.id,
                Bill.trang_thai == 'da_thanh_toan'
            )
        ).count()
        unpaid_bills = total_bills - paid_bills
        
        # Tổng số tiền đã thanh toán
        total_paid_amount = db.query(func.sum(Bill.so_tien)).filter(
            and_(
                Bill.khach_hang_id == customer.id,
                Bill.trang_thai == 'da_thanh_toan'
            )
        ).scalar() or Decimal('0')
        
        # Số dư ví
        wallet_balance = customer.so_du_vi or Decimal('0')
        
        return CustomerStats(
            total_bills=total_bills,
            paid_bills=paid_bills,
            unpaid_bills=unpaid_bills,
            total_paid_amount=total_paid_amount,
            wallet_balance=wallet_balance
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi lấy thống kê: {str(e)}"
        )

@router.get("/bills")
async def get_customer_bills(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_customer_user),
    db: Session = Depends(get_db)
):
    """Lấy danh sách hóa đơn của khách hàng"""
    try:
        customer = db.query(Customer).filter(Customer.nguoi_dung_id == current_user.id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy thông tin khách hàng"
            )
        
        query = db.query(Bill).filter(Bill.khach_hang_id == customer.id)
        
        if status:
            query = query.filter(Bill.trang_thai == status)
        
        if from_date:
            query = query.filter(func.date(Bill.ky_hoa_don) >= from_date)
        
        if to_date:
            query = query.filter(func.date(Bill.ky_hoa_don) <= to_date)
        
        total = query.count()
        bills = query.order_by(Bill.ky_hoa_don.desc()).offset(skip).limit(limit).all()
        
        return {
            "total": total,
            "bills": bills,
            "skip": skip,
            "limit": limit
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi lấy danh sách hóa đơn: {str(e)}"
        )

@router.get("/bills/{bill_id}")
async def get_bill_detail(
    bill_id: str,
    current_user: User = Depends(get_current_customer_user),
    db: Session = Depends(get_db)
):
    """Lấy chi tiết hóa đơn"""
    try:
        customer = db.query(Customer).filter(Customer.nguoi_dung_id == current_user.id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy thông tin khách hàng"
            )
        
        bill = db.query(Bill).filter(
            and_(
                Bill.id == bill_id,
                Bill.khach_hang_id == customer.id
            )
        ).first()
        
        if not bill:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy hóa đơn"
            )
        
        return bill
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi lấy chi tiết hóa đơn: {str(e)}"
        )

@router.post("/bills/{bill_id}/pay")
async def pay_bill(
    bill_id: str,
    payment_data: BillPayment,
    current_user: User = Depends(get_current_customer_user),
    db: Session = Depends(get_db)
):
    """Thanh toán hóa đơn"""
    try:
        customer = db.query(Customer).filter(Customer.nguoi_dung_id == current_user.id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy thông tin khách hàng"
            )
        
        bill = db.query(Bill).filter(
            and_(
                Bill.id == bill_id,
                Bill.khach_hang_id == customer.id,
                Bill.trang_thai == 'chua_thanh_toan'
            )
        ).first()
        
        if not bill:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy hóa đơn hoặc hóa đơn đã được thanh toán"
            )
        
        # Kiểm tra số tiền
        if payment_data.so_tien != bill.so_tien:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Số tiền thanh toán không khớp với số tiền hóa đơn"
            )
        
        # Kiểm tra số dư ví nếu thanh toán bằng ví
        if payment_data.phuong_thuc_thanh_toan == 'vi_dien_tu':
            if customer.so_du_vi < payment_data.so_tien:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Số dư ví không đủ để thanh toán"
                )
            
            # Trừ tiền từ ví
            customer.so_du_vi -= payment_data.so_tien
        
        # Cập nhật trạng thái hóa đơn
        bill.trang_thai = 'da_thanh_toan'
        bill.thoi_gian_thanh_toan = datetime.utcnow()
        bill.phuong_thuc_thanh_toan = payment_data.phuong_thuc_thanh_toan
        
        # Tạo giao dịch
        transaction = Transaction(
            khach_hang_id=customer.id,
            dai_ly_id=customer.dai_ly_id,
            hoa_don_id=bill.id,
            loai_giao_dich='thanh_toan_hoa_don',
            so_tien=payment_data.so_tien,
            phuong_thuc_thanh_toan=payment_data.phuong_thuc_thanh_toan,
            trang_thai='thanh_cong',
            ghi_chu=payment_data.ghi_chu,
            ma_giao_dich=f"PAY_{datetime.now().strftime('%Y%m%d%H%M%S')}_{customer.id}"
        )
        
        db.add(transaction)
        db.commit()
        
        return {
            "message": "Thanh toán hóa đơn thành công",
            "transaction_id": transaction.id,
            "remaining_balance": customer.so_du_vi
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi thanh toán hóa đơn: {str(e)}"
        )

@router.get("/wallet")
async def get_wallet_info(
    current_user: User = Depends(get_current_customer_user),
    db: Session = Depends(get_db)
):
    """Lấy thông tin ví của khách hàng"""
    try:
        customer = db.query(Customer).filter(Customer.nguoi_dung_id == current_user.id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy thông tin khách hàng"
            )
        
        # Lấy lịch sử giao dịch ví gần đây
        recent_transactions = db.query(Transaction).filter(
            and_(
                Transaction.khach_hang_id == customer.id,
                Transaction.loai_giao_dich.in_(['nap_vi', 'thanh_toan_hoa_don'])
            )
        ).order_by(Transaction.thoi_gian_tao.desc()).limit(10).all()
        
        return {
            "balance": customer.so_du_vi or Decimal('0'),
            "recent_transactions": recent_transactions,
            "last_updated": customer.thoi_gian_cap_nhat
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi lấy thông tin ví: {str(e)}"
        )

@router.post("/wallet/topup")
async def topup_wallet(
    topup_data: WalletTopUp,
    current_user: User = Depends(get_current_customer_user),
    db: Session = Depends(get_db)
):
    """Nạp tiền vào ví"""
    try:
        customer = db.query(Customer).filter(Customer.nguoi_dung_id == current_user.id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy thông tin khách hàng"
            )
        
        # Cập nhật số dư ví
        if customer.so_du_vi is None:
            customer.so_du_vi = Decimal('0')
        
        customer.so_du_vi += topup_data.so_tien
        customer.thoi_gian_cap_nhat = datetime.utcnow()
        
        # Tạo giao dịch nạp tiền
        transaction = Transaction(
            khach_hang_id=customer.id,
            dai_ly_id=customer.dai_ly_id,
            loai_giao_dich='nap_vi',
            so_tien=topup_data.so_tien,
            phuong_thuc_thanh_toan=topup_data.phuong_thuc_nap,
            trang_thai='thanh_cong',
            ghi_chu=f"Nạp tiền vào ví qua {topup_data.phuong_thuc_nap}",
            ma_giao_dich=f"TOP_{datetime.now().strftime('%Y%m%d%H%M%S')}_{customer.id}"
        )
        
        db.add(transaction)
        db.commit()
        
        return {
            "message": "Nạp tiền thành công",
            "transaction_id": transaction.id,
            "new_balance": customer.so_du_vi
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi nạp tiền: {str(e)}"
        )

@router.get("/transactions")
async def get_customer_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    transaction_type: Optional[str] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_customer_user),
    db: Session = Depends(get_db)
):
    """Lấy lịch sử giao dịch của khách hàng"""
    try:
        customer = db.query(Customer).filter(Customer.nguoi_dung_id == current_user.id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy thông tin khách hàng"
            )
        
        query = db.query(Transaction).filter(Transaction.khach_hang_id == customer.id)
        
        if transaction_type:
            query = query.filter(Transaction.loai_giao_dich == transaction_type)
        
        if from_date:
            query = query.filter(func.date(Transaction.thoi_gian_tao) >= from_date)
        
        if to_date:
            query = query.filter(func.date(Transaction.thoi_gian_tao) <= to_date)
        
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
            detail=f"Lỗi lấy lịch sử giao dịch: {str(e)}"
        )