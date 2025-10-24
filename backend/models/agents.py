"""
Agent and Agent Wallet models
"""

from sqlalchemy import Column, String, Numeric, Integer, ForeignKey, Text, JSON, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class AgentStatus(str, enum.Enum):
    ACTIVE = "hoat_dong"
    INACTIVE = "tam_dung"
    SUSPENDED = "bi_khoa"
    PENDING = "cho_duyet"

class Agent(BaseModel):
    """Bảng đại lý thu hộ"""
    __tablename__ = "dai_ly"
    
    user_id = Column(String, ForeignKey("nguoi_dung.id"), unique=True, nullable=False)
    agent_code = Column(String(20), unique=True, nullable=False, comment="Mã đại lý")
    agent_name = Column(String(100), nullable=False, comment="Tên đại lý")
    
    # Thông tin liên hệ
    owner_name = Column(String(100), nullable=False, comment="Tên chủ đại lý")
    phone = Column(String(20), nullable=False, comment="Số điện thoại")
    email = Column(String(100), nullable=True, comment="Email")
    address = Column(Text, nullable=False, comment="Địa chỉ đại lý")
    
    # Thông tin kinh doanh
    region = Column(String(50), default="mien_nam", comment="Khu vực")
    commission_rate = Column(Numeric(5,2), default=1.0, comment="Tỷ lệ hoa hồng (%)")
    status = Column(Enum(AgentStatus), default=AgentStatus.PENDING, comment="Trạng thái")
    
    # Thông tin pháp nhân
    business_license = Column(String(50), nullable=True, comment="Số giấy phép kinh doanh")
    tax_code = Column(String(20), nullable=True, comment="Mã số thuế")
    legal_representative = Column(String(100), nullable=True, comment="Người đại diện pháp luật")
    
    # Thông tin ngân hàng
    bank_info = Column(JSON, default={}, comment="Thông tin ngân hàng")
    
    # Thống kê
    total_sales = Column(String(20), default="0", comment="Tổng doanh số")
    total_commission = Column(String(20), default="0", comment="Tổng hoa hồng")
    total_transactions = Column(Integer, default=0, comment="Tổng số giao dịch")
    
    # Nhân viên phụ trách
    staff_id = Column(String, ForeignKey("nhan_vien.id"), nullable=True, comment="Nhân viên phụ trách")
    
    # Hình ảnh và tài liệu
    documents = Column(JSON, default=[], comment="Danh sách tài liệu")
    
    # Relationships
    user = relationship("User", back_populates="agent")
    staff = relationship("Staff")
    wallet = relationship("AgentWallet", back_populates="agent", uselist=False)

class AgentWallet(BaseModel):
    """Ví điện tử đại lý"""
    __tablename__ = "vi_dai_ly"
    
    agent_id = Column(String, ForeignKey("dai_ly.id"), unique=True, nullable=False)
    
    # Số dư
    balance = Column(String(20), default="0", comment="Số dư hiện tại (VND)")
    available_balance = Column(String(20), default="0", comment="Số dư khả dụng")
    frozen_balance = Column(String(20), default="0", comment="Số dư bị đóng băng")
    
    # Điểm thưởng
    reward_points = Column(Integer, default=0, comment="Điểm thưởng")
    lifetime_points = Column(Integer, default=0, comment="Tổng điểm tích lũy")
    
    # Thống kê giao dịch
    total_deposits = Column(String(20), default="0", comment="Tổng nạp tiền")
    total_withdrawals = Column(String(20), default="0", comment="Tổng rút tiền")
    total_commissions = Column(String(20), default="0", comment="Tổng hoa hồng nhận")
    
    # Cài đặt ví
    daily_limit = Column(String(20), default="50000000", comment="Hạn mức giao dịch hàng ngày")
    monthly_limit = Column(String(20), default="1000000000", comment="Hạn mức giao dịch hàng tháng")
    
    # Relationships
    agent = relationship("Agent", back_populates="wallet")