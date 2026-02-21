"""
Página de Reportes y Análisis Financiero
"""
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from src.ui.components import frame, label, button, card, separator, KPICard, page_header
from src.ui.theme import DEFAULT_COLORS as C, DEFAULT_FONTS as F
from src.utils.formatters import format_money
from src.services.report_service import ReportService
from src.services.finance_service import FinanceService
from src.services.goal_service import GoalService

class ReportsPage(tk.Frame):
    """Página de reportes y análisis financiero"""
    
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg=C['bg'], **kwargs)
        self.app = app
        self.user_id = app.current_user.id
        self.report_service = ReportService
        self._build()
    
    def _build(self):
        """Construye la página"""
        page_header(self, "📊 Reportes & Análisis")
        
        # Resumen financiero
        self._build_summary()
        
        # Gráficos
        self._build_charts()
    
    def _build_summary(self):
        """Construye resumen financiero"""
        summary = self.report_service.get_financial_summary(self.user_id)
        
        kpi_frame = frame(self, bg=C['bg'])
        kpi_frame.pack(fill="x", padx=30, pady=(0, 16))
        kpi_frame.columnconfigure((0, 1, 2, 3), weight=1, uniform="k")
        
        kpis = [
            ("DEUDA TOTAL", format_money(summary['total_debt']), "Deudas activas", C['red'], "💳"),
            ("CUOTA MENSUAL", format_money(summary['total_monthly_payments']), "Mínimo a pagar", C['orange'], "📅"),
            ("DEUDAS ACTIVAS", str(summary['debt_count']), "Total acreedores", C['accent'], "⚠️"),
            ("METAS ACTIVAS", str(summary['goal_count']), f"En progreso", C['teal'], "🎯"),
        ]
        
        for i, (title, value, subtitle, color, icon) in enumerate(kpis):
            kc = KPICard(kpi_frame, title, value, subtitle, icon, color)
            kc.grid(row=0, column=i, padx=8, pady=4, sticky="ew")
    
    def _build_charts(self):
        """Construye gráficos"""
        container = frame(self, bg=C['bg'])
        container.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        
        # Crear notebook para tabs
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background=C['bg'], borderwidth=0)
        style.configure('TNotebook.Tab', background=C['card'], foreground=C['text'])
        
        notebook = ttk.Notebook(container)
        notebook.pack(fill="both", expand=True)
        
        # Tab 1: Ingresos vs Gastos
        tab1 = frame(notebook, bg=C['bg'])
        notebook.add(tab1, text="📊 Ingresos vs Gastos")
        self._build_income_expense_chart(tab1)
        
        # Tab 2: Proyección de Deuda
        tab2 = frame(notebook, bg=C['bg'])
        notebook.add(tab2, text="📉 Proyección de Deuda")
        self._build_debt_projection_chart(tab2)
        
        # Tab 3: Gastos por Categoría
        tab3 = frame(notebook, bg=C['bg'])
        notebook.add(tab3, text="🥧 Gastos por Categoría")
        self._build_expense_breakdown_chart(tab3)
        
        # Tab 4: Resumen Mensual
        tab4 = frame(notebook, bg=C['bg'])
        notebook.add(tab4, text="📅 Resumen Mensual")
        self._build_monthly_summary(tab4)
    
    def _build_income_expense_chart(self, parent):
        """Gráfico de ingresos vs gastos"""
        try:
            monthly = self.report_service.get_monthly_summary(self.user_id)
            
            months = [m.get('month', f'Mes {idx+1}') for idx, m in enumerate(monthly)]
            income = [m.get('income', 0) for m in monthly]
            expenses = [m.get('expenses', 0) for m in monthly]
            
            fig = Figure(figsize=(10, 5), dpi=80, facecolor=C['bg'], edgecolor='none')
            ax = fig.add_subplot(111, facecolor=C['card'])
            ax.tick_params(colors=C['text2'], labelsize=9)
            
            x = list(range(len(months)))
            width = 0.35
            
            ax.bar([i - width/2 for i in x], income, width, label='Ingresos', color=C['green'], alpha=0.8)
            ax.bar([i + width/2 for i in x], expenses, width, label='Gastos', color=C['red'], alpha=0.8)
            
            ax.set_xticks(x)
            ax.set_xticklabels(months, rotation=20)
            ax.set_ylabel('Monto ($)', color=C['text2'], fontsize=10)
            ax.legend(loc='upper left', facecolor=C['card'], edgecolor=C['border'],
                     labelcolor=C['text'])
            ax.grid(axis='y', alpha=0.3, color=C['border'])
            
            for spine in ax.spines.values():
                spine.set_color(C['border'])
            
            canvas = FigureCanvasTkAgg(fig, master=parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        except Exception as e:
            label(parent, f"Error al cargar gráfico: {e}", bg=C['bg'], fg=C['red']).pack(pady=20)
    
    def _build_debt_projection_chart(self, parent):
        """Gráfico de proyección de deuda"""
        try:
            projection = self.report_service.get_debt_projection(self.user_id)
            
            months = list(range(0, len(projection)))
            amounts = [p.get('projected_debt', 0) for p in projection]
            
            fig = Figure(figsize=(10, 5), dpi=80, facecolor=C['bg'], edgecolor='none')
            ax = fig.add_subplot(111, facecolor=C['card'])
            ax.tick_params(colors=C['text2'], labelsize=9)
            
            ax.plot(months, amounts, color=C['orange'], linewidth=2.5, marker='o', markersize=6)
            ax.fill_between(months, amounts, alpha=0.3, color=C['orange'])
            
            ax.set_xlabel('Meses', color=C['text2'], fontsize=10)
            ax.set_ylabel('Deuda Proyectada ($)', color=C['text2'], fontsize=10)
            ax.grid(True, alpha=0.3, color=C['border'])
            
            for spine in ax.spines.values():
                spine.set_color(C['border'])
            
            canvas = FigureCanvasTkAgg(fig, master=parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        except Exception as e:
            label(parent, f"Error al cargar gráfico: {e}", bg=C['bg'], fg=C['red']).pack(pady=20)
    
    def _build_expense_breakdown_chart(self, parent):
        """Gráfico de gastos por categoría"""
        try:
            breakdown = self.report_service.get_expense_breakdown(self.user_id)
            
            categories = list(breakdown.keys())
            amounts = list(breakdown.values())
            
            fig = Figure(figsize=(10, 6), dpi=80, facecolor=C['bg'], edgecolor='none')
            ax = fig.add_subplot(111, facecolor=C['card'])
            
            colors = [C['red'], C['orange'], C['yellow'], C['green'], C['teal'], C['purple']]
            colors = (colors * ((len(categories) // len(colors)) + 1))[:len(categories)]
            
            wedges, texts, autotexts = ax.pie(amounts, labels=categories, autopct='%1.1f%%',
                                              colors=colors, startangle=90, textprops={'color': C['text']})
            
            for autotext in autotexts:
                autotext.set_color(C['bg'])
                autotext.set_fontsize(9)
                autotext.set_weight('bold')
            
            canvas = FigureCanvasTkAgg(fig, master=parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        except Exception as e:
            label(parent, f"Error al cargar gráfico: {e}", bg=C['bg'], fg=C['red']).pack(pady=20)
    
    def _build_monthly_summary(self, parent):
        """Resumen mensual detallado"""
        try:
            monthly = self.report_service.get_monthly_summary(self.user_id)
            
            summary_frame = card(parent)
            summary_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            label(summary_frame, "Últimos 6 Meses", font=F['lg'], bg=C['card'],
                  fg=C['text']).pack(anchor="w", padx=16, pady=(14, 8))
            
            # Encabezados
            header = frame(summary_frame, bg=C['card2'])
            header.pack(fill="x", padx=10, pady=(0, 6))
            header.columnconfigure((0, 1, 2, 3, 4), weight=1)
            
            for col, text in enumerate(['Mes', 'Ingresos', 'Gastos', 'Balance', 'Pagos']):
                label(header, text, font=F['sm_b'], bg=C['card2'],
                      fg=C['text2']).grid(row=0, column=col, padx=4, pady=4, sticky="w")
            
            # Filas
            for i, m in enumerate(monthly[-6:]):
                row_frame = frame(summary_frame, bg=C['card'] if i % 2 == 0 else C['card2'])
                row_frame.pack(fill="x", padx=10, pady=2)
                row_frame.columnconfigure((0, 1, 2, 3, 4), weight=1)
                
                income = m.get('income', 0)
                expenses = m.get('expenses', 0)
                balance = m.get('balance', income - expenses)
                payments = m.get('payments', m.get('debt_payments', 0))
                month_label = m.get('month', f"Mes {i+1}")
                
                label(row_frame, month_label, font=F['sm'], bg=row_frame['bg'],
                      fg=C['text']).grid(row=0, column=0, padx=4, pady=4, sticky="w")
                label(row_frame, format_money(income), font=F['sm'], bg=row_frame['bg'],
                      fg=C['green']).grid(row=0, column=1, padx=4, pady=4, sticky="w")
                label(row_frame, format_money(expenses), font=F['sm'], bg=row_frame['bg'],
                      fg=C['red']).grid(row=0, column=2, padx=4, pady=4, sticky="w")
                
                color = C['green'] if balance > 0 else C['red']
                label(row_frame, format_money(balance), font=F['sm_b'], bg=row_frame['bg'],
                      fg=color).grid(row=0, column=3, padx=4, pady=4, sticky="w")
                label(row_frame, format_money(payments), font=F['sm'], bg=row_frame['bg'],
                      fg=C['orange']).grid(row=0, column=4, padx=4, pady=4, sticky="w")
        except Exception as e:
            label(parent, f"Error al cargar resumen: {e}", bg=C['bg'], fg=C['red']).pack(pady=20)
