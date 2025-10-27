from __future__ import annotations

import argparse
import sys
import time

import schedule

from src.core.config import load_config
from src.core.logger import setup_logger
from src.core.timeutils import now_iso, today_ymd
from src.services.fetch_dollar_rate import fetch_rate, RateFetchError
from src.writers.writer import append_or_update_csv, mirror_to_excel


def job_once() -> int:
    cfg = load_config()
    log = setup_logger(cfg.logging.file, cfg.logging.level)

    try:
        rate = fetch_rate(cfg.api.url, cfg.api.base, cfg.api.quote, retries=3)
        log.info(f"Tasa {cfg.api.base}->{cfg.api.quote}: {rate}")
    except RateFetchError as e:
        log.error(f"Error al obtener tasa: {e}")
        return 1

    row = {
        "date": today_ymd(cfg.app.timezone),
        "base": cfg.api.base,
        "quote": cfg.api.quote,
        "rate": rate,
        "source": "exchangerate.host",
        "fetched_at": now_iso(cfg.app.timezone),
    }

    append_or_update_csv(cfg.output.csv_path, row, ensure_headers=cfg.output.ensure_headers)
    if cfg.output.write_excel:
        mirror_to_excel(cfg.output.csv_path, cfg.output.xlsx_path)

    log.info(f"Guardado en {cfg.output.csv_path}")
    if cfg.output.write_excel:
        log.info(f"Excel actualizado en {cfg.output.xlsx_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Reporte de dólar diario")
    parser.add_argument(
        "--loop",
        action="store_true",
        help="Queda corriendo y ejecuta cada día a la hora configurada (run_hour/run_minute).",
    )
    args = parser.parse_args()

    if not args.loop:
        return job_once()

    # Modo loop con schedule (para pruebas/uso simple)
    cfg = load_config()
    log = setup_logger(cfg.logging.file, cfg.logging.level)
    hh, mm = cfg.app.run_hour, cfg.app.run_minute
    cron_time = f"{hh:02d}:{mm:02d}"

    schedule.clear()
    schedule.every().day.at(cron_time).do(job_once)
    log.info(f"Runner activo. Ejecutará todos los días a las {cron_time} ({cfg.app.timezone}). Ctrl+C para salir.")

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        log.info("Runner detenido por el usuario.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
