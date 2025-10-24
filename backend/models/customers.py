"""
Customer and Credit Card models
"""

from sqlalchemy import Column, String, Integer, Date, Numeric, ForeignKey, Text, JSON, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class CustomerStatus(str, enum.Enum):
    ACTIVE = "hoat_dong"
    INACTIVE = "tam_dung"
    SUSPENDED = "bi_khoa"
    PENDING = "cho_duyet"

class CardStatus(str, enum.Enum):
    ACTIVE = "hoat_dong"
    EXPIRED = "het_han"
    BLOCKED = "bi_khoa"
    NEAR_DUE = "sat_han"

class Customer(BaseModel):
    """Bảng khách hàng thẻ"""
    __tablename__ = "khach_the"
    
    user_id = Column(String, ForeignKey("nguoi_dung.id"), unique=True, nullable=False)
    customer_code = Column(String(20), unique=True, nullable=False, comment="Mã khách hàng")
    
    # Thông tin cá nhân
    full_name = Column(String(100), nullable=False, comment="Họ tên đầy đủ")
    phone = Column(String(20), nullable=False, comment="Số điện thoại")
    email = Column(String(100), nullable=True, comment="Email")
    address = Column(Text, nullable=True, comment="Địa chỉ")
    
    # Thông tin pháp nhân
    id_number = Column(String(20), nullable=True, comment="Số CMND/CCCD")
    id_issued_date = Column(Date, nullable=True, comment="Ngày cấp")
    id_issued_place = Column(String(100), nullable=True, comment="Nơi cấp")
    
    # Thông tin tài chính
    monthly_income = Column(String(20), default="0", comment="Thu nhập hàng tháng")
    occupation = Column(String(100), nullable=True, comment="Nghề nghiệp")
    
    # Thông tin ví
    wallet_balance = Column(String(20), default="0", comment="Số dư ví")
    total_spent = Column(String(20), default="0", comment="Tổng chi tiêu")
    total_earned = Column(String(20), default="0", comment="Tổng thu nhập")
    
    # Thông tin ngân hàng
    bank_accounts = Column(JSON, default=[], comment="Danh sách tài khoản ngân hàng")
    
    # Trạng thái
    status = Column(Enum(CustomerStatus), default=CustomerStatus.PENDING, comment="Trạng thái")
    kyc_verified = Column(String(10), default="false", comment="Đã xác minh KYC")
    
    # Hình ảnh và tài liệu
    documents = Column(JSON, default=[], comment="Danh sách tài liệu")
    
    # Relationships
    user = relationship("User", back_populates="customer")
    credit_cards = relationship("CreditCard", back_populates="customer")

class CreditCard(BaseModel):
    """Bảng thẻ tín dụng"""
    __tablename__ = "the_tin_dung"
    
    customer_id = Column(String, ForeignKey("khach_the.id"), nullable=False)
    
    # Thông tin thẻ
    card_number = Column(String(20), unique=True, nullable=False, comment="Số thẻ")
    card_holder_name = Column(String(100), nullable=False, comment="Tên chủ thẻ")
    expiry_date = Column(Date, nullable=False, comment="Ngày hết hạn")
    cvv = Column(String(4), nullable=False, comment="Mã CVV")
    
    # Thông tin ngân hàng
    bank_name = Column(String(100), nullable=False, comment="Tên ngân hàng")
    bank_code = Column(String(10), nullable=True, comment="Mã ngân hàng")
    card_type = Column(String(50), nullable=False, comment="Loại thẻ")
    
    # Chu kỳ thanh toán
    statement_date = Column(Integer, nullable=False, comment="Ngày chốt sao kê (1-31)")
    grace_period = Column(Integer, default=45, comment="Thời gian miễn lãi (ngày)")
    
    # Hạn mức
    credit_limit = Column(String(20), nullable=False, comment="Hạn mức thẻ")
    available_limit = Column(String(20), nullable=False, comment="Hạn mức khả dụng")
    used_limit = Column(String(20), default="0", comment="Hạn mức đã sử dụng")
    
    # Ưu đãi
    benefits = Column(Text, nullable=True, comment="Ưu đãi thẻ")
    cashback_rate = Column(Numeric(5,2), default=0, comment="Tỷ lệ hoàn tiền (%)")
    
    # Quản lý thiết bị
    device_name = Column(String(100), nullable=True, comment="Tên thiết bị quản lý")
    
    # Trạng thái
    status = Column(Enum(CardStatus), default=CardStatus.ACTIVE, comment="Trạng thái thẻ")
    
    # Số tiền cần đáo và đã đáo
    required_payment = Column(String(20), default="0", comment="Số tiền cần đáo")
    paid_amount = Column(String(20), default="0", comment="Số tiền đã đáo")
    
    # Ghi chú
    notes = Column(Text, nullable=True, comment="Ghi chú")
    
    # Relationships
    customer = relationship("Customer", back_populates="credit_cards")