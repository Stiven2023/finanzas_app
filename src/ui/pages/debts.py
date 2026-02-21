"""
Página de Gestión de Deudas
"""
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import date
from src.ui.components import frame, label, button, entry, card, separator, KPICard, DialogWindow, page_header
from src.ui.theme import DEFAULT_COLORS as C, DEFAULT_FONTS as F
from src.utils.formatters import format_money
from src.services.finance_service import FinanceService
from src.models.debt import Debt

class DebtsPage(tk.Frame):
    """Página de gestión de deudas"""
    
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg=C['bg'], **kwargs)
        self.app = app
        self.user_id = app.current_user.id
        self._build()
    
    def _build(self):
        """Construye la página"""
        page_header(self, "💳 Gestión de Deudas", "+ Nueva Deuda", self._show_create_dialog)
        
        # KPIs
        self._build_kpis()
        
        # Tabla de deudas
        self._build_debts_table()
    
    def _build_kpis(self):
        """Construye las tarjetas KPI"""
        total_debt = FinanceService.get_total_debt(self.user_id)
        total_payments = FinanceService.get_total_monthly_payments(self.user_id)
        debts = FinanceService.get_all_debts(self.user_id)
        
        urgent_count = len([d for d in debts if d.is_urgent])
        
        kpi_frame = frame(self, bg=C['bg'])
        kpi_frame.pack(fill="x", padx=30, pady=(0, 16))
        kpi_frame.columnconfigure((0, 1, 2, 3), weight=1, uniform="k")
        
        kpis = [
            ("DEUDA TOTAL", format_money(total_debt), "Todas las deudas", C['red'], "💳"),
            ("CUOTA MENSUAL", format_money(total_payments), "Pago mínimo total", C['orange'], "📅"),
            ("DEUDAS ACTIVAS", str(len(debts)), "Créditos registrados", C['purple'], "📋"),
            ("DEUDAS URGENTES", str(urgent_count), "Próximas a vencer", C['red'], "⚠️"),
        ]
        
        for i, (title, value, subtitle, color, icon) in enumerate(kpis):
            kc = KPICard(kpi_frame, title, value, subtitle, icon, color)
            kc.grid(row=0, column=i, padx=8, pady=4, sticky="ew")
    
    def _build_debts_table(self):
        """Construye la tabla de deudas"""
        tbl_frame = card(self)
        tbl_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        
        label(tbl_frame, "📊 Tus Deudas", font=F['lg'], bg=C['card'],
              fg=C['text']).pack(anchor="w", padx=16, pady=(14, 4))
        separator(tbl_frame, C['border']).pack(fill="x", padx=16, pady=(0, 8))
        
        # Encabezados
        hdr = frame(tbl_frame, bg=C['card2'])
        hdr.pack(fill="x", padx=16, pady=(0, 4))
        
        cols = [("Acreedor", 25), ("Saldo", 15), ("Cuota", 15), ("Fecha", 18), ("Estado", 12), ("Acciones", 15)]
        for col_name, width in cols:
            label(hdr, col_name, font=F['sm_b'], bg=C['card2'],
                  fg=C['text2'], width=width).pack(side="left", padx=5, pady=8)
        
        # Canvas con scroll
        canvas = tk.Canvas(tbl_frame, bg=C['card'], highlightthickness=0, height=300)
        scrollbar = ttk.Scrollbar(tbl_frame, orient="vertical", command=canvas.yview)
        self.content_frame = frame(canvas, bg=C['card'])
        self.content_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=16, pady=(0, 12))
        scrollbar.pack(side="right", fill="y")
        
        self._load_debts()
    
    def _load_debts(self):
        """Carga la lista de deudas"""
        for w in self.content_frame.winfo_children():
            w.destroy()
        
        debts = FinanceService.get_all_debts(self.user_id)
        
        if not debts:
            label(self.content_frame, "Sin deudas registradas",
                  font=F['sm'], bg=C['card'],
                  fg=C['text2']).pack(expand=True, pady=20)
            return
        
        for i, debt in enumerate(debts):
            bg = C['card'] if i % 2 == 0 else C['card2']
            row = frame(self.content_frame, bg=bg)
            row.pack(fill="x", pady=1)
            
            # Acreedor
            label(row, debt.creditor[:30], font=F['sm'],
                  bg=bg, fg=C['text'], width=25, anchor="w").pack(side="left", padx=5, pady=8)
            
            # Saldo
            label(row, format_money(debt.balance), font=F['sm_b'],
                  bg=bg, fg=C['red'], width=15, anchor="w").pack(side="left", padx=5)
            
            # Cuota
            label(row, format_money(debt.monthly_payment), font=F['sm'],
                  bg=bg, fg=C['text2'], width=15, anchor="w").pack(side="left", padx=5)
            
            # Fecha
            label(row, debt.payment_date[:18], font=F['sm'],
                  bg=bg, fg=C['text2'], width=18, anchor="w").pack(side="left", padx=5)
            
            # Estado
            label(row, debt.status, font=F['sm'],
                  bg=bg, fg=C['teal'], width=12, anchor="w").pack(side="left", padx=5)
            
            # Acciones
            actions_frame = frame(row, bg=bg)
            actions_frame.pack(side="left", padx=5)
            button(actions_frame, "✏️", lambda d=debt: self._edit_debt(d),
                   bg=C['accent2'], font=F['sm'], pad=(6, 4)).pack(side="left", padx=2)
            button(actions_frame, "✅", lambda d=debt: self._mark_paid(d),
                   bg=C['green'], font=F['sm'], pad=(6, 4)).pack(side="left", padx=2)
            button(actions_frame, "🗑️", lambda d=debt: self._delete_debt(d),
                   bg=C['red'], font=F['sm'], pad=(6, 4)).pack(side="left", padx=2)
    
    def _show_create_dialog(self):
        """Muestra diálogo para crear deuda"""
        self._show_debt_dialog()
    
    def _edit_debt(self, debt):
        """Edita una deuda existente"""
        self._show_debt_dialog(debt)
    
    def _show_debt_dialog(self, debt=None):
        """Diálogo para crear/editar deuda"""
        win = DialogWindow(parent=self, title="Nueva Deuda" if not debt else f"Editar {debt.creditor}",
                          width=560, height=700)
        
        label(win.header, "💳 " + ("Nueva Deuda" if not debt else "Editar Deuda"),
              font=F['lg'], bg=C['bg'], fg=C['text']).pack(anchor="w")
        separator(win.header, C['border']).pack(fill="x", pady=(8, 0))
        
        # Campos
        fields = [
            ("Acreedor (nombre del deudor)", "creditor", debt.creditor if debt else ""),
            ("Saldo Actual ($)", "balance", str(debt.balance) if debt else ""),
            ("Cuota Mensual ($)", "monthly_payment", str(debt.monthly_payment) if debt else ""),
            ("Fecha de Pago (próximo vencimiento, YYYY-MM-DD)", "payment_date", debt.payment_date if debt else ""),
            ("Categoría", "category", debt.category if debt else "personal"),
            ("Prioridad (1-5)", "priority", str(debt.priority) if debt else "3"),
            ("Estado", "status", debt.status if debt else "active"),
        ]
        
        self.entries = {}
        for label_txt, field_name, value in fields:
            f = frame(win.content, bg=C['bg'])
            f.pack(fill="x", pady=6)
            label(f, label_txt, font=F['sm_b'], bg=C['bg'],
                  fg=C['text2']).pack(anchor="w")

            if field_name == "payment_date":
                row = frame(f, bg=C['bg'])
                row.pack(fill="x", pady=(2, 0))
                e = entry(row, width=36)
                e.insert(0, value)
                e.pack(side="left", fill="x", expand=True, ipady=6)
                button(
                    row,
                    "📅",
                    lambda target=e: self._open_date_picker(target),
                    bg=C['card2'],
                    font=F['sm_b'],
                    pad=(10, 6)
                ).pack(side="left", padx=(8, 0))
            else:
                e = entry(f, width=45)
                e.insert(0, value)
                e.pack(fill="x", pady=(2, 0), ipady=6)

            self.entries[field_name] = e

        inline_actions = frame(win.content, bg=C['bg'])
        inline_actions.pack(fill="x", pady=(12, 4))
        button(inline_actions, "💾 Guardar", lambda: self._save_debt(debt, win),
               bg=C['teal'], pad=(16, 8)).pack(side="left", padx=(0, 10), fill="x", expand=True)
        button(inline_actions, "Cancelar", win.destroy,
               bg=C['card2'], pad=(16, 8)).pack(side="left", fill="x", expand=True)
        
        # Botones
        button(win.footer, "💾 Guardar", lambda: self._save_debt(debt, win),
               bg=C['teal'], pad=(16, 8)).pack(side="left", padx=(0, 10), fill="x", expand=True)
        button(win.footer, "Cancelar", win.destroy,
               bg=C['card2'], pad=(16, 8)).pack(side="left", fill="x", expand=True)

         win.bind("<Control-s>", lambda e: self._save_debt(debt, win))
         win.bind("<Control-S>", lambda e: self._save_debt(debt, win))
         win.bind("<Command-s>", lambda e: self._save_debt(debt, win))
         win.bind("<Command-S>", lambda e: self._save_debt(debt, win))
         win.bind("<Escape>", lambda e: win.destroy())
         first_entry = self.entries.get("creditor")
         if first_entry:
             first_entry.focus_set()

    def _open_date_picker(self, target_entry):
        """Abre selector simple de fecha y la coloca en el Entry destino."""
        picker = tk.Toplevel(self)
        picker.title("Seleccionar fecha")
        picker.configure(bg=C['bg'])
        picker.resizable(False, False)
        picker.grab_set()

        today = date.today()
        try:
            current_text = target_entry.get().strip()
            if current_text:
                y, m, d = [int(x) for x in current_text[:10].split("-")]
                initial = date(y, m, d)
            else:
                initial = today
        except Exception:
            initial = today

        cont = frame(picker, bg=C['bg'])
        cont.pack(fill="both", expand=True, padx=16, pady=16)

        label(cont, "Año", bg=C['bg'], fg=C['text2'], font=F['sm_b']).grid(row=0, column=0, sticky="w")
        label(cont, "Mes", bg=C['bg'], fg=C['text2'], font=F['sm_b']).grid(row=0, column=1, sticky="w", padx=(8, 0))
        label(cont, "Día", bg=C['bg'], fg=C['text2'], font=F['sm_b']).grid(row=0, column=2, sticky="w", padx=(8, 0))

        year_var = tk.IntVar(value=initial.year)
        month_var = tk.IntVar(value=initial.month)
        day_var = tk.IntVar(value=initial.day)

        tk.Spinbox(cont, from_=2000, to=2100, textvariable=year_var, width=8).grid(row=1, column=0, sticky="w", pady=(4, 10))
        tk.Spinbox(cont, from_=1, to=12, textvariable=month_var, width=5).grid(row=1, column=1, sticky="w", padx=(8, 0), pady=(4, 10))
        tk.Spinbox(cont, from_=1, to=31, textvariable=day_var, width=5).grid(row=1, column=2, sticky="w", padx=(8, 0), pady=(4, 10))

        def apply_date():
            try:
                selected = date(year_var.get(), month_var.get(), day_var.get())
                target_entry.delete(0, tk.END)
                target_entry.insert(0, selected.isoformat())
                picker.destroy()
            except ValueError:
                messagebox.showwarning("Fecha inválida", "La fecha seleccionada no es válida")

        actions = frame(cont, bg=C['bg'])
        actions.grid(row=2, column=0, columnspan=3, sticky="ew")
        button(actions, "Aplicar", apply_date, bg=C['teal'], pad=(12, 6)).pack(side="left", padx=(0, 8))
        button(actions, "Hoy", lambda: [target_entry.delete(0, tk.END), target_entry.insert(0, today.isoformat()), picker.destroy()],
               bg=C['card2'], pad=(12, 6)).pack(side="left", padx=(0, 8))
        button(actions, "Cancelar", picker.destroy, bg=C['card2'], pad=(12, 6)).pack(side="left")
    
    def _save_debt(self, debt, win):
        """Guarda una deuda"""
        try:
            creditor = self.entries['creditor'].get().strip()
            balance = float(self.entries['balance'].get().replace("$", "").replace(",", ""))
            monthly = float(self.entries['monthly_payment'].get() or 0)
            payment_date = self.entries['payment_date'].get().strip()
            category = self.entries['category'].get().strip()
            priority = int(self.entries['priority'].get() or 3)
            status = self.entries['status'].get().strip()
            
            if not creditor or balance < 0:
                messagebox.showwarning("Error", "Completa los campos requeridos")
                return
            
            if debt:
                # Editar
                debt.creditor = creditor
                debt.balance = balance
                debt.monthly_payment = monthly
                debt.payment_date = payment_date
                debt.category = category
                debt.priority = priority
                debt.status = status
                FinanceService.update_debt_balance(debt.id, balance)
            else:
                # Crear
                FinanceService.create_debt(
                    self.user_id, creditor, balance, monthly,
                    payment_date, priority, category=category
                )
            
            win.destroy()
            self._load_debts()
            self._build_kpis()
            messagebox.showinfo("Éxito", "Deuda guardada correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {e}")
    
    def _mark_paid(self, debt):
        """Marca una deuda como pagada"""
        if messagebox.askyesno("Confirmar", f"¿Marcar '{debt.creditor}' como pagada?"):
            FinanceService.mark_debt_paid(debt.id)
            self._load_debts()
            self._build_kpis()
            messagebox.showinfo("Éxito", "🎉 ¡Deuda eliminada!")
    
    def _delete_debt(self, debt):
        """Elimina una deuda"""
        if messagebox.askyesno("Confirmar", f"¿Eliminar deuda '{debt.creditor}'?"):
            FinanceService.delete_debt(debt.id)
            self._load_debts()
            self._build_kpis()
