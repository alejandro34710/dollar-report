from __future__ import annotations

import os
import pandas as pd


REQUIRED_COLUMNS = ["date", "base", "quote", "rate", "source", "fetched_at"]


def ensure_parent(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)


def append_or_update_csv(csv_path: str, row: dict, ensure_headers: bool = True) -> None:
    """
    Idempotente por fecha: si ya existe 'date' => actualiza la fila;
    si no existe => agrega nueva.
    """
    ensure_parent(csv_path)

    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
    else:
        df = pd.DataFrame(columns=REQUIRED_COLUMNS)

    # Asegurar columnas y orden
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            df[col] = pd.Series(dtype="object")
    df = df[REQUIRED_COLUMNS]

    date_val = row["date"]
    mask = df["date"] == date_val

    if mask.any():
        # Actualiza esa fila
        idx = df.index[mask][0]
        for k, v in row.items():
            df.at[idx, k] = v
    else:
        # Agrega nueva
        df.loc[len(df)] = row

    df.to_csv(csv_path, index=False)


def mirror_to_excel(csv_path: str, xlsx_path: str) -> None:
    ensure_parent(xlsx_path)
    df = pd.read_csv(csv_path)
    df.to_excel(xlsx_path, index=False)
