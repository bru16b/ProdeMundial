# =============================================================
#  Configuración global de la aplicación Prode Mundial 2026
# =============================================================

from pathlib import Path

APP_TITLE = "⚽ Prode Mundial 2026"

# Ruta base del proyecto (siempre relativa a este archivo, sin importar
# desde dónde se ejecute el comando streamlit run)
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = str(BASE_DIR / "data")

# Credenciales del administrador
ADMIN_PASSWORD = "admin2026"

# Sistema de puntaje
PUNTOS_EXACTO = 3       # Pronóstico exacto (ej: 2-1 → fue 2-1)
PUNTOS_RESULTADO = 1    # Resultado correcto (ej: 1-0 → fue 2-0)
PUNTOS_ERROR = 0        # Pronóstico incorrecto

# Opciones de grupos
GRUPOS = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]
