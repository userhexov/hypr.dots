"""
utils.py — общие утилиты проекта.
"""

import subprocess
import sys
from pathlib import Path


# ── ANSI цвета для вывода в терминал ──────────────────────────────────────────
class C:
    OK      = "\033[92m"   # зелёный
    WARN    = "\033[93m"   # жёлтый
    ERR     = "\033[91m"   # красный
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    RESET   = "\033[0m"


def ok(msg: str)   -> None: print(f"{C.OK}✓{C.RESET} {msg}")
def warn(msg: str) -> None: print(f"{C.WARN}⚠{C.RESET}  {msg}", file=sys.stderr)
def err(msg: str)  -> None: print(f"{C.ERR}✗{C.RESET} {msg}", file=sys.stderr)


def run(cmd: str, silent: bool = True) -> bool:
    """
    Запускает shell-команду.
    Возвращает True при успехе, False при ошибке.
    silent=True  → подавляет stdout/stderr команды.
    """
    kwargs = {"shell": True, "check": False}
    if silent:
        kwargs["stdout"] = subprocess.DEVNULL
        kwargs["stderr"] = subprocess.DEVNULL
    result = subprocess.run(**kwargs, args=cmd)
    return result.returncode == 0


def require_arg(argv: list, idx: int, hint: str) -> str:
    """
    Возвращает argv[idx] или печатает подсказку и завершает программу.
    """
    if idx >= len(argv):
        err(f"Необходим аргумент: {hint}")
        sys.exit(1)
    return argv[idx]


def ensure_dir(path: Path) -> Path:
    """Создаёт директорию если её нет, возвращает path."""
    path.mkdir(parents=True, exist_ok=True)
    return path
