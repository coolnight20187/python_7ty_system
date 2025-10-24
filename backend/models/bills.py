"""
Electric Bill and Provider models
"""

from sqlalchemy import Column, String, Date, ForeignKey, Text, JSON, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class BillStatus(str, enum.Enum):
    AVAILABLE = "co_san"
    RESERVED = "da_dat"
    SOLD = "da_ban"
    EXPIRED = "het_han"
    PROCESSING = "dang_xu_ly"

class ProviderStatus(str, enum.Enum):
    ACTIVE = "hoat_dong"
    INACTIVE = "tam_dung"
    MAINTENANCE = "bao_tri"

class Provider(BaseModel):
    """Bảng nhà cung cấp điện"""
    __tablename__ = "nha_cung_cap"
    
    provider_code = Column(String(10), unique=True, nullable=False, comment="Mã nhà cung cấp")
    provider_name = Column(String(100), nullable=False, comment="Tên nhà cung cấp")
    provider_type = Column(String(20), default="dien", comment="Loại dịch vụ")
    region = Column(String(50), nullable=True, comment="Khu vực phục vụ")
    
    # API thông tin
    api_endpoint = Column(String(500), nullable=True, comment="Endpoint API tra cứu")
    api_key = Column(String(200), nullable=True, comment="API Key")
    api_config = Column(JSON, default={}, comment="Cấu hình API")
    
    # Trạng thái
    status = Column(Enum(ProviderStatus), default=ProviderStatus.ACTIVE, comment="Trạng thái")
    
    # Thông tin liên hệ
    contact_info = Column(JSON, default={}, comment="Thông tin liên hệ")
    
    # Relationships
    bills = relationship("ElectricBill", back_populates="provider")

class ElectricBill(BaseModel):
    """Bảng hóa đơn điện"""
    __tablename__ = "hoa_don_dien"
    
    # Thông tin khách hàng
    customer_code = Column(String(13), nullable=False, index=True, comment="Mã khách hàng")
    customer_name = Column(String(100), nullable=False, comment="Tên khách hàng")
    customer_address = Column(Text, nullable=False, comment="Địa chỉ khách hàng")
    
    # Thông tin nhà cung cấp
    provider_id = Column(String, ForeignKey("nha_cung_cap.id"), nullable=False)
    provider_code = Column(String(10), nullable=False, comment="Mã nhà cung cấp")
    provider_name = Column(String(100), nullable=True, comment="Tên nhà cung cấp")
    
    # Thông tin kỳ thanh toán
    period = Column(String(10), nullable=False, comment="Kỳ thanh toán (MM/YYYY)")
    due_date = Column(Date, nullable=True, comment="Hạn thanh toán")
    
    # Số tiền
    previous_amount = Column(String(20), default="0", comment="Tiền kỳ trước")
    current_amount = Column(String(20), nullable=False, comment="Tiền kỳ này")
    total_amount = Column(String(20), nullable=False, comment="Tổng tiền")
    
    # Thông tin kho
    added_by_type = Column(String(20), default="admin", comment="Loại người nhập (admin/agent)")
    added_by_id = Column(String, nullable=True, comment="ID người nhập kho")
    added_by_name = Column(String(100), nullable=True, comment="Tên người nhập kho")
    
    # Thông tin xuất kho
    exported_at = Column(String(50), nullable=True, comment="Thời gian xuất kho")
    exported_to_id = Column(String, nullable=True, comment="ID khách hàng xuất kho")
    exported_to_name = Column(String(100), nullable=True, comment="Tên khách hàng xuất kho")
    
    # Trạng thái và xử lý
    status = Column(Enum(BillStatus), default=BillStatus.AVAILABLE, comment="Trạng thái hóa đơn")
    payment_status = Column(String(20), default="chua_thanh_toan", comment="Trạng thái thanh toán")
    
    # Biên nhận và hình ảnh
    receipt_image_url = Column(String(500), nullable=True, comment="Ảnh biên nhận")
    qr_code = Column(String(500), nullable=True, comment="Mã QR của hóa đơn")
    
    # Phí và hoa hồng
    fee_amount = Column(String(20), default="0", comment="Phí giao dịch")
    commission_amount = Column(String(20), default="0", comment="Hoa hồng")
    commission_rate = Column(String(10), default="0", comment="Tỷ lệ hoa hồng")
    
    # Ghi chú
    notes = Column(Text, nullable=True, comment="Ghi chú")
    
    # Metadata
    metadata = Column(JSON, default={}, comment="Thông tin bổ sung")
    
    # Relationships
    provider = relationship("Provider", back_populates="bills")