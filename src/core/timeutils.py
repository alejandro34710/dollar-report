# Habilitar el uso de anotaciones de tipo más modernas.
from __future__ import annotations

# Módulo estándar para trabajar con fechas y horas.
from datetime import datetime
# Librería 'dateutil' para manejar zonas horarias de forma más robusta.
from dateutil import tz


def now_iso(tz_name: str) -> str:
    """
    Obtiene la fecha y hora actual en formato ISO 8601, ajustada a la zona horaria especificada.

    Args:
        tz_name (str): Nombre de la zona horaria (e.g., 'America/Bogota').

    Returns:
        str: Cadena de fecha y hora en formato ISO 8601 (e.g., 'YYYY-MM-DDTHH:MM:SS+00:00').
    """
    # Obtiene la información de la zona horaria a partir de su nombre.
    zone = tz.gettz(tz_name)
    
    # 1. Obtiene el momento actual.
    # 2. Lo ajusta a la zona horaria obtenida.
    # 3. Lo formatea como ISO 8601, incluyendo la hora, minuto y segundo exactos.
    return datetime.now(zone).isoformat(timespec="seconds")


def today_ymd(tz_name: str) -> str:
    """
    Obtiene la fecha actual (solo año, mes y día) ajustada a la zona horaria especificada.

    Args:
        tz_name (str): Nombre de la zona horaria (e.g., 'America/Bogota').

    Returns:
        str: Cadena de fecha en formato 'YYYY-MM-DD'.
    """
    # Obtiene la información de la zona horaria.
    zone = tz.gettz(tz_name)
    
    # 1. Obtiene el momento actual con la zona horaria correcta.
    # 2. Extrae solo la parte de la fecha (.date()).
    # 3. La convierte al formato ISO (YYYY-MM-DD), que es ideal para guardar en CSV.
    return datetime.now(zone).date().isoformat()
