# src/utils.py
from datetime import datetime

def file_debug(message: str):
    """Escribe un mensaje con timestamp exacto en el archivo de depuración compartida"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open("installation-debug.txt", "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        pass # Evitar que un problema de permisos de archivo rompa la app