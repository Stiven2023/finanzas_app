"""
Componentes UI reutilizables para la aplicación
"""
import tkinter as tk
from tkinter import ttk
from src.ui.theme import DEFAULT_COLORS as C, DEFAULT_FONTS as F
from src.utils.formatters import format_money


def _hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def _rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(*rgb)


def _blend(color_a, color_b, ratio=0.12):
    ra, ga, ba = _hex_to_rgb(color_a)
    rb, gb, bb = _hex_to_rgb(color_b)
    mixed = (
        int(ra + (rb - ra) * ratio),
        int(ga + (gb - ga) * ratio),
        int(ba + (bb - ba) * ratio),
    )
    return _rgb_to_hex(mixed)

# ── COMPONENTES BÁSICOS ────────────────────────────────────────────────────

def frame(parent, bg=None, **kwargs):
    """Crea un Frame con estilos por defecto"""
    return tk.Frame(parent, bg=bg or C['bg'], **kwargs)

def label(parent, text, font=None, fg=None, bg=None, **kwargs):
    """Crea un Label con estilos por defecto"""
    return tk.Label(
        parent, text=text, font=font or F['base'],
        fg=fg or C['text'], bg=bg or C['bg'], **kwargs
    )

def button(parent, text, cmd, bg=None, fg=None, font=None, pad=(14, 10), **kwargs):
    """Crea un Button avec mejor visual y feedback"""
    bg_color = bg or C['accent']
    
    hover_bg = _blend(bg_color, C['white'], 0.08) if bg_color != C['card2'] else _blend(bg_color, C['white'], 0.15)

    btn = tk.Button(
        parent, text=text, command=cmd,
        bg=bg_color, fg=fg or C['white'],
        font=font or F['base_b'], relief="flat", cursor="hand2",
        activebackground=hover_bg,
        activeforeground=C['white'],
        padx=pad[0], pady=pad[1], bd=0, 
        highlightthickness=1,
        highlightbackground=bg_color,
        **kwargs
    )
    
    # Mejorar hover visual
    def on_enter(e):
        if btn['state'] != 'disabled':
            btn.config(bg=hover_bg, highlightbackground=hover_bg)
    
    def on_leave(e):
        if btn['state'] != 'disabled':
            btn.config(bg=bg_color, highlightbackground=bg_color)
    
    btn.bind('<Enter>', on_enter)
    btn.bind('<Leave>', on_leave)
    
    return btn

def entry(parent, width=20, **kwargs):
    """Crea un Entry con estilos mejorados"""
    e = tk.Entry(
        parent, bg=C['input'], fg=C['text'], font=F['base'],
        insertbackground=C['text'], relief="flat",
        highlightthickness=1, highlightcolor=C['accent'],
        highlightbackground=C['border'], width=width, 
        bd=0, readonlybackground=C['input'],
        disabledbackground=C['card2'], disabledforeground=C['text2'],
        **kwargs
    )
    
    def on_focus_in(event):
        if e['highlightbackground'] != C['accent']:
            e.config(highlightbackground=C['accent'], highlightthickness=2)
    
    def on_focus_out(event):
        e.config(highlightbackground=C['border'], highlightthickness=1)
    
    e.bind('<FocusIn>', on_focus_in)
    e.bind('<FocusOut>', on_focus_out)
    
    return e

def card(parent, **kwargs):
    """Crea un Frame tipo "card" con estilo"""
    return tk.Frame(
        parent, bg=C['card'], bd=0, relief="flat",
        highlightthickness=1, highlightbackground=C['border'],
        padx=2, pady=2, **kwargs
    )

def separator(parent, color=None, height=1):
    """Crea un separador visual"""
    return tk.Frame(parent, bg=color or C['border'], height=height)


def page_header(parent, title, action_text=None, action_cmd=None):
    """Encabezado estándar para páginas."""
    hdr = frame(parent, bg=C['bg'])
    hdr.pack(fill="x", padx=30, pady=(24, 0))
    label(hdr, title, font=F['xl'], bg=C['bg'], fg=C['text']).pack(side="left")
    if action_text and action_cmd:
        button(hdr, action_text, action_cmd, bg=C['teal']).pack(side="right")
    separator(parent, C['border']).pack(fill="x", padx=30, pady=14)
    return hdr

# ── COMPONENTES COMPLEJOS ──────────────────────────────────────────────────

class KPICard(tk.Frame):
    """Tarjeta de KPI (Key Performance Indicator) mejorada"""
    
    def __init__(self, parent, title, value, subtitle="", icon="", color=None, **kwargs):
        super().__init__(parent, bg=C['card'], padx=18, pady=18, **kwargs)
        self.config(highlightthickness=1, highlightbackground=C['border'], relief="flat")
        color = color or C['accent']
        
        # Barra de color superior (más visible)
        tk.Frame(self, bg=color, height=5).pack(fill="x", pady=(0, 14))
        
        # Encabezado con ícono y título
        top = frame(self, bg=C['card'])
        top.pack(fill="x", pady=(0, 8))
        
        if icon:
            label(top, icon, font=("Segoe UI", 24), bg=C['card'],
                  fg=color, width=2).pack(side="left", padx=(0, 8))
        
        label(top, title, font=F['sm_b'], bg=C['card'],
              fg=C['text2']).pack(side="left", padx=(0, 0))
        
        # Valor principal (más grande y destacado)
        value_label = label(self, value, font=("Segoe UI", 22, "bold"),
              bg=C['card'], fg=color)
        value_label.pack(anchor="w", pady=(4, 6))
        
        # Subtítulo
        if subtitle:
            label(self, subtitle, font=F['sm'], bg=C['card'],
                  fg=C['text2']).pack(anchor="w", pady=(0, 0))


class DataTable(tk.Frame):
    """Tabla de datos con scroll"""
    
    def __init__(self, parent, columns, **kwargs):
        super().__init__(parent, bg=C['card'], **kwargs)
        self.columns = columns
        self.rows = []
        
        # Encabezado
        header_frame = frame(self, bg=C['card2'])
        header_frame.pack(fill="x", padx=16, pady=(12, 4))
        
        for col_name, col_width in columns:
            label(header_frame, col_name, font=F['sm_b'],
                  bg=C['card2'], fg=C['text2'],
                  width=col_width).pack(side="left", padx=5, pady=8)
        
        # Canvas con scroll
        canvas = tk.Canvas(self, bg=C['card'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        
        self.content_frame = frame(canvas, bg=C['card'])
        self.content_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=16, pady=(0, 12))
        scrollbar.pack(side="right", fill="y")
    
    def add_row(self, data, bg_color=None):
        """Agrega una fila a la tabla con alternancia de colores mejorada"""
        # Alternar colores de fondo para mejor legibilidad
        row_bg = bg_color or (C['card'] if len(self.rows) % 2 == 0 else C['input'])
        row_frame = frame(self.content_frame, bg=row_bg)
        row_frame.pack(fill="x", pady=0)
        
        for i, (value, col_width) in enumerate(
            zip(data, [col[1] for col in self.columns])
        ):
            label(row_frame, str(value), font=F['sm'], bg=row_bg,
                  fg=C['text'], width=col_width).pack(side="left", padx=5, pady=10)
        
        self.rows.append(row_frame)
    
    def clear(self):
        """Limpia todas las filas"""
        for row in self.rows:
            row.destroy()
        self.rows = []


class ProgressBar(tk.Frame):
    """Barra de progreso visual"""
    
    def __init__(self, parent, progress=0, color=None, **kwargs):
        super().__init__(parent, bg=C['border'], height=20, **kwargs)
        self.pack_propagate(False)
        self.progress = progress
        self.color = color or C['accent']
        
        # Barra de relleno
        self.fill_frame = tk.Frame(
            self, bg=self.color, height=20
        )
        self.fill_frame.place(relwidth=max(0.01, progress/100), relheight=1)
        
        # Texto de porcentaje
        self.label = label(
            self, f"{progress:.1f}%", font=F['sm_b'],
            bg=C['border'], fg=C['white']
        )
        self.label.place(x=4, rely=0.5, anchor="w")
    
    def set_progress(self, progress, color=None):
        """Actualiza el progreso"""
        self.progress = min(100, max(0, progress))
        if color:
            self.color = color
        
        self.fill_frame.config(bg=self.color)
        self.fill_frame.place(relwidth=max(0.01, self.progress/100), relheight=1)
        self.label.config(text=f"{self.progress:.1f}%")


class DialogWindow(tk.Toplevel):
    """Ventana de diálogo mejorada con mejor estilo"""
    
    def __init__(self, parent, title, width=480, height=400, **kwargs):
        super().__init__(parent, **kwargs)
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.configure(bg=C['bg'])
        self.grab_set()
        self.resizable(True, True)
        self.minsize(420, 360)
        self.result = None
        
        # Centrar en pantalla
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"+{x}+{y}")
        
        # Encabezado con fondo tintado
        self.header = frame(self, bg=C['bg'])
        self.header.pack(fill="x", padx=24, pady=(20, 12))
        
        # Separador visual para encabezado
        sep = tk.Frame(self, bg=C['accent'], height=3)
        sep.pack(fill="x", pady=(0, 0))
        
        # Contenido con scroll
        self.content_host = frame(self, bg=C['bg'])
        self.content_host.pack(fill="both", expand=True, padx=24, pady=16)

        self.content_canvas = tk.Canvas(
            self.content_host,
            bg=C['bg'],
            highlightthickness=0,
            bd=0,
        )
        self.content_scroll = ttk.Scrollbar(
            self.content_host,
            orient="vertical",
            command=self.content_canvas.yview,
        )
        self.content_canvas.configure(yscrollcommand=self.content_scroll.set)

        self.content = frame(self.content_canvas, bg=C['bg'])
        self.content_window = self.content_canvas.create_window(
            (0, 0), window=self.content, anchor="nw"
        )

        self.content_canvas.pack(side="left", fill="both", expand=True)
        self.content_scroll.pack(side="right", fill="y")

        self.content.bind(
            "<Configure>",
            lambda e: self.content_canvas.configure(scrollregion=self.content_canvas.bbox("all"))
        )
        self.content_canvas.bind(
            "<Configure>",
            lambda e: self.content_canvas.itemconfigure(self.content_window, width=e.width)
        )
        
        # Separador antes del footer
        sep2 = tk.Frame(self, bg=C['border'], height=1)
        sep2.pack(fill="x", pady=(0, 0))
        
        # Pie
        self.footer = frame(self, bg=C['bg'])
        self.footer.pack(fill="x", padx=24, pady=16)


class NotificationBanner(tk.Frame):
    """Banner de notificación"""
    
    TYPES = {
        'info': {'bg': '#1E40AF', 'fg': '#93C5FD', 'icon': 'ℹ️'},
        'success': {'bg': '#065F46', 'fg': '#86EFAC', 'icon': '✅'},
        'warning': {'bg': '#7C2D12', 'fg': '#FED7AA', 'icon': '⚠️'},
        'error': {'bg': '#7F1D1D', 'fg': '#FCA5A5', 'icon': '❌'},
    }
    
    def __init__(self, parent, message, type='info', **kwargs):
        type_config = self.TYPES.get(type, self.TYPES['info'])
        
        super().__init__(
            parent, bg=type_config['bg'],
            highlightthickness=1, highlightbackground=type_config['fg'],
            **kwargs
        )
        
        content = frame(self, bg=type_config['bg'])
        content.pack(fill="x", padx=16, pady=10)
        
        label(
            content, f"{type_config['icon']}  {message}",
            font=F['sm_b'], bg=type_config['bg'],
            fg=type_config['fg']
        ).pack(anchor="w")
