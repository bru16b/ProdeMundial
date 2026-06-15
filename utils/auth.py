# utils/auth.py — Autenticación simple para el administrador

from config import ADMIN_PASSWORD


def check_admin_password(password: str) -> bool:
    """Verifica si la contraseña ingresada corresponde al administrador."""
    return password == ADMIN_PASSWORD
