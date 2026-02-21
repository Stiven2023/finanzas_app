from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QHBoxLayout,
)

from src.services.auth_service import AuthService


class LoginWidget(QWidget):
    login_success = Signal(object)

    def __init__(self):
        super().__init__()
        self.is_register_mode = False
        self._build_ui()
        self._load_remembered()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(12)

        title = QLabel("Flujo · Inicia Sesión")
        title.setObjectName("title")
        layout.addWidget(title)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Nombre de usuario")
        layout.addWidget(self.username)

        pwd_row = QHBoxLayout()
        self.password = QLineEdit()
        self.password.setPlaceholderText("Contraseña")
        self.password.setEchoMode(QLineEdit.Password)
        pwd_row.addWidget(self.password)

        self.toggle_pwd_btn = QPushButton("👁")
        self.toggle_pwd_btn.setFixedWidth(42)
        self.toggle_pwd_btn.clicked.connect(self._toggle_password)
        pwd_row.addWidget(self.toggle_pwd_btn)
        layout.addLayout(pwd_row)

        self.confirm_password = QLineEdit()
        self.confirm_password.setPlaceholderText("Confirmar contraseña")
        self.confirm_password.setEchoMode(QLineEdit.Password)
        self.confirm_password.hide()
        layout.addWidget(self.confirm_password)

        self.email = QLineEdit()
        self.email.setPlaceholderText("Email (opcional)")
        self.email.hide()
        layout.addWidget(self.email)

        self.remember = QCheckBox("Recordar contraseña")
        layout.addWidget(self.remember)

        self.error = QLabel("")
        self.error.setObjectName("error")
        layout.addWidget(self.error)

        action_row = QHBoxLayout()
        self.submit_btn = QPushButton("Entrar")
        self.submit_btn.clicked.connect(self._submit)
        action_row.addWidget(self.submit_btn)

        self.toggle_mode_btn = QPushButton("Crear cuenta")
        self.toggle_mode_btn.clicked.connect(self._toggle_mode)
        action_row.addWidget(self.toggle_mode_btn)
        layout.addLayout(action_row)

        self.setStyleSheet(
            """
            QWidget { background:#0b1220; color:#e5e7eb; font-size:14px; }
            QLabel#title { font-size:24px; font-weight:700; color:#f9fafb; }
            QLineEdit { background:#111827; border:1px solid #334155; border-radius:8px; padding:10px; }
            QLineEdit:focus { border:1px solid #00C896; }
            QPushButton { background:#00C896; color:#ffffff; border:none; border-radius:8px; padding:10px; font-weight:600; }
            QPushButton:hover { background:#02b187; }
            QLabel#error { color:#f87171; }
            QCheckBox { color:#cbd5e1; }
            """
        )

        self.username.returnPressed.connect(self._submit)
        self.password.returnPressed.connect(self._submit)
        self.confirm_password.returnPressed.connect(self._submit)

    def _toggle_password(self):
        is_hidden = self.password.echoMode() == QLineEdit.Password
        self.password.setEchoMode(QLineEdit.Normal if is_hidden else QLineEdit.Password)
        self.toggle_pwd_btn.setText("🙈" if is_hidden else "👁")

    def _toggle_mode(self):
        self.is_register_mode = not self.is_register_mode

        if self.is_register_mode:
            self.submit_btn.setText("Registrarse")
            self.toggle_mode_btn.setText("Volver a login")
            self.confirm_password.show()
            self.email.show()
        else:
            self.submit_btn.setText("Entrar")
            self.toggle_mode_btn.setText("Crear cuenta")
            self.confirm_password.hide()
            self.email.hide()

        self.error.setText("")

    def _load_remembered(self):
        username, password = AuthService.get_remembered_credentials()
        if username:
            self.username.setText(username)
            self.remember.setChecked(True)
        if password:
            self.password.setText(password)

    def _submit(self):
        username = self.username.text().strip()
        password = self.password.text()

        if not username or not password:
            self.error.setText("Completa usuario y contraseña")
            return

        if self.is_register_mode:
            confirm = self.confirm_password.text()
            email = self.email.text().strip() or None

            if password != confirm:
                self.error.setText("Las contraseñas no coinciden")
                return

            ok, message = AuthService.validate_password_strength(password)
            if not ok:
                self.error.setText(message)
                return

            user_id = AuthService.register_user(username, password, email)
            if not user_id:
                self.error.setText("No se pudo registrar. Usuario o email ya existe")
                return

        user = AuthService.login(username, password)
        if not user:
            self.error.setText("Usuario o contraseña incorrectos")
            return

        if self.remember.isChecked():
            AuthService.remember_credentials(username, password)
        else:
            AuthService.clear_remembered_credentials()

        self.login_success.emit(user)
