from __future__ import annotations

import time
from typing import Dict, Any, Tuple
from urllib.parse import urlparse

import requests


class RateFetchError(Exception):
    pass


def _build_request(api_url: str, base: str, quote: str) -> Tuple[str, Dict[str, Any] | None]:
    """
    Devuelve (request_url, params) según el host.
    - open.er-api.com: GET {api_url}/{base}  (sin params, devuelve todas las rates)
    - exchangerate.host: GET {api_url}?base=USD&symbols=COP
    - frankfurter.app:   GET {api_url}?from=USD&to=COP
    """
    host = urlparse(api_url).netloc.lower()
    if "open.er-api.com" in host:
        # /v6/latest/USD
        return f"{api_url.rstrip('/')}/{base}", None
    if "frankfurter" in host:
        return api_url, {"from": base, "to": quote, "amount": 1}
    # default: exchangerate.host style
    return api_url, {"base": base, "symbols": quote}


def _extract_rate(api_url: str, quote: str, data: Dict[str, Any]) -> float:
    """
    Normaliza extracción de la tasa desde distintas APIs.
    """
    host = urlparse(api_url).netloc.lower()
    # open.er-api.com
    if "open.er-api.com" in host:
        # Estructura: { "result":"success", "base_code":"USD", "rates": { "COP": 4xxx.xx, ... } }
        if data.get("result") != "success":
            raise RateFetchError(f"Respuesta no exitosa: {data}")
        rates = data.get("rates") or {}
        if quote not in rates:
            raise RateFetchError(f"No vino la divisa {quote} en la respuesta: {data}")
        return float(rates[quote])

    # frankfurter / exchangerate.host
    rates = data.get("rates") or {}
    if quote not in rates:
        raise RateFetchError(f"No vino la divisa {quote} en la respuesta: {data}")
    return float(rates[quote])


def fetch_rate(api_url: str, base: str, quote: str, retries: int = 3) -> float:
    """
    Obtiene la tasa base->quote desde una API pública (sin llave).
    Soporta:
      - open.er-api.com (recomendado para COP)
      - exchangerate.host
      - frankfurter.app (no soporta COP, pero se deja por compatibilidad)
    """
    request_url, params = _build_request(api_url, base, quote)
    last_err: Exception | None = None

    for attempt in range(1, retries + 1):
        try:
            r = requests.get(request_url, params=params, timeout=10)
            r.raise_for_status()
            data: Dict[str, Any] = r.json()
            return _extract_rate(api_url, quote, data)
        except Exception as e:  # noqa: BLE001
            last_err = e
            time.sleep(2 * attempt - 1)  # backoff: 1s, 3s, 5s...

    raise RateFetchError(f"No fue posible obtener la tasa tras {retries} intentos: {last_err}")
