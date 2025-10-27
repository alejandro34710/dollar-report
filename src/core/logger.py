import logging # Módulo principal de Python para el sistema de logging.
import os # Se usa para interactuar con el sistema operativo (crear directorios).
from logging.handlers import RotatingFileHandler # Handler para manejar archivos de log con rotación.


def setup_logger(log_file: str, level: str = "INFO") -> logging.Logger:
    """
    Configura y devuelve un logger con handlers para consola y archivo rotativo.

    Args:
        log_file (str): Ruta completa al archivo donde se guardarán los logs.
        level (str): Nivel de logging a usar (e.g., 'INFO', 'DEBUG', 'WARNING').

    Returns:
        logging.Logger: Instancia del logger configurado.
    """
    # 1. Creación del Directorio de Logs
    # Asegura que el directorio del archivo de log exista. 'exist_ok=True' evita errores si ya existe.
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # 2. Inicialización del Logger
    logger = logging.getLogger("dollar_report") # Obtiene o crea el logger con un nombre específico.
    logger.setLevel(level.upper()) # Establece el nivel mínimo de logging (convirtiendo a mayúsculas).

    # 3. Configuración de Handlers (Se añade solo si el logger no tiene handlers ya configurados)
    if not logger.handlers:
        
        # --- Handler para Consola (StreamHandler) ---
        ch = logging.StreamHandler()
        ch.setLevel(level.upper()) # Establece el nivel para la salida en consola.
        # Define el formato de los mensajes en consola: solo [NIVEL] MENSAJE.
        ch.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
        logger.addHandler(ch)

        # --- Handler para Archivo Rotativo (RotatingFileHandler) ---
        # Crea un handler que rotará el archivo cuando exceda 1MB, manteniendo 3 copias de backup.
        fh = RotatingFileHandler(
            log_file, 
            maxBytes=1_000_000, # Tamaño máximo del archivo de log antes de rotar (1 MB).
            backupCount=3,      # Número de archivos de backup a mantener.
            encoding="utf-8"    # Codificación de los logs.
        )
        fh.setLevel(level.upper()) # Establece el nivel para la escritura en el archivo.
        # Define el formato de los mensajes en el archivo: FECHA | NIVEL | MENSAJE.
        fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
        logger.addHandler(fh)

    return logger # Devuelve la instancia del logger lista para usarse.
