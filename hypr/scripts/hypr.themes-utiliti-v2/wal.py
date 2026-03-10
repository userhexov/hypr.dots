"""
wal.py — интеграция с pywal.

Генерирует цвета из изображения и применяет обои через
настроенный бекенд (swww, feh, swaybg и др.).

Возвращаемый словарь цветов имеет плоскую структуру:
    {
        "background": "#1a1b26",
        "foreground": "#c0caf5",
        "cursor":     "#c0caf5",
        "color0":     "#1a1b26",
        ...
        "color15":    "#c0caf5",
    }
"""

import json
from pathlib import Path

from config import Paths, Settings, Tools
from utils import err, ok, run, warn


# ── Применение обоев ──────────────────────────────────────────────────────────

def _set_wallpaper(image: Path) -> None:
    """Устанавливает обои через доступный бекенд."""
    backend = Settings.WALLPAPER_BACKEND

    # Если настроенный бекенд недоступен — пробуем определить автоматически
    if not Tools.available(backend):
        backend = Tools.detect_wallpaper_backend()
        if backend is None:
            warn("Бекенд обоев не найден (swww / feh / swaybg / nitrogen)")
            return
        warn(f"Бекенд '{Settings.WALLPAPER_BACKEND}' не найден, используем '{backend}'")

    if backend == "swww":
        run(f"swww img '{image}' {Settings.SWWW_FLAGS} &")
    elif backend == "feh":
        run(f"feh {Settings.FEH_FLAGS} '{image}'")
    elif backend == "swaybg":
        run(f"swaybg -i '{image}' -m fill &")
    elif backend == "nitrogen":
        run(f"nitrogen --set-scaled '{image}'")
    elif backend == "xwallpaper":
        run(f"xwallpaper --zoom '{image}'")


# ── Чтение цветов ─────────────────────────────────────────────────────────────

def _colors_from_json() -> dict:
    """Читает цвета из colors.json (предпочтительный способ)."""
    data = json.loads(Paths.WAL_JSON.read_text())

    colors = {}
    colors.update(data.get("special", {}))          # background, foreground, cursor
    for key, val in data.get("colors", {}).items():  # color0..color15
        colors[key] = val
    return colors


def _colors_from_sh() -> dict:
    """Запасной способ: парсит colors.sh."""
    colors = {}
    for line in Paths.WAL_SH.read_text().splitlines():
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        colors[key.strip()] = value.strip().strip("'\"")
    return colors


def _read_colors() -> dict:
    """Читает цвета из кэша pywal (JSON → SH → ошибка)."""
    if Paths.WAL_JSON.exists():
        return _colors_from_json()
    if Paths.WAL_SH.exists():
        warn("colors.json не найден, используем colors.sh")
        return _colors_from_sh()
    raise RuntimeError(
        "Кэш pywal не найден. Убедись, что wal сгенерировал цвета."
    )


# ── Публичный API ─────────────────────────────────────────────────────────────

def apply(image: Path) -> dict:
    """
    Применяет обои и генерирует цвета через pywal.
    Возвращает словарь цветов.
    Вызывает RuntimeError если wal не установлен или не сработал.
    """
    if not image.exists():
        raise FileNotFoundError(f"Файл не найден: {image}")

    if not Tools.has_wal():
        raise RuntimeError(
            "pywal не установлен. Установи: pip install pywal"
        )

    # Генерируем цвета (без применения обоев через wal, -n)
    success = run(f"wal -i '{image}' -n -q")
    if not success:
        raise RuntimeError("wal завершился с ошибкой")

    # Применяем обои отдельно
    _set_wallpaper(image)

    # Перезагружаем kitty если используется
    if Tools.has_kitty():
        run("killall -SIGUSR1 kitty 2>/dev/null")

    return _read_colors()
