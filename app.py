"""
╔══════════════════════════════════════════════════════════╗
║           FLUJO — Gestor Financiero Personal             ║
║       App de Escritorio Moderno y Escalable v2.0         ║
║       Requiere: Python 3.8+  |  pip install -r req...    ║
╚══════════════════════════════════════════════════════════╝
"""
import logging
import sys
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent))

from src.ui.main_window import MainWindow
from src.database.db import db

def main():
    """Punto de entrada de la aplicación"""
    try:
        logger.info("Iniciando Flujo - Gestor Financiero...")
        
        # Inicializar base de datos
        db.init_db()
        logger.info("Base de datos verificada y lista")
        
        # Crear ventana principal
        app = MainWindow()
        logger.info("Ventana principal creada")
        
        # Ejecutar
        app.mainloop()
        
    except Exception as e:
        logger.error(f"Error fatal: {e}", exc_info=True)
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
