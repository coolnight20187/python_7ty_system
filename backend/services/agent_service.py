"""
Agent service layer for business logic
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from decimal import Decimal
from datetime import datetime, date

from ..models.agents import Agent
from ..models.users import User
from ..models.customers import Customer
from ..models.transactions import Transaction
from ..auth.password import get_password_hash

class AgentService:
    
    @staticmethod
    def create_agent(db: Session, user_data: Dict, agent_data: Dict) -> Agent:
        """Tạo đại lý mới"""
        # Tạo user trước
        new_user = User(
            ten_dang_nhap=user_data['ten_dang_nhap'],
            email=user_data['email'],
            ho_ten=user_data['ho_ten'],
            so_dien_thoai=user_data['so_dien_thoai'],
            vai_tro='dai_ly',
            mat_khau_hash=get_password_hash(user_data['mat_khau']),
            trang_thai='cho_duyet'
        )
        
        db.add(new_user)
        db.flush()  # Để lấy ID
        
        # Tạo agent
        new_agent = Agent(
            nguoi_dung_id=new_user.id,
            ma_dai_ly=f"DL{datetime.now().strftime('%Y%m%d')}{new_user.id:04d}",
            dia_chi=agent_data['dia_chi'],
            tinh_thanh=agent_data['tinh_thanh'],
            quan_huyen=agent_data['quan_huyen'],
            phuong_xa=agent_data['phuong_xa'],
            so_du_hien_tai=Decimal('0'),
            trang_thai='cho_duyet'
        )
        
        db.add(new_agent)
        return new_agent
    
    @staticmethod
    def get_agent_stats(db: Session, agent: Agent) -> Dict:
        """Lấy thống kê đại lý"""
        total_customers = db.query(Customer).filter(Customer.dai_ly_id == agent.id).count()
        
        total_transactions = db.query(Transaction).filter(
            Transaction.dai_ly_id == agent.id
        ).count()
        
        total_commission = db.query(func.sum(Transaction.hoa_hong)).filter(
            and_(
                Transaction.dai_ly_id == agent.id,
                Transaction.trang_thai == 'thanh_cong'
            )
        ).scalar() or Decimal('0')
        
        current_month = datetime.now().replace(day=1)
        monthly_revenue = db.query(func.sum(Transaction.so_tien)).filter(
            and_(
                Transaction.dai_ly_id == agent.id,
                Transaction.trang_thai == 'thanh_cong',
                Transaction.thoi_gian_tao >= current_month
            )
        ).scalar() or Decimal('0')
        
        return {
            'total_customers': total_customers,
            'total_transactions': total_transactions,
            'total_commission': total_commission,
            'monthly_revenue': monthly_revenue
        }
    
    @staticmethod
    def calculate_commission(transaction_amount: Decimal, agent_level: str = 'basic') -> Decimal:
        """Tính hoa hồng cho đại lý"""
        commission_rates = {
            'basic': Decimal('0.02'),  # 2%
            'silver': Decimal('0.025'),  # 2.5%
            'gold': Decimal('0.03'),  # 3%
            'platinum': Decimal('0.035')  # 3.5%
        }
        
        rate = commission_rates.get(agent_level, commission_rates['basic'])
        return transaction_amount * rate
    
    @staticmethod
    def update_agent_balance(db: Session, agent: Agent) -> Decimal:
        """Cập nhật số dư đại lý"""
        total_income = db.query(func.sum(Transaction.hoa_hong)).filter(
            and_(
                Transaction.dai_ly_id == agent.id,
                Transaction.trang_thai == 'thanh_cong',
                Transaction.loai_giao_dich.in_(['hoa_hong', 'nap_tien'])
            )
        ).scalar() or Decimal('0')
        
        total_expense = db.query(func.sum(Transaction.so_tien)).filter(
            and_(
                Transaction.dai_ly_id == agent.id,
                Transaction.trang_thai == 'thanh_cong',
                Transaction.loai_giao_dich.in_(['rut_tien', 'thanh_toan'])
            )
        ).scalar() or Decimal('0')
        
        current_balance = total_income - total_expense
        agent.so_du_hien_tai = current_balance
        
        return current_balance