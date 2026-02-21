"""
Modelos de datos - Transacción
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Transaction:
    """Representa una transacción financiera"""
    id: Optional[int] = None
    user_id: int = None
    amount: float = 0.0
    currency: str = "COP"
    type: str = "expense"  # expense, income, transfer
    category: str = ""
    description: str = ""
    date: str = ""
    week_id: Optional[int] = None
    goal_id: Optional[int] = None
    debt_id: Optional[int] = None
    notes: str = ""
    created_at: Optional[datetime] = None
    
    def is_income(self):
        """Indica si es un ingreso"""
        return self.type == "income"
    
    def is_expense(self):
        """Indica si es un gasto"""
        return self.type == "expense"
    
    def to_dict(self):
        """Convierte a diccionario"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'amount': self.amount,
            'currency': self.currency,
            'type': self.type,
            'category': self.category,
            'description': self.description,
            'date': self.date,
            'week_id': self.week_id,
            'goal_id': self.goal_id,
            'debt_id': self.debt_id,
            'notes': self.notes,
        }
