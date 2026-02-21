"""
Servicio de Finanzas - Lógica de negocio para deudas y transacciones
"""
import logging
from typing import List, Optional
from datetime import datetime, date
from src.database.db import db
from src.models.debt import Debt
from src.models.transaction import Transaction

logger = logging.getLogger(__name__)

class FinanceService:
    """Servicio para operaciones financieras"""

    @staticmethod
    def _normalize_date_string(value: str) -> str:
        """Normaliza fechas a formato YYYY-MM-DD."""
        if not value:
            return ""
        if isinstance(value, str) and len(value) >= 10:
            return value[:10]
        return str(value)
    
    @staticmethod
    def get_all_debts(user_id: int) -> List[Debt]:
        """Obtiene todas las deudas de un usuario"""
        query = """
            SELECT id, user_id, creditor, balance, original_balance, 
                   monthly_payment, payment_date, status, priority, 
                   priority_label, category, interest_rate
            FROM debts WHERE user_id = ? ORDER BY priority
        """
        results = db.execute_query(query, (user_id,))
        debts = []
        for row in results:
            debt = Debt(
                id=row[0], user_id=row[1], creditor=row[2],
                balance=row[3], original_balance=row[4],
                monthly_payment=row[5], payment_date=row[6],
                status=row[7], priority=row[8], priority_label=row[9],
                category=row[10], interest_rate=row[11]
            )
            debts.append(debt)
        return debts
    
    @staticmethod
    def get_debt_by_id(debt_id: int) -> Optional[Debt]:
        """Obtiene una deuda específica"""
        query = """
            SELECT id, user_id, creditor, balance, original_balance,
                   monthly_payment, payment_date, status, priority,
                   priority_label, category, interest_rate
            FROM debts WHERE id = ?
        """
        results = db.execute_query(query, (debt_id,))
        if results:
            row = results[0]
            return Debt(
                id=row[0], user_id=row[1], creditor=row[2],
                balance=row[3], original_balance=row[4],
                monthly_payment=row[5], payment_date=row[6],
                status=row[7], priority=row[8], priority_label=row[9],
                category=row[10], interest_rate=row[11]
            )
        return None
    
    @staticmethod
    def create_debt(user_id: int, creditor: str, balance: float,
                   monthly_payment: float = 0, payment_date: str = "",
                   priority: int = 5, priority_label: str = "Media",
                   category: str = "personal") -> Optional[int]:
        """Crea una nueva deuda"""
        try:
            query = """
                INSERT INTO debts 
                (user_id, creditor, balance, original_balance, monthly_payment,
                 payment_date, priority, priority_label, category, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')
            """
            debt_id = db.execute_insert(query, (
                user_id, creditor, balance, balance, monthly_payment,
                payment_date, priority, priority_label, category
            ))
            logger.info(f"Deuda creada: {creditor} por ${balance}")
            return debt_id
        except Exception as e:
            logger.error(f"Error creando deuda: {e}")
            return None
    
    @staticmethod
    def update_debt_balance(debt_id: int, new_balance: float) -> bool:
        """Actualiza el saldo de una deuda"""
        query = "UPDATE debts SET balance = ? WHERE id = ?"
        return db.execute_update(query, (new_balance, debt_id))
    
    @staticmethod
    def mark_debt_paid(debt_id: int) -> bool:
        """Marca una deuda como pagada"""
        query = "UPDATE debts SET status = 'paid', balance = 0 WHERE id = ?"
        return db.execute_update(query, (debt_id,))
    
    @staticmethod
    def delete_debt(debt_id: int) -> bool:
        """Elimina una deuda"""
        query = "DELETE FROM debts WHERE id = ?"
        return db.execute_delete(query, (debt_id,))
    
    @staticmethod
    def get_total_debt(user_id: int) -> float:
        """Obtiene deuda total de un usuario"""
        query = "SELECT SUM(balance) FROM debts WHERE user_id = ? AND status = 'active'"
        results = db.execute_query(query, (user_id,))
        return results[0][0] or 0.0 if results else 0.0
    
    @staticmethod
    def get_total_monthly_payments(user_id: int) -> float:
        """Obtiene total de pagos mensuales"""
        query = "SELECT SUM(monthly_payment) FROM debts WHERE user_id = ? AND status = 'active'"
        results = db.execute_query(query, (user_id,))
        return results[0][0] or 0.0 if results else 0.0
    
    @staticmethod
    def get_debts_by_category(user_id: int, category: str) -> List[Debt]:
        """Obtiene deudas por categoría"""
        query = """
            SELECT id, user_id, creditor, balance, original_balance,
                   monthly_payment, payment_date, status, priority,
                   priority_label, category, interest_rate
            FROM debts WHERE user_id = ? AND category = ? AND status = 'active'
        """
        results = db.execute_query(query, (user_id, category))
        debts = []
        for row in results:
            debt = Debt(
                id=row[0], user_id=row[1], creditor=row[2],
                balance=row[3], original_balance=row[4],
                monthly_payment=row[5], payment_date=row[6],
                status=row[7], priority=row[8], priority_label=row[9],
                category=row[10], interest_rate=row[11]
            )
            debts.append(debt)
        return debts
    
    @staticmethod
    def create_transaction(user_id: int, amount: float, trans_type: str,
                          category: str, description: str = "",
                          currency: str = "COP", transaction_date: str = None) -> Optional[int]:
        """Crea una transacción
        
        Args:
            user_id: ID del usuario
            amount: Monto de la transacción
            trans_type: Tipo ('income', 'expense', 'payment')
            category: Categoría de transacción
            description: Descripción optional
            currency: Moneda (default 'COP')
            transaction_date: Fecha ISO format (default: hoy)
        """
        try:
            if transaction_date is None:
                transaction_date = date.today().isoformat()
            
            query = """
                INSERT INTO transactions
                (user_id, amount, currency, type, category, description, date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            trans_id = db.execute_insert(query, (
                user_id, amount, currency, trans_type, category, description, transaction_date
            ))
            logger.info(f"Transacción creada: {trans_type} {amount} {currency}")
            return trans_id
        except Exception as e:
            logger.error(f"Error creando transacción: {e}")
            return None
    
    @staticmethod
    def get_transactions_by_date_range(user_id: int, start_date: str,
                                      end_date: str) -> List[Transaction]:
        """Obtiene transacciones en un rango de fechas"""
        start_date = FinanceService._normalize_date_string(start_date)
        end_date = FinanceService._normalize_date_string(end_date)

        query = """
            SELECT id, user_id, amount, currency, type, category,
                   description, date, week_id, goal_id, debt_id
            FROM transactions
            WHERE user_id = ? AND date BETWEEN ? AND ?
            ORDER BY date DESC
        """
        results = db.execute_query(query, (user_id, start_date, end_date))
        transactions = []
        for row in results:
            trans = Transaction(
                id=row[0], user_id=row[1], amount=row[2],
                currency=row[3], type=row[4], category=row[5],
                description=row[6], date=row[7],
                week_id=row[8], goal_id=row[9], debt_id=row[10]
            )
            transactions.append(trans)
        return transactions
