"""
Approval and Approval Step models
"""

from sqlalchemy import Column, String, Integer, ForeignKey, Text, JSON, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class ApprovalType(str, enum.Enum):
    AGENT_REGISTRATION = "dang_ky_dai_ly"
    CUSTOMER_REGISTRATION = "dang_ky_khach_hang"
    DEPOSIT = "nap_tien"
    WITHDRAWAL = "rut_tien"
    TRANSACTION = "giao_dich"
    COMMISSION = "hoa_hong"

class ApprovalStatus(str, enum.Enum):
    PENDING = "cho_duyet"
    IN_PROGRESS = "dang_duyet"
    APPROVED = "da_duyet"
    REJECTED = "tu_choi"
    CANCELLED = "da_huy"

class StepStatus(str, enum.Enum):
    PENDING = "cho_duyet"
    APPROVED = "da_duyet"
    REJECTED = "tu_choi"
    SKIPPED = "bo_qua"

class Approval(BaseModel):
    """Bảng phê duyệt"""
    __tablename__ = "phe_duyet"
    
    # Thông tin cơ bản
    approval_code = Column(String(20), unique=True, nullable=False, comment="Mã phê duyệt")
    approval_type = Column(Enum(ApprovalType), nullable=False, comment="Loại phê duyệt")
    status = Column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING, comment="Trạng thái")
    
    # Thông tin đối tượng cần duyệt
    target_id = Column(String, nullable=False, comment="ID đối tượng cần duyệt")
    target_type = Column(String(20), nullable=False, comment="Loại đối tượng")
    target_data = Column(JSON, default={}, comment="Dữ liệu đối tượng")
    
    # Thông tin người yêu cầu
    requester_id = Column(String, ForeignKey("nguoi_dung.id"), nullable=False)
    requester_name = Column(String(100), nullable=False, comment="Tên người yêu cầu")
    requester_type = Column(String(20), nullable=False, comment="Loại người yêu cầu")
    
    # Thông tin phê duyệt
    current_step = Column(Integer, default=1, comment="Bước hiện tại")
    total_steps = Column(Integer, default=1, comment="Tổng số bước")
    
    # Mô tả và lý do
    title = Column(String(200), nullable=False, comment="Tiêu đề phê duyệt")
    description = Column(Text, nullable=True, comment="Mô tả chi tiết")
    reason = Column(Text, nullable=True, comment="Lý do yêu cầu")
    
    # Thời gian
    submitted_at = Column(String(50), nullable=True, comment="Thời gian gửi yêu cầu")
    completed_at = Column(String(50), nullable=True, comment="Thời gian hoàn thành")
    
    # Kết quả
    final_decision = Column(String(20), nullable=True, comment="Quyết định cuối cùng")
    final_notes = Column(Text, nullable=True, comment="Ghi chú cuối cùng")
    
    # Metadata
    metadata = Column(JSON, default={}, comment="Thông tin bổ sung")
    
    # Relationships
    requester = relationship("User")
    steps = relationship("ApprovalStep", back_populates="approval", order_by="ApprovalStep.step_order")

class ApprovalStep(BaseModel):
    """Bảng bước phê duyệt"""
    __tablename__ = "buoc_phe_duyet"
    
    approval_id = Column(String, ForeignKey("phe_duyet.id"), nullable=False)
    
    # Thông tin bước
    step_order = Column(Integer, nullable=False, comment="Thứ tự bước")
    step_name = Column(String(100), nullable=False, comment="Tên bước")
    step_description = Column(Text, nullable=True, comment="Mô tả bước")
    
    # Người phê duyệt
    approver_id = Column(String, ForeignKey("nguoi_dung.id"), nullable=True)
    approver_name = Column(String(100), nullable=True, comment="Tên người phê duyệt")
    approver_role = Column(String(20), nullable=True, comment="Vai trò người phê duyệt")
    
    # Trạng thái và quyết định
    status = Column(Enum(StepStatus), default=StepStatus.PENDING, comment="Trạng thái bước")
    decision = Column(String(20), nullable=True, comment="Quyết định")
    decision_notes = Column(Text, nullable=True, comment="Ghi chú quyết định")
    
    # Thời gian
    assigned_at = Column(String(50), nullable=True, comment="Thời gian giao việc")
    processed_at = Column(String(50), nullable=True, comment="Thời gian xử lý")
    
    # Cấu hình bước
    is_required = Column(String(10), default="true", comment="Bước bắt buộc")
    can_skip = Column(String(10), default="false", comment="Có thể bỏ qua")
    timeout_hours = Column(Integer, default=24, comment="Thời gian timeout (giờ)")
    
    # Relationships
    approval = relationship("Approval", back_populates="steps")
    approver = relationship("User")