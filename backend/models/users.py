"""
User and Staff models
"""

from sqlalchemy import Column, String, Enum, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    STAFF = "nhan_vien"
    AGENT = "dai_ly"
    CUSTOMER = "khach_the"

class User(BaseModel):
    """Bảng người dùng chính"""
    __tablename__ = "nguoi_dung"
    
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False, comment="Họ tên đầy đủ")
    phone = Column(String(20), unique=True, nullable=False, index=True, comment="Số điện thoại")
    email = Column(String(100), unique=True, nullable=True, comment="Email")
    role = Column(Enum(UserRole), nullable=False, default=UserRole.AGENT, comment="Vai trò")
    
    # Thông tin bổ sung
    avatar_url = Column(String(500), nullable=True, comment="Ảnh đại diện")
    address = Column(Text, nullable=True, comment="Địa chỉ")
    id_number = Column(String(20), nullable=True, comment="Số CMND/CCCD")
    id_issued_date = Column(String(20), nullable=True, comment="Ngày cấp CMND/CCCD")
    id_issued_place = Column(String(100), nullable=True, comment="Nơi cấp CMND/CCCD")
    
    # Metadata và cài đặt
    metadata = Column(JSON, default={}, comment="Thông tin bổ sung")
    settings = Column(JSON, default={}, comment="Cài đặt cá nhân")
    last_login = Column(String(50), nullable=True, comment="Lần đăng nhập cuối")
    
    # Relationships
    staff = relationship("Staff", back_populates="user", uselist=False)
    agent = relationship("Agent", back_populates="user", uselist=False)
    customer = relationship("Customer", back_populates="user", uselist=False)

class Staff(BaseModel):
    """Bảng nhân viên"""
    __tablename__ = "nhan_vien"
    
    user_id = Column(String, ForeignKey("nguoi_dung.id"), unique=True, nullable=False)
    staff_code = Column(String(20), unique=True, nullable=False, comment="Mã nhân viên")
    department = Column(String(50), nullable=True, comment="Phòng ban")
    position = Column(String(50), nullable=True, comment="Chức vụ")
    
    # Quyền hạn
    permissions = Column(JSON, default=[], comment="Danh sách quyền")
    can_approve_agents = Column(String(10), default="false", comment="Có thể duyệt đại lý")
    can_approve_transactions = Column(String(10), default="false", comment="Có thể duyệt giao dịch")
    max_approval_amount = Column(String(20), default="0", comment="Hạn mức duyệt tối đa")
    
    # Thông tin công việc
    manager_id = Column(String, ForeignKey("nhan_vien.id"), nullable=True, comment="ID quản lý trực tiếp")
    region = Column(String(50), default="mien_nam", comment="Khu vực phụ trách")
    
    # Relationships
    user = relationship("User", back_populates="staff")
    manager = relationship("Staff", remote_side=[BaseModel.id])
    subordinates = relationship("Staff", back_populates="manager")