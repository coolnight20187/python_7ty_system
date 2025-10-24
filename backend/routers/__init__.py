"""
API Routers for 7tỷ.vn system
"""

from .auth import router as auth_router
from .admin import router as admin_router
from .agent import router as agent_router
from .customer import router as customer_router
from .bills import router as bill_router
from .transactions import router as transaction_router
from .approvals import router as approval_router
from .files import router as file_router

__all__ = [
    "auth_router",
    "admin_router", 
    "agent_router",
    "customer_router",
    "bill_router",
    "transaction_router",
    "approval_router",
    "file_router"
]