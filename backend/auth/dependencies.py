"""
Authentication dependencies
"""

from typing import List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .jwt_handler import get_current_user
from ..database import get_db
from ..models.users import User

security = HTTPBearer()

async def get_current_active_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Lấy người dùng hiện tại đang hoạt động"""
    
    # Verify token
    current_user_data = await get_current_user(credentials.credentials)
    
    # Get user from database
    user = db.query(User).filter(
        User.id == current_user_data["user_id"],
        User.is_active == True,
        User.deleted_at.is_(None)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng"
        )
    
    return user

def require_role(allowed_roles: List[str]):
    """Decorator yêu cầu vai trò cụ thể"""
    def role_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Không có quyền truy cập"
            )
        return current_user
    return role_checker

# Pre-defined role dependencies
require_admin = require_role(["admin"])
require_staff = require_role(["admin", "nhan_vien"])
require_agent = require_role(["admin", "nhan_vien", "dai_ly"])
require_customer = require_role(["admin", "nhan_vien", "khach_the"])