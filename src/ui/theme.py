"""
Sistema de Tema y Estilos para UI - Flujo Brand
"""
import tkinter as tk
from tkinter import ttk
from config import FONTS

class Theme:
    """Clase para gestionar temas de la aplicación con identidad Flujo"""
    
    # Temas predefinidos según Flujo Brand Identity
    THEMES = {
        'dark': {
            # Base Flujo - Oscuro profesional
            'bg': "#090D12",          # Obsidiana - fondo principal
            'sidebar': "#111827",     # Tinta - sidebar
            'card': "#1C2736",        # Pizarra - cards principales
            'card2': "#2E3D50",       # Mist - superficie alternativa
            'input': "#111827",       # Input background
            'border': "#334155",      # Borde sutil
            
            # Primario Flujo - Jade (éxito, ingresos)
            'accent': "#00C896",      # Jade principal
            'teal': "#00C896",        # Jade (alias)
            'green': "#00C896",       # Jade (alias)
            
            # Secundario Flujo - Violeta (progreso, accent)
            'accent2': "#7B61FF",     # Violeta
            'purple': "#7B61FF",      # Violeta (alias)
            
            # Estados y alertas
            'red': "#FF5E57",         # Coral - deudas, alertas
            'orange': "#FFAA33",      # Ámbar - cuotas, avisos
            'yellow': "#FFAA33",      # Ámbar (alias)
            
            # Tipografía
            'text': "#EEF3F8",        # Nieve - texto principal
            'text2': "#9DB4C8",       # Escarcha - texto secundario
            'white': "#FFFFFF",       # Blanco puro

            # Semánticos de interfaz
            'success_bg': "#063D30",
            'warning_bg': "#4A2E06",
            'danger_bg': "#451A1A",
            'info_bg': "#1B365D",
            'focus': "#00C896",
        },
        'light': {
            # Light theme - versión clara
            'bg': "#F8F9FA",
            'sidebar': "#EEF3F8",
            'card': "#FFFFFF",
            'card2': "#F1F3F5",
            'input': "#FFFFFF",
            'border': "#D1D5DB",
            
            # Colores Flujo adaptados para light
            'accent': "#009A74",      # Jade oscuro
            'teal': "#009A74",
            'green': "#009A74",
            
            'accent2': "#6B51EF",     # Violeta oscuro
            'purple': "#6B51EF",
            
            'red': "#DC2626",
            'orange': "#D97706",
            'yellow': "#D97706",
            
            'text': "#111827",
            'text2': "#6B7280",
            'white': "#FFFFFF",

            # Semánticos de interfaz
            'success_bg': "#DCFCE7",
            'warning_bg': "#FEF3C7",
            'danger_bg': "#FEE2E2",
            'info_bg': "#DBEAFE",
            'focus': "#009A74",
        },
    }
    
    STATUS_COLORS = {
        'active': '#00C896',      # Verde Jade
        'paid': '#00C896',        # Verde Jade
        'overdue': '#FF5E57',     # Coral
        'pending': '#FFAA33',     # Ámbar
        'completed': '#00C896',   # Verde Jade
        'paused': '#9DB4C8',      # Escarcha
        'cancelled': '#6B7280',   # Gris
    }
    
    PRIORITY_COLORS = {
        'Crítica': '#FF5E57',     # Coral
        'Alta': '#FFAA33',        # Ámbar
        'Media': '#FFAA33',       # Ámbar
        'Baja': '#00C896',        # Verde Jade
    }
    
    @staticmethod
    def get_theme(theme_name='dark'):
        """Obtiene un tema específico"""
        return Theme.THEMES.get(theme_name, Theme.THEMES['dark'])
    
    @staticmethod
    def get_status_color(status):
        """Obtiene color para un estado"""
        return Theme.STATUS_COLORS.get(status, '#7B61FF')
    
    @staticmethod
    def get_priority_color(priority):
        """Obtiene color para una prioridad"""
        return Theme.PRIORITY_COLORS.get(priority, '#00C896')
    
    @staticmethod
    def merge_colors(primary_color, alpha=0.1):
        """Crea color con transparencia"""
        return primary_color


def apply_ttk_theme(root: tk.Misc, colors=None, fonts=None):
    """Aplica estilos ttk para mejorar consistencia visual."""
    c = colors or DEFAULT_COLORS
    f = fonts or DEFAULT_FONTS

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(
        "TNotebook",
        background=c['bg'],
        borderwidth=0,
    )
    style.configure(
        "TNotebook.Tab",
        background=c['card2'],
        foreground=c['text2'],
        padding=(12, 8),
        font=f['sm_b'],
        borderwidth=0,
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", c['card'])],
        foreground=[("selected", c['text'])],
    )

    style.configure(
        "TCombobox",
        fieldbackground=c['input'],
        background=c['input'],
        foreground=c['text'],
        bordercolor=c['border'],
        lightcolor=c['border'],
        darkcolor=c['border'],
        arrowcolor=c['text2'],
        insertcolor=c['text'],
        relief="flat",
        padding=6,
        font=f['base'],
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", c['input'])],
        foreground=[("readonly", c['text'])],
        selectbackground=[("readonly", c['card2'])],
        selectforeground=[("readonly", c['text'])],
    )

    style.configure(
        "Vertical.TScrollbar",
        background=c['card2'],
        troughcolor=c['card'],
        bordercolor=c['card'],
        arrowcolor=c['text2'],
    )
    style.map(
        "Vertical.TScrollbar",
        background=[("active", c['accent2'])],
    )

    style.configure(
        "Treeview",
        background=c['card'],
        fieldbackground=c['card'],
        foreground=c['text'],
        bordercolor=c['border'],
        rowheight=30,
        font=f['base'],
    )
    style.configure(
        "Treeview.Heading",
        background=c['card2'],
        foreground=c['text'],
        relief="flat",
        font=f['sm_b'],
        padding=6,
    )
    style.map(
        "Treeview",
        background=[("selected", c['accent2'])],
        foreground=[("selected", c['white'])],
    )
    style.map(
        "Treeview.Heading",
        background=[("active", c['accent'])],
        foreground=[("active", c['white'])],
    )

    root.option_add("*TCombobox*Listbox*Background", c['card'])
    root.option_add("*TCombobox*Listbox*Foreground", c['text'])
    root.option_add("*TCombobox*Listbox*selectBackground", c['accent2'])
    root.option_add("*TCombobox*Listbox*selectForeground", c['white'])

# Exportar colores y fuentes por defecto
DEFAULT_COLORS = Theme.get_theme('dark')
DEFAULT_FONTS = FONTS
THEMES = Theme.THEMES
