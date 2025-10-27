# Habilitar el uso de anotaciones de tipo más modernas.
from __future__ import annotations

import os # Para interactuar con el sistema de archivos (directorios, existencia de archivos).
import pandas as pd # Librería principal para el manejo de datos (DataFrames) y CSV/Excel.


# Columnas requeridas y su orden en el archivo CSV.
REQUIRED_COLUMNS = ["date", "base", "quote", "rate", "source", "fetched_at"]


def ensure_parent(path: str) -> None:
    """
    Asegura que el directorio padre del path dado exista. Lo crea si es necesario.
    
    Args:
        path (str): Ruta completa del archivo (CSV o XLSX).
    """
    # Crea el directorio del archivo (os.path.dirname(path)) si no existe.
    # 'exist_ok=True' evita un error si el directorio ya existe.
    os.makedirs(os.path.dirname(path), exist_ok=True)


def append_or_update_csv(csv_path: str, row: dict, ensure_headers: bool = True) -> None:
    """
    Guarda o actualiza una fila de datos en el archivo CSV.
    Es idempotente por 'date': si la fecha ya existe, actualiza la fila; si no, agrega una nueva.

    Args:
        csv_path (str): Ruta al archivo CSV.
        row (dict): Diccionario de datos a insertar/actualizar.
        ensure_headers (bool): (Parámetro no usado en la implementación actual de pandas).
    """
    # Asegura que la carpeta donde se guardará el CSV exista.
    ensure_parent(csv_path)

    # 1. Cargar el DataFrame existente o crear uno nuevo
    if os.path.exists(csv_path):
        # Lee el archivo CSV existente en un DataFrame de pandas.
        df = pd.read_csv(csv_path)
    else:
        # Si el archivo no existe, crea un DataFrame vacío con las columnas requeridas.
        df = pd.DataFrame(columns=REQUIRED_COLUMNS)

    # 2. Asegurar y ordenar las columnas
    # Garantiza que todas las columnas requeridas existan, rellenando si es necesario.
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            df[col] = pd.Series(dtype="object")
    # Reordena las columnas para mantener un formato consistente.
    df = df[REQUIRED_COLUMNS]

    # 3. Lógica de Idempotencia: Verificar si la fecha ya existe
    date_val = row["date"]
    # Crea una máscara booleana: True donde la columna 'date' coincide con la nueva fecha.
    mask = df["date"] == date_val

    if mask.any():
        # Caso de ACTUALIZACIÓN: La fecha ya existe
        # Obtiene el índice de la primera coincidencia (asumiendo una sola entrada por fecha).
        idx = df.index[mask][0]
        # Itera sobre los datos de la nueva fila (row) y actualiza el valor en el DataFrame.
        for k, v in row.items():
            df.at[idx, k] = v # .at es eficiente para la asignación de un solo valor.
    else:
        # Caso de ADICIÓN: La fecha no existe
        # Agrega la nueva fila al final del DataFrame.
        df.loc[len(df)] = row

    # 4. Escribir el DataFrame de vuelta al CSV
    # Guarda el DataFrame modificado en el archivo CSV, sin incluir el índice interno de pandas.
    df.to_csv(csv_path, index=False)


def mirror_to_excel(csv_path: str, xlsx_path: str) -> None:
    """
    Lee el contenido del archivo CSV y lo guarda como un archivo Excel (XLSX).
    Esto sirve como una copia espejo o un reporte fácil de usar.

    Args:
        csv_path (str): Ruta al archivo CSV fuente.
        xlsx_path (str): Ruta donde se guardará el archivo Excel de destino.
    """
    # Asegura que la carpeta donde se guardará el Excel exista.
    ensure_parent(xlsx_path)
    
    # 1. Leer el CSV completo.
    df = pd.read_csv(csv_path)
    
    # 2. Escribir al Excel
    # Guarda el DataFrame en formato Excel, sin incluir el índice de pandas.
    df.to_excel(xlsx_path, index=False)

