"""
File Upload model
"""

from sqlalchemy import Column, String, Integer, ForeignKey, Text, JSON, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class FileType(str, enum.Enum):
    IMAGE = "hinh_anh"
    DOCUMENT = "tai_lieu"
    RECEIPT = "bien_nhan"
    ID_CARD = "cmnd_cccd"
    BUSINESS_LICENSE = "giay_phep_kd"
    BANK_STATEMENT = "sao_ke_ngan_hang"

class FileStatus(str, enum.Enum):
    UPLOADING = "dang_tai_len"
    UPLOADED = "da_tai_len"
    PROCESSING = "dang_xu_ly"
    PROCESSED = "da_xu_ly"
    FAILED = "that_bai"
    DELETED = "da_xoa"

class FileUpload(BaseModel):
    """Bảng tải lên tệp tin"""
    __tablename__ = "tai_len_tep"
    
    # Thông tin tệp tin
    original_filename = Column(String(255), nullable=False, comment="Tên tệp gốc")
    stored_filename = Column(String(255), nullable=False, comment="Tên tệp lưu trữ")
    file_path = Column(String(500), nullable=False, comment="Đường dẫn tệp")
    file_url = Column(String(500), nullable=True, comment="URL truy cập tệp")
    
    # Thông tin kỹ thuật
    file_size = Column(Integer, nullable=False, comment="Kích thước tệp (bytes)")
    file_type = Column(Enum(FileType), nullable=False, comment="Loại tệp")
    mime_type = Column(String(100), nullable=False, comment="MIME type")
    file_extension = Column(String(10), nullable=False, comment="Phần mở rộng")
    
    # Thông tin liên kết
    owner_id = Column(String, ForeignKey("nguoi_dung.id"), nullable=False)
    owner_type = Column(String(20), nullable=False, comment="Loại chủ sở hữu")
    related_id = Column(String, nullable=True, comment="ID đối tượng liên quan")
    related_type = Column(String(20), nullable=True, comment="Loại đối tượng liên quan")
    
    # Trạng thái
    status = Column(Enum(FileStatus), default=FileStatus.UPLOADING, comment="Trạng thái tệp")
    
    # Thông tin xử lý
    processing_result = Column(JSON, default={}, comment="Kết quả xử lý")
    ocr_text = Column(Text, nullable=True, comment="Văn bản OCR")
    
    # Mô tả
    title = Column(String(200), nullable=True, comment="Tiêu đề tệp")
    description = Column(Text, nullable=True, comment="Mô tả tệp")
    tags = Column(JSON, default=[], comment="Thẻ tag")
    
    # Bảo mật
    is_public = Column(String(10), default="false", comment="Công khai")
    access_permissions = Column(JSON, default=[], comment="Quyền truy cập")
    
    # Metadata
    metadata = Column(JSON, default={}, comment="Thông tin bổ sung")
    
    # Relationships
    owner = relationship("User")