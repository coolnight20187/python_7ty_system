"""
Electric Bill Service - Business Logic
"""

import uuid
import asyncio
import httpx
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import UploadFile
import os

from ..models.bills import ElectricBill, Provider
from ..models.customers import Customer

class BillService:
    def __init__(self, db: Session):
        self.db = db
    
    def find_bill_by_customer_code(self, customer_code: str, provider_id: str) -> Optional[ElectricBill]:
        """Tìm hóa đơn theo mã khách hàng"""
        return self.db.query(ElectricBill).filter(
            ElectricBill.customer_code == customer_code,
            ElectricBill.provider_id == provider_id,
            ElectricBill.deleted_at.is_(None)
        ).first()
    
    async def lookup_external_bill(self, customer_code: str, provider_id: str) -> Optional[Dict[str, Any]]:
        """Tra cứu hóa đơn từ API bên ngoài"""
        
        # Get provider info
        provider = self.db.query(Provider).filter(Provider.id == provider_id).first()
        if not provider or not provider.api_endpoint:
            return None
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Mock external API call - replace with real API integration
                response = await self._mock_external_api_call(customer_code, provider)
                
                if response and response.get("success"):
                    return {
                        "id": str(uuid.uuid4()),
                        "customer_code": customer_code,
                        "customer_name": response.get("customer_name", f"Khách hàng {customer_code[-4:]}"),
                        "customer_address": response.get("address", f"Địa chỉ {customer_code[-4:]}"),
                        "provider_name": provider.provider_name,
                        "period": response.get("period", "11/2024"),
                        "previous_amount": str(response.get("previous_amount", 0)),
                        "current_amount": str(response.get("current_amount", 0)),
                        "total_amount": str(response.get("total_amount", 0)),
                        "status": "co_san",
                        "created_at": datetime.utcnow().isoformat(),
                        "source": "external_api"
                    }
                
        except Exception as e:
            print(f"External API error: {e}")
            return None
        
        return None
    
    async def _mock_external_api_call(self, customer_code: str, provider: Provider) -> Dict[str, Any]:
        """Mock external API call for demonstration"""
        
        # Simulate API delay
        await asyncio.sleep(0.1)
        
        # Generate mock data based on customer code
        code_hash = hash(customer_code) % 1000000
        
        return {
            "success": True,
            "customer_name": f"Khách hàng {customer_code[-4:]}",
            "address": f"Địa chỉ số {code_hash % 999 + 1}, Quận {(code_hash % 12) + 1}, TP.HCM",
            "period": "11/2024",
            "previous_amount": (code_hash % 100000) * 100,
            "current_amount": (150000 + (code_hash % 500000)) * 100,
            "total_amount": ((code_hash % 100000) + 150000 + (code_hash % 500000)) * 100,
            "due_date": "2024-12-15"
        }
    
    async def bulk_lookup_bills(
        self, 
        customer_codes: List[str], 
        provider_id: str,
        use_external_api: bool = True
    ) -> List[Dict[str, Any]]:
        """Tra cứu hóa đơn hàng loạt"""
        
        results = []
        
        for customer_code in customer_codes:
            try:
                customer_code = customer_code.strip()
                if not customer_code:
                    continue
                
                # Check local database first
                bill = self.find_bill_by_customer_code(customer_code, provider_id)
                
                if bill:
                    results.append({
                        "customer_code": customer_code,
                        "customer_name": bill.customer_name,
                        "customer_address": bill.customer_address,
                        "amount_previous": float(bill.previous_amount) / 100,
                        "amount_current": float(bill.current_amount) / 100,
                        "total_amount": float(bill.total_amount) / 100,
                        "period": bill.period,
                        "provider_name": bill.provider_name,
                        "status": bill.status,
                        "success": True,
                        "source": "database"
                    })
                elif use_external_api:
                    # Try external API
                    external_result = await self.lookup_external_bill(customer_code, provider_id)
                    
                    if external_result:
                        results.append({
                            "customer_code": customer_code,
                            "customer_name": external_result["customer_name"],
                            "customer_address": external_result["customer_address"],
                            "amount_previous": float(external_result["previous_amount"]) / 100,
                            "amount_current": float(external_result["current_amount"]) / 100,
                            "total_amount": float(external_result["total_amount"]) / 100,
                            "period": external_result["period"],
                            "provider_name": external_result["provider_name"],
                            "status": external_result["status"],
                            "success": True,
                            "source": "external_api"
                        })
                    else:
                        results.append({
                            "customer_code": customer_code,
                            "customer_name": "Không tìm thấy",
                            "customer_address": "N/A",
                            "amount_previous": 0,
                            "amount_current": 0,
                            "total_amount": 0,
                            "period": "N/A",
                            "provider_name": "N/A",
                            "status": "not_found",
                            "success": False,
                            "error": "Không tìm thấy hóa đơn"
                        })
                else:
                    results.append({
                        "customer_code": customer_code,
                        "customer_name": "Không tìm thấy",
                        "customer_address": "N/A",
                        "amount_previous": 0,
                        "amount_current": 0,
                        "total_amount": 0,
                        "period": "N/A",
                        "provider_name": "N/A",
                        "status": "not_found",
                        "success": False,
                        "error": "Không tìm thấy trong cơ sở dữ liệu"
                    })
                    
            except Exception as e:
                results.append({
                    "customer_code": customer_code,
                    "customer_name": "Lỗi tra cứu",
                    "customer_address": f"Error: {str(e)}",
                    "amount_previous": 0,
                    "amount_current": 0,
                    "total_amount": 0,
                    "period": "N/A",
                    "provider_name": "N/A",
                    "status": "error",
                    "success": False,
                    "error": str(e)
                })
        
        return results
    
    def create_bill(
        self,
        customer_code: str,
        customer_name: str,
        customer_address: str,
        provider_id: str,
        period: str,
        previous_amount: str,
        current_amount: str,
        total_amount: str,
        added_by_id: str,
        added_by_name: str,
        notes: str = None
    ) -> ElectricBill:
        """Tạo hóa đơn mới"""
        
        # Get provider info
        provider = self.db.query(Provider).filter(Provider.id == provider_id).first()
        
        bill = ElectricBill(
            customer_code=customer_code,
            customer_name=customer_name,
            customer_address=customer_address,
            provider_id=provider_id,
            provider_code=provider.provider_code if provider else "",
            provider_name=provider.provider_name if provider else "",
            period=period,
            previous_amount=previous_amount,
            current_amount=current_amount,
            total_amount=total_amount,
            added_by_type="admin",
            added_by_id=added_by_id,
            added_by_name=added_by_name,
            status="co_san",
            notes=notes
        )
        
        self.db.add(bill)
        self.db.commit()
        self.db.refresh(bill)
        
        return bill
    
    def export_bill_to_customer(
        self,
        bill_id: str,
        customer_id: str,
        exported_by_id: str,
        exported_by_name: str
    ) -> Dict[str, Any]:
        """Xuất hóa đơn cho khách hàng"""
        
        bill = self.db.query(ElectricBill).filter(ElectricBill.id == bill_id).first()
        if not bill:
            raise ValueError("Không tìm thấy hóa đơn")
        
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise ValueError("Không tìm thấy khách hàng")
        
        # Update bill status
        bill.status = "da_ban"
        bill.exported_at = datetime.utcnow().isoformat()
        bill.exported_to_id = customer_id
        bill.exported_to_name = customer.full_name
        
        self.db.commit()
        
        return {
            "exported_at": bill.exported_at,
            "customer_name": customer.full_name
        }
    
    async def upload_receipt_image(
        self,
        bill_id: str,
        file: UploadFile,
        uploaded_by_id: str
    ) -> Dict[str, Any]:
        """Upload ảnh biên nhận"""
        
        bill = self.db.query(ElectricBill).filter(ElectricBill.id == bill_id).first()
        if not bill:
            raise ValueError("Không tìm thấy hóa đơn")
        
        # Create upload directory
        upload_dir = "uploads/receipts"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        filename = f"{bill_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{file_extension}"
        file_path = os.path.join(upload_dir, filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Update bill with image URL
        bill.receipt_image_url = f"/uploads/receipts/{filename}"
        self.db.commit()
        
        return {
            "image_url": bill.receipt_image_url,
            "filename": filename
        }