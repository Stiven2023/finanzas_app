"""
Gestión de base de datos - Sistema de Finanzas
Soporta múltiples usuarios, metas y monedas
"""
import sqlite3
import logging
from pathlib import Path
from config import DB_PATH

logger = logging.getLogger(__name__)

class Database:
    """Gestor de base de datos SQLite"""
    
    def __init__(self, db_path=DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()
    
    def get_connection(self):
        """Obtiene conexión a la BD"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Inicializa esquema de base de datos"""
        conn = self.get_connection()
        c = conn.cursor()
        
        # Tabla de usuarios
        c.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE,
            currency TEXT DEFAULT 'COP',
            language TEXT DEFAULT 'es',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        
        # Tabla de configuración por usuario
        c.execute("""CREATE TABLE IF NOT EXISTS user_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            setting_key TEXT NOT NULL,
            setting_value TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, setting_key)
        )""")
        
        # Tabla de deudas mejorada
        c.execute("""CREATE TABLE IF NOT EXISTS debts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            creditor TEXT NOT NULL,
            balance REAL DEFAULT 0,
            original_balance REAL DEFAULT 0,
            monthly_payment REAL DEFAULT 0,
            payment_date TEXT,
            status TEXT DEFAULT 'active',
            priority INTEGER DEFAULT 5,
            priority_label TEXT DEFAULT 'Media',
            category TEXT DEFAULT 'personal',
            interest_rate REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )""")
        
        # Tabla de metas globales (no solo carro)
        c.execute("""CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            target_amount REAL NOT NULL,
            current_amount REAL DEFAULT 0,
            currency TEXT DEFAULT 'COP',
            target_date TEXT,
            category TEXT DEFAULT 'general',
            icon TEXT DEFAULT '🎯',
            color TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )""")
        
        # Tabla de semanas mejorada
        c.execute("""CREATE TABLE IF NOT EXISTS weeks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            week_number INTEGER NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            income REAL DEFAULT 0,
            fixed_expenses REAL DEFAULT 0,
            debt_payments REAL DEFAULT 0,
            extra_expenses REAL DEFAULT 0,
            savings REAL DEFAULT 0,
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )""")
        
        # Tabla de transacciones detalladas
        c.execute("""CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            currency TEXT DEFAULT 'COP',
            type TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL,
            week_id INTEGER,
            goal_id INTEGER,
            debt_id INTEGER,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (week_id) REFERENCES weeks(id),
            FOREIGN KEY (goal_id) REFERENCES goals(id),
            FOREIGN KEY (debt_id) REFERENCES debts(id)
        )""")
        
        # Tabla de alertas y notificaciones
        c.execute("""CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            message TEXT,
            is_read BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )""")
        
        # Tabla de tasas de cambio
        c.execute("""CREATE TABLE IF NOT EXISTS exchange_rates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_currency TEXT NOT NULL,
            to_currency TEXT NOT NULL,
            rate REAL NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(from_currency, to_currency)
        )""")
        
        # Crear índices para mejor rendimiento
        c.execute("""CREATE INDEX IF NOT EXISTS idx_debts_user ON debts(user_id)""")
        c.execute("""CREATE INDEX IF NOT EXISTS idx_goals_user ON goals(user_id)""")
        c.execute("""CREATE INDEX IF NOT EXISTS idx_weeks_user ON weeks(user_id)""")
        c.execute("""CREATE INDEX IF NOT EXISTS idx_transactions_user ON transactions(user_id)""")
        c.execute("""CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id)""")
        
        conn.commit()
        conn.close()
        logger.info("Base de datos inicializada correctamente")
    
    def execute_query(self, query, params=None):
        """Ejecuta una consulta SELECT"""
        try:
            conn = self.get_connection()
            c = conn.cursor()
            if params:
                c.execute(query, params)
            else:
                c.execute(query)
            result = c.fetchall()
            conn.close()
            return result
        except Exception as e:
            logger.error(f"Error ejecutando consulta: {e}")
            return []
    
    def execute_insert(self, query, params):
        """Ejecuta una inserción y retorna el ID"""
        try:
            conn = self.get_connection()
            c = conn.cursor()
            c.execute(query, params)
            conn.commit()
            last_id = c.lastrowid
            conn.close()
            return last_id
        except Exception as e:
            logger.error(f"Error en inserción: {e}")
            return None
    
    def execute_update(self, query, params):
        """Ejecuta una actualización"""
        try:
            conn = self.get_connection()
            c = conn.cursor()
            c.execute(query, params)
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error en actualización: {e}")
            return False
    
    def execute_delete(self, query, params):
        """Ejecuta un borrado"""
        return self.execute_update(query, params)

# Instancia global
db = Database()
