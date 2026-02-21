"""
╔══════════════════════════════════════════════════════════╗
║    CONFIGURACIÓN GLOBAL - Finanzas App                   ║
╚══════════════════════════════════════════════════════════╝
"""
import os
import json
from pathlib import Path
from datetime import date

# ── RUTAS ──────────────────────────────────────────────────────────────────
BASE_PATH = Path(__file__).parent
DATA_PATH = BASE_PATH / "data"
DB_PATH = DATA_PATH / "finanzas.db"
CONFIG_FILE = DATA_PATH / "config.json"

# Crear directorio si no existe
DATA_PATH.mkdir(parents=True, exist_ok=True)

# ── COLORES & TEMA (Paleta Flujo) ────────────────────────────────────────────────────
COLORS = {
    "bg":       "#090D12",      # Obsidiana
    "sidebar":  "#111827",      # Tinta
    "card":     "#1C2736",      # Pizarra
    "card2":    "#2E3D50",      # Mist
    "accent":   "#00C896",      # Jade (éxito)
    "accent2":  "#7B61FF",      # Violeta (progreso)
    "teal":     "#00C896",      # Jade
    "red":      "#FF5E57",      # Coral (alertas)
    "orange":   "#FFAA33",      # Ámbar (avisos)
    "green":    "#00C896",      # Jade
    "yellow":   "#FFAA33",      # Ámbar
    "text":     "#EEF3F8",      # Nieve
    "text2":    "#9DB4C8",      # Escarcha
    "border":   "#334155",      # Borde sutil
    "input":    "#111827",      # Tinta
    "white":    "#FFFFFF",      # Blanco puro
    "purple":   "#7B61FF",      # Violeta
}

FONTS = {
    "base":     ("Segoe UI", 11),
    "base_b":   ("Segoe UI", 11, "bold"),
    "lg":       ("Segoe UI", 14, "bold"),
    "lg_b":     ("Segoe UI", 14, "bold"),
    "xl":       ("Segoe UI", 24, "bold"),
    "sm":       ("Segoe UI", 10),
    "sm_b":     ("Segoe UI", 10, "bold"),
}

# ── CONFIGURACIÓN DE APLICACIÓN ────────────────────────────────────────────
APP_NAME = "Flujo"
APP_VERSION = "2.0.0"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 800
MIN_WIDTH = 1100
MIN_HEIGHT = 700

# ── MONEDAS SOPORTADAS ─────────────────────────────────────────────────────
SUPPORTED_CURRENCIES = {
    "USD": {"symbol": "$", "name": "Dólar Estadounidense", "decimals": 2},
    "COP": {"symbol": "$", "name": "Peso Colombiano", "decimals": 0},
    "EUR": {"symbol": "€", "name": "Euro", "decimals": 2},
    "MXN": {"symbol": "$", "name": "Peso Mexicano", "decimals": 2},
}

DEFAULT_CURRENCY = "COP"
DEFAULT_START_DATE = date(2026, 2, 20)
DEFAULT_END_DATE = date(2026, 12, 31)

# ── CONFIGURACIÓN DE USUARIO (Cargada dinámicamente) ───────────────────────
class UserConfig:
    """Gestiona configuración del usuario"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UserConfig, cls).__new__(cls)
            cls._instance.load()
        return cls._instance
    
    def load(self):
        """Carga configuración desde archivo JSON"""
        self.currency = DEFAULT_CURRENCY
        self.language = "es"
        self.theme = "dark"
        self.enable_notifications = True
        self.start_date = DEFAULT_START_DATE
        self.end_date = DEFAULT_END_DATE
        self.remember_me = False
        self.remembered_username = ""
        
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.currency = data.get("currency", DEFAULT_CURRENCY)
                    self.language = data.get("language", "es")
                    self.theme = data.get("theme", "dark")
                    self.enable_notifications = data.get("notifications", True)
                    self.remember_me = data.get("remember_me", False)
                    self.remembered_username = data.get("remembered_username", "")
            except:
                pass
    
    def get(self, key, default=None):
        """Obtiene un valor de configuración"""
        return getattr(self, key, default)
    
    def set(self, key, value):
        """Establece un valor de configuración"""
        setattr(self, key, value)
        self.save()
    
    def save(self):
        """Guarda configuración en archivo JSON"""
        config_data = {
            "currency": self.currency,
            "language": self.language,
            "theme": self.theme,
            "notifications": self.enable_notifications,
            "remember_me": self.remember_me,
            "remembered_username": self.remembered_username,
        }
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error guardando configuración: {e}")

# Crear instancia global
config = UserConfig()
