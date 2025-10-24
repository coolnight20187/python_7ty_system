"""
Approval API endpoints for 7tỷ.vn system
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal

from ..database import get_db
from ..models.users import User
from ..models.approvals import Approval
from ..models.transactions import Transaction
from ..models.agents import Agent
from ..auth.dependencies import get_current_user

router = APIRouter()

# Pydantic models
class ApprovalCreate(BaseModel):
    loai_duyet: str
    doi_tuong_id: str
    ly_do: str
    du_lieu_cu: Optional[Dict] = None
    du_lieu_moi: Optional[Dict] = None

class ApprovalUpdate(BaseModel):
    trang_thai: str
    ghi_chu_duyet: Optional[str] = None

class ApprovalStats(BaseModel):
    total_pending: int
    total_approved: int
    total_rejected: int
    today_pending: int

@router.get("/stats", response_model=ApprovalStats)
async def get_approval_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy thống kê phê duyệt"""
    try:
        if current_user.vai_tro not in ['admin', 'quan_ly']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Không có quyền xem thống kê phê duyệt"
            )
        
        today = date.today()
        
        stats = ApprovalStats(
            total_pending=db.query(Approval).filter(Approval.trang_thai == 'cho_duyet').count(),
            total_approved=db.query(Approval).filter(Approval.trang_thai == 'da_duyet').count(),
            total_rejected=db.query(Approval).filter(Approval.trang_thai == 'tu_choi').count(),
            today_pending=db.query(Approval).filter(
                and_(
                    Approval.trang_thai == 'cho_duyet',
                    func.date(Approval.thoi_gian_tao) == today
                )
            ).count()
        )
        
        return stats
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi lấy thống kê phê duyệt: {str(e)}"
        )

@router.get("/")
async def get_approvals(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    approval_type: Optional[str] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy danh sách phê duyệt"""
    try:
        if current_user.vai_tro not in ['admin', 'quan_ly']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Không có quyền xem danh sách phê duyệt"
            )
        
        query = db.query(Approval)
        
        if status:
            query = query.filter(Approval.trang_thai == status)
        
        if approval_type:
            query = query.filter(Approval.loai_duyet == approval_type)
        
        if from_date:
            query = query.filter(func.date(Approval.thoi_gian_tao) >= from_date)
        
        if to_date:
            query = query.filter(func.date(Approval.thoi_gian_tao) <= to_date)
        
        total = query.count()
        approvals = query.order_by(Approval.thoi_gian_tao.desc()).offset(skip).limit(limit).all()
        
        return {
            "total": total,
            "approvals": approvals,
            "skip": skip,
            "limit": limit
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi lấy danh sách phê duyệt: {str(e)}"
        )

@router.get("/{approval_id}")
async def get_approval_detail(
    approval_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy chi tiết phê duyệt"""
    try:
        if current_user.vai_tro not in ['admin', 'quan_ly']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Không có quyền xem chi tiết phê duyệt"
            )
        
        approval = db.query(Approval).filter(Approval.id == approval_id).first()
        if not approval:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy phê duyệt"
            )
        
        return approval
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi lấy chi tiết phê duyệt: {str(e)}"
        )

@router.post("/")
async def create_approval(
    approval_data: ApprovalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Tạo yêu cầu phê duyệt"""
    try:
        # Tạo yêu cầu phê duyệt mới
        new_approval = Approval(
            loai_duyet=approval_data.loai_duyet,
            doi_tuong_id=approval_data.doi_tuong_id,
            ly_do=approval_data.ly_do,
            du_lieu_cu=approval_data.du_lieu_cu,
            du_lieu_moi=approval_data.du_lieu_moi,
            nguoi_gui_id=current_user.id,
            trang_thai='cho_duyet'
        )
        
        db.add(new_approval)
        db.commit()
        db.refresh(new_approval)
        
        return {
            "message": "Tạo yêu cầu phê duyệt thành công",
            "approval_id": new_approval.id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi tạo yêu cầu phê duyệt: {str(e)}"
        )

@router.put("/{approval_id}")
async def update_approval(
    approval_id: str,
    approval_data: ApprovalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cập nhật trạng thái phê duyệt"""
    try:
        if current_user.vai_tro not in ['admin', 'quan_ly']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Không có quyền phê duyệt"
            )
        
        approval = db.query(Approval).filter(
            and_(
                Approval.id == approval_id,
                Approval.trang_thai == 'cho_duyet'
            )
        ).first()
        
        if not approval:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy yêu cầu phê duyệt hoặc đã được xử lý"
            )
        
        # Cập nhật trạng thái
        approval.trang_thai = approval_data.trang_thai
        approval.ghi_chu_duyet = approval_data.ghi_chu_duyet
        approval.nguoi_duyet_id = current_user.id
        approval.thoi_gian_duyet = datetime.utcnow()
        
        # Xử lý logic nghiệp vụ dựa trên loại phê duyệt
        if approval_data.trang_thai == 'da_duyet':
            await _process_approved_request(approval, db)
        
        db.commit()
        
        return {"message": "Cập nhật phê duyệt thành công"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cập nhật phê duyệt: {str(e)}"
        )

@router.post("/{approval_id}/approve")
async def approve_request(
    approval_id: str,
    note: Optional[str] = Query(None, description="Ghi chú phê duyệt"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Phê duyệt yêu cầu"""
    try:
        if current_user.vai_tro not in ['admin', 'quan_ly']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Không có quyền phê duyệt"
            )
        
        approval = db.query(Approval).filter(
            and_(
                Approval.id == approval_id,
                Approval.trang_thai == 'cho_duyet'
            )
        ).first()
        
        if not approval:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy yêu cầu phê duyệt hoặc đã được xử lý"
            )
        
        # Cập nhật trạng thái
        approval.trang_thai = 'da_duyet'
        approval.ghi_chu_duyet = note
        approval.nguoi_duyet_id = current_user.id
        approval.thoi_gian_duyet = datetime.utcnow()
        
        # Xử lý logic nghiệp vụ
        await _process_approved_request(approval, db)
        
        db.commit()
        
        return {"message": "Phê duyệt thành công"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi phê duyệt: {str(e)}"
        )

@router.post("/{approval_id}/reject")
async def reject_request(
    approval_id: str,
    reason: str = Query(..., description="Lý do từ chối"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Từ chối yêu cầu phê duyệt"""
    try:
        if current_user.vai_tro not in ['admin', 'quan_ly']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Không có quyền từ chối phê duyệt"
            )
        
        approval = db.query(Approval).filter(
            and_(
                Approval.id == approval_id,
                Approval.trang_thai == 'cho_duyet'
            )
        ).first()
        
        if not approval:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy yêu cầu phê duyệt hoặc đã được xử lý"
            )
        
        # Cập nhật trạng thái
        approval.trang_thai = 'tu_choi'
        approval.ghi_chu_duyet = reason
        approval.nguoi_duyet_id = current_user.id
        approval.thoi_gian_duyet = datetime.utcnow()
        
        db.commit()
        
        return {"message": "Từ chối phê duyệt thành công"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi từ chối phê duyệt: {str(e)}"
        )

@router.get("/my-requests")
async def get_my_approval_requests(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy danh sách yêu cầu phê duyệt của tôi"""
    try:
        query = db.query(Approval).filter(Approval.nguoi_gui_id == current_user.id)
        
        if status:
            query = query.filter(Approval.trang_thai == status)
        
        total = query.count()
        approvals = query.order_by(Approval.thoi_gian_tao.desc()).offset(skip).limit(limit).all()
        
        return {
            "total": total,
            "approvals": approvals,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi lấy danh sách yêu cầu: {str(e)}"
        )

async def _process_approved_request(approval: Approval, db: Session):
    """Xử lý logic nghiệp vụ khi yêu cầu được phê duyệt"""
    try:
        if approval.loai_duyet == 'dang_ky_dai_ly':
            # Kích hoạt tài khoản đại lý
            agent = db.query(Agent).filter(Agent.id == approval.doi_tuong_id).first()
            if agent:
                agent.trang_thai = 'hoat_dong'
                agent.thoi_gian_kich_hoat = datetime.utcnow()
        
        elif approval.loai_duyet == 'rut_tien':
            # Xử lý yêu cầu rút tiền
            transaction = db.query(Transaction).filter(Transaction.id == approval.doi_tuong_id).first()
            if transaction:
                transaction.trang_thai = 'da_duyet'
                # Cập nhật số dư đại lý
                if transaction.dai_ly_id:
                    agent = db.query(Agent).filter(Agent.id == transaction.dai_ly_id).first()
                    if agent and agent.so_du_hien_tai >= transaction.so_tien:
                        agent.so_du_hien_tai -= transaction.so_tien
        
        elif approval.loai_duyet == 'cap_nhat_thong_tin':
            # Áp dụng thay đổi thông tin
            if approval.du_lieu_moi:
                # Logic cập nhật thông tin dựa trên du_lieu_moi
                pass
        
    except Exception as e:
        # Log error nhưng không raise để không ảnh hưởng đến việc phê duyệt
        print(f"Error processing approved request: {str(e)}")