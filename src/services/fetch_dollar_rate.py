# Habilitar el uso de anotaciones de tipo más modernas.
from __future__ import annotations

import time # Necesario para la función de espera (sleep) entre reintentos.
from typing import Dict, Any, Tuple # Tipos para mejorar la legibilidad y el chequeo de tipos.
from urllib.parse import urlparse # Se usa para parsear la URL de la API y determinar el host.

import requests # Librería para realizar las solicitudes HTTP.


class RateFetchError(Exception):
    """Excepción personalizada para errores específicos al obtener la tasa de cambio."""
    pass


def _build_request(api_url: str, base: str, quote: str) -> Tuple[str, Dict[str, Any] | None]:
    """
    Construye la URL y los parámetros de la solicitud GET basándose en el host de la API.

    Args:
        api_url (str): URL base de la API (ej. 'https://api.exchangerate.host/latest').
        base (str): Divisa base (ej. 'USD').
        quote (str): Divisa a cotizar (ej. 'COP').

    Returns:
        Tuple[str, Dict[str, Any] | None]: La URL final de la solicitud y los parámetros (o None).
    """
    # Extrae el dominio (netloc) de la URL para identificar la API.
    host = urlparse(api_url).netloc.lower()
    
    # Lógica de construcción para open.er-api.com
    if "open.er-api.com" in host:
        # Esta API usa la divisa base como parte del path: /v6/latest/USD
        # No requiere parámetros de consulta (params).
        return f"{api_url.rstrip('/')}/{base}", None
        
    # Lógica de construcción para frankfurter.app
    if "frankfurter" in host:
        # Usa 'from' y 'to' como nombres de parámetros.
        return api_url, {"from": base, "to": quote, "amount": 1}
        
    # Lógica por defecto (para exchangerate.host y otras APIs compatibles)
    # Usa 'base' y 'symbols' como nombres de parámetros.
    return api_url, {"base": base, "symbols": quote}


def _extract_rate(api_url: str, quote: str, data: Dict[str, Any]) -> float:
    """
    Normaliza y extrae el valor de la tasa de cambio desde la respuesta JSON de la API.

    Args:
        api_url (str): URL de la API (para determinar la lógica de extracción).
        quote (str): La divisa a buscar en la respuesta (ej. 'COP').
        data (Dict[str, Any]): El objeto JSON decodificado de la respuesta.

    Returns:
        float: El valor numérico de la tasa de cambio.

    Raises:
        RateFetchError: Si la respuesta indica fallo o no contiene la divisa de cotización.
    """
    host = urlparse(api_url).netloc.lower()
    
    # Lógica de extracción específica para open.er-api.com
    if "open.er-api.com" in host:
        # Verifica el campo de éxito ('result')
        if data.get("result") != "success":
            raise RateFetchError(f"Respuesta no exitosa: {data}")
            
        # Intenta obtener el diccionario de tasas.
        rates = data.get("rates") or {}
        
        # Verifica que la divisa de cotización exista en las tasas.
        if quote not in rates:
            raise RateFetchError(f"No vino la divisa {quote} en la respuesta: {data}")
            
        # Devuelve la tasa convertida a float.
        return float(rates[quote])

    # Lógica de extracción para frankfurter.app / exchangerate.host (estructura similar)
    rates = data.get("rates") or {}
    
    if quote not in rates:
        raise RateFetchError(f"No vino la divisa {quote} en la respuesta: {data}")
        
    return float(rates[quote])


def fetch_rate(api_url: str, base: str, quote: str, retries: int = 3) -> float:
    """
    Intenta obtener la tasa de cambio, reintentando si falla.

    Args:
        api_url (str): URL base de la API.
        base (str): Divisa base.
        quote (str): Divisa a cotizar.
        retries (int): Número máximo de intentos de solicitud.

    Returns:
        float: La tasa de cambio obtenida.

    Raises:
        RateFetchError: Si no se pudo obtener la tasa después de todos los reintentos.
    """
    # 1. Preparar la Solicitud
    # Obtiene la URL formateada y los parámetros de consulta específicos de la API.
    request_url, params = _build_request(api_url, base, quote)
    last_err: Exception | None = None # Guarda el último error para reportarlo si fallan todos los reintentos.

    # 2. Bucle de Reintentos
    for attempt in range(1, retries + 1):
        try:
            # Realiza la solicitud HTTP GET con un timeout de 10 segundos.
            r = requests.get(request_url, params=params, timeout=10)
            
            # Lanza una excepción si el código de estado HTTP es 4xx o 5xx.
            r.raise_for_status() 
            
            # Decodifica la respuesta JSON.
            data: Dict[str, Any] = r.json()
            
            # Extrae la tasa y la devuelve si tiene éxito.
            return _extract_rate(api_url, quote, data)
            
        except Exception as e:  # Captura cualquier excepción (conexión, timeout, estado HTTP).
            last_err = e
            # Espera con un backoff exponencial (1s, 3s, 5s, ...) antes del siguiente intento.
            time.sleep(2 * attempt - 1) 

    # 3. Fallo Final
    # Si el bucle termina sin un 'return', significa que todos los reintentos fallaron.
    raise RateFetchError(f"No fue posible obtener la tasa tras {retries} intentos: {last_err}")
