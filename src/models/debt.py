"""
Modelos de datos - Deuda
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Debt:
    """Representa una deuda de un usuario"""
    id: Optional[int] = None
    user_id: int = None
    creditor: str = ""
    balance: float = 0.0
    original_balance: float = 0.0
    monthly_payment: float = 0.0
    payment_date: str = ""
    status: str = "active"  # active, paid, overdue
    priority: int = 5
    priority_label: str = "Media"
    category: str = "personal"  # personal, business, credit_card, etc
    interest_rate: float = 0.0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @property
    def remaining_months(self):
        """Calcula meses restantes para pagar"""
        if self.monthly_payment > 0:
            return max(0, self.balance / self.monthly_payment)
        return 0
    
    @property
    def is_urgent(self):
        """Indica si es una deuda urgente"""
        return self.priority <= 2
    
    @property
    def progress_percentage(self):
        """Porcentaje pagado"""
        if self.original_balance > 0:
            return ((self.original_balance - self.balance) / self.original_balance) * 100
        return 0
    
    def to_dict(self):
        """Convierte a diccionario"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'creditor': self.creditor,
            'balance': self.balance,
            'original_balance': self.original_balance,
            'monthly_payment': self.monthly_payment,
            'payment_date': self.payment_date,
            'status': self.status,
            'priority': self.priority,
            'priority_label': self.priority_label,
            'category': self.category,
            'interest_rate': self.interest_rate,
        }
