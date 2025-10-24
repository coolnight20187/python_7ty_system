"""
Transaction and Commission models
"""

from sqlalchemy import Column, String, ForeignKey, Text, JSON, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class TransactionType(str, enum.Enum):
    DEPOSIT = "nap_tien"
    WITHDRAWAL = "rut_tien"
    PAYMENT = "thanh_toan"
    COMMISSION = "hoa_hong"
    REFUND = "hoan_tien"
    TRANSFER = "chuyen_tien"

class TransactionStatus(str, enum.Enum):
    PENDING = "cho_xu_ly"
    PROCESSING = "dang_xu_ly"
    COMPLETED = "thanh_cong"
    FAILED = "that_bai"
    CANCELLED = "da_huy"

class PaymentMethod(str, enum.Enum):
    BANK_TRANSFER = "chuyen_khoan"
    CASH = "tien_mat"
    E_WALLET = "vi_dien_tu"
    QR_CODE = "ma_qr"
    CREDIT_CARD = "the_tin_dung"

class Transaction(BaseModel):
    """Bảng giao dịch"""
    __tablename__ = "giao_dich"
    
    # Mã giao dịch
    transaction_code = Column(String(20), unique=True, nullable=False, comment="Mã giao dịch")
    
    # Loại và trạng thái
    transaction_type = Column(Enum(TransactionType), nullable=False, comment="Loại giao dịch")
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING, comment="Trạng thái")
    
    # Số tiền
    amount = Column(String(20), nullable=False, comment="Số tiền giao dịch")
    fee_amount = Column(String(20), default="0", comment="Phí giao dịch")
    commission_amount = Column(String(20), default="0", comment="Hoa hồng")
    net_amount = Column(String(20), nullable=False, comment="Số tiền thực nhận")
    
    # Thông tin người giao dịch
    user_id = Column(String, ForeignKey("nguoi_dung.id"), nullable=True)
    user_type = Column(String(20), nullable=True, comment="Loại người dùng")
    user_name = Column(String(100), nullable=True, comment="Tên người giao dịch")
    
    # Thông tin liên quan
    related_id = Column(String, nullable=True, comment="ID liên quan (bill_id, card_id, etc)")
    related_type = Column(String(20), nullable=True, comment="Loại đối tượng liên quan")
    
    # Phương thức thanh toán
    payment_method = Column(Enum(PaymentMethod), nullable=True, comment="Phương thức thanh toán")
    payment_reference = Column(String(100), nullable=True, comment="Mã tham chiếu thanh toán")
    
    # Thông tin ngân hàng
    bank_info = Column(JSON, default={}, comment="Thông tin ngân hàng")
    
    # Mô tả và ghi chú
    description = Column(Text, nullable=True, comment="Mô tả giao dịch")
    notes = Column(Text, nullable=True, comment="Ghi chú")
    
    # Thời gian xử lý
    processed_at = Column(String(50), nullable=True, comment="Thời gian xử lý")
    completed_at = Column(String(50), nullable=True, comment="Thời gian hoàn thành")
    
    # Thông tin bổ sung
    metadata = Column(JSON, default={}, comment="Thông tin bổ sung")
    
    # Relationships
    user = relationship("User")
    commissions = relationship("Commission", back_populates="transaction")

class Commission(BaseModel):
    """Bảng hoa hồng"""
    __tablename__ = "hoa_hong"
    
    transaction_id = Column(String, ForeignKey("giao_dich.id"), nullable=False)
    
    # Thông tin người nhận hoa hồng
    recipient_id = Column(String, ForeignKey("nguoi_dung.id"), nullable=False)
    recipient_type = Column(String(20), nullable=False, comment="Loại người nhận (agent/staff)")
    recipient_name = Column(String(100), nullable=False, comment="Tên người nhận")
    
    # Thông tin hoa hồng
    commission_type = Column(String(20), nullable=False, comment="Loại hoa hồng")
    base_amount = Column(String(20), nullable=False, comment="Số tiền gốc tính hoa hồng")
    commission_rate = Column(String(10), nullable=False, comment="Tỷ lệ hoa hồng (%)")
    commission_amount = Column(String(20), nullable=False, comment="Số tiền hoa hồng")
    
    # Trạng thái
    status = Column(String(20), default="pending", comment="Trạng thái hoa hồng")
    paid_at = Column(String(50), nullable=True, comment="Thời gian chi trả")
    
    # Ghi chú
    notes = Column(Text, nullable=True, comment="Ghi chú")
    
    # Relationships
    transaction = relationship("Transaction", back_populates="commissions")
    recipient = relationship("User")