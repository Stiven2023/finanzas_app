"""
Página Dashboard - Página principal con resumen financiero
"""
import tkinter as tk
from datetime import date

try:
    import matplotlib
    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

from src.ui.components import frame, label, card, separator, KPICard, button
from src.ui.theme import DEFAULT_COLORS as C, DEFAULT_FONTS as F
from src.utils.formatters import format_money
from src.services.finance_service import FinanceService
from src.services.goal_service import GoalService
from src.services.report_service import ReportService


class DashboardPage(tk.Frame):
    """Página principal con resumen financiero"""
    
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg=C['bg'], **kwargs)
        self.app = app
        self.user_id = app.current_user.id
        self._build()
    
    def _build(self):
        """Construye la página"""
        # Encabezado
        hdr = frame(self, bg=C['bg'])
        hdr.pack(fill="x", padx=30, pady=(24, 0))
        label(hdr, "📊 Dashboard", font=F['xl'], bg=C['bg'],
              fg=C['text']).pack(side="left")
        label(hdr, f"  Resumen al {date.today().strftime('%d de %B de %Y')}",
              font=F['base'], bg=C['bg'], fg=C['text2']).pack(side="left", pady=(10, 0))
        
        separator(self, C['border']).pack(fill="x", padx=30, pady=14)
        
        # KPIs
        self._build_kpis()
        
        # Contenido principal
        mid = frame(self, bg=C['bg'])
        mid.pack(fill="both", expand=True, padx=30, pady=16)
        mid.columnconfigure(0, weight=3)
        mid.columnconfigure(1, weight=2)
        
        # Deudas
        self._build_debts_section(mid)
        
        # Gráficas
        self._build_charts_section(mid)
        
        # Alerta
        self._build_alert_section()
    
    def _build_kpis(self):
        """Construye las tarjetas de KPI"""
        summary = ReportService.get_financial_summary(self.user_id)
        goals_summary = GoalService.get_total_goals_progress(self.user_id)
        
        kpi_frame = frame(self, bg=C['bg'])
        kpi_frame.pack(fill="x", padx=30)
        kpi_frame.columnconfigure((0, 1, 2, 3), weight=1, uniform="k")
        
        kpis = [
            ("DEUDA TOTAL", format_money(summary['total_debt']),
             "Todas las deudas", C['red'], "💳"),
            ("CUOTA MENSUAL", format_money(summary['total_monthly_payments']),
             "Pago mínimo total/mes", C['orange'], "📅"),
            ("METAS ACTIVAS", str(goals_summary['active_goals']),
             f"De {goals_summary['total_goals']} totales", C['purple'], "🎯"),
            ("PROGRESO METAS", f"{goals_summary['overall_progress']:.1f}%",
             f"${goals_summary['total_current']:.0f} de ${goals_summary['total_target']:.0f}",
             C['teal'], "📈"),
        ]
        
        for i, (title, value, subtitle, color, icon) in enumerate(kpis):
            kc = KPICard(kpi_frame, title, value, subtitle, icon, color)
            kc.grid(row=0, column=i, padx=8, pady=4, sticky="ew")
    
    def _build_debts_section(self, parent):
        """Construye sección de deudas"""
        left = card(parent)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        label(left, "💳  Deudas Activas", font=F['lg'], bg=C['card'],
              fg=C['text']).pack(anchor="w", padx=16, pady=(14, 4))
        separator(left, C['border']).pack(fill="x", padx=16, pady=(0, 8))
        
        debts = FinanceService.get_all_debts(self.user_id)
        
        if debts:
            # Encabezados
            cols_hdr = frame(left, bg=C['card2'])
            cols_hdr.pack(fill="x", padx=16, pady=(0, 4))
            for txt, w in [("Acreedor", 200), ("Saldo", 120),
                          ("Cuota", 120), ("Estado", 110)]:
                label(cols_hdr, txt, font=F['sm_b'], bg=C['card2'],
                      fg=C['text2'], width=w//8).pack(side="left", padx=4, pady=6)
            
            # Filas
            for i, debt in enumerate(debts[:10]):  # Mostrar máximo 10
                row_bg = C['card'] if i % 2 == 0 else C['card2']
                r = frame(left, bg=row_bg)
                r.pack(fill="x", padx=16, pady=1)
                
                label(r, debt.creditor[:28], font=F['sm_b'],
                      bg=row_bg, fg=C['text'], width=25,
                      anchor="w").pack(side="left", padx=4, pady=5)
                label(r, format_money(debt.balance), font=F['sm_b'],
                      bg=row_bg, fg=C['red'], width=13).pack(side="left", padx=4)
                label(r, format_money(debt.monthly_payment), font=F['sm'],
                      bg=row_bg, fg=C['text2'], width=13).pack(side="left", padx=4)
                label(r, debt.status[:14], font=F['sm'],
                      bg=row_bg, fg=C['text2'], width=13).pack(side="left", padx=4)
        else:
            label(left, "Sin deudas registradas", font=F['sm'],
                  bg=C['card'], fg=C['text2']).pack(expand=True)
    
    def _build_charts_section(self, parent):
        """Construye sección de gráficas"""
        right = card(parent)
        right.grid(row=0, column=1, sticky="nsew")
        
        label(right, "📊  Metas de Ahorro", font=F['lg'],
              bg=C['card'], fg=C['text']).pack(anchor="w", padx=16, pady=(14, 4))
        separator(right, C['border']).pack(fill="x", padx=16, pady=(0, 8))
        
        goals = GoalService.get_all_goals(self.user_id)
        
        # Filtrar solo metas con valores válidos (> 0)
        valid_goals = [g for g in goals if g.current_amount > 0]
        
        if HAS_MPL and valid_goals:
            try:
                fig, ax = plt.subplots(figsize=(4.2, 3.4), facecolor=C['card'])
                ax.set_facecolor(C['card'])
                
                labels = [g.name[:18] for g in valid_goals]
                sizes = [g.current_amount for g in valid_goals]
                colors = [g.color if g.color else C['accent'] for g in valid_goals]
                
                wedges, texts, autotexts = ax.pie(
                    sizes, labels=None, autopct=lambda p: f'{p:.0f}%' if p > 4 else '',
                    colors=colors, startangle=140,
                    wedgeprops=dict(edgecolor=C['card'], linewidth=2),
                    pctdistance=0.75
                )
                
                for at in autotexts:
                    at.set_color(C['white'])
                    at.set_fontsize(8)
                
                canvas = FigureCanvasTkAgg(fig, master=right)
                canvas.draw()
                canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=(0, 8))
                plt.close(fig)
            except Exception as e:
                # Si hay error en matplotlib, mostrar placeholder
                label(right, "Error mostrando gráfico\n📊", font=F['sm'],
                      bg=C['card'], fg=C['text2']).pack(expand=True)
        else:
            label(right, "Configura tus metas\npara ver el progreso\n📊",
                  font=F['sm'], bg=C['card'], fg=C['text2']).pack(expand=True)
    
    def _build_alert_section(self):
        """Construye sección de alertas"""
        debts = FinanceService.get_all_debts(self.user_id)
        urgent_debts = [d for d in debts if d.is_urgent and d.status == 'active']
        
        if urgent_debts:
            alert = tk.Frame(self, bg=C['danger_bg'], highlightthickness=1,
                           highlightbackground=C['red'])
            alert.pack(fill="x", padx=30, pady=(0, 16))
            
            alert_text = "⚠️  DEUDAS URGENTES: " + ", ".join(
                [f"{d.creditor} (${d.balance:,.0f})" for d in urgent_debts[:3]]
            )
            
            label(alert, alert_text, font=F['sm_b'], bg=C['danger_bg'],
                fg=C['red']).pack(padx=16, pady=10)
