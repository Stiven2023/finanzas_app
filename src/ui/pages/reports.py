"""
Página de Reportes y Análisis Financiero
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
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
        self.range_options = {
            "Últimos 3 meses": 3,
            "Últimos 6 meses": 6,
            "Últimos 12 meses": 12,
            "Todo": None,
        }
        self.selected_range = tk.StringVar(value="Últimos 6 meses")
        self._build()
    
    def _build(self):
        """Construye la página"""
        page_header(self, "📊 Reportes & Análisis", "⬇ Exportar Excel", self._export_to_excel)
        
        # Resumen financiero
        self._build_summary()
        
        # Gráficos
        self._build_charts()

    def _create_chart_panel(self, parent, title, subtitle):
        """Crea contenedor visual estándar para cada reporte."""
        panel = card(parent)
        panel.pack(fill="both", expand=True, padx=10, pady=10)

        head = frame(panel, bg=C['card'])
        head.pack(fill="x", padx=16, pady=(14, 6))
        label(head, title, font=F['lg'], bg=C['card'], fg=C['text']).pack(anchor="w")
        label(head, subtitle, font=F['sm'], bg=C['card'], fg=C['text2']).pack(anchor="w", pady=(2, 0))
        separator(panel, C['border']).pack(fill="x", padx=16, pady=(0, 8))

        content = frame(panel, bg=C['card'])
        content.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        return content

    def _build_stat_strip(self, parent, stats):
        """Muestra mini métricas arriba del gráfico."""
        strip = frame(parent, bg=C['card'])
        strip.pack(fill="x", pady=(0, 8))

        columns = len(stats)
        for index in range(columns):
            strip.columnconfigure(index, weight=1, uniform="stats")

        for index, (title, value, color) in enumerate(stats):
            box = frame(strip, bg=C['card2'])
            box.grid(row=0, column=index, padx=4, sticky="ew")
            label(box, title, font=F['sm'], bg=C['card2'], fg=C['text2']).pack(anchor="w", padx=10, pady=(8, 0))
            label(box, value, font=F['sm_b'], bg=C['card2'], fg=color).pack(anchor="w", padx=10, pady=(0, 8))

    def _show_empty_state(self, parent, message):
        """Muestra estado vacío consistente."""
        empty = frame(parent, bg=C['card2'])
        empty.pack(fill="both", expand=True, pady=8)
        label(empty, "📭", font=F['xl'], bg=C['card2'], fg=C['text2']).pack(pady=(24, 6))
        label(empty, message, font=F['sm'], bg=C['card2'], fg=C['text2']).pack(pady=(0, 24))

    def _get_selected_month_limit(self):
        """Obtiene límite de meses según selector actual."""
        return self.range_options.get(self.selected_range.get(), 6)

    def _get_filtered_monthly_summary(self):
        """Devuelve resumen mensual filtrado según el rango seleccionado."""
        monthly = self.report_service.get_monthly_summary(self.user_id)
        month_limit = self._get_selected_month_limit()
        if month_limit is None:
            return monthly
        return monthly[-month_limit:]

    def _on_range_change(self, *_):
        """Refresca pestañas al cambiar rango de tiempo."""
        self._refresh_charts()

    def _refresh_charts(self):
        """Reconstruye contenido de las pestañas de reportes."""
        for tab in (self.tab_income_expense, self.tab_debt_projection, self.tab_expense_breakdown, self.tab_monthly_summary):
            for widget in tab.winfo_children():
                widget.destroy()

        self._build_income_expense_chart(self.tab_income_expense)
        self._build_debt_projection_chart(self.tab_debt_projection)
        self._build_expense_breakdown_chart(self.tab_expense_breakdown)
        self._build_monthly_summary(self.tab_monthly_summary)

    def _export_to_excel(self):
        """Exporta reportes a archivo Excel."""
        default_name = f"reporte_flujo_user_{self.user_id}.xlsx"
        file_path = filedialog.asksaveasfilename(
            title="Guardar reporte en Excel",
            defaultextension=".xlsx",
            initialfile=default_name,
            filetypes=[("Excel", "*.xlsx")],
        )

        if not file_path:
            return

        try:
            saved = self.report_service.export_reports_to_excel(self.user_id, file_path)
            messagebox.showinfo("Exportación completada", f"Reporte guardado en:\n{saved}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar el reporte:\n{e}")
    
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

        range_bar = frame(container, bg=C['bg'])
        range_bar.pack(fill="x", pady=(0, 8))
        label(range_bar, "Periodo:", font=F['sm_b'], bg=C['bg'], fg=C['text2']).pack(side="left", padx=(0, 8))

        range_combo = ttk.Combobox(
            range_bar,
            values=list(self.range_options.keys()),
            state="readonly",
            width=18,
            textvariable=self.selected_range,
        )
        range_combo.pack(side="left")
        range_combo.bind("<<ComboboxSelected>>", self._on_range_change)
        
        # Crear notebook para tabs
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background=C['bg'], borderwidth=0)
        style.configure('TNotebook.Tab', background=C['card2'], foreground=C['text2'], padding=(12, 8), borderwidth=0)
        style.map('TNotebook.Tab',
              background=[('selected', C['card'])],
              foreground=[('selected', C['text'])])
        
        self.notebook = ttk.Notebook(container)
        self.notebook.pack(fill="both", expand=True)
        
        # Tab 1: Ingresos vs Gastos
        self.tab_income_expense = frame(self.notebook, bg=C['bg'])
        self.notebook.add(self.tab_income_expense, text="📊 Ingresos vs Gastos")
        
        # Tab 2: Proyección de Deuda
        self.tab_debt_projection = frame(self.notebook, bg=C['bg'])
        self.notebook.add(self.tab_debt_projection, text="📉 Proyección de Deuda")
        
        # Tab 3: Gastos por Categoría
        self.tab_expense_breakdown = frame(self.notebook, bg=C['bg'])
        self.notebook.add(self.tab_expense_breakdown, text="🥧 Gastos por Categoría")
        
        # Tab 4: Resumen Mensual
        self.tab_monthly_summary = frame(self.notebook, bg=C['bg'])
        self.notebook.add(self.tab_monthly_summary, text="📅 Resumen Mensual")

        self._refresh_charts()
    
    def _build_income_expense_chart(self, parent):
        """Gráfico de ingresos vs gastos"""
        try:
            monthly = self._get_filtered_monthly_summary()

            panel = self._create_chart_panel(
                parent,
                "📊 Ingresos vs Gastos",
                "Compara el flujo mensual de entradas y salidas"
            )

            if not monthly:
                self._show_empty_state(panel, "Aún no hay movimientos para mostrar en este gráfico")
                return
            
            months = [m.get('month', f'Mes {idx+1}') for idx, m in enumerate(monthly)]
            income = [m.get('income', 0) for m in monthly]
            expenses = [m.get('expenses', 0) for m in monthly]

            self._build_stat_strip(panel, [
                ("Total ingresos", format_money(sum(income)), C['green']),
                ("Total gastos", format_money(sum(expenses)), C['red']),
                ("Balance", format_money(sum(income) - sum(expenses)), C['teal'] if sum(income) >= sum(expenses) else C['orange']),
            ])
            
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
            ax.set_title('Comparativo mensual', color=C['text'], fontsize=11, pad=10)
            ax.legend(loc='upper left', facecolor=C['card'], edgecolor=C['border'],
                     labelcolor=C['text'])
            ax.grid(axis='y', alpha=0.3, color=C['border'])
            
            for spine in ax.spines.values():
                spine.set_color(C['border'])
            
            canvas = FigureCanvasTkAgg(fig, master=panel)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=(0, 4))
        except Exception as e:
            label(parent, f"Error al cargar gráfico: {e}", bg=C['bg'], fg=C['red']).pack(pady=20)
    
    def _build_debt_projection_chart(self, parent):
        """Gráfico de proyección de deuda"""
        try:
            projection = self.report_service.get_debt_projection(self.user_id)
            month_limit = self._get_selected_month_limit()
            if month_limit is not None:
                projection = projection[:month_limit]

            panel = self._create_chart_panel(
                parent,
                "📉 Proyección de Deuda",
                "Estimación de deuda futura según tus pagos mensuales"
            )

            if not projection:
                self._show_empty_state(panel, "No hay datos suficientes para proyectar deuda")
                return
            
            months = list(range(0, len(projection)))
            amounts = [p.get('projected_debt', 0) for p in projection]

            current_amount = amounts[0] if amounts else 0
            final_amount = amounts[-1] if amounts else 0
            trend_color = C['green'] if final_amount <= current_amount else C['red']
            self._build_stat_strip(panel, [
                ("Deuda actual", format_money(current_amount), C['orange']),
                ("Deuda proyectada", format_money(final_amount), trend_color),
                ("Meses", str(len(months)), C['text']),
            ])
            
            fig = Figure(figsize=(10, 5), dpi=80, facecolor=C['bg'], edgecolor='none')
            ax = fig.add_subplot(111, facecolor=C['card'])
            ax.tick_params(colors=C['text2'], labelsize=9)
            
            ax.plot(months, amounts, color=C['orange'], linewidth=2.5, marker='o', markersize=6)
            ax.fill_between(months, amounts, alpha=0.3, color=C['orange'])
            
            ax.set_xlabel('Meses', color=C['text2'], fontsize=10)
            ax.set_ylabel('Deuda Proyectada ($)', color=C['text2'], fontsize=10)
            ax.set_title('Evolución estimada', color=C['text'], fontsize=11, pad=10)
            ax.grid(True, alpha=0.3, color=C['border'])
            
            for spine in ax.spines.values():
                spine.set_color(C['border'])
            
            canvas = FigureCanvasTkAgg(fig, master=panel)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=(0, 4))
        except Exception as e:
            label(parent, f"Error al cargar gráfico: {e}", bg=C['bg'], fg=C['red']).pack(pady=20)
    
    def _build_expense_breakdown_chart(self, parent):
        """Gráfico de gastos por categoría"""
        try:
            breakdown = self.report_service.get_expense_breakdown(self.user_id)

            panel = self._create_chart_panel(
                parent,
                "🥧 Gastos por Categoría",
                "Distribución de tus gastos por tipo"
            )

            if not breakdown:
                self._show_empty_state(panel, "No hay gastos registrados para distribuir por categoría")
                return
            
            categories = list(breakdown.keys())
            amounts = list(breakdown.values())

            if sum(amounts) <= 0:
                self._show_empty_state(panel, "Los gastos del periodo son 0; no se puede graficar pastel")
                return

            top_category = categories[amounts.index(max(amounts))] if categories else "-"
            self._build_stat_strip(panel, [
                ("Total gastos", format_money(sum(amounts)), C['red']),
                ("Categorías", str(len(categories)), C['text']),
                ("Mayor peso", top_category, C['orange']),
            ])
            
            fig = Figure(figsize=(10, 6), dpi=80, facecolor=C['bg'], edgecolor='none')
            ax = fig.add_subplot(111, facecolor=C['card'])
            
            colors = [C['red'], C['orange'], C['yellow'], C['green'], C['teal'], C['purple']]
            colors = (colors * ((len(categories) // len(colors)) + 1))[:len(categories)]
            
            wedges, texts, autotexts = ax.pie(amounts, labels=categories, autopct='%1.1f%%',
                                              colors=colors, startangle=90, textprops={'color': C['text']})
            ax.set_title('Participación por categoría', color=C['text'], fontsize=11, pad=10)
            
            for autotext in autotexts:
                autotext.set_color(C['bg'])
                autotext.set_fontsize(9)
                autotext.set_weight('bold')
            
            canvas = FigureCanvasTkAgg(fig, master=panel)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=(0, 4))
        except Exception as e:
            label(parent, f"Error al cargar gráfico: {e}", bg=C['bg'], fg=C['red']).pack(pady=20)
    
    def _build_monthly_summary(self, parent):
        """Resumen mensual detallado"""
        try:
            monthly = self._get_filtered_monthly_summary()

            panel = self._create_chart_panel(
                parent,
                "📅 Resumen Mensual",
                "Vista tabular según el periodo seleccionado"
            )

            if not monthly:
                self._show_empty_state(panel, "No hay información mensual disponible aún")
                return

            recent = monthly
            total_income = sum(m.get('income', 0) for m in recent)
            total_expenses = sum(m.get('expenses', 0) for m in recent)
            total_balance = total_income - total_expenses

            self._build_stat_strip(panel, [
                ("Ingresos 6M", format_money(total_income), C['green']),
                ("Gastos 6M", format_money(total_expenses), C['red']),
                ("Balance 6M", format_money(total_balance), C['teal'] if total_balance >= 0 else C['orange']),
            ])
            
            summary_frame = frame(panel, bg=C['card'])
            summary_frame.pack(fill="both", expand=True)
            
            label(summary_frame, "Últimos 6 Meses", font=F['lg'], bg=C['card'],
                  fg=C['text']).pack(anchor="w", padx=10, pady=(4, 8))
            
            # Encabezados
            header = frame(summary_frame, bg=C['card2'])
            header.pack(fill="x", padx=10, pady=(0, 8))
            header.columnconfigure((0, 1, 2, 3, 4), weight=1)
            
            for col, text in enumerate(['Mes', 'Ingresos', 'Gastos', 'Balance', 'Pagos']):
                label(header, text, font=F['sm_b'], bg=C['card2'],
                      fg=C['text2']).grid(row=0, column=col, padx=4, pady=4, sticky="w")
            
            # Filas
            for i, m in enumerate(recent):
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
