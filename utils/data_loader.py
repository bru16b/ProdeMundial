# utils/data_loader.py — Lectura y escritura de archivos CSV

import os
import pandas as pd
from config import DATA_DIR


def _path(filename: str) -> str:
    """Retorna la ruta completa al archivo de datos."""
    return os.path.join(DATA_DIR, filename)


# ─────────────────────────────────────────────
#  LECTURA
# ─────────────────────────────────────────────

def read_partidos() -> pd.DataFrame:
    df = pd.read_csv(_path("partidos.csv"))
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df


def read_participantes() -> pd.DataFrame:
    df = pd.read_csv(_path("participantes.csv"))
    if not df.empty:
        df["usuario_id"] = df["usuario_id"].astype(int)
    return df


def read_pronosticos() -> pd.DataFrame:
    df = pd.read_csv(_path("pronosticos.csv"))
    if not df.empty:
        for col in ["pronostico_id", "usuario_id", "partido_id", "goles_local", "goles_visitante"]:
            df[col] = df[col].astype(int)
    return df


def read_resultados() -> pd.DataFrame:
    df = pd.read_csv(_path("resultados.csv"))
    if not df.empty:
        for col in ["partido_id", "goles_local", "goles_visitante"]:
            df[col] = df[col].astype(int)
    return df


# ─────────────────────────────────────────────
#  ESCRITURA
# ─────────────────────────────────────────────

def save_pronostico(usuario_id: int, partido_id: int, goles_local: int, goles_visitante: int) -> None:
    """Guarda o actualiza un pronóstico de un usuario para un partido."""
    df = read_pronosticos()
    mask = (df["usuario_id"] == usuario_id) & (df["partido_id"] == partido_id)

    if mask.any():
        df.loc[mask, "goles_local"] = goles_local
        df.loc[mask, "goles_visitante"] = goles_visitante
        df.loc[mask, "fecha_carga"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    else:
        new_id = int(df["pronostico_id"].max()) + 1 if not df.empty else 1
        new_row = pd.DataFrame([{
            "pronostico_id": new_id,
            "usuario_id": int(usuario_id),
            "partido_id": int(partido_id),
            "goles_local": int(goles_local),
            "goles_visitante": int(goles_visitante),
            "fecha_carga": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        }])
        df = pd.concat([df, new_row], ignore_index=True)

    df.to_csv(_path("pronosticos.csv"), index=False)


def save_resultado(partido_id: int, goles_local: int, goles_visitante: int) -> None:
    """Guarda o actualiza el resultado real de un partido (solo admin)."""
    df = read_resultados()
    mask = df["partido_id"] == partido_id

    if mask.any():
        df.loc[mask, "goles_local"] = goles_local
        df.loc[mask, "goles_visitante"] = goles_visitante
        df.loc[mask, "fecha_carga"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    else:
        new_row = pd.DataFrame([{
            "partido_id": int(partido_id),
            "goles_local": int(goles_local),
            "goles_visitante": int(goles_visitante),
            "fecha_carga": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        }])
        df = pd.concat([df, new_row], ignore_index=True)

    df.to_csv(_path("resultados.csv"), index=False)


def add_participante(nombre: str, email: str = "") -> tuple[bool, str]:
    """Agrega un nuevo participante. Retorna (éxito, mensaje)."""
    df = read_participantes()

    # Unicidad por nombre (case-insensitive)
    if not df.empty and nombre.strip().lower() in df["nombre"].str.lower().values:
        return False, f"❌ Ya existe un participante llamado **{nombre.strip()}**."

    new_id = int(df["usuario_id"].max()) + 1 if not df.empty else 1
    new_row = pd.DataFrame([{
        "usuario_id": new_id,
        "nombre": nombre.strip(),
        "email": email.strip().lower(),
        "fecha_registro": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
    }])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(_path("participantes.csv"), index=False)
    return True, f"✅ **{nombre.strip()}** agregado correctamente."


def delete_participante(usuario_id: int) -> None:
    """Elimina un participante por su ID."""
    df = read_participantes()
    df = df[df["usuario_id"] != usuario_id]
    df.to_csv(_path("participantes.csv"), index=False)
