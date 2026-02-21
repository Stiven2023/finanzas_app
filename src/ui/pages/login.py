"""
Página de Login y Registro
"""
import tkinter as tk
from tkinter import messagebox
from src.ui.components import frame, label, button, entry, separator
from src.ui.theme import DEFAULT_COLORS as C, DEFAULT_FONTS as F
from src.services.auth_service import AuthService

class LoginPage(tk.Frame):
    """Página de login y registro"""
    
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg=C['bg'], **kwargs)
        self.app = app
        self.current_mode = "login"  # login o register
        self.show_password = False
        self.show_confirm_password = False
        self.remember_var = tk.BooleanVar(value=False)
        self._build()
    
    def _build(self):
        """Construye la página"""
        # Centro
        center_frame = frame(self, bg=C['bg'])
        center_frame.pack(expand=True)
        
        # Logo y branding
        logo_frame = frame(center_frame, bg=C['bg'])
        logo_frame.pack(pady=(0, 40))
        
        label(logo_frame, "🌊", font=("Segoe UI", 60), bg=C['bg'],
              fg=C['accent']).pack()
        label(logo_frame, "Flujo", font=("Segoe UI", 32, "bold"),
              bg=C['bg'], fg=C['text']).pack(pady=(10, 0))
        label(logo_frame, "Gestor Financiero Profesional", font=F['sm'],
              bg=C['bg'], fg=C['text2']).pack()
        
        separator(center_frame, C['border']).pack(fill="x", pady=20, padx=40)
        
        # Tarjeta de login
        card_frame = tk.Frame(center_frame, bg=C['card'], padx=40, pady=40)
        card_frame.pack(fill="both", padx=40, pady=(0, 40))
        card_frame.config(highlightthickness=1, highlightbackground=C['border'])
        
        self.title_label = label(card_frame, "Inicia Sesión", font=("Segoe UI", 20, "bold"),
                                 bg=C['card'], fg=C['text'])
        self.title_label.pack(pady=(0, 20))
        
        # Usuario
        label(card_frame, "Nombre de usuario", font=F['sm_b'],
              bg=C['card'], fg=C['text']).pack(anchor="w")
        self.username_entry = entry(card_frame, width=40)
        self.username_entry.pack(fill="x", pady=(4, 16), ipady=8)
        
        # Contraseña
        label(card_frame, "Contraseña", font=F['sm_b'],
              bg=C['card'], fg=C['text']).pack(anchor="w")
        self.password_wrap = frame(card_frame, bg=C['card'])
        self.password_wrap.pack(fill="x", pady=(4, 16))
        self.password_entry = entry(self.password_wrap, width=40)
        self.password_entry.pack(side="left", fill="x", expand=True, ipady=8)
        self.password_entry.config(show="●")
        self.toggle_password_btn = button(
            self.password_wrap,
            "👁",
            self._toggle_password_visibility,
            bg=C['card2'],
            font=F['sm_b'],
            pad=(10, 6)
        )
        self.toggle_password_btn.pack(side="left", padx=(8, 0))
        
        # Campo de confirmar contraseña (solo registro)
        self.confirm_pwd_label = label(card_frame, "Confirmar contraseña", font=F['sm_b'],
                                       bg=C['card'], fg=C['text'])
        self.confirm_pwd_wrap = frame(card_frame, bg=C['card'])
        self.confirm_pwd_entry = entry(self.confirm_pwd_wrap, width=40)
        self.confirm_pwd_entry.pack(side="left", fill="x", expand=True, ipady=8)
        self.confirm_pwd_entry.config(show="●")
        self.toggle_confirm_btn = button(
            self.confirm_pwd_wrap,
            "👁",
            self._toggle_confirm_visibility,
            bg=C['card2'],
            font=F['sm_b'],
            pad=(10, 6)
        )
        self.toggle_confirm_btn.pack(side="left", padx=(8, 0))
        
        # Email (solo registro)
        self.email_label = label(card_frame, "Email (opcional)", font=F['sm_b'],
                                 bg=C['card'], fg=C['text'])
        self.email_entry = entry(card_frame, width=40)

        remember_frame = frame(card_frame, bg=C['card'])
        remember_frame.pack(fill="x", pady=(0, 12))
        self.remember_check = tk.Checkbutton(
            remember_frame,
            text="Recordar contraseña",
            variable=self.remember_var,
            bg=C['card'],
            fg=C['text2'],
            selectcolor=C['card2'],
            activebackground=C['card'],
            activeforeground=C['text'],
            font=F['sm'],
            cursor="hand2",
        )
        self.remember_check.pack(anchor="w")
        
        # Botones
        button_frame = frame(card_frame, bg=C['card'])
        button_frame.pack(fill="x", pady=(8, 14))
        
        self.login_btn = button(button_frame, "Entrar", self._on_login,
                               bg=C['accent'], font=F['base_b'])
        self.login_btn.pack(side="left", padx=(0, 10), fill="x", expand=True, ipady=6)
        
        self.toggle_btn = button(button_frame, "Crear Cuenta", self._toggle_mode,
                                bg=C['accent2'], font=F['base_b'])
        self.toggle_btn.pack(side="left", fill="x", expand=True, ipady=6)

        self.bind_all("<Return>", lambda e: self._on_login())
        
        # Mensaje de error
        self.error_label = label(card_frame, "", font=F['sm'],
                                bg=C['card'], fg=C['red'])
        self.error_label.pack(pady=(10, 0))
        
        # Versión
        label(self, "Flujo v2.0 | © 2026",
              font=F['sm'], bg=C['bg'],
              fg=C['text2']).pack(side="bottom", pady=10)

        self._load_remembered_credentials()

    def _load_remembered_credentials(self):
        """Precarga credenciales si el usuario eligió recordarlas."""
        username, password = AuthService.get_remembered_credentials()
        if username:
            self.username_entry.delete(0, tk.END)
            self.username_entry.insert(0, username)
            self.remember_var.set(True)
        if password:
            self.password_entry.delete(0, tk.END)
            self.password_entry.insert(0, password)

    def _toggle_password_visibility(self):
        self.show_password = not self.show_password
        self.password_entry.config(show="" if self.show_password else "●")
        self.toggle_password_btn.config(text="🙈" if self.show_password else "👁")

    def _toggle_confirm_visibility(self):
        self.show_confirm_password = not self.show_confirm_password
        self.confirm_pwd_entry.config(show="" if self.show_confirm_password else "●")
        self.toggle_confirm_btn.config(text="🙈" if self.show_confirm_password else "👁")
    
    def _on_login(self):
        """Maneja el login"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            self._show_error("Por favor completa todos los campos")
            return
        
        if self.current_mode == "login":
            user = AuthService.login(username, password)
            if user:
                if self.remember_var.get():
                    AuthService.remember_credentials(username, password)
                else:
                    AuthService.clear_remembered_credentials()
                self.app.on_login_success(user)
            else:
                self._show_error("Usuario o contraseña incorrectos")
        else:
            # Registro
            confirm_pwd = self.confirm_pwd_entry.get()
            email = self.email_entry.get().strip() or None
            
            if password != confirm_pwd:
                self._show_error("Las contraseñas no coinciden")
                return
            
            is_valid, msg = AuthService.validate_password_strength(password)
            if not is_valid:
                self._show_error(msg)
                return
            
            user_id = AuthService.register_user(username, password, email)
            if user_id:
                user = AuthService.login(username, password)
                if user:
                    if self.remember_var.get():
                        AuthService.remember_credentials(username, password)
                    else:
                        AuthService.clear_remembered_credentials()
                    self.app.on_login_success(user)
            else:
                self._show_error("El usuario ya existe o el email está registrado")
    
    def _toggle_mode(self):
        """Alterna entre login y registro"""
        if self.current_mode == "login":
            # Cambiar a registro
            self.current_mode = "register"
            self.title_label.config(text="Crear Cuenta")
            self.login_btn.config(text="Registrarse")
            self.toggle_btn.config(text="Volver a Login")
            
            self.confirm_pwd_label.pack(anchor="w")
            self.confirm_pwd_wrap.pack(fill="x", pady=(4, 16))
            self.email_label.pack(anchor="w")
            self.email_entry.pack(fill="x", pady=(4, 16), ipady=8)
            
            # Limpiar
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            self.confirm_pwd_entry.delete(0, tk.END)
            self.email_entry.delete(0, tk.END)
            self.error_label.config(text="")
        else:
            # Cambiar a login
            self.current_mode = "login"
            self.title_label.config(text="Inicia Sesión")
            self.login_btn.config(text="Iniciar Sesión")
            self.toggle_btn.config(text="Crear Cuenta")
            
            self.confirm_pwd_label.pack_forget()
            self.confirm_pwd_wrap.pack_forget()
            self.email_label.pack_forget()
            self.email_entry.pack_forget()
            
            # Limpiar
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            self.error_label.config(text="")
    
    def _show_error(self, message):
        """Muestra un mensaje de error"""
        self.error_label.config(text=message)
