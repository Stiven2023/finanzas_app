"""
Página de Gestión de Metas Financieras
"""
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import date
from src.ui.components import frame, label, button, entry, card, separator, KPICard, ProgressBar, DialogWindow, page_header
from src.ui.theme import DEFAULT_COLORS as C, DEFAULT_FONTS as F
from src.utils.formatters import format_money
from src.services.goal_service import GoalService

class GoalsPage(tk.Frame):
    """Página de gestión de metas financieras"""
    
    GOAL_CATEGORIES = {
        'car': ('🚗', 'Vehículo'),
        'house': ('🏠', 'Vivienda'),
        'vacation': ('🏖️', 'Vacaciones'),
        'education': ('📚', 'Educación'),
        'emergency': ('🚨', 'Fondo Emergencia'),
        'investment': ('📈', 'Inversión'),
        'wedding': ('💍', 'Boda'),
        'general': ('🎯', 'General'),
    }
    
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg=C['bg'], **kwargs)
        self.app = app
        self.user_id = app.current_user.id
        self._build()
    
    def _build(self):
        """Construye la página"""
        page_header(self, "🎯 Mis Metas Financieras", "+ Nueva Meta", self._show_create_dialog)
        
        # KPIs
        self._build_kpis()
        
        # Metas
        self._build_goals_list()
    
    def _build_kpis(self):
        """Construye las tarjetas KPI"""
        summary = GoalService.get_total_goals_progress(self.user_id)
        
        kpi_frame = frame(self, bg=C['bg'])
        kpi_frame.pack(fill="x", padx=30, pady=(0, 16))
        kpi_frame.columnconfigure((0, 1, 2, 3), weight=1, uniform="k")
        
        kpis = [
            ("METAS ACTIVAS", str(summary['active_goals']), "En progreso", C['teal'], "🎯"),
            ("METAS COMPLETADAS", str(summary['completed_goals']), "Logradas", C['green'], "✅"),
            ("PROGRESO TOTAL", f"{summary['overall_progress']:.1f}%", "De tu objetivo", C['accent'], "📊"),
            ("AHORRADO", format_money(summary['total_current']), f"De {format_money(summary['total_target'])}", C['purple'], "💰"),
        ]
        
        for i, (title, value, subtitle, color, icon) in enumerate(kpis):
            kc = KPICard(kpi_frame, title, value, subtitle, icon, color)
            kc.grid(row=0, column=i, padx=8, pady=4, sticky="ew")
    
    def _build_goals_list(self):
        """Construye la lista de metas"""
        goals = GoalService.get_all_goals(self.user_id)
        
        if not goals:
            empty_frame = frame(self, bg=C['bg'])
            empty_frame.pack(fill="both", expand=True, padx=30, pady=20)
            label(empty_frame, "Sin metas creadas", font=F['lg'],
                  bg=C['bg'], fg=C['text2']).pack(expand=True)
            return
        
        # Separar activas y completadas
        active_goals = [g for g in goals if g.status == 'active']
        completed_goals = [g for g in goals if g.status == 'completed']
        
        container = frame(self, bg=C['bg'])
        container.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        
        # Metas activas
        if active_goals:
            self._build_goals_section(container, "🎯 Metas Activas", active_goals, True)
        
        # Metas completadas
        if completed_goals:
            self._build_goals_section(container, "✅ Metas Completadas", completed_goals, False)
    
    def _build_goals_section(self, parent, title, goals_list, is_active):
        """Construye una sección de metas"""
        section = card(parent)
        section.pack(fill="x", pady=(0, 16))
        
        label(section, title, font=F['lg'], bg=C['card'],
              fg=C['text']).pack(anchor="w", padx=16, pady=(14, 8))
        
        for goal in goals_list:
            self._build_goal_card(section, goal, is_active)
    
    def _build_goal_card(self, parent, goal, is_active):
        """Construye tarjeta de meta"""
        card_frame = frame(parent, bg=C['card2'])
        card_frame.pack(fill="x", padx=16, pady=8)
        
        # Encabezado
        hdr = frame(card_frame, bg=C['card2'])
        hdr.pack(fill="x", padx=12, pady=(8, 0))
        
        icon, _ = self.GOAL_CATEGORIES.get(goal.category, ('🎯', 'Meta'))
        label(hdr, f"{icon} {goal.name}", font=F['base_b'],
              bg=C['card2'], fg=C['text']).pack(side="left")
        
        if is_active:
            label(hdr, f"{goal.progress_percentage:.1f}%", font=F['sm_b'],
                  bg=C['card2'], fg=goal.color).pack(side="right")
        else:
            label(hdr, "✓ Completada", font=F['sm'],
                  bg=C['card2'], fg=C['green']).pack(side="right")
        
        # Descripcióne/Fecha
        if goal.description:
            label(card_frame, goal.description, font=F['sm'],
                  bg=C['card2'], fg=C['text2']).pack(anchor="w", padx=12)
        
        if goal.target_date:
            label(card_frame, f"📅 Meta: {goal.target_date}", font=F['sm'],
                  bg=C['card2'], fg=C['text2']).pack(anchor="w", padx=12)
        
        # Barra de progreso
        progress_frame = frame(card_frame, bg=C['card2'])
        progress_frame.pack(fill="x", padx=12, pady=8)
        
        progress = ProgressBar(progress_frame, progress=goal.progress_percentage,
                              color=goal.color if goal.color else C['accent'])
        progress.pack(fill="x")
        
        # Info
        info_frame = frame(card_frame, bg=C['card2'])
        info_frame.pack(fill="x", padx=12, pady=(0, 8))
        
        label(info_frame, f"{format_money(goal.current_amount)} / {format_money(goal.target_amount)}",
              font=F['sm'], bg=C['card2'], fg=C['text']).pack(side="left")
        label(info_frame, f"Falta: {format_money(goal.remaining_amount)}", font=F['sm'],
              bg=C['card2'], fg=C['text2']).pack(side="right")
        
        # Acciones
        if is_active:
            action_frame = frame(card_frame, bg=C['card2'])
            action_frame.pack(fill="x", padx=12, pady=(0, 8))
            
            button(action_frame, "+ Agregar Dinero", lambda g=goal: self._add_progress(g),
                   bg=C['green'], font=F['sm'], pad=(8, 4)).pack(side="left", padx=(0, 4), expand=True, fill="x")
            button(action_frame, "✏️ Editar", lambda g=goal: self._edit_goal(g),
                   bg=C['accent2'], font=F['sm'], pad=(8, 4)).pack(side="left", padx=2, expand=True, fill="x")
            button(action_frame, "🗑️ Eliminar", lambda g=goal: self._delete_goal(g),
                   bg=C['red'], font=F['sm'], pad=(8, 4)).pack(side="left", padx=2, expand=True, fill="x")
    
    def _show_create_dialog(self):
        """Muestra diálogo para crear meta"""
        self._show_goal_dialog()
    
    def _edit_goal(self, goal):
        """Edita una meta"""
        self._show_goal_dialog(goal)
    
    def _show_goal_dialog(self, goal=None):
        """Diálogo para crear/editar meta"""
        win = DialogWindow(parent=self, title="Nueva Meta" if not goal else f"Editar {goal.name}",
                          width=580, height=680)
        
        label(win.header, "🎯 " + ("Nueva Meta" if not goal else f"Editar Meta"),
              font=F['lg'], bg=C['bg'], fg=C['text']).pack(anchor="w")
        separator(win.header, C['border']).pack(fill="x", pady=(8, 0))
        
        # Campos
        fields = [
            ("Nombre de la Meta", "name", goal.name if goal else ""),
            ("Descripción", "description", goal.description if goal else ""),
            ("Monto Objetivo ($)", "target_amount", str(goal.target_amount) if goal else ""),
            ("Fecha Límite (cuándo quieres cumplirla, YYYY-MM-DD)", "target_date", goal.target_date if goal else ""),
            ("Categoría", "category", goal.category if goal else "general"),
        ]
        
        self.entries = {}
        for label_txt, field_name, value in fields:
            f = frame(win.content, bg=C['bg'])
            f.pack(fill="x", pady=6)
            label(f, label_txt, font=F['sm_b'], bg=C['bg'],
                  fg=C['text2']).pack(anchor="w")
            
            if field_name == "category":
                combo = ttk.Combobox(f, values=list(self.GOAL_CATEGORIES.values()), state="readonly", width=42)
                combo.set(self.GOAL_CATEGORIES.get(value, ('🎯', 'General'))[1])
                combo.pack(fill="x", pady=(2, 0), ipady=6)
                self.entries[field_name] = combo
            elif field_name == "target_date":
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
                self.entries[field_name] = e
            else:
                e = entry(f, width=45)
                e.insert(0, value)
                e.pack(fill="x", pady=(2, 0), ipady=6)
                self.entries[field_name] = e

        inline_actions = frame(win.content, bg=C['bg'])
        inline_actions.pack(fill="x", pady=(12, 4))
        button(inline_actions, "💾 Guardar", lambda: self._save_goal(goal, win),
               bg=C['teal'], pad=(16, 8)).pack(side="left", padx=(0, 10), fill="x", expand=True)
        button(inline_actions, "Cancelar", win.destroy,
               bg=C['card2'], pad=(16, 8)).pack(side="left", fill="x", expand=True)
        
        # Botones
        button(win.footer, "💾 Guardar", lambda: self._save_goal(goal, win),
               bg=C['teal'], pad=(16, 8)).pack(side="left", padx=(0, 10), fill="x", expand=True)
        button(win.footer, "Cancelar", win.destroy,
               bg=C['card2'], pad=(16, 8)).pack(side="left", fill="x", expand=True)

         win.bind("<Control-s>", lambda e: self._save_goal(goal, win))
         win.bind("<Control-S>", lambda e: self._save_goal(goal, win))
         win.bind("<Command-s>", lambda e: self._save_goal(goal, win))
         win.bind("<Command-S>", lambda e: self._save_goal(goal, win))
         win.bind("<Escape>", lambda e: win.destroy())
         first_entry = self.entries.get("name")
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
    
    def _save_goal(self, goal, win):
        """Guarda una meta"""
        try:
            name = self.entries['name'].get().strip()
            description = self.entries['description'].get().strip()
            target_amount = float(self.entries['target_amount'].get().replace("$", "").replace(",", ""))
            target_date = self.entries['target_date'].get().strip()
            category = self.entries['category'].get()
            
            # Obtener key de categoría
            category_key = next((k for k, v in self.GOAL_CATEGORIES.items() if v[1] == category), 'general')
            
            if not name or target_amount <= 0:
                messagebox.showwarning("Error", "Completa los campos requeridos")
                return
            
            if goal:
                # Editar
                GoalService.update_goal(
                    goal.id,
                    name=name,
                    description=description,
                    target_amount=target_amount,
                    target_date=target_date,
                    category=category_key
                )
            else:
                # Crear
                GoalService.create_goal(
                    self.user_id,
                    name=name,
                    target_amount=target_amount,
                    target_date=target_date,
                    category=category_key,
                    description=description,
                    icon=self.GOAL_CATEGORIES[category_key][0]
                )
            
            win.destroy()
            self._build()
            messagebox.showinfo("Éxito", "Meta guardada correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {e}")
    
    def _add_progress(self, goal):
        """Agrega progreso a una meta"""
        win = tk.Toplevel(self)
        win.title("Agregar Dinero")
        win.geometry("350x200")
        win.configure(bg=C['bg'])
        win.grab_set()
        
        label(win, f"Agregar dinero a: {goal.name}", font=F['lg'],
              bg=C['bg'], fg=C['text']).pack(pady=(20, 10), padx=20)
        
        f = frame(win, bg=C['bg'])
        f.pack(fill="x", padx=20, pady=10)
        label(f, "Cantidad ($)", font=F['sm_b'], bg=C['bg'],
              fg=C['text']).pack(anchor="w")
        amount_entry = entry(f, width=30)
        amount_entry.pack(fill="x", pady=(2, 0), ipady=6)
        
        def save_progress():
            try:
                amount = float(amount_entry.get().replace("$", "").replace(",", ""))
                if amount <= 0:
                    messagebox.showwarning("Error", "Ingresa una cantidad válida")
                    return
                GoalService.add_progress_to_goal(goal.id, amount)
                win.destroy()
                self._build()
                messagebox.showinfo("Éxito", f"✅ ${amount:,.0f} agregado a '{goal.name}'")
            except:
                messagebox.showerror("Error", "Cantidad inválida")
        
        button(win, "Agregar Dinero", save_progress, bg=C['teal']).pack(pady=20, padx=20, fill="x", ipady=8)
    
    def _delete_goal(self, goal):
        """Elimina una meta"""
        if messagebox.askyesno("Confirmar", f"¿Eliminar meta '{goal.name}'?"):
            GoalService.delete_goal(goal.id)
            self._build()
