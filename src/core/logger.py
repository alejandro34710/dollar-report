import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logger(log_file: str, level: str = "INFO") -> logging.Logger:
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logger = logging.getLogger("dollar_report")
    logger.setLevel(level.upper())

    if not logger.handlers:
        # Consola
        ch = logging.StreamHandler()
        ch.setLevel(level.upper())
        ch.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
        logger.addHandler(ch)

        # Archivo rotativo (~1MB, 3 backups)
        fh = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
        fh.setLevel(level.upper())
        fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
        logger.addHandler(fh)

    return logger
