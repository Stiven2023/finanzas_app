"""
Servicio de Reportes y Análisis
"""
import logging
from typing import Dict, List
from datetime import datetime, timedelta
from pathlib import Path
from tempfile import NamedTemporaryFile
import os

from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import matplotlib.pyplot as plt
from src.database.db import db
from src.services.finance_service import FinanceService
from src.services.goal_service import GoalService

logger = logging.getLogger(__name__)

class ReportService:
    """Servicio para generar reportes y análisis"""

    INCOME_TYPES = ("income", "entrada", "ingreso")
    EXPENSE_TYPES = ("expense", "gasto")
    PAYMENT_TYPES = ("payment", "pago")
    HEADER_FILL = PatternFill(fill_type="solid", fgColor="1F2937")
    HEADER_FONT = Font(color="FFFFFF", bold=True)
    TITLE_FILL = PatternFill(fill_type="solid", fgColor="0B1220")
    TITLE_FONT = Font(color="E5E7EB", bold=True, size=13)
    BODY_BORDER = Border(
        left=Side(style="thin", color="CBD5E1"),
        right=Side(style="thin", color="CBD5E1"),
        top=Side(style="thin", color="CBD5E1"),
        bottom=Side(style="thin", color="CBD5E1"),
    )

    @staticmethod
    def _style_title(ws, text: str, cell: str = "A1"):
        ws[cell] = text
        ws[cell].fill = ReportService.TITLE_FILL
        ws[cell].font = ReportService.TITLE_FONT
        ws[cell].alignment = Alignment(horizontal="left", vertical="center")

    @staticmethod
    def _style_header_row(ws, header_row: int = 2):
        for col in range(1, ws.max_column + 1):
            c = ws.cell(row=header_row, column=col)
            c.fill = ReportService.HEADER_FILL
            c.font = ReportService.HEADER_FONT
            c.alignment = Alignment(horizontal="center", vertical="center")
            c.border = ReportService.BODY_BORDER

    @staticmethod
    def _style_body(ws, start_row: int = 3, currency_cols: list[int] | None = None):
        currency_cols = currency_cols or []
        for row in range(start_row, ws.max_row + 1):
            for col in range(1, ws.max_column + 1):
                cell = ws.cell(row=row, column=col)
                cell.border = ReportService.BODY_BORDER
                if col in currency_cols and isinstance(cell.value, (int, float)):
                    cell.number_format = '#,##0.00'
                if isinstance(cell.value, (int, float)):
                    cell.alignment = Alignment(horizontal="right", vertical="center")
                else:
                    cell.alignment = Alignment(horizontal="left", vertical="center")

    @staticmethod
    def _autosize_columns(ws, min_width: int = 12, max_width: int = 40):
        for col in range(1, ws.max_column + 1):
            letter = get_column_letter(col)
            max_len = 0
            for row in range(1, ws.max_row + 1):
                value = ws.cell(row=row, column=col).value
                if value is None:
                    continue
                max_len = max(max_len, len(str(value)))
            ws.column_dimensions[letter].width = max(min_width, min(max_width, max_len + 2))

    @staticmethod
    def _apply_table_features(ws, header_row: int = 2):
        ws.freeze_panes = f"A{header_row + 1}"
        ws.auto_filter.ref = f"A{header_row}:{get_column_letter(ws.max_column)}{ws.max_row}"

    @staticmethod
    def _create_chart_image(monthly: List[Dict], breakdown: Dict, projection: List[Dict], chart_type: str) -> str | None:
        """Genera imagen temporal de gráfico para incrustar en Excel."""
        try:
            fig, ax = plt.subplots(figsize=(8, 4.5), dpi=120)

            if chart_type == "income_expense":
                labels = [row.get('month', '') for row in monthly]
                income = [row.get('income', 0.0) for row in monthly]
                expenses = [row.get('expenses', 0.0) for row in monthly]
                x = list(range(len(labels)))
                width = 0.38
                ax.bar([i - width / 2 for i in x], income, width, label='Ingresos', color="#00C896")
                ax.bar([i + width / 2 for i in x], expenses, width, label='Gastos', color="#FF5E57")
                ax.set_xticks(x)
                ax.set_xticklabels(labels, rotation=20)
                ax.set_title("Ingresos vs Gastos")
                ax.legend()
                ax.grid(axis='y', alpha=0.25)

            elif chart_type == "expense_breakdown":
                categories = list(breakdown.keys())
                totals = list(breakdown.values())
                total_sum = sum(totals) if totals else 0
                if not categories or total_sum <= 0:
                    ax.bar(["Sin datos"], [1], color="#64748b")
                    ax.set_ylim(0, 1.5)
                else:
                    ax.pie(totals, labels=categories, autopct='%1.1f%%', startangle=90)
                ax.set_title("Gastos por categoría")

            elif chart_type == "debt_projection":
                labels = [row.get('month', '') for row in projection]
                values = [row.get('projected_debt', 0.0) for row in projection]
                x = list(range(len(labels)))
                ax.plot(x, values, marker='o', color="#FFAA33", linewidth=2)
                ax.fill_between(x, values, color="#FFAA33", alpha=0.25)
                ax.set_xticks(x)
                ax.set_xticklabels(labels, rotation=25)
                ax.set_title("Proyección de deuda")
                ax.grid(alpha=0.25)

            fig.tight_layout()

            temp = NamedTemporaryFile(delete=False, suffix=".png")
            temp_path = temp.name
            temp.close()
            fig.savefig(temp_path)
            plt.close(fig)
            return temp_path
        except Exception as e:
            logger.warning("No se pudo generar gráfico %s: %s", chart_type, e)
            try:
                plt.close('all')
            except Exception:
                pass
            return None
    
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
        results = db.execute_query(query, (user_id, user_id, user_id, user_id))
        
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
                SUM(CASE WHEN type IN ('income','entrada','ingreso') THEN amount ELSE 0 END) as total_income,
                SUM(CASE WHEN type IN ('expense','gasto') THEN amount ELSE 0 END) as total_expenses,
                SUM(CASE WHEN type IN ('payment','pago') THEN amount ELSE 0 END) as total_debt_paid
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
                substr(date, 1, 7) as month,
                SUM(CASE WHEN type IN ('income','entrada','ingreso') THEN amount ELSE 0 END) as total_income,
                SUM(CASE WHEN type IN ('expense','gasto') THEN amount ELSE 0 END) as total_expenses,
                SUM(CASE WHEN type IN ('payment','pago') THEN amount ELSE 0 END) as total_payments
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
            WHERE user_id = ? AND type IN ('expense','gasto')
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
                substr(date, 1, 7) as month,
                SUM(CASE WHEN type IN ('income','entrada','ingreso') THEN amount ELSE 0 END) as income,
                SUM(CASE WHEN type IN ('expense','gasto') THEN amount ELSE 0 END) as expenses
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

    @staticmethod
    def export_reports_to_excel(user_id: int, output_path: str) -> str:
        """Exporta reportes a un archivo Excel (.xlsx)."""
        wb = Workbook()
        generated_chart_paths = []

        summary = ReportService.get_financial_summary(user_id)
        goals = GoalService.get_total_goals_progress(user_id)
        monthly = ReportService.get_last_months_summary(user_id, 6)
        breakdown = ReportService.get_expense_breakdown(user_id)
        projection = ReportService.get_debt_projection(user_id, 12)

        ws_summary = wb.active
        ws_summary.title = "Resumen"
        ReportService._style_title(ws_summary, f"Flujo · Reporte financiero (Usuario {user_id})")
        ws_summary.append(["Métrica", "Valor"])
        ws_summary.append(["Generado", datetime.now().strftime("%Y-%m-%d %H:%M")])
        ws_summary.append(["Deuda total", summary.get('total_debt', 0.0)])
        ws_summary.append(["Pagos mensuales", summary.get('total_monthly_payments', 0.0)])
        ws_summary.append(["Deudas activas", summary.get('debt_count', 0)])
        ws_summary.append(["Metas activas", summary.get('goal_count', 0)])
        ws_summary.append(["Total metas", goals.get('total_goals', 0)])
        ws_summary.append(["Metas completadas", goals.get('completed_goals', 0)])
        ws_summary.append(["Progreso metas (%)", goals.get('overall_progress', 0.0)])

        ws_monthly = wb.create_sheet("Mensual")
        ReportService._style_title(ws_monthly, "Flujo · Resumen mensual")
        ws_monthly.append(["Mes", "Ingresos", "Gastos", "Pagos", "Balance"])
        for row in monthly:
            ws_monthly.append([
                row.get('month', ''),
                row.get('income', 0.0),
                row.get('expenses', 0.0),
                row.get('payments', 0.0),
                row.get('balance', 0.0),
            ])

        ws_expenses = wb.create_sheet("Gastos por categoría")
        ReportService._style_title(ws_expenses, "Flujo · Gastos por categoría")
        ws_expenses.append(["Categoría", "Total"])
        for category, total in breakdown.items():
            ws_expenses.append([category, total])

        ws_projection = wb.create_sheet("Proyección deuda")
        ReportService._style_title(ws_projection, "Flujo · Proyección de deuda")
        ws_projection.append(["Mes", "Deuda proyectada", "Pagos estimados"])
        for row in projection:
            ws_projection.append([
                row.get('month', ''),
                row.get('projected_debt', 0.0),
                row.get('total_payments', 0.0),
            ])

        ws_charts = wb.create_sheet("Gráficos")
        ReportService._style_title(ws_charts, "Flujo · Reportes visuales")

        income_expense_img = ReportService._create_chart_image(monthly, breakdown, projection, "income_expense")
        expense_breakdown_img = ReportService._create_chart_image(monthly, breakdown, projection, "expense_breakdown")
        debt_projection_img = ReportService._create_chart_image(monthly, breakdown, projection, "debt_projection")

        if income_expense_img:
            generated_chart_paths.append(income_expense_img)
            ws_charts.add_image(XLImage(income_expense_img), "A3")
        if expense_breakdown_img:
            generated_chart_paths.append(expense_breakdown_img)
            ws_charts.add_image(XLImage(expense_breakdown_img), "A26")
        if debt_projection_img:
            generated_chart_paths.append(debt_projection_img)
            ws_charts.add_image(XLImage(debt_projection_img), "A49")

        ReportService._style_header_row(ws_summary, header_row=2)
        ReportService._style_body(ws_summary, start_row=3, currency_cols=[2])
        ReportService._apply_table_features(ws_summary, header_row=2)
        ReportService._autosize_columns(ws_summary)

        ReportService._style_header_row(ws_monthly, header_row=2)
        ReportService._style_body(ws_monthly, start_row=3, currency_cols=[2, 3, 4, 5])
        ReportService._apply_table_features(ws_monthly, header_row=2)
        ReportService._autosize_columns(ws_monthly)

        ReportService._style_header_row(ws_expenses, header_row=2)
        ReportService._style_body(ws_expenses, start_row=3, currency_cols=[2])
        ReportService._apply_table_features(ws_expenses, header_row=2)
        ReportService._autosize_columns(ws_expenses)

        ReportService._style_header_row(ws_projection, header_row=2)
        ReportService._style_body(ws_projection, start_row=3, currency_cols=[2, 3])
        ReportService._apply_table_features(ws_projection, header_row=2)
        ReportService._autosize_columns(ws_projection)

        ws_charts.column_dimensions['A'].width = 80

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        wb.save(output)

        for chart_path in generated_chart_paths:
            try:
                if os.path.exists(chart_path):
                    os.remove(chart_path)
            except Exception:
                pass

        return str(output)
