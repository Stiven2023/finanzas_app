"""
Servicio de Monedas y Conversión
"""
import logging
from typing import Dict, Optional
from src.database.db import db
from config import SUPPORTED_CURRENCIES, config

logger = logging.getLogger(__name__)

class CurrencyService:
    """Servicio para gestión de monedas y conversiones"""
    
    # Tasas de cambio en caché (en producción usar API externa)
    EXCHANGE_RATES = {
        'USD_COP': 4000.0,  # 1 USD = 4000 COP (ejemplo)
        'EUR_COP': 4400.0,
        'USD_EUR': 0.92,
        'COP_USD': 0.00025,
    }
    
    @staticmethod
    def get_supported_currencies() -> Dict:
        """Retorna monedas soportadas"""
        return SUPPORTED_CURRENCIES
    
    @staticmethod
    def get_exchange_rate(from_currency: str, to_currency: str) -> Optional[float]:
        """Obtiene tasa de cambio entre dos monedas"""
        if from_currency == to_currency:
            return 1.0
        
        key = f"{from_currency}_{to_currency}"
        
        # Intentar obtener de BD
        query = """
            SELECT rate FROM exchange_rates
            WHERE from_currency = ? AND to_currency = ?
        """
        results = db.execute_query(query, (from_currency, to_currency))
        
        if results:
            return results[0][0]
        
        # Si no está en BD, intentar invertir
        reverse_key = f"{to_currency}_{from_currency}"
        results = db.execute_query(query, (to_currency, from_currency))
        if results:
            return 1.0 / results[0][0]
        
        # Usar tasas de caché
        if key in CurrencyService.EXCHANGE_RATES:
            return CurrencyService.EXCHANGE_RATES[key]
        
        logger.warning(f"Tasa de cambio no encontrada: {from_currency} -> {to_currency}")
        return None
    
    @staticmethod
    def set_exchange_rate(from_currency: str, to_currency: str, rate: float) -> bool:
        """Establece una tasa de cambio"""
        try:
            # Verificar que exista
            query = """
                SELECT id FROM exchange_rates
                WHERE from_currency = ? AND to_currency = ?
            """
            results = db.execute_query(query, (from_currency, to_currency))
            
            if results:
                # Actualizar
                query = """
                    UPDATE exchange_rates SET rate = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE from_currency = ? AND to_currency = ?
                """
                return db.execute_update(query, (rate, from_currency, to_currency))
            else:
                # Insertar
                query = """
                    INSERT INTO exchange_rates (from_currency, to_currency, rate)
                    VALUES (?, ?, ?)
                """
                db.execute_insert(query, (from_currency, to_currency, rate))
                return True
        except Exception as e:
            logger.error(f"Error estableciendo tasa de cambio: {e}")
            return False
    
    @staticmethod
    def convert(amount: float, from_currency: str, to_currency: str) -> float:
        """
        Convierte una cantidad de una moneda a otra
        
        Args:
            amount: Cantidad a convertir
            from_currency: Moneda origen
            to_currency: Moneda destino
        
        Returns:
            Cantidad convertida
        """
        if from_currency == to_currency:
            return amount
        
        rate = CurrencyService.get_exchange_rate(from_currency, to_currency)
        if rate is None:
            logger.warning(f"No se puede convertir {from_currency} a {to_currency}")
            return amount
        
        return amount * rate
    
    @staticmethod
    def format_amount(amount: float, currency: str = None) -> str:
        """Formatea cantidad con símbolo de moneda"""
        if currency is None:
            currency = config.currency
        
        if currency not in SUPPORTED_CURRENCIES:
            currency = "USD"
        
        curr_info = SUPPORTED_CURRENCIES[currency]
        symbol = curr_info["symbol"]
        decimals = curr_info["decimals"]
        
        if decimals == 0:
            return f"{symbol}{amount:,.0f}"
        else:
            return f"{symbol}{amount:,.{decimals}f}"
    
    @staticmethod
    def get_user_currency(user_id: int) -> str:
        """Obtiene la moneda configurada de un usuario"""
        query = "SELECT currency FROM users WHERE id = ?"
        results = db.execute_query(query, (user_id,))
        return results[0][0] if results else DEFAULT_CURRENCY
    
    @staticmethod
    def set_user_currency(user_id: int, currency: str) -> bool:
        """Establece la moneda de un usuario"""
        if currency not in SUPPORTED_CURRENCIES:
            return False
        
        query = "UPDATE users SET currency = ? WHERE id = ?"
        return db.execute_update(query, (currency, user_id))

DEFAULT_CURRENCY = "COP"
