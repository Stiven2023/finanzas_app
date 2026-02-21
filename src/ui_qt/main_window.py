from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QStackedWidget,
    QPushButton,
    QHBoxLayout,
)

from src.ui_qt.login_widget import LoginWidget
from src.services.report_service import ReportService


class MainWindowQt(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_user = None
        self.setWindowTitle("Flujo - PySide6")
        self.resize(1200, 760)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()
        root.addWidget(self.stack)

        self.login_page = LoginWidget()
        self.login_page.login_success.connect(self._on_login)
        self.stack.addWidget(self.login_page)

        self.app_shell = QWidget()
        shell_layout = QVBoxLayout(self.app_shell)

        self.header = QLabel("Dashboard")
        self.header.setStyleSheet("font-size:24px; font-weight:700; margin:12px;")
        shell_layout.addWidget(self.header)

        nav = QHBoxLayout()
        self.btn_dashboard = QPushButton("Dashboard")
        self.btn_dashboard.clicked.connect(self._load_dashboard)
        self.btn_logout = QPushButton("Cerrar sesión")
        self.btn_logout.clicked.connect(self._logout)
        nav.addWidget(self.btn_dashboard)
        nav.addStretch(1)
        nav.addWidget(self.btn_logout)
        shell_layout.addLayout(nav)

        self.content = QLabel("Inicia sesión para ver datos")
        self.content.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.content.setStyleSheet("padding:16px; font-size:15px;")
        shell_layout.addWidget(self.content)

        self.app_shell.setStyleSheet(
            "QWidget { background:#0b1220; color:#e5e7eb; }"
            "QPushButton { background:#1f2937; color:#e5e7eb; border:none; border-radius:8px; padding:8px 12px; }"
            "QPushButton:hover { background:#334155; }"
        )

        self.stack.addWidget(self.app_shell)
        self.stack.setCurrentWidget(self.login_page)

    def _on_login(self, user):
        self.current_user = user
        self.stack.setCurrentWidget(self.app_shell)
        self._load_dashboard()

    def _load_dashboard(self):
        summary = ReportService.get_financial_summary(self.current_user.id)
        self.header.setText(f"Dashboard · {self.current_user.username}")
        self.content.setText(
            f"Deuda total: {summary['total_debt']:.2f}\n"
            f"Pagos mensuales: {summary['total_monthly_payments']:.2f}\n"
            f"Deudas activas: {summary['debt_count']}\n"
            f"Metas activas: {summary['goal_count']}"
        )

    def _logout(self):
        self.current_user = None
        self.stack.setCurrentWidget(self.login_page)
