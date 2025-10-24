"""
File management API endpoints for 7tỷ.vn system
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from pydantic import BaseModel
from datetime import datetime, date
import os
import uuid
import shutil
from pathlib import Path

from ..database import get_db
from ..models.users import User
from ..models.files import FileRecord
from ..auth.dependencies import get_current_user

router = APIRouter()

# Configuration
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt'}

# Pydantic models
class FileInfo(BaseModel):
    id: str
    ten_file: str
    duong_dan: str
    kich_thuoc: int
    loai_file: str
    mo_ta: Optional[str] = None
    thoi_gian_tao: datetime

class FileUploadResponse(BaseModel):
    message: str
    file_id: str
    file_url: str
    file_info: FileInfo

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    mo_ta: Optional[str] = Form(None),
    loai_file: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload file lên hệ thống"""
    try:
        # Kiểm tra file
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không có file được chọn"
            )
        
        # Kiểm tra extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Định dạng file không được hỗ trợ. Chỉ chấp nhận: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Kiểm tra kích thước file
        file_content = await file.read()
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File quá lớn. Kích thước tối đa: {MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        # Tạo tên file unique
        file_id = str(uuid.uuid4())
        new_filename = f"{file_id}{file_ext}"
        file_path = UPLOAD_DIR / new_filename
        
        # Lưu file
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        
        # Lưu thông tin file vào database
        file_record = FileRecord(
            id=file_id,
            ten_file=file.filename,
            ten_file_goc=file.filename,
            duong_dan=str(file_path),
            kich_thuoc=len(file_content),
            loai_file=loai_file or file.content_type or 'unknown',
            mo_ta=mo_ta,
            nguoi_tao_id=current_user.id,
            trang_thai='hoat_dong'
        )
        
        db.add(file_record)
        db.commit()
        db.refresh(file_record)
        
        file_info = FileInfo(
            id=file_record.id,
            ten_file=file_record.ten_file,
            duong_dan=file_record.duong_dan,
            kich_thuoc=file_record.kich_thuoc,
            loai_file=file_record.loai_file,
            mo_ta=file_record.mo_ta,
            thoi_gian_tao=file_record.thoi_gian_tao
        )
        
        return FileUploadResponse(
            message="Upload file thành công",
            file_id=file_record.id,
            file_url=f"/api/files/{file_record.id}/download",
            file_info=file_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Xóa file nếu có lỗi
        if 'file_path' in locals() and file_path.exists():
            file_path.unlink()
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi upload file: {str(e)}"
        )

@router.get("/")
async def get_files(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    file_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy danh sách file"""
    try:
        query = db.query(FileRecord).filter(FileRecord.trang_thai == 'hoat_dong')
        
        # Phân quyền: user chỉ xem file của mình, admin xem tất cả
        if current_user.vai_tro not in ['admin', 'quan_ly']:
            query = query.filter(FileRecord.nguoi_tao_id == current_user.id)
        
        if search:
            query = query.filter(
                or_(
                    FileRecord.ten_file.ilike(f"%{search}%"),
                    FileRecord.mo_ta.ilike(f"%{search}%")
                )
            )
        
        if file_type:
            query = query.filter(FileRecord.loai_file.ilike(f"%{file_type}%"))
        
        total = query.count()
        files = query.order_by(FileRecord.thoi_gian_tao.desc()).offset(skip).limit(limit).all()
        
        return {
            "total": total,
            "files": files,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi lấy danh sách file: {str(e)}"
        )

@router.get("/{file_id}")
async def get_file_info(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy thông tin file"""
    try:
        query = db.query(FileRecord).filter(
            and_(
                FileRecord.id == file_id,
                FileRecord.trang_thai == 'hoat_dong'
            )
        )
        
        # Phân quyền
        if current_user.vai_tro not in ['admin', 'quan_ly']:
            query = query.filter(FileRecord.nguoi_tao_id == current_user.id)
        
        file_record = query.first()
        if not file_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy file"
            )
        
        return file_record
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi lấy thông tin file: {str(e)}"
        )

@router.get("/{file_id}/download")
async def download_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download file"""
    try:
        query = db.query(FileRecord).filter(
            and_(
                FileRecord.id == file_id,
                FileRecord.trang_thai == 'hoat_dong'
            )
        )
        
        # Phân quyền
        if current_user.vai_tro not in ['admin', 'quan_ly']:
            query = query.filter(FileRecord.nguoi_tao_id == current_user.id)
        
        file_record = query.first()
        if not file_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy file"
            )
        
        file_path = Path(file_record.duong_dan)
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File không tồn tại trên hệ thống"
            )
        
        # Cập nhật số lần tải
        file_record.so_lan_tai = (file_record.so_lan_tai or 0) + 1
        file_record.lan_tai_cuoi = datetime.utcnow()
        db.commit()
        
        return FileResponse(
            path=file_path,
            filename=file_record.ten_file_goc,
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi download file: {str(e)}"
        )

@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Xóa file"""
    try:
        query = db.query(FileRecord).filter(FileRecord.id == file_id)
        
        # Phân quyền
        if current_user.vai_tro not in ['admin', 'quan_ly']:
            query = query.filter(FileRecord.nguoi_tao_id == current_user.id)
        
        file_record = query.first()
        if not file_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy file"
            )
        
        # Soft delete
        file_record.trang_thai = 'da_xoa'
        file_record.thoi_gian_xoa = datetime.utcnow()
        file_record.nguoi_xoa_id = current_user.id
        
        db.commit()
        
        return {"message": "Xóa file thành công"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi xóa file: {str(e)}"
        )

@router.post("/upload-multiple")
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    mo_ta: Optional[str] = Form(None),
    loai_file: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload nhiều file cùng lúc"""
    try:
        if len(files) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chỉ được upload tối đa 10 file cùng lúc"
            )
        
        uploaded_files = []
        
        for file in files:
            if not file.filename:
                continue
                
            # Kiểm tra extension
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in ALLOWED_EXTENSIONS:
                continue
            
            # Kiểm tra kích thước
            file_content = await file.read()
            if len(file_content) > MAX_FILE_SIZE:
                continue
            
            # Tạo tên file unique
            file_id = str(uuid.uuid4())
            new_filename = f"{file_id}{file_ext}"
            file_path = UPLOAD_DIR / new_filename
            
            # Lưu file
            with open(file_path, "wb") as buffer:
                buffer.write(file_content)
            
            # Lưu vào database
            file_record = FileRecord(
                id=file_id,
                ten_file=file.filename,
                ten_file_goc=file.filename,
                duong_dan=str(file_path),
                kich_thuoc=len(file_content),
                loai_file=loai_file or file.content_type or 'unknown',
                mo_ta=mo_ta,
                nguoi_tao_id=current_user.id,
                trang_thai='hoat_dong'
            )
            
            db.add(file_record)
            uploaded_files.append({
                "file_id": file_id,
                "filename": file.filename,
                "size": len(file_content),
                "url": f"/api/files/{file_id}/download"
            })
        
        db.commit()
        
        return {
            "message": f"Upload thành công {len(uploaded_files)} file",
            "uploaded_files": uploaded_files
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        # Cleanup uploaded files on error
        for file_info in uploaded_files:
            file_path = UPLOAD_DIR / f"{file_info['file_id']}{Path(file_info['filename']).suffix}"
            if file_path.exists():
                file_path.unlink()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi upload files: {str(e)}"
        )

@router.get("/stats/summary")
async def get_file_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy thống kê file"""
    try:
        query = db.query(FileRecord).filter(FileRecord.trang_thai == 'hoat_dong')
        
        # Phân quyền
        if current_user.vai_tro not in ['admin', 'quan_ly']:
            query = query.filter(FileRecord.nguoi_tao_id == current_user.id)
        
        total_files = query.count()
        total_size = query.with_entities(func.sum(FileRecord.kich_thuoc)).scalar() or 0
        
        # Thống kê theo loại file
        file_types = db.query(
            FileRecord.loai_file,
            func.count(FileRecord.id).label('count'),
            func.sum(FileRecord.kich_thuoc).label('total_size')
        ).filter(FileRecord.trang_thai == 'hoat_dong')
        
        if current_user.vai_tro not in ['admin', 'quan_ly']:
            file_types = file_types.filter(FileRecord.nguoi_tao_id == current_user.id)
        
        file_types = file_types.group_by(FileRecord.loai_file).all()
        
        return {
            "total_files": total_files,
            "total_size": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "file_types": [
                {
                    "type": ft.loai_file,
                    "count": ft.count,
                    "size": ft.total_size or 0,
                    "size_mb": round((ft.total_size or 0) / (1024 * 1024), 2)
                }
                for ft in file_types
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi lấy thống kê file: {str(e)}"
        )