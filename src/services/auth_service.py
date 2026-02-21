"""
Servicio de Autenticación y Seguridad
"""
import hashlib
import secrets
import logging
from typing import Optional
from src.database.db import db
from src.models.user import User
from config import config

try:
    import keyring
except ImportError:
    keyring = None

logger = logging.getLogger(__name__)

class AuthService:
    """Servicio de autenticación y gestión de usuarios"""
    
    SALT_LENGTH = 32  # Longitud del salt en bytes
    HASH_ITERATIONS = 100000  # Iteraciones para PBKDF2
    KEYRING_SERVICE = "FlujoFinanzasApp"
    
    @staticmethod
    def hash_password(password: str, salt: str = None) -> tuple:
        """
        Genera hash de contraseña con salt
        
        Returns:
            (hashed_password, salt)
        """
        if salt is None:
            salt = secrets.token_hex(AuthService.SALT_LENGTH)
        
        # Usar PBKDF2 con SHA-256
        hashed = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            AuthService.HASH_ITERATIONS
        )
        
        return hashed.hex(), salt
    
    @staticmethod
    def verify_password(password: str, hashed: str, salt: str) -> bool:
        """Verifica si una contraseña coincide con el hash"""
        computed, _ = AuthService.hash_password(password, salt)
        return computed == hashed
    
    @staticmethod
    def register_user(username: str, password: str, email: str = None) -> Optional[int]:
        """
        Registra un nuevo usuario
        
        Returns:
            user_id si es exitoso, None si falla
        """
        # Validar que el usuario no exista
        query = "SELECT id FROM users WHERE username = ?"
        results = db.execute_query(query, (username,))
        
        if results:
            logger.warning(f"Intento de registrar usuario existente: {username}")
            return None
        
        # Validar que el email no exista (si se proporciona)
        if email:
            query = "SELECT id FROM users WHERE email = ?"
            results = db.execute_query(query, (email,))
            if results:
                logger.warning(f"Email ya registrado: {email}")
                return None
        
        # Generar hash de contraseña
        hashed_password, salt = AuthService.hash_password(password)
        
        try:
            # Crear tabla de passwords si no existe
            query = """CREATE TABLE IF NOT EXISTS user_passwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_changed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )"""
            conn = db.get_connection()
            c = conn.cursor()
            c.execute(query)
            conn.commit()
            conn.close()
            
            # Crear usuario
            query = """
                INSERT INTO users (username, email, currency, language)
                VALUES (?, ?, 'COP', 'es')
            """
            user_id = db.execute_insert(query, (username, email))
            
            if user_id:
                # Guardar contraseña
                query = """
                    INSERT INTO user_passwords (user_id, password_hash, password_salt)
                    VALUES (?, ?, ?)
                """
                db.execute_insert(query, (user_id, hashed_password, salt))
                logger.info(f"Usuario registrado: {username}")
                return user_id
            
        except Exception as e:
            logger.error(f"Error registrando usuario: {e}")
        
        return None
    
    @staticmethod
    def login(username: str, password: str) -> Optional[User]:
        """
        Autentica un usuario
        
        Returns:
            User object si es exitoso, None si falla
        """
        try:
            # Obtener usuario
            query = "SELECT id, username, email, currency, language FROM users WHERE username = ?"
            results = db.execute_query(query, (username,))
            
            if not results:
                logger.warning(f"Intento de login con usuario inexistente: {username}")
                return None
            
            user_row = results[0]
            user_id = user_row[0]
            
            # Obtener contraseña hash y salt
            query = "SELECT password_hash, password_salt FROM user_passwords WHERE user_id = ?"
            pwd_results = db.execute_query(query, (user_id,))
            
            if not pwd_results:
                logger.warning(f"Usuario sin contraseña configurada: {username}")
                return None
            
            pwd_hash = pwd_results[0][0]
            pwd_salt = pwd_results[0][1]
            
            # Verificar contraseña
            if not AuthService.verify_password(password, pwd_hash, pwd_salt):
                logger.warning(f"Login fallido - contraseña incorrecta: {username}")
                return None
            
            # Crear objeto User
            user = User(
                id=user_row[0],
                username=user_row[1],
                email=user_row[2],
                currency=user_row[3],
                language=user_row[4]
            )
            
            logger.info(f"Login exitoso: {username}")
            return user
            
        except Exception as e:
            logger.error(f"Error en login: {e}")
            return None
    
    @staticmethod
    def change_password(user_id: int, old_password: str, new_password: str) -> bool:
        """Cambia la contraseña de un usuario"""
        try:
            # Obtener usuario
            query = "SELECT username FROM users WHERE id = ?"
            results = db.execute_query(query, (user_id,))
            
            if not results:
                return False
            
            username = results[0][0]
            
            # Verificar contraseña antigua
            query = "SELECT password_hash, password_salt FROM user_passwords WHERE user_id = ?"
            pwd_results = db.execute_query(query, (user_id,))
            
            if not pwd_results:
                return False
            
            pwd_hash = pwd_results[0][0]
            pwd_salt = pwd_results[0][1]
            
            if not AuthService.verify_password(old_password, pwd_hash, pwd_salt):
                logger.warning(f"Cambio de contraseña fallido - contraseña antigua incorrecta: {username}")
                return False
            
            # Generar nueva contraseña
            new_hashed, new_salt = AuthService.hash_password(new_password)
            
            # Actualizar
            query = """
                UPDATE user_passwords
                SET password_hash = ?, password_salt = ?, last_changed = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """
            return db.execute_update(query, (new_hashed, new_salt, user_id))
            
        except Exception as e:
            logger.error(f"Error cambiando contraseña: {e}")
            return False
    
    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, str]:
        """
        Valida la fortaleza de una contraseña
        
        Returns:
            (is_valid, message)
        """
        if len(password) < 6:
            return False, "La contraseña debe tener al menos 6 caracteres"
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        
        if not (has_upper and has_lower and has_digit):
            return False, "La contraseña debe incluir mayúsculas, minúsculas y números"
        
        return True, "Contraseña válida"

    @staticmethod
    def remember_credentials(username: str, password: str) -> bool:
        """Guarda credenciales de forma segura para autocompletar login."""
        try:
            config.set('remember_me', True)
            config.set('remembered_username', username)

            if keyring is not None:
                keyring.set_password(AuthService.KEYRING_SERVICE, username, password)
                return True

            logger.warning("keyring no disponible; solo se recordará el usuario")
            return False
        except Exception as e:
            logger.error(f"No se pudieron guardar credenciales recordadas: {e}")
            return False

    @staticmethod
    def get_remembered_credentials() -> tuple[str, str]:
        """Obtiene credenciales recordadas (username, password)."""
        try:
            if not config.get('remember_me', False):
                return "", ""

            username = config.get('remembered_username', '') or ""
            if not username:
                return "", ""

            if keyring is None:
                return username, ""

            password = keyring.get_password(AuthService.KEYRING_SERVICE, username) or ""
            return username, password
        except Exception as e:
            logger.error(f"No se pudieron recuperar credenciales recordadas: {e}")
            return "", ""

    @staticmethod
    def clear_remembered_credentials() -> bool:
        """Elimina credenciales recordadas."""
        try:
            username = config.get('remembered_username', '') or ""
            config.set('remember_me', False)
            config.set('remembered_username', '')

            if keyring is not None and username:
                try:
                    keyring.delete_password(AuthService.KEYRING_SERVICE, username)
                except Exception:
                    pass

            return True
        except Exception as e:
            logger.error(f"No se pudieron limpiar credenciales recordadas: {e}")
            return False
