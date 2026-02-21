"""
Funciones de validación de datos
"""

def validate_email(email):
    """Valida formato de email"""
    import re
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validate_currency(amount):
    """Valida que sea un número válido"""
    try:
        value = float(amount)
        return value >= 0, value
    except (ValueError, TypeError):
        return False, 0

def validate_date(date_str):
    """Valida formato de fecha (YYYY-MM-DD)"""
    try:
        parts = date_str.split('-')
        if len(parts) != 3:
            return False
        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
        return 1900 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31
    except:
        return False

def validate_percentage(value):
    """Valida porcentaje (0-100)"""
    try:
        num = float(value)
        return 0 <= num <= 100, num
    except:
        return False, 0
