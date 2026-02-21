import sys
from PySide6.QtWidgets import QApplication
from src.database.runtime_config import configure_database_engine


def main():
    configure_database_engine()

    from src.database.db import db
    from src.ui_qt.main_window import MainWindowQt

    app = QApplication(sys.argv)
    app.setApplicationName("Flujo")

    window = MainWindowQt()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
