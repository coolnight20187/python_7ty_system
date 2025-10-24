"""
Electric Bills API endpoints
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from pydantic import BaseModel
import json
import asyncio
import httpx
from datetime import datetime

from ..database import get_db
from ..models.bills import ElectricBill, Provider
from ..models.users import User
from ..auth.dependencies import get_current_active_user, require_admin, require_staff
from ..services.bill_service import BillService
from ..services.excel_service import ExcelService

router = APIRouter()

class BillLookupRequest(BaseModel):
    customer_code: str
    provider_id: str

class BulkLookupRequest(BaseModel):
    customer_codes: List[str]
    provider_id: str
    use_external_api: bool = True

class BillResponse(BaseModel):
    id: str
    customer_code: str
    customer_name: str
    customer_address: str
    provider_name: str
    period: str
    previous_amount: str
    current_amount: str
    total_amount: str
    status: str
    created_at: str
    qr_code: str = None
    receipt_image_url: str = None

class BillCreateRequest(BaseModel):
    customer_code: str
    customer_name: str
    customer_address: str
    provider_id: str
    period: str
    previous_amount: str = "0"
    current_amount: str
    total_amount: str
    notes: str = None

@router.get("/providers")
async def get_providers(db: Session = Depends(get_db)):
    """Lấy danh sách nhà cung cấp điện"""
    
    providers = db.query(Provider).filter(
        Provider.status == "hoat_dong",
        Provider.deleted_at.is_(None)
    ).all()
    
    return [
        {
            "id": str(provider.id),
            "provider_code": provider.provider_code,
            "provider_name": provider.provider_name,
            "provider_type": provider.provider_type,
            "region": provider.region,
            "status": provider.status
        }
        for provider in providers
    ]

@router.post("/lookup")
async def lookup_single_bill(
    request: BillLookupRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Tra cứu hóa đơn điện đơn lẻ"""
    
    bill_service = BillService(db)
    
    try:
        # First check local database
        bill = bill_service.find_bill_by_customer_code(
            request.customer_code, 
            request.provider_id
        )
        
        if bill:
            return BillResponse(
                id=str(bill.id),
                customer_code=bill.customer_code,
                customer_name=bill.customer_name,
                customer_address=bill.customer_address,
                provider_name=bill.provider_name,
                period=bill.period,
                previous_amount=bill.previous_amount,
                current_amount=bill.current_amount,
                total_amount=bill.total_amount,
                status=bill.status,
                created_at=bill.created_at.isoformat() if bill.created_at else "",
                qr_code=bill.qr_code,
                receipt_image_url=bill.receipt_image_url
            )
        
        # If not found locally, try external API
        external_result = await bill_service.lookup_external_bill(
            request.customer_code,
            request.provider_id
        )
        
        if external_result:
            return external_result
        
        raise HTTPException(
            status_code=404,
            detail=f"Không tìm thấy hóa đơn cho mã khách hàng {request.customer_code}"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi tra cứu hóa đơn: {str(e)}"
        )

@router.post("/bulk-lookup")
async def bulk_lookup_bills(
    request: BulkLookupRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Công cụ tra cứu hóa đơn điện hàng loạt - Enhanced Version"""
    
    if len(request.customer_codes) > 1000:
        raise HTTPException(
            status_code=400,
            detail="Số lượng mã khách hàng vượt quá giới hạn (tối đa 1000)"
        )
    
    bill_service = BillService(db)
    results = []
    
    try:
        # Process in batches for better performance
        batch_size = 50
        for i in range(0, len(request.customer_codes), batch_size):
            batch = request.customer_codes[i:i + batch_size]
            
            # Process batch
            batch_results = await bill_service.bulk_lookup_bills(
                batch,
                request.provider_id,
                use_external_api=request.use_external_api
            )
            
            results.extend(batch_results)
            
            # Small delay to prevent overwhelming external APIs
            if request.use_external_api and i + batch_size < len(request.customer_codes):
                await asyncio.sleep(0.1)
        
        # Statistics
        successful_lookups = len([r for r in results if r.get("success", False)])
        failed_lookups = len(results) - successful_lookups
        
        return {
            "results": results,
            "statistics": {
                "total_requested": len(request.customer_codes),
                "successful_lookups": successful_lookups,
                "failed_lookups": failed_lookups,
                "success_rate": f"{(successful_lookups/len(request.customer_codes)*100):.1f}%"
            },
            "timestamp": datetime.utcnow().isoformat(),
            "processed_by": current_user.full_name
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi tra cứu hàng loạt: {str(e)}"
        )

@router.get("/warehouse")
async def get_warehouse_bills(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None),
    provider_id: Optional[str] = Query(None),
    period: Optional[str] = Query(None),
    min_amount: Optional[str] = Query(None),
    max_amount: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Lấy danh sách hóa đơn trong kho"""
    
    query = db.query(ElectricBill).filter(ElectricBill.deleted_at.is_(None))
    
    # Apply filters
    if status:
        query = query.filter(ElectricBill.status == status)
    
    if provider_id:
        query = query.filter(ElectricBill.provider_id == provider_id)
    
    if period:
        query = query.filter(ElectricBill.period == period)
    
    if min_amount:
        query = query.filter(ElectricBill.total_amount >= min_amount)
    
    if max_amount:
        query = query.filter(ElectricBill.total_amount <= max_amount)
    
    if search:
        search_filter = or_(
            ElectricBill.customer_code.ilike(f"%{search}%"),
            ElectricBill.customer_name.ilike(f"%{search}%"),
            ElectricBill.customer_address.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    # Get total count
    total = query.count()
    
    # Get paginated results
    bills = query.offset(skip).limit(limit).all()
    
    return {
        "bills": [
            {
                "id": str(bill.id),
                "customer_code": bill.customer_code,
                "customer_name": bill.customer_name,
                "customer_address": bill.customer_address,
                "provider_name": bill.provider_name,
                "period": bill.period,
                "previous_amount": bill.previous_amount,
                "current_amount": bill.current_amount,
                "total_amount": bill.total_amount,
                "status": bill.status,
                "added_by_name": bill.added_by_name,
                "exported_to_name": bill.exported_to_name,
                "created_at": bill.created_at.isoformat() if bill.created_at else "",
                "exported_at": bill.exported_at,
                "receipt_image_url": bill.receipt_image_url,
                "notes": bill.notes
            }
            for bill in bills
        ],
        "pagination": {
            "total": total,
            "skip": skip,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }
    }

@router.post("/warehouse")
async def add_bill_to_warehouse(
    request: BillCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff)
):
    """Thêm hóa đơn vào kho"""
    
    bill_service = BillService(db)
    
    try:
        # Check if bill already exists
        existing_bill = bill_service.find_bill_by_customer_code(
            request.customer_code,
            request.provider_id
        )
        
        if existing_bill:
            raise HTTPException(
                status_code=400,
                detail=f"Hóa đơn cho mã khách hàng {request.customer_code} đã tồn tại"
            )
        
        # Create new bill
        bill = bill_service.create_bill(
            customer_code=request.customer_code,
            customer_name=request.customer_name,
            customer_address=request.customer_address,
            provider_id=request.provider_id,
            period=request.period,
            previous_amount=request.previous_amount,
            current_amount=request.current_amount,
            total_amount=request.total_amount,
            added_by_id=str(current_user.id),
            added_by_name=current_user.full_name,
            notes=request.notes
        )
        
        return {
            "message": "Thêm hóa đơn vào kho thành công",
            "bill_id": str(bill.id),
            "customer_code": bill.customer_code
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi thêm hóa đơn: {str(e)}"
        )

@router.post("/export-warehouse")
async def export_warehouse_to_excel(
    provider_id: Optional[str] = None,
    status: Optional[str] = None,
    period: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff)
):
    """Xuất danh sách kho hóa đơn ra Excel"""
    
    try:
        query = db.query(ElectricBill).filter(ElectricBill.deleted_at.is_(None))
        
        # Apply filters
        if provider_id:
            query = query.filter(ElectricBill.provider_id == provider_id)
        if status:
            query = query.filter(ElectricBill.status == status)
        if period:
            query = query.filter(ElectricBill.period == period)
        
        bills = query.all()
        
        excel_service = ExcelService()
        file_path = await excel_service.export_bills_to_excel(bills)
        
        return {
            "message": "Xuất Excel thành công",
            "file_path": file_path,
            "total_records": len(bills),
            "exported_by": current_user.full_name,
            "exported_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi xuất Excel: {str(e)}"
        )

@router.post("/{bill_id}/export")
async def export_bill_to_customer(
    bill_id: str,
    customer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Xuất hóa đơn cho khách hàng"""
    
    bill_service = BillService(db)
    
    try:
        result = bill_service.export_bill_to_customer(
            bill_id=bill_id,
            customer_id=customer_id,
            exported_by_id=str(current_user.id),
            exported_by_name=current_user.full_name
        )
        
        return {
            "message": "Xuất hóa đơn thành công",
            "bill_id": bill_id,
            "customer_id": customer_id,
            "exported_at": result["exported_at"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi xuất hóa đơn: {str(e)}"
        )

@router.post("/{bill_id}/upload-receipt")
async def upload_receipt_image(
    bill_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Upload ảnh biên nhận thanh toán"""
    
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail="Chỉ chấp nhận file hình ảnh"
        )
    
    bill_service = BillService(db)
    
    try:
        result = await bill_service.upload_receipt_image(
            bill_id=bill_id,
            file=file,
            uploaded_by_id=str(current_user.id)
        )
        
        return {
            "message": "Upload ảnh biên nhận thành công",
            "bill_id": bill_id,
            "image_url": result["image_url"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi upload ảnh: {str(e)}"
        )

@router.get("/statistics")
async def get_bill_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff)
):
    """Thống kê hóa đơn trong hệ thống"""
    
    try:
        # Total bills by status
        total_available = db.query(ElectricBill).filter(
            ElectricBill.status == "co_san",
            ElectricBill.deleted_at.is_(None)
        ).count()
        
        total_sold = db.query(ElectricBill).filter(
            ElectricBill.status == "da_ban",
            ElectricBill.deleted_at.is_(None)
        ).count()
        
        total_reserved = db.query(ElectricBill).filter(
            ElectricBill.status == "da_dat",
            ElectricBill.deleted_at.is_(None)
        ).count()
        
        # Total amount
        from sqlalchemy import func
        total_amount_result = db.query(
            func.sum(func.cast(ElectricBill.total_amount, db.Integer))
        ).filter(ElectricBill.deleted_at.is_(None)).scalar()
        
        total_amount = total_amount_result or 0
        
        return {
            "bill_statistics": {
                "total_available": total_available,
                "total_sold": total_sold,
                "total_reserved": total_reserved,
                "total_bills": total_available + total_sold + total_reserved
            },
            "financial_statistics": {
                "total_amount": str(total_amount),
                "formatted_amount": f"{total_amount:,} VND"
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi thống kê: {str(e)}"
        )