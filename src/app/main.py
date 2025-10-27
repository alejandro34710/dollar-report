# Permite usar anotaciones de tipo como 'list[str]' incluso si Python es una versión anterior a 3.9.
from __future__ import annotations

# Módulos de la librería estándar
import argparse # Para manejar argumentos de línea de comandos (e.g., --loop).
import sys      # Para interactuar con el intérprete de Python (usado para sys.exit).
import time     # Para el manejo de pausas en el modo bucle.

# Módulos de librerías de terceros
import schedule # Para programar la ejecución de la tarea a una hora específica en modo bucle.

# Módulos de tu proyecto (asumiendo esta estructura)
from src.core.config import load_config           # Función para cargar la configuración de la aplicación.
from src.core.logger import setup_logger          # Función para configurar el sistema de logging.
from src.core.timeutils import now_iso, today_ymd # Utilidades para obtener la fecha y hora con formato.
from src.services.fetch_dollar_rate import fetch_rate, RateFetchError # Función para obtener la tasa y su excepción.
from src.writers.writer import append_or_update_csv, mirror_to_excel # Funciones para escribir datos a CSV/Excel.


def job_once() -> int:
    """
    Función principal que ejecuta la lógica de obtener y guardar la tasa de cambio una sola vez.

    Returns:
        int: 0 si la ejecución fue exitosa, 1 si hubo un error.
    """
    # 1. Carga de Configuración y Logger
    cfg = load_config() # Carga la configuración de la aplicación (e.g., URLs de API, rutas de archivo).
    log = setup_logger(cfg.logging.file, cfg.logging.level) # Configura el logger con el archivo y nivel definidos.

    # 2. Obtención de la Tasa de Cambio
    try:
        # Intenta obtener la tasa de cambio del dólar (u otra divisa) de la API, con reintentos.
        rate = fetch_rate(cfg.api.url, cfg.api.base, cfg.api.quote, retries=3)
        log.info(f"Tasa {cfg.api.base}->{cfg.api.quote}: {rate}") # Registra la tasa obtenida.
    except RateFetchError as e:
        # Si falla la obtención después de los reintentos, registra el error.
        log.error(f"Error al obtener tasa: {e}")
        return 1 # Devuelve 1 para indicar que la tarea falló.

    # 3. Preparación de los Datos
    row = {
        # Obtiene la fecha de hoy en formato YYYY-MM-DD (usando la zona horaria configurada).
        "date": today_ymd(cfg.app.timezone),
        "base": cfg.api.base,   # Divisa base (e.g., 'USD').
        "quote": cfg.api.quote, # Divisa a cotizar (e.g., 'COP', 'ARS', etc.).
        "rate": rate,           # El valor de la tasa de cambio obtenido.
        "source": "exchangerate.host", # Fuente de la información (hardcodeada o desde config).
        # Obtiene el momento exacto en formato ISO 8601 en que se obtuvieron los datos.
        "fetched_at": now_iso(cfg.app.timezone),
    }

    # 4. Escritura en CSV
    # Añade o actualiza la fila en el archivo CSV.
    # 'ensure_headers' asegura que las columnas existan si el archivo está vacío.
    append_or_update_csv(cfg.output.csv_path, row, ensure_headers=cfg.output.ensure_headers)
    
    # 5. Mirroring a Excel (opcional)
    if cfg.output.write_excel:
        # Si la configuración lo indica, copia el contenido del CSV al archivo Excel (.xlsx).
        mirror_to_excel(cfg.output.csv_path, cfg.output.xlsx_path)

    # 6. Registro de Éxito
    log.info(f"Guardado en {cfg.output.csv_path}")
    if cfg.output.write_excel:
        log.info(f"Excel actualizado en {cfg.output.xlsx_path}")
        
    return 0 # Devuelve 0 para indicar que la tarea fue exitosa.


def main() -> int:
    """
    Función principal de ejecución del script, maneja los argumentos de línea de comandos.

    Returns:
        int: El código de salida del programa.
    """
    # Configura el analizador de argumentos de línea de comandos.
    parser = argparse.ArgumentParser(description="Reporte de dólar diario")
    parser.add_argument(
        "--loop",
        action="store_true", # Se convierte en True si se especifica --loop.
        help="Queda corriendo y ejecuta cada día a la hora configurada (run_hour/run_minute).",
    )
    args = parser.parse_args() # Procesa los argumentos de la línea de comandos.

    # Modo de ejecución única (por defecto)
    if not args.loop:
        # Si no se especifica --loop, ejecuta la tarea una sola vez y sale.
        return job_once()

    # Modo loop con schedule (para pruebas/uso simple)
    # Carga la configuración y el logger para el modo bucle.
    cfg = load_config()
    log = setup_logger(cfg.logging.file, cfg.logging.level)
    
    # Define la hora y minuto de ejecución desde la configuración.
    hh, mm = cfg.app.run_hour, cfg.app.run_minute
    # Formatea la hora para el schedule (e.g., "08:30").
    cron_time = f"{hh:02d}:{mm:02d}" 

    # Configura el scheduler
    schedule.clear() # Limpia cualquier tarea programada previamente.
    # Programa la función 'job_once' para que se ejecute todos los días a la hora definida.
    schedule.every().day.at(cron_time).do(job_once)
    log.info(f"Runner activo. Ejecutará todos los días a las {cron_time} ({cfg.app.timezone}). Ctrl+C para salir.")

    # Bucle de ejecución (Loop)
    try:
        while True:
            # Ejecuta las tareas que están pendientes según la hora programada.
            schedule.run_pending()
            # Pausa el bucle por un segundo para evitar el consumo excesivo de CPU.
            time.sleep(1)
    except KeyboardInterrupt:
        # Captura la interrupción por teclado (Ctrl+C) para salir elegantemente.
        log.info("Runner detenido por el usuario.")
        return 0 # Retorna 0 (éxito) al detener la ejecución.


if __name__ == "__main__":
    # Punto de entrada principal: llama a la función main() y usa su valor de retorno
    # como código de salida del script.
    sys.exit(main())
6