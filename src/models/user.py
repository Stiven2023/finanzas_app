"""
Modelos de datos - Usuario
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    """Representa un usuario del sistema"""
    id: Optional[int] = None
    username: str = ""
    email: str = ""
    currency: str = "COP"
    language: str = "es"
    created_at: Optional[datetime] = None
    
    def to_dict(self):
        """Convierte a diccionario"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'currency': self.currency,
            'language': self.language,
        }
