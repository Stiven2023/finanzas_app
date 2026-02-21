"""
Servicio de Reportes y Análisis
"""
import logging
from typing import Dict, List
from datetime import datetime, timedelta
from src.database.db import db
from src.services.finance_service import FinanceService
from src.services.goal_service import GoalService

logger = logging.getLogger(__name__)

class ReportService:
    """Servicio para generar reportes y análisis"""
    
    @staticmethod
    def get_financial_summary(user_id: int) -> Dict:
        """Obtiene resumen financiero general"""
        query = """
            SELECT
                (SELECT SUM(balance) FROM debts WHERE user_id = ? AND status = 'active') as total_debt,
                (SELECT SUM(monthly_payment) FROM debts WHERE user_id = ? AND status = 'active') as total_payments,
                (SELECT COUNT(*) FROM debts WHERE user_id = ? AND status = 'active') as debt_count,
                (SELECT COUNT(*) FROM goals WHERE user_id = ? AND status = 'active') as goal_count
        """
        results = db.execute_query(query.replace("(SELECT", f"(SELECT"), (user_id, user_id, user_id, user_id))
        
        if results:
            row = results[0]
            return {
                'total_debt': row[0] or 0.0,
                'total_monthly_payments': row[1] or 0.0,
                'debt_count': row[2] or 0,
                'goal_count': row[3] or 0,
            }
        
        return {
            'total_debt': 0.0,
            'total_monthly_payments': 0.0,
            'debt_count': 0,
            'goal_count': 0,
        }
    
    @staticmethod
    def get_monthly_summary(user_id: int, year: int = None, month: int = None) -> Dict:
        """Obtiene resumen - si no se especifica año/mes, retorna últimos 6 meses"""
        if year is None or month is None:
            # Retornar últimos 6 meses como lista
            return ReportService.get_last_months_summary(user_id, 6)
        
        # Si se especifica, retornar mes específico
        start_date = f"{year:04d}-{month:02d}-01"
        
        # Calcular último día del mes
        if month == 12:
            end_date = f"{year+1:04d}-01-01"
        else:
            end_date = f"{year:04d}-{month+1:02d}-01"
        
        # Usar datos de transacciones
        query = """
            SELECT
                SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as total_income,
                SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as total_expenses,
                SUM(CASE WHEN type = 'payment' THEN amount ELSE 0 END) as total_debt_paid
            FROM transactions
            WHERE user_id = ? AND date >= ? AND date < ?
        """
        
        results = db.execute_query(query, (user_id, start_date, end_date))
        
        if results:
            row = results[0]
            income = row[0] or 0.0
            expenses = row[1] or 0.0
            debt_paid = row[2] or 0.0
            
            return {
                'income': income,
                'expenses': expenses,
                'debt_payments': debt_paid,
                'balance': income - expenses - debt_paid,
            }
        
        return {
            'income': 0.0,
            'expenses': 0.0,
            'debt_payments': 0.0,
            'balance': 0.0,
        }
    
    @staticmethod
    def get_last_months_summary(user_id: int, num_months: int = 6) -> List[Dict]:
        """Obtiene resumen de últimos N meses usando transacciones"""
        query = """
            SELECT
                strftime('%Y-%m', date) as month,
                SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as total_income,
                SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as total_expenses,
                SUM(CASE WHEN type = 'payment' THEN amount ELSE 0 END) as total_payments
            FROM transactions
            WHERE user_id = ?
            GROUP BY month
            ORDER BY month DESC
            LIMIT ?
        """
        
        results = db.execute_query(query, (user_id, num_months))
        
        monthly_data = []
        for row in results:
            income = row[1] or 0.0
            expenses = row[2] or 0.0
            payments = row[3] or 0.0
            
            monthly_data.append({
                'month': row[0],
                'income': income,
                'expenses': expenses,
                'payments': payments,
                'balance': income - expenses - payments,
            })
        
        return list(reversed(monthly_data))
    
    @staticmethod
    def get_debt_projection(user_id: int, months: int = 12) -> List[Dict]:
        """Calcula proyección de deudas para N meses"""
        debts = FinanceService.get_all_debts(user_id)
        
        projection = []
        current_date = datetime.now().replace(day=1)
        
        for i in range(months):
            month_debts = []
            total_pending = 0.0
            total_payments = 0.0
            
            for debt in debts:
                if debt.status != 'paid' and debt.balance > 0:
                    # Simular pago mensual
                    new_balance = max(0, debt.balance - debt.monthly_payment)
                    month_debts.append({
                        'creditor': debt.creditor,
                        'balance': new_balance,
                        'payment': debt.monthly_payment,
                    })
                    total_pending += new_balance
                    total_payments += debt.monthly_payment
            
            projection.append({
                'month': current_date.strftime("%Y-%m"),
                'month_name': current_date.strftime("%B"),
                'projected_debt': total_pending,
                'total_payments': total_payments,
                'debts': month_debts,
            })
            
            # Avanzar al siguiente mes
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        return projection
    
    @staticmethod
    def get_expense_breakdown(user_id: int, start_date: str = None, end_date: str = None) -> Dict:
        """Obtiene desglose de gastos por categoría - últimos 30 días por defecto"""
        if start_date is None or end_date is None:
            # Últimos 30 días
            end = datetime.now()
            start = end - timedelta(days=30)
            start_date = start.strftime("%Y-%m-%d")
            end_date = end.strftime("%Y-%m-%d")
        
        query = """
            SELECT category, SUM(amount) as total
            FROM transactions
            WHERE user_id = ? AND type = 'expense'
            AND date BETWEEN ? AND ?
            GROUP BY category
            ORDER BY total DESC
        """
        
        results = db.execute_query(query, (user_id, start_date, end_date))
        
        breakdown = {}
        total = 0.0
        
        for row in results:
            category = row[0] or "Sin categoría"
            amount = row[1] or 0.0
            breakdown[category] = amount
            total += amount
        
        # Si no hay datos, retornar estructura vacía
        if not breakdown:
            breakdown = {'Sin gastos': 0}
        
        return breakdown
    
    @staticmethod
    def get_income_vs_expenses(user_id: int, months: int = 6) -> Dict:
        """Compara ingresos vs gastos en últimos N meses"""
        query = """
            SELECT
                strftime('%Y-%m', date) as month,
                SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as income,
                SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as expenses
            FROM transactions
            WHERE user_id = ?
            GROUP BY month
            ORDER BY month DESC
            LIMIT ?
        """
        
        results = db.execute_query(query, (user_id, months))
        
        data = []
        for row in results:
            data.append({
                'month': row[0],
                'income': row[1] or 0.0,
                'expenses': row[2] or 0.0,
                'balance': (row[1] or 0.0) - (row[2] or 0.0),
            })
        
        return {'monthly_data': list(reversed(data))}
