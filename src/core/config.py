from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict

import yaml


@dataclass
class AppConfig:
    timezone: str
    run_hour: int
    run_minute: int


@dataclass
class ApiConfig:
    url: str
    base: str
    quote: str


@dataclass
class OutputConfig:
    csv_path: str
    xlsx_path: str
    write_excel: bool
    ensure_headers: bool


@dataclass
class LoggingConfig:
    file: str
    level: str


@dataclass
class Config:
    app: AppConfig
    api: ApiConfig
    output: OutputConfig
    logging: LoggingConfig

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Config":
        return Config(
            app=AppConfig(**d["app"]),
            api=ApiConfig(**d["api"]),
            output=OutputConfig(**d["output"]),
            logging=LoggingConfig(**d["logging"]),
        )


def load_config(path: str = "config/config.yaml") -> Config:
    if not os.path.exists(path):
        raise FileNotFoundError(f"No se encontró el archivo de configuración: {path}")
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return Config.from_dict(raw)
