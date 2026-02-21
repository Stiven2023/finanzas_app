"""
Funciones de formato para datos financieros
"""
from config import config, SUPPORTED_CURRENCIES

def format_money(value, currency=None):
    """
    Formatea un número como moneda
    
    Args:
        value: Cantidad a formatear
        currency: Código de moneda (USD, COP, etc). Si es None usa config
    
    Returns:
        String formateado con símbolo de moneda
    """
    if currency is None:
        currency = config.currency
    
    try:
        value = float(value)
    except (ValueError, TypeError):
        return "-"
    
    curr_info = SUPPORTED_CURRENCIES.get(currency, SUPPORTED_CURRENCIES["USD"])
    symbol = curr_info["symbol"]
    decimals = curr_info["decimals"]
    
    if decimals == 0:
        return f"{symbol}{value:,.0f}"
    else:
        return f"{symbol}{value:,.{decimals}f}"

def format_percentage(value, decimals=1):
    """Formatea como porcentaje"""
    try:
        return f"{float(value):.{decimals}f}%"
    except:
        return "-"

def format_date(date_obj, format_str="%d/%m/%Y"):
    """Formatea una fecha"""
    try:
        return date_obj.strftime(format_str)
    except:
        return str(date_obj)

def format_month_name(month_num, year=None):
    """Retorna nombre del mes en español"""
    months = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }
    month_name = months.get(month_num, "Mes")
    if year:
        return f"{month_name} {year}"
    return month_name

def truncate_text(text, max_length=30):
    """Trunca texto a longitud máxima"""
    return text[:max_length-3] + "..." if len(text) > max_length else text

def format_duration(days):
    """Formatea duración en días/meses/años"""
    if days < 7:
        return f"{days} días"
    elif days < 365:
        months = int(days / 30)
        return f"{months} meses"
    else:
        years = int(days / 365)
        return f"{years} años"
