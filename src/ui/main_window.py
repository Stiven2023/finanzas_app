"""
Ventana Principal de la Aplicación
"""
import tkinter as tk
from tkinter import messagebox
from datetime import date

from config import APP_NAME, APP_VERSION, WINDOW_WIDTH, WINDOW_HEIGHT, MIN_WIDTH, MIN_HEIGHT
from src.ui.theme import DEFAULT_COLORS as C, DEFAULT_FONTS as F, apply_ttk_theme
from src.ui.components import frame, label, button, separator
from src.ui.pages.login import LoginPage
from src.ui.pages.dashboard import DashboardPage
from src.ui.pages.debts import DebtsPage
from src.ui.pages.goals import GoalsPage
from src.ui.pages.weekly import WeeklyPage
from src.ui.pages.reports import ReportsPage
from src.ui.pages.settings import SettingsPage
from src.database.db import db
from src.services.finance_service import FinanceService


class MainWindow(tk.Tk):
    """Ventana principal de la aplicación"""
    
    def __init__(self):
        super().__init__()
        self.title(f"💰 {APP_NAME} v{APP_VERSION}")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(MIN_WIDTH, MIN_HEIGHT)
        self.configure(bg=C['bg'])
        apply_ttk_theme(self)
        self._set_window_icon()
        
        try:
            self.state("zoomed")  # Windows
        except tk.TclError:
            pass
        
        # Usuario actual
        self.current_user = None
        
        # Variable para página activa
        self.active_page = tk.StringVar(value="login")
        
        # Construir UI
        self._build_ui()
        self.show_page("login")
    
    
    def _build_navigation(self):
        """Construye la navegación (solo después de login)"""
        # Limpiar navegación anterior
        for w in self.nav_frame.winfo_children():
            w.destroy()
        for w in self.footer_frame.winfo_children():
            w.destroy()
        
        self.nav_btns = {}
        
        # Menú
        nav_items = [
            ("📊", "Dashboard", "dashboard"),
            ("💳", "Deudas", "debts"),
            ("🎯", "Metas", "goals"),
            ("📅", "Semanas", "weekly"),
            ("💰", "Reportes", "reports"),
            ("⚙️", "Configuración", "settings"),
        ]
        
        for icon, label_txt, page in nav_items:
            b = self._create_nav_btn(self.nav_frame, icon, label_txt, page)
            self.nav_btns[page] = b
        
        # Footer con fecha
        separator(self.footer_frame, C['border']).pack(fill="x", padx=16, pady=12)
        label(self.footer_frame, f"📅 {date.today().strftime('%d %b %Y')}",
              font=F['sm'], bg=C['sidebar'], fg=C['text2']).pack(side="bottom", pady=(0, 16))

    def _set_window_icon(self):
        """Configura un ícono de app para barra de título y taskbar."""
        try:
            icon = tk.PhotoImage(width=32, height=32)
            icon.put(C['bg'], to=(0, 0, 31, 31))
            icon.put(C['accent2'], to=(2, 2, 29, 29))
            icon.put(C['accent'], to=(6, 6, 25, 25))
            icon.put(C['bg'], to=(11, 11, 20, 20))
            self.iconphoto(True, icon)
            self._icon_ref = icon
        except tk.TclError:
            pass
    
    def _remove_navigation(self):
        """Elimina la navegación (para login)"""
        for w in self.nav_frame.winfo_children():
            w.destroy()
        for w in self.footer_frame.winfo_children():
            w.destroy()
        self.nav_btns = {}

    
    def _build_ui(self):
        """Construye la interfaz"""
        # Sidebar (inicialmente vacío, se llena cuando autenticado)
        self.sidebar = tk.Frame(self, bg=C['sidebar'], width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        # Logo en el sidebar (siempre visible)
        logo_f = frame(self.sidebar, bg=C['sidebar'])
        logo_f.pack(fill="x", pady=(24, 8), padx=16)
        label(logo_f, "💰", font=("Segoe UI", 28), bg=C['sidebar'],
              fg=C['accent']).pack(anchor="w")
        label(logo_f, f"{APP_NAME}", font=F['lg'], bg=C['sidebar'],
              fg=C['text']).pack(anchor="w")
        label(logo_f, "v2.0.0", font=F['sm'], bg=C['sidebar'],
              fg=C['text2']).pack(anchor="w")
        
        separator(self.sidebar, C['border']).pack(fill="x", padx=16, pady=12)
        
        self.nav_frame = frame(self.sidebar, bg=C['sidebar'])
        self.nav_frame.pack(fill="both", expand=True)
        
        self.footer_frame = frame(self.sidebar, bg=C['sidebar'])
        self.footer_frame.pack(fill="x", side="bottom")
        
        # Área de contenido
        self.content = frame(self, bg=C['bg'])
        self.content.pack(side="left", fill="both", expand=True)
        
        # Diccionario de páginas
        self.pages = {}
        self.nav_btns = {}
    
    def _create_nav_btn(self, parent, icon, text, page):
        """Crea botón de navegación"""
        f = tk.Frame(parent, bg=C['sidebar'], cursor="hand2")
        f.pack(fill="x", padx=10, pady=2)
        
        def on_click():
            self.show_page(page)
        
        def on_enter(e):
            if self.active_page.get() != page:
                f.config(bg=C['card2'])
                for w in f.winfo_children():
                    w.config(bg=C['card2'])
        
        def on_leave(e):
            if self.active_page.get() != page:
                f.config(bg=C['sidebar'])
                for w in f.winfo_children():
                    w.config(bg=C['sidebar'])
        
        f.bind("<Button-1>", lambda e: on_click())
        f.bind("<Enter>", on_enter)
        f.bind("<Leave>", on_leave)
        
        lbl_icon = tk.Label(f, text=icon, font=("Segoe UI", 14), bg=C['sidebar'],
                           fg=C['accent'], padx=8, pady=10)
        lbl_icon.pack(side="left")
        lbl_icon.bind("<Button-1>", lambda e: on_click())
        lbl_icon.bind("<Enter>", on_enter)
        lbl_icon.bind("<Leave>", on_leave)
        
        lbl_txt = tk.Label(f, text=text, font=F['base_b'], bg=C['sidebar'],
                          fg=C['text'], pady=10)
        lbl_txt.pack(side="left")
        lbl_txt.bind("<Button-1>", lambda e: on_click())
        lbl_txt.bind("<Enter>", on_enter)
        lbl_txt.bind("<Leave>", on_leave)
        
        return (f, lbl_icon, lbl_txt)
    
    def _set_nav_active(self, page):
        """Destaca el botón de navegación activo"""
        for p, (f, li, lt) in self.nav_btns.items():
            if p == page:
                f.config(bg=C['accent'])
                li.config(bg=C['accent'], fg=C['white'])
                lt.config(bg=C['accent'], fg=C['white'])
            else:
                f.config(bg=C['sidebar'])
                li.config(bg=C['sidebar'], fg=C['accent'])
                lt.config(bg=C['sidebar'], fg=C['text'])
    
    def show_page(self, page):
        """Muestra una página específica"""
        self.active_page.set(page)
        
        # Limpiar contenido
        for w in self.content.winfo_children():
            w.destroy()
        
        # Mostrar página
        if page == "login":
            self._remove_navigation()
            LoginPage(self.content, self).pack(fill="both", expand=True)
        elif self.current_user is None:
            # Si no hay usuario autenticado, mostrar login
            self.show_page("login")
        else:
            # Usuario autenticado, mostrar otras páginas
            self._set_nav_active(page)
            
            if page == "dashboard":
                DashboardPage(self.content, self).pack(fill="both", expand=True)
            elif page == "debts":
                DebtsPage(self.content, self).pack(fill="both", expand=True)
            elif page == "goals":
                GoalsPage(self.content, self).pack(fill="both", expand=True)
            elif page == "weekly":
                WeeklyPage(self.content, self).pack(fill="both", expand=True)
            elif page == "reports":
                ReportsPage(self.content, self).pack(fill="both", expand=True)
            elif page == "settings":
                SettingsPage(self.content, self).pack(fill="both", expand=True)
    
    def on_login_success(self, user):
        """Callback cuando login es exitoso"""
        self.current_user = user
        self._build_navigation()
        self.show_page("dashboard")
    
    def logout(self):
        """Cierra sesión"""
        self.current_user = None
        self._remove_navigation()
        self.show_page("login")
