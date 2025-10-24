"""
Authentication API endpoints
"""

from datetime import timedelta
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..database import get_db
from ..models.users import User
from ..auth.jwt_handler import create_access_token
from ..auth.password import verify_password
from ..auth.dependencies import get_current_active_user

router = APIRouter()

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user_info: Dict[str, Any]
    message: str

class UserInfo(BaseModel):
    id: str
    username: str
    full_name: str
    role: str
    phone: str
    email: str = None

@router.post("/login", response_model=LoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Đăng nhập hệ thống"""
    
    # Find user by username
    user = db.query(User).filter(
        User.username == form_data.username,
        User.is_active == True,
        User.deleted_at.is_(None)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không chính xác"
        )
    
    # Verify password
    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không chính xác"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=1440)  # 24 hours
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "username": user.username,
            "role": user.role,
            "full_name": user.full_name
        },
        expires_delta=access_token_expires
    )
    
    # Update last login
    user.last_login = str(datetime.utcnow())
    db.commit()
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=86400,  # 24 hours in seconds
        user_info={
            "id": str(user.id),
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role,
            "phone": user.phone,
            "email": user.email
        },
        message="Đăng nhập thành công"
    )

@router.get("/me", response_model=UserInfo)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Lấy thông tin người dùng hiện tại"""
    
    return UserInfo(
        id=str(current_user.id),
        username=current_user.username,
        full_name=current_user.full_name,
        role=current_user.role,
        phone=current_user.phone,
        email=current_user.email
    )

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user)
):
    """Đăng xuất hệ thống"""
    
    return {
        "message": "Đăng xuất thành công",
        "user": current_user.username
    }

@router.post("/refresh-token")
async def refresh_token(
    current_user: User = Depends(get_current_active_user)
):
    """Làm mới token"""
    
    # Create new access token
    access_token_expires = timedelta(minutes=1440)  # 24 hours
    access_token = create_access_token(
        data={
            "sub": str(current_user.id),
            "username": current_user.username,
            "role": current_user.role,
            "full_name": current_user.full_name
        },
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 86400,
        "message": "Token đã được làm mới"
    }