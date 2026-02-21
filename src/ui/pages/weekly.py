"""
Página de Seguimiento Semanal
"""
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime, timedelta
from src.ui.components import frame, label, button, entry, card, separator, KPICard, DialogWindow, page_header
from src.ui.theme import DEFAULT_COLORS as C, DEFAULT_FONTS as F
from src.utils.formatters import format_money
from src.services.finance_service import FinanceService

class WeeklyPage(tk.Frame):
    """Página de seguimiento semanal"""
    
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg=C['bg'], **kwargs)
        self.app = app
        self.user_id = app.current_user.id
        self.current_date = datetime.now()
        self._build()
    
    def _build(self):
        """Construye la página"""
        for widget in self.winfo_children():
            widget.destroy()

        page_header(self, "📅 Seguimiento Semanal")

        nav_frame = frame(self, bg=C['bg'])
        nav_frame.pack(fill="x", padx=30, pady=(0, 10))

        button(
            nav_frame,
            "← Anterior",
            self._previous_week,
            bg=C['card2'],
            pad=(8, 4),
            font=F['sm'],
        ).pack(side="left", padx=2)
        button(
            nav_frame,
            "Hoy",
            self._go_to_today,
            bg=C['accent'],
            pad=(8, 4),
            font=F['sm'],
        ).pack(side="left", padx=2)
        button(
            nav_frame,
            "Siguiente →",
            self._next_week,
            bg=C['card2'],
            pad=(8, 4),
            font=F['sm'],
        ).pack(side="left", padx=2)
        button(
            nav_frame,
            "+ Registro Hoy",
            self._add_today_entry,
            bg=C['teal'],
            pad=(10, 4),
            font=F['sm_b'],
        ).pack(side="left", padx=(8, 2))
        
        # Información de semana
        self._build_week_info()
        
        # Vistas tipo tabla (excel)
        self._build_excel_views()

    def _add_today_entry(self):
        """Abre registro rápido para hoy."""
        self._show_day_entry(datetime.now())
    
    def _get_week_range(self):
        """Obtiene el rango de la semana actual"""
        start = self.current_date - timedelta(days=self.current_date.weekday())
        end = start + timedelta(days=6)
        return start, end
    
    def _previous_week(self):
        """Va a la semana anterior"""
        self.current_date -= timedelta(days=7)
        self._build()
    
    def _next_week(self):
        """Va a la siguiente semana"""
        self.current_date += timedelta(days=7)
        self._build()
    
    def _go_to_today(self):
        """Va a la semana actual"""
        self.current_date = datetime.now()
        self._build()
    
    def _build_week_info(self):
        """Construye información de la semana"""
        start, end = self._get_week_range()
        
        info_frame = frame(self, bg=C['bg'])
        info_frame.pack(fill="x", padx=30, pady=(0, 16))
        
        week_str = f"{start.strftime('%d %b %Y')} - {end.strftime('%d %b %Y')}"
        label(info_frame, f"📆 Semana: {week_str}", font=F['lg_b'],
              bg=C['bg'], fg=C['text']).pack(anchor="w")
        
        # KPIs semanales
        self._build_week_kpis()
    
    def _build_week_kpis(self):
        """Construye KPIs semanales"""
        start, end = self._get_week_range()
        
        # Calcular datos de la semana desde transacciones
        transactions = FinanceService.get_transactions_by_date_range(
            self.user_id, 
            start.strftime('%Y-%m-%d'), 
            end.strftime('%Y-%m-%d')
        )
        
        total_income = sum(t.amount for t in transactions if t.type == 'income')
        total_expenses = sum(t.amount for t in transactions if t.type == 'expense')
        total_paid = sum(t.amount for t in transactions if t.type == 'payment')
        
        kpi_frame = frame(self, bg=C['bg'])
        kpi_frame.pack(fill="x", padx=30, pady=(0, 16))
        kpi_frame.columnconfigure((0, 1, 2, 3), weight=1, uniform="k")
        
        kpis = [
            ("INGRESOS", format_money(total_income), "Esta semana", C['green'], "💵"),
            ("GASTOS", format_money(total_expenses), "Esta semana", C['red'], "📤"),
            ("PAGOS", format_money(total_paid), "A deudas", C['orange'], "💳"),
            ("BALANCE", format_money(total_income - total_expenses - total_paid), "Neto", C['teal'], "⚖️"),
        ]
        
        for i, (title, value, subtitle, color, icon) in enumerate(kpis):
            kc = KPICard(kpi_frame, title, value, subtitle, icon, color)
            kc.grid(row=0, column=i, padx=8, pady=4, sticky="ew")

    def _build_excel_views(self):
        """Construye vistas diaria y semanal tipo Excel."""
        container = card(self)
        container.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        tabs = ttk.Notebook(container)
        tabs.pack(fill="both", expand=True, padx=12, pady=12)

        self.daily_tab = frame(tabs, bg=C['card'])
        self.weekly_tab = frame(tabs, bg=C['card'])
        tabs.add(self.daily_tab, text="📅 Diario")
        tabs.add(self.weekly_tab, text="📊 Semanal")

        self._build_daily_excel_tab()
        self._build_weekly_excel_tab()

    def _build_daily_excel_tab(self):
        top = frame(self.daily_tab, bg=C['card'])
        top.pack(fill="x", padx=8, pady=(8, 6))

        top.columnconfigure(1, weight=1)

        label(top, "Fecha (YYYY-MM-DD)", font=F['sm_b'], bg=C['card'], fg=C['text2']).grid(row=0, column=0, sticky="w", padx=(0, 8), pady=2)
        self.daily_date_var = tk.StringVar(value=self.current_date.strftime('%Y-%m-%d'))
        date_entry = entry(top, width=16, textvariable=self.daily_date_var)
        date_entry.grid(row=0, column=1, sticky="w", padx=(0, 8), pady=2)
        button(top, "Ver Día", self._refresh_daily_table, bg=C['card2'], pad=(10, 5), font=F['sm']).grid(row=0, column=2, sticky="w", padx=(0, 8), pady=2)
        button(top, "+ Registrar", self._add_selected_day_entry, bg=C['teal'], pad=(12, 5), font=F['sm_b']).grid(row=0, column=3, sticky="w", pady=2)

        table_wrap = frame(self.daily_tab, bg=C['card'])
        table_wrap.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        columns = ("date", "type", "category", "description", "amount")
        self.daily_tree = ttk.Treeview(table_wrap, columns=columns, show="headings", height=14)
        headings = {
            "date": "Fecha",
            "type": "Tipo",
            "category": "Categoría",
            "description": "Descripción",
            "amount": "Monto",
        }
        widths = {"date": 110, "type": 100, "category": 140, "description": 320, "amount": 120}
        for col in columns:
            self.daily_tree.heading(col, text=headings[col])
            self.daily_tree.column(col, width=widths[col], anchor="w")
        self.daily_tree.column("amount", anchor="e")

        yscroll = ttk.Scrollbar(table_wrap, orient="vertical", command=self.daily_tree.yview)
        self.daily_tree.configure(yscrollcommand=yscroll.set)
        self.daily_tree.pack(side="left", fill="both", expand=True)
        yscroll.pack(side="right", fill="y")

        self.daily_total_label = label(self.daily_tab, "", font=F['sm_b'], bg=C['card'], fg=C['text'])
        self.daily_total_label.pack(anchor="e", padx=14, pady=(0, 8))

        self._refresh_daily_table()

    def _build_weekly_excel_tab(self):
        top = frame(self.weekly_tab, bg=C['card'])
        top.pack(fill="x", padx=8, pady=(8, 6))
        button(top, "Actualizar semana", self._refresh_weekly_table, bg=C['card2'], pad=(10, 5), font=F['sm']).pack(side="left")

        table_wrap = frame(self.weekly_tab, bg=C['card'])
        table_wrap.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        columns = ("day", "income", "expense", "payment", "balance")
        self.weekly_tree = ttk.Treeview(table_wrap, columns=columns, show="headings", height=14)
        headings = {
            "day": "Día",
            "income": "Ingresos",
            "expense": "Gastos",
            "payment": "Pagos",
            "balance": "Balance",
        }
        widths = {"day": 180, "income": 120, "expense": 120, "payment": 120, "balance": 120}
        for col in columns:
            self.weekly_tree.heading(col, text=headings[col])
            self.weekly_tree.column(col, width=widths[col], anchor="e" if col != "day" else "w")

        yscroll = ttk.Scrollbar(table_wrap, orient="vertical", command=self.weekly_tree.yview)
        self.weekly_tree.configure(yscrollcommand=yscroll.set)
        self.weekly_tree.pack(side="left", fill="both", expand=True)
        yscroll.pack(side="right", fill="y")

        self.weekly_total_label = label(self.weekly_tab, "", font=F['sm_b'], bg=C['card'], fg=C['text'])
        self.weekly_total_label.pack(anchor="e", padx=14, pady=(0, 8))

        self._refresh_weekly_table()

    def _add_selected_day_entry(self):
        """Abre registro para la fecha seleccionada en la vista diaria."""
        try:
            selected = datetime.strptime(self.daily_date_var.get().strip(), "%Y-%m-%d")
            self._show_day_entry(selected)
        except ValueError:
            messagebox.showwarning("Fecha inválida", "Usa formato YYYY-MM-DD")

    def _refresh_daily_table(self):
        """Recarga tabla diaria."""
        if not hasattr(self, 'daily_tree'):
            return

        for row in self.daily_tree.get_children():
            self.daily_tree.delete(row)

        try:
            day = datetime.strptime(self.daily_date_var.get().strip(), "%Y-%m-%d")
        except ValueError:
            self.daily_total_label.config(text="Fecha inválida")
            return

        day_iso = day.strftime('%Y-%m-%d')
        transactions = FinanceService.get_transactions_by_date_range(self.user_id, day_iso, day_iso)

        type_map = {
            'income': 'Ingreso',
            'expense': 'Gasto',
            'payment': 'Pago',
        }

        total = 0.0
        for trans in transactions:
            sign = 1 if trans.type == 'income' else -1
            total += sign * trans.amount
            self.daily_tree.insert("", "end", values=(
                trans.date,
                type_map.get(trans.type, trans.type),
                trans.category,
                trans.description or "-",
                format_money(trans.amount)
            ))

        self.daily_total_label.config(text=f"Total neto del día: {format_money(total)}")

    def _refresh_weekly_table(self):
        """Recarga tabla semanal tipo resumen por día."""
        if not hasattr(self, 'weekly_tree'):
            return

        for row in self.weekly_tree.get_children():
            self.weekly_tree.delete(row)

        start, end = self._get_week_range()
        s = start.strftime('%Y-%m-%d')
        e = end.strftime('%Y-%m-%d')
        transactions = FinanceService.get_transactions_by_date_range(self.user_id, s, e)

        day_buckets = {}
        current = start
        while current <= end:
            key = current.strftime('%Y-%m-%d')
            day_buckets[key] = {'income': 0.0, 'expense': 0.0, 'payment': 0.0}
            current += timedelta(days=1)

        for trans in transactions:
            key = (trans.date or "")[:10]
            if key in day_buckets and trans.type in day_buckets[key]:
                day_buckets[key][trans.type] += trans.amount

        total_income = total_expense = total_payment = 0.0
        for day_key in sorted(day_buckets.keys()):
            income = day_buckets[day_key]['income']
            expense = day_buckets[day_key]['expense']
            payment = day_buckets[day_key]['payment']
            balance = income - expense - payment

            total_income += income
            total_expense += expense
            total_payment += payment

            dt = datetime.strptime(day_key, "%Y-%m-%d")
            day_text = f"{dt.strftime('%A %d/%m')}"
            self.weekly_tree.insert("", "end", values=(
                day_text,
                format_money(income),
                format_money(expense),
                format_money(payment),
                format_money(balance),
            ))

        total_balance = total_income - total_expense - total_payment
        self.weekly_total_label.config(
            text=f"Total semana | Ingresos: {format_money(total_income)} | Gastos: {format_money(total_expense)} | Pagos: {format_money(total_payment)} | Balance: {format_money(total_balance)}"
        )
    
    def _show_day_entry(self, day):
        """Muestra diálogo para agregar entrada del día"""
        win = DialogWindow(parent=self, title=f"Nuevo registro - {day.strftime('%d/%m/%Y')}", 
                          width=500, height=550)
        
        date_str = day.strftime('%d de %B de %Y')
        label(win.header, f"📅 {date_str}", font=F['lg'], bg=C['bg'],
              fg=C['text']).pack(anchor="w", padx=4, pady=(2, 0))
        label(win.header, "Registra un nuevo ingreso, gasto o pago", font=F['sm'], 
              bg=C['bg'], fg=C['text2']).pack(anchor="w", padx=4, pady=(0, 2))
        separator(win.header, C['border']).pack(fill="x", pady=(8, 0))
        
        # Tipo de entrada mejorado
        type_frame = frame(win.content, bg=C['bg'])
        type_frame.pack(fill="x", pady=(12, 8), padx=0)
        
        label(type_frame, "Tipo de registro:", font=F['sm_b'], bg=C['bg'],
              fg=C['text']).pack(anchor="w", padx=4, pady=(0, 8))
        
        entry_type = tk.StringVar(value="expense")
        
        radio_frame = frame(type_frame, bg=C['bg'])
        radio_frame.pack(fill="x")
        
        type_options = [
            ("💰 Ingreso", "income", C['green']),
            ("📤 Gasto", "expense", C['red']),
            ("💳 Pago de Deuda", "payment", C['orange']),
        ]
        
        for text, value, color in type_options:
            tk.Radiobutton(radio_frame, text=text, variable=entry_type, value=value,
                           bg=C['bg'], fg=C['text'], selectcolor=C['card'],
                           activebackground=C['bg'], activeforeground=color,
                           font=F['sm']).pack(side="left", padx=8)
        
        # Cantidad mejorada
        amount_frame = frame(win.content, bg=C['bg'])
        amount_frame.pack(fill="x", pady=10, padx=0)
        label(amount_frame, "Cantidad ($):", font=F['sm_b'], bg=C['bg'],
              fg=C['text']).pack(anchor="w", padx=4, pady=(0, 4))
        amount_entry = entry(amount_frame, width=50)
        amount_entry.pack(fill="x", pady=(0, 2), ipady=8, padx=4)
        
        # Descripción mejorada
        desc_frame = frame(win.content, bg=C['bg'])
        desc_frame.pack(fill="x", pady=10, padx=0)
        label(desc_frame, "Descripción (opcional):", font=F['sm_b'], bg=C['bg'],
              fg=C['text']).pack(anchor="w", padx=4, pady=(0, 4))
        desc_entry = entry(desc_frame, width=50)
        desc_entry.pack(fill="x", pady=(0, 2), ipady=8, padx=4)
        
        # Categoría mejorada
        category_frame = frame(win.content, bg=C['bg'])
        category_frame.pack(fill="x", pady=10, padx=0)
        label(category_frame, "Categoría:", font=F['sm_b'], bg=C['bg'],
              fg=C['text']).pack(anchor="w", padx=4, pady=(0, 4))
        
        from tkinter import ttk
        categories = ['Alimentación', 'Transporte', 'Servicios', 'Entretenimiento', 'Salud', 'Educación', 'Diversión', 'Otro']
        cat_combo = ttk.Combobox(category_frame, 
                                values=categories,
                                state="readonly", width=46, font=F['sm'])
        cat_combo.set('Otro')
        cat_combo.pack(fill="x", padx=4, pady=(0, 2), ipady=6)
        
        # Footer mejorado
        footer_frame = frame(win.footer, bg=C['bg'])
        footer_frame.pack(fill="x")
        
        def save_entry():
            try:
                amount = float(amount_entry.get())
                if amount <= 0:
                    messagebox.showwarning("❌ Error", "La cantidad debe ser mayor a 0")
                    return
                
                description = desc_entry.get().strip()
                entry_category = cat_combo.get()
                entry_type_val = entry_type.get()
                trans_date = day.isoformat()
                
                # Guardar transacción en BD
                result = FinanceService.create_transaction(
                    user_id=self.user_id,
                    amount=amount,
                    trans_type=entry_type_val,
                    category=entry_category,
                    description=description,
                    transaction_date=trans_date
                )
                
                if result:
                    type_emoji = {'income': '💰', 'expense': '📤', 'payment': '💳'}.get(entry_type_val, '💵')
                    type_name = {'income': 'Ingreso', 'expense': 'Gasto', 'payment': 'Pago'}[entry_type_val]
                    messagebox.showinfo(
                        f"✅ {type_emoji} Éxito", 
                        f"{type_name} registrado para {day.strftime('%d/%m/%Y')}\n"
                        f"${amount:.2f} - {entry_category}"
                    )
                    win.destroy()
                    self._build()
                else:
                    messagebox.showerror("❌ Error", "Error al guardar la transacción")
            except ValueError:
                messagebox.showerror("❌ Error", "Ingresa una cantidad válida")
        
        button(footer_frame, "💾 Guardar Entrada", save_entry,
               bg=C['teal'], pad=(16, 10), font=F['base_b']).pack(side="left", padx=4, fill="x", expand=True)
        button(footer_frame, "Cancelar", win.destroy,
               bg=C['card2'], pad=(16, 10), font=F['base']).pack(side="left", padx=4, fill="x", expand=True)
