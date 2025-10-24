"""
Audit Log model
"""

from sqlalchemy import Column, String, ForeignKey, Text, JSON, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class AuditAction(str, enum.Enum):
    CREATE = "tao_moi"
    UPDATE = "cap_nhat"
    DELETE = "xoa"
    LOGIN = "dang_nhap"
    LOGOUT = "dang_xuat"
    APPROVE = "phe_duyet"
    REJECT = "tu_choi"
    EXPORT = "xuat_du_lieu"
    IMPORT = "nhap_du_lieu"

class AuditLog(BaseModel):
    """Bảng nhật ký kiểm toán"""
    __tablename__ = "nhat_ky_kiem_toan"
    
    # Thông tin người thực hiện
    user_id = Column(String, ForeignKey("nguoi_dung.id"), nullable=True)
    user_name = Column(String(100), nullable=True, comment="Tên người thực hiện")
    user_role = Column(String(20), nullable=True, comment="Vai trò người thực hiện")
    
    # Thông tin hành động
    action = Column(Enum(AuditAction), nullable=False, comment="Hành động")
    action_description = Column(String(200), nullable=False, comment="Mô tả hành động")
    
    # Thông tin đối tượng
    target_type = Column(String(50), nullable=False, comment="Loại đối tượng")
    target_id = Column(String, nullable=True, comment="ID đối tượng")
    target_name = Column(String(200), nullable=True, comment="Tên đối tượng")
    
    # Dữ liệu thay đổi
    old_values = Column(JSON, nullable=True, comment="Giá trị cũ")
    new_values = Column(JSON, nullable=True, comment="Giá trị mới")
    changes = Column(JSON, nullable=True, comment="Chi tiết thay đổi")
    
    # Thông tin kỹ thuật
    ip_address = Column(String(45), nullable=True, comment="Địa chỉ IP")
    user_agent = Column(Text, nullable=True, comment="User Agent")
    session_id = Column(String(100), nullable=True, comment="Session ID")
    request_id = Column(String(100), nullable=True, comment="Request ID")
    
    # Kết quả
    success = Column(String(10), default="true", comment="Thành công")
    error_message = Column(Text, nullable=True, comment="Thông báo lỗi")
    
    # Thời gian
    timestamp = Column(String(50), nullable=False, comment="Thời gian thực hiện")
    duration_ms = Column(String(10), nullable=True, comment="Thời gian xử lý (ms)")
    
    # Metadata
    metadata = Column(JSON, default={}, comment="Thông tin bổ sung")
    
    # Relationships
    user = relationship("User")