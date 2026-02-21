"""
Gestión de base de datos - Sistema de Finanzas
Soporta SQLite (default) y PostgreSQL (Docker) vía variables de entorno.
"""

import logging
import os
import sqlite3
from pathlib import Path

from config import DB_PATH

logger = logging.getLogger(__name__)

try:
    import psycopg2
except ImportError:
    psycopg2 = None


class Database:
    """Gestor de base de datos multi-motor."""

    def __init__(self, db_path=DB_PATH):
        self.engine = os.getenv("DB_ENGINE", "sqlite").lower().strip()
        self.db_path = Path(db_path)

        self.pg_host = os.getenv("DB_HOST", "postgres")
        self.pg_port = int(os.getenv("DB_PORT", "5432"))
        self.pg_name = os.getenv("DB_NAME", "flujo")
        self.pg_user = os.getenv("DB_USER", "flujo")
        self.pg_password = os.getenv("DB_PASSWORD", "flujo123")

        if self.engine == "sqlite":
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.init_db()

    def _is_postgres(self) -> bool:
        return self.engine == "postgres"

    def _adapt_query(self, query: str) -> str:
        if self._is_postgres():
            return query.replace("?", "%s")
        return query

    def _ensure_returning_id(self, query: str) -> str:
        q = query.strip()
        lower = q.lower()
        if self._is_postgres() and lower.startswith("insert") and "returning" not in lower:
            return f"{q} RETURNING id"
        return q

    def get_connection(self):
        """Obtiene conexión a la BD."""
        if self._is_postgres():
            if psycopg2 is None:
                raise RuntimeError("psycopg2 no está instalado para usar PostgreSQL")
            return psycopg2.connect(
                host=self.pg_host,
                port=self.pg_port,
                dbname=self.pg_name,
                user=self.pg_user,
                password=self.pg_password,
                connect_timeout=10,
            )

        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Inicializa esquema de base de datos."""
        conn = self.get_connection()
        c = conn.cursor()

        schema_statements = self._postgres_schema() if self._is_postgres() else self._sqlite_schema()

        for statement in schema_statements:
            c.execute(statement)

        conn.commit()
        conn.close()
        logger.info("Base de datos inicializada correctamente (%s)", self.engine)

    def _sqlite_schema(self):
        return [
            """CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE,
                currency TEXT DEFAULT 'COP',
                language TEXT DEFAULT 'es',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS user_passwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_changed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )""",
            """CREATE TABLE IF NOT EXISTS user_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                setting_key TEXT NOT NULL,
                setting_value TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id, setting_key)
            )""",
            """CREATE TABLE IF NOT EXISTS debts (
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
            )""",
            """CREATE TABLE IF NOT EXISTS goals (
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
            )""",
            """CREATE TABLE IF NOT EXISTS weeks (
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
            )""",
            """CREATE TABLE IF NOT EXISTS transactions (
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
            )""",
            """CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT,
                is_read BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )""",
            """CREATE TABLE IF NOT EXISTS exchange_rates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_currency TEXT NOT NULL,
                to_currency TEXT NOT NULL,
                rate REAL NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(from_currency, to_currency)
            )""",
            "CREATE INDEX IF NOT EXISTS idx_debts_user ON debts(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_goals_user ON goals(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_weeks_user ON weeks(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_transactions_user ON transactions(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id)",
        ]

    def _postgres_schema(self):
        return [
            """CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE,
                currency TEXT DEFAULT 'COP',
                language TEXT DEFAULT 'es',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS user_passwords (
                id SERIAL PRIMARY KEY,
                user_id INTEGER UNIQUE NOT NULL REFERENCES users(id),
                password_hash TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_changed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS user_settings (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                setting_key TEXT NOT NULL,
                setting_value TEXT,
                UNIQUE(user_id, setting_key)
            )""",
            """CREATE TABLE IF NOT EXISTS debts (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                creditor TEXT NOT NULL,
                balance DOUBLE PRECISION DEFAULT 0,
                original_balance DOUBLE PRECISION DEFAULT 0,
                monthly_payment DOUBLE PRECISION DEFAULT 0,
                payment_date TEXT,
                status TEXT DEFAULT 'active',
                priority INTEGER DEFAULT 5,
                priority_label TEXT DEFAULT 'Media',
                category TEXT DEFAULT 'personal',
                interest_rate DOUBLE PRECISION DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS goals (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                name TEXT NOT NULL,
                description TEXT,
                target_amount DOUBLE PRECISION NOT NULL,
                current_amount DOUBLE PRECISION DEFAULT 0,
                currency TEXT DEFAULT 'COP',
                target_date TEXT,
                category TEXT DEFAULT 'general',
                icon TEXT DEFAULT '🎯',
                color TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS weeks (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                week_number INTEGER NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                income DOUBLE PRECISION DEFAULT 0,
                fixed_expenses DOUBLE PRECISION DEFAULT 0,
                debt_payments DOUBLE PRECISION DEFAULT 0,
                extra_expenses DOUBLE PRECISION DEFAULT 0,
                savings DOUBLE PRECISION DEFAULT 0,
                notes TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS transactions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                amount DOUBLE PRECISION NOT NULL,
                currency TEXT DEFAULT 'COP',
                type TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                date TEXT NOT NULL,
                week_id INTEGER REFERENCES weeks(id),
                goal_id INTEGER REFERENCES goals(id),
                debt_id INTEGER REFERENCES debts(id),
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS notifications (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                type TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT,
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS exchange_rates (
                id SERIAL PRIMARY KEY,
                from_currency TEXT NOT NULL,
                to_currency TEXT NOT NULL,
                rate DOUBLE PRECISION NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(from_currency, to_currency)
            )""",
            "CREATE INDEX IF NOT EXISTS idx_debts_user ON debts(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_goals_user ON goals(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_weeks_user ON weeks(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_transactions_user ON transactions(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id)",
        ]

    def execute_query(self, query, params=None):
        """Ejecuta una consulta SELECT."""
        try:
            conn = self.get_connection()
            c = conn.cursor()
            query = self._adapt_query(query)
            c.execute(query, params or ())
            result = c.fetchall()
            conn.close()
            return result
        except Exception as e:
            logger.error(f"Error ejecutando consulta: {e}")
            return []

    def execute_insert(self, query, params):
        """Ejecuta una inserción y retorna el ID."""
        try:
            conn = self.get_connection()
            c = conn.cursor()
            query = self._adapt_query(self._ensure_returning_id(query))
            c.execute(query, params)
            if self._is_postgres():
                last_id = c.fetchone()[0]
            else:
                last_id = c.lastrowid
            conn.commit()
            conn.close()
            return last_id
        except Exception as e:
            logger.error(f"Error en inserción: {e}")
            return None

    def execute_update(self, query, params):
        """Ejecuta una actualización."""
        try:
            conn = self.get_connection()
            c = conn.cursor()
            query = self._adapt_query(query)
            c.execute(query, params)
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error en actualización: {e}")
            return False

    def execute_delete(self, query, params):
        """Ejecuta un borrado."""
        return self.execute_update(query, params)


# Instancia global

db = Database()
