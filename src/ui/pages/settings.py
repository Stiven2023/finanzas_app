"""
Página de Configuración de la Aplicación
"""
import tkinter as tk
from tkinter import messagebox, ttk
from src.ui.components import frame, label, button, entry, card, separator, DialogWindow, page_header
from src.ui.theme import DEFAULT_COLORS as C, DEFAULT_FONTS as F, THEMES
from src.services.auth_service import AuthService
from config import UserConfig, SUPPORTED_CURRENCIES
from src.database.db import Database
from src.utils.formatters import format_money

class SettingsPage(tk.Frame):
    """Página de configuración de la aplicación"""
    
    LANGUAGES = {
        'es': '🇪🇸 Español',
        'en': '🇬🇧 English',
        'fr': '🇫🇷 Français',
    }
    
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg=C['bg'], **kwargs)
        self.app = app
        self.user_id = app.current_user.id
        self.config = UserConfig()
        self._build()
    
    def _build(self):
        """Construye la página"""
        page_header(self, "⚙️ Configuración")
        
        # Scroll container
        canvas = tk.Canvas(self, bg=C['bg'], highlightthickness=0)
        canvas.pack(fill="both", expand=True, padx=30)
        
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        content = frame(canvas, bg=C['bg'])
        canvas.create_window((0, 0), window=content, anchor="nw")
        
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Secciones
        self._build_user_section(content)
        self._build_preferences_section(content)
        self._build_security_section(content)
        self._build_about_section(content)
    
    def _build_user_section(self, parent):
        """Sección de información de usuario"""
        section = card(parent)
        section.pack(fill="x", pady=(0, 20))
        
        label(section, "👤 Información de Usuario", font=F['lg'], bg=C['card'],
              fg=C['text']).pack(anchor="w", padx=16, pady=(14, 8))
        
        separator(section, C['border']).pack(fill="x", padx=16, pady=(0, 12))
        
        # Usuario
        user_frame = frame(section, bg=C['card'])
        user_frame.pack(fill="x", padx=16, pady=8)
        label(user_frame, "Usuario conectado:", font=F['sm_b'],
              bg=C['card'], fg=C['text2']).pack(anchor="w")
        label(user_frame, f"🎯 {self.app.current_user.username}", font=F['base'],
              bg=C['card'], fg=C['text']).pack(anchor="w", pady=(2, 0))
        
        # Email
        email_frame = frame(section, bg=C['card'])
        email_frame.pack(fill="x", padx=16, pady=8)
        label(email_frame, "Email:", font=F['sm_b'],
              bg=C['card'], fg=C['text2']).pack(anchor="w")
        label(email_frame, self.app.current_user.email or "No registrado", font=F['base'],
              bg=C['card'], fg=C['text']).pack(anchor="w", pady=(2, 0))
        
        # Botón de cerrar sesión
        button(section, "🚪 Cerrar Sesión", self._logout,
               bg=C['red'], pad=(16, 8)).pack(fill="x", padx=16, pady=(0, 14))
    
    def _build_preferences_section(self, parent):
        """Sección de preferencias"""
        section = card(parent)
        section.pack(fill="x", pady=(0, 20))
        
        label(section, "🎨 Preferencias", font=F['lg'], bg=C['card'],
              fg=C['text']).pack(anchor="w", padx=16, pady=(14, 8))
        
        separator(section, C['border']).pack(fill="x", padx=16, pady=(0, 12))
        
        # Moneda
        currency_frame = frame(section, bg=C['card'])
        currency_frame.pack(fill="x", padx=16, pady=8)
        label(currency_frame, "💱 Moneda Predeterminada:", font=F['sm_b'],
              bg=C['card'], fg=C['text2']).pack(anchor="w")
        
        # Dropdown de moneda
        current_currency = self.config.get('currency', 'COP')
        currency_options = [f"{curr} - {SUPPORTED_CURRENCIES.get(curr, '')}" for curr in SUPPORTED_CURRENCIES.keys()]
        
        coin_dropdown = ttk.Combobox(currency_frame, values=currency_options, state="readonly", width=40)
        coin_dropdown.set(f"{current_currency} - {SUPPORTED_CURRENCIES.get(current_currency, '')}")
        coin_dropdown.pack(fill="x", pady=(2, 0), ipady=6)
        
        def save_currency():
            selected = coin_dropdown.get().split(" - ")[0]
            self.config.set('currency', selected)
            messagebox.showinfo("Éxito", f"Moneda establecida como {selected}")
        
        button(currency_frame, "💾 Guardar Moneda", save_currency,
               bg=C['teal'], pad=(8, 4)).pack(fill="x", pady=(6, 0))
        
        # Idioma
        language_frame = frame(section, bg=C['card'])
        language_frame.pack(fill="x", padx=16, pady=8)
        label(language_frame, "🌐 Idioma:", font=F['sm_b'],
              bg=C['card'], fg=C['text2']).pack(anchor="w")
        
        current_lang = self.config.get('language', 'es')
        lang_options = list(self.LANGUAGES.values())
        
        lang_dropdown = ttk.Combobox(language_frame, values=lang_options, state="readonly", width=40)
        lang_dropdown.set(self.LANGUAGES.get(current_lang, 'Español'))
        lang_dropdown.pack(fill="x", pady=(2, 0), ipady=6)
        
        def save_language():
            selected_lang = next((k for k, v in self.LANGUAGES.items() if v == lang_dropdown.get()), 'es')
            self.config.set('language', selected_lang)
            messagebox.showinfo("Éxito", f"Idioma establecido correctamente")
        
        button(language_frame, "💾 Guardar Idioma", save_language,
               bg=C['teal'], pad=(8, 4)).pack(fill="x", pady=(6, 0))
        
        # Tema
        theme_frame = frame(section, bg=C['card'])
        theme_frame.pack(fill="x", padx=16, pady=(8, 14))
        label(theme_frame, "🌙 Tema:", font=F['sm_b'],
              bg=C['card'], fg=C['text2']).pack(anchor="w")
        
        current_theme = self.config.get('theme', 'dark')
        theme_options = ['🌙 Oscuro', '☀️ Claro']
        
        theme_dropdown = ttk.Combobox(theme_frame, values=theme_options, state="readonly", width=40)
        theme_dropdown.set('🌙 Oscuro' if current_theme == 'dark' else '☀️ Claro')
        theme_dropdown.pack(fill="x", pady=(2, 0), ipady=6)
        
        def save_theme():
            selected_theme = 'dark' if '🌙' in theme_dropdown.get() else 'light'
            self.config.set('theme', selected_theme)
            messagebox.showinfo("Éxito", "Tema establecido correctamente\n(Se aplicará en próxima ejecución)")
        
        button(theme_frame, "💾 Guardar Tema", save_theme,
               bg=C['teal'], pad=(8, 4)).pack(fill="x", pady=(6, 0))
    
    def _build_security_section(self, parent):
        """Sección de seguridad"""
        section = card(parent)
        section.pack(fill="x", pady=(0, 20))
        
        label(section, "🔐 Seguridad", font=F['lg'], bg=C['card'],
              fg=C['text']).pack(anchor="w", padx=16, pady=(14, 8))
        
        separator(section, C['border']).pack(fill="x", padx=16, pady=(0, 12))
        
        # Cambiar contraseña
        pwd_frame = frame(section, bg=C['card'])
        pwd_frame.pack(fill="x", padx=16, pady=8)
        label(pwd_frame, "🔑 Cambiar Contraseña:", font=F['sm_b'],
              bg=C['card'], fg=C['text2']).pack(anchor="w")
        
        button(pwd_frame, "Cambiar Contraseña", self._show_change_password_dialog,
               bg=C['accent'], pad=(8, 4)).pack(fill="x", pady=(6, 0))
        
        # Información de seguridad
        info_frame = frame(section, bg=C['card2'])
        info_frame.pack(fill="x", padx=16, pady=(0, 14), ipady=8)
        
        label(info_frame, "✅ Contraseña encriptada con PBKDF2-SHA256", font=F['sm'],
              bg=C['card2'], fg=C['green']).pack(anchor="w")
        label(info_frame, "✅ 100,000 iteraciones de hash", font=F['sm'],
              bg=C['card2'], fg=C['green']).pack(anchor="w")
        label(info_frame, "✅ Salt aleatorio de 32 bytes", font=F['sm'],
              bg=C['card2'], fg=C['green']).pack(anchor="w")
    
    def _build_about_section(self, parent):
        """Sección de información"""
        section = card(parent)
        section.pack(fill="x", pady=(0, 20))
        
        label(section, "ℹ️ Acerca de Flujo", font=F['lg'], bg=C['card'],
              fg=C['text']).pack(anchor="w", padx=16, pady=(14, 8))
        
        separator(section, C['border']).pack(fill="x", padx=16, pady=(0, 12))
        
        info_text = """Flujo - Gestor Financiero Inteligente
Versión 2.0.0

Una aplicación moderna para gestionar tus deudas, metas y finanzas personales con múltiples monedas y análisis detallados.

Características:
• 💳 Gestión de deudas con categorías
• 🎯 Metas financieras flexibles
• 💱 Soporte para 4 monedas (COP, USD, EUR, MXN)
• 📊 Reportes y análisis detallados
• 👥 Multi-usuario con autenticación segura
• 🔐 Contraseñas encriptadas con PBKDF2-SHA256

© 2026 Flujo - Todos los derechos reservados
Desarrollado con ❤️ en Python"""
        
        label(section, info_text, font=F['sm'], bg=C['card'],
              fg=C['text2'], justify="left").pack(anchor="w", padx=16, pady=12)
    
    def _show_change_password_dialog(self):
        """Muestra diálogo para cambiar contraseña"""
        win = DialogWindow(parent=self, title="Cambiar Contraseña", width=450, height=350)
        
        label(win.header, "🔑 Cambiar Contraseña", font=F['lg'], bg=C['bg'],
              fg=C['text']).pack(anchor="w")
        separator(win.header, C['border']).pack(fill="x", pady=(8, 0))
        
        # Contraseña actual
        f1 = frame(win.content, bg=C['bg'])
        f1.pack(fill="x", pady=8)
        label(f1, "Contraseña Actual:", font=F['sm_b'], bg=C['bg'],
              fg=C['text2']).pack(anchor="w")
        old_wrap = frame(f1, bg=C['bg'])
        old_wrap.pack(fill="x", pady=(2, 0))
        old_pwd = tk.Entry(old_wrap, font=F['base'], bg=C['input'], fg=C['text'],
                           show='•', width=45)
        old_pwd.pack(side="left", fill="x", expand=True, ipady=6)
        old_visible = {'value': False}

        def toggle_old_pwd():
            old_visible['value'] = not old_visible['value']
            old_pwd.config(show='' if old_visible['value'] else '•')
            old_eye_btn.config(text='🙈' if old_visible['value'] else '👁')

        old_eye_btn = button(old_wrap, '👁', toggle_old_pwd, bg=C['card2'], font=F['sm_b'], pad=(10, 6))
        old_eye_btn.pack(side="left", padx=(8, 0))
        
        # Nueva contraseña
        f2 = frame(win.content, bg=C['bg'])
        f2.pack(fill="x", pady=8)
        label(f2, "Nueva Contraseña:", font=F['sm_b'], bg=C['bg'],
              fg=C['text2']).pack(anchor="w")
        new_wrap = frame(f2, bg=C['bg'])
        new_wrap.pack(fill="x", pady=(2, 0))
        new_pwd = tk.Entry(new_wrap, font=F['base'], bg=C['input'], fg=C['text'],
                           show='•', width=45)
        new_pwd.pack(side="left", fill="x", expand=True, ipady=6)
        new_visible = {'value': False}

        def toggle_new_pwd():
            new_visible['value'] = not new_visible['value']
            new_pwd.config(show='' if new_visible['value'] else '•')
            new_eye_btn.config(text='🙈' if new_visible['value'] else '👁')

        new_eye_btn = button(new_wrap, '👁', toggle_new_pwd, bg=C['card2'], font=F['sm_b'], pad=(10, 6))
        new_eye_btn.pack(side="left", padx=(8, 0))
        
        # Confirmar nueva
        f3 = frame(win.content, bg=C['bg'])
        f3.pack(fill="x", pady=8)
        label(f3, "Confirmar Nueva Contraseña:", font=F['sm_b'], bg=C['bg'],
              fg=C['text2']).pack(anchor="w")
        confirm_wrap = frame(f3, bg=C['bg'])
        confirm_wrap.pack(fill="x", pady=(2, 0))
        confirm_pwd = tk.Entry(confirm_wrap, font=F['base'], bg=C['input'], fg=C['text'],
                               show='•', width=45)
        confirm_pwd.pack(side="left", fill="x", expand=True, ipady=6)
        confirm_visible = {'value': False}

        def toggle_confirm_pwd():
            confirm_visible['value'] = not confirm_visible['value']
            confirm_pwd.config(show='' if confirm_visible['value'] else '•')
            confirm_eye_btn.config(text='🙈' if confirm_visible['value'] else '👁')

        confirm_eye_btn = button(confirm_wrap, '👁', toggle_confirm_pwd, bg=C['card2'], font=F['sm_b'], pad=(10, 6))
        confirm_eye_btn.pack(side="left", padx=(8, 0))
        
        # Info
        info_frame = frame(win.content, bg=C['card2'])
        info_frame.pack(fill="x", pady=16, padx=0, ipady=8)
        label(info_frame, "Requisitos de contraseña:", font=F['sm_b'], bg=C['card2'],
              fg=C['text2']).pack(anchor="w", padx=8)
        label(info_frame, "• Mínimo 6 caracteres", font=F['sm'], bg=C['card2'],
              fg=C['text2']).pack(anchor="w", padx=8)
        label(info_frame, "• Incluir mayúsculas y minúsculas", font=F['sm'], bg=C['card2'],
              fg=C['text2']).pack(anchor="w", padx=8)
        label(info_frame, "• Incluir al menos un número", font=F['sm'], bg=C['card2'],
              fg=C['text2']).pack(anchor="w", padx=8)
        
        def save_password():
            old = old_pwd.get()
            new = new_pwd.get()
            confirm = confirm_pwd.get()
            
            if not old or not new or not confirm:
                messagebox.showwarning("Error", "Completa todos los campos")
                return
            
            if new != confirm:
                messagebox.showwarning("Error", "Las nuevas contraseñas no coinciden")
                return
            
            is_valid, message = AuthService.validate_password_strength(new)
            if not is_valid:
                messagebox.showwarning("Error", message)
                return
            
            try:
                AuthService.change_password(self.user_id, old, new)
                win.destroy()
                messagebox.showinfo("Éxito", "Contraseña cambiada correctamente")
            except ValueError as e:
                messagebox.showerror("Error", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"Error al cambiar: {e}")
        
        button(win.footer, "💾 Cambiar Contraseña", save_password,
               bg=C['teal'], pad=(16, 8)).pack(side="left", padx=(0, 10), fill="x", expand=True)
        button(win.footer, "Cancelar", win.destroy,
               bg=C['card2'], pad=(16, 8)).pack(side="left", fill="x", expand=True)
    
    def _logout(self):
        """Cierra sesión"""
        if messagebox.askyesno("Confirmar", "¿Deseas cerrar sesión?"):
            self.app.logout()
