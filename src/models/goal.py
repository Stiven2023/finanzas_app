"""
Modelos de datos - Meta Financiera
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Goal:
    """Representa una meta financiera"""
    id: Optional[int] = None
    user_id: int = None
    name: str = ""
    description: str = ""
    target_amount: float = 0.0
    current_amount: float = 0.0
    currency: str = "COP"
    target_date: Optional[str] = None
    category: str = "general"  # car, house, vacation, emergency, education, etc
    icon: str = "🎯"
    color: str = "#6366F1"
    status: str = "active"  # active, completed, paused, cancelled
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @property
    def remaining_amount(self):
        """Cantidad faltante para alcanzar la meta"""
        return max(0, self.target_amount - self.current_amount)
    
    @property
    def progress_percentage(self):
        """Porcentaje de progreso"""
        if self.target_amount > 0:
            return (self.current_amount / self.target_amount) * 100
        return 0
    
    @property
    def is_completed(self):
        """Indica si la meta está completada"""
        return self.current_amount >= self.target_amount
    
    def add_progress(self, amount):
        """Agrega progreso a la meta"""
        self.current_amount += amount
        if self.is_completed:
            self.status = "completed"
    
    def to_dict(self):
        """Convierte a diccionario"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'target_amount': self.target_amount,
            'current_amount': self.current_amount,
            'currency': self.currency,
            'target_date': self.target_date,
            'category': self.category,
            'icon': self.icon,
            'color': self.color,
            'status': self.status,
        }
