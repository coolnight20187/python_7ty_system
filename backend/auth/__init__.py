"""
Authentication module
"""

from .jwt_handler import create_access_token, verify_token, get_current_user
from .dependencies import get_current_active_user, require_role
from .password import hash_password, verify_password

__all__ = [
    "create_access_token",
    "verify_token", 
    "get_current_user",
    "get_current_active_user",
    "require_role",
    "hash_password",
    "verify_password"
]