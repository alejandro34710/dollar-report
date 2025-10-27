# Permite usar anotaciones de tipo como 'list[str]' incluso si Python es una versión anterior a 3.9.
from __future__ import annotations

import os # Se usa para verificar si el archivo de configuración existe.
from dataclasses import dataclass # Se utiliza para crear clases que solo contienen datos (configuración).
from typing import Any, Dict # Se usa para definir el tipo de datos en el método from_dict.

import yaml # Librería para leer y parsear el archivo de configuración YAML.


@dataclass
class AppConfig:
    """Configuración general de la aplicación."""
    timezone: str # Zona horaria para manejar fechas y horas correctamente (e.g., 'America/Bogota').
    run_hour: int # Hora (0-23) en la que se debe ejecutar el job diario.
    run_minute: int # Minuto (0-59) en el que se debe ejecutar el job diario.


@dataclass
class ApiConfig:
    """Configuración de la API para obtener la tasa de cambio."""
    url: str # URL base de la API de tasas de cambio (e.g., 'https://api.exchangerate.host/latest').
    base: str # Divisa base para la cotización (e.g., 'USD').
    quote: str # Divisa a la que se quiere cotizar (e.g., 'COP').


@dataclass
class OutputConfig:
    """Configuración de las rutas de salida y formato de los datos."""
    csv_path: str # Ruta completa al archivo CSV donde se guardarán los datos históricos.
    xlsx_path: str # Ruta completa al archivo Excel (XLSX) que se generará como espejo.
    write_excel: bool # Booleano para activar o desactivar la escritura al archivo Excel.
    ensure_headers: bool # Asegura que las cabeceras se escriban en el CSV si el archivo está vacío.


@dataclass
class LoggingConfig:
    """Configuración del sistema de logging."""
    file: str # Ruta al archivo donde se guardarán los logs.
    level: str # Nivel mínimo de logs a registrar (e.g., 'INFO', 'DEBUG', 'ERROR').


@dataclass
class Config:
    """
    Clase principal que agrupa todas las secciones de configuración.
    Esta es la estructura final de la configuración.
    """
    app: AppConfig
    api: ApiConfig
    output: OutputConfig
    logging: LoggingConfig

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Config":
        """
        Método estático para crear un objeto Config a partir de un diccionario.
        
        Toma el diccionario cargado del YAML y usa el operador ** para desempaquetar
        cada subdiccionario en su clase dataclass correspondiente.
        """
        return Config(
            # Desempaqueta el diccionario 'app' en los argumentos de AppConfig.
            app=AppConfig(**d["app"]),
            # Desempaqueta el diccionario 'api' en los argumentos de ApiConfig.
            api=ApiConfig(**d["api"]),
            # Desempaqueta el diccionario 'output' en los argumentos de OutputConfig.
            output=OutputConfig(**d["output"]),
            # Desempaqueta el diccionario 'logging' en los argumentos de LoggingConfig.
            logging=LoggingConfig(**d["logging"]),
        )


def load_config(path: str = "config/config.yaml") -> Config:
    """
    Función para cargar la configuración desde un archivo YAML.

    Args:
        path (str): Ruta al archivo de configuración YAML.

    Returns:
        Config: Una instancia de la clase Config con los valores cargados.

    Raises:
        FileNotFoundError: Si el archivo de configuración no existe en la ruta especificada.
    """
    # Verifica si el archivo de configuración existe antes de intentar abrirlo.
    if not os.path.exists(path):
        raise FileNotFoundError(f"No se encontró el archivo de configuración: {path}")
        
    # Abre y lee el archivo YAML de forma segura.
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) # Carga el contenido como un diccionario estándar de Python.
        
    # Convierte el diccionario cargado en una instancia del objeto Config.
    return Config.from_dict(raw)
