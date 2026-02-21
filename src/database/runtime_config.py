"""Configuración de motor de base de datos en tiempo de ejecución."""

import logging
import os
import socket
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None

logger = logging.getLogger(__name__)


def _can_connect(host: str, port: int, timeout: float = 0.8) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def configure_database_engine() -> str:
    """
    Configura el motor de BD antes de importar `src.database.db`.

    Prioridad:
    1) `DB_ENGINE` explícito por entorno/.env
    2) Autodetección PostgreSQL en localhost:5432
    3) Fallback a SQLite
    """
    root = Path(__file__).resolve().parents[2]
    env_file = root / ".env"

    if load_dotenv is not None and env_file.exists():
        load_dotenv(env_file)

    explicit_engine = (os.getenv("DB_ENGINE") or "").strip().lower()
    if explicit_engine in {"sqlite", "postgres"}:
        logger.info("DB_ENGINE definido explícitamente: %s", explicit_engine)
        return explicit_engine

    host = os.getenv("DB_HOST", "localhost")
    port = int(os.getenv("DB_PORT", "5432"))

    if _can_connect(host, port):
        os.environ["DB_ENGINE"] = "postgres"
        os.environ.setdefault("DB_HOST", host)
        os.environ.setdefault("DB_PORT", str(port))
        os.environ.setdefault("DB_NAME", "flujo")
        os.environ.setdefault("DB_USER", "flujo")
        os.environ.setdefault("DB_PASSWORD", "flujo123")
        logger.info("PostgreSQL detectado en %s:%s. Usando motor postgres.", host, port)
        return "postgres"

    os.environ["DB_ENGINE"] = "sqlite"
    logger.info("PostgreSQL no detectado. Usando SQLite local.")
    return "sqlite"
