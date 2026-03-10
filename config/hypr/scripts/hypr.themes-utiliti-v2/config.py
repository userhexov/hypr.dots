"""
config.py — центральная конфигурация.

Все пути и настройки собраны здесь.
Меняй под своё окружение только этот файл.
"""

import shutil
from pathlib import Path

HOME = Path.home()


# ══════════════════════════════════════════════════════════════════════════════
# Пути
# ══════════════════════════════════════════════════════════════════════════════


class Paths:
    # ── EWW ───────────────────────────────────────────────────────────────────
    EWW_DIR = HOME / ".config/eww"
    EWW_COLORS = EWW_DIR / "colors-dynamic.scss"
    EWW_THEMES_DIR = EWW_DIR / "themes"
    EWW_CURRENT_IMG = EWW_DIR / "current-wal-image.txt"

    # ── Rofi ──────────────────────────────────────────────────────────────────
    ROFI_DIR = HOME / ".config/rofi"
    ROFI_COLORS = ROFI_DIR / "colors.rasi"

    # ── Zed ───────────────────────────────────────────────────────────────────
    ZED_DIR = HOME / ".config/zed"
    ZED_THEMES_DIR = ZED_DIR / "themes"
    ZED_THEME_FILE = ZED_THEMES_DIR / "wal-dynamic.json"
    ZED_SETTINGS = ZED_DIR / "settings.json"

    # ── Firefox ───────────────────────────────────────────────────────────────
    # Скрипт ищет профиль автоматически (первый *.default* в ~/.mozilla/firefox/)
    # Можно задать явно: FIREFOX_PROFILE = HOME / ".mozilla/firefox/YOURPROFILE"
    FIREFOX_PROFILES_DIR = HOME / ".mozilla/firefox"
    FIREFOX_PROFILE = None  # None = автоопределение

    # ── Obsidian ──────────────────────────────────────────────────────────────
    # Укажи путь к своему vault (или список vaults).
    # Если None — модуль пропустит Obsidian с предупреждением.
    OBSIDIAN_VAULTS: list[Path] = [
        # HOME / "Documents/MyVault",   # ← раскомментируй и укажи свой vault
    ]

    # ── Pywal cache ───────────────────────────────────────────────────────────
    WAL_CACHE = HOME / ".cache/wal"
    WAL_JSON = WAL_CACHE / "colors.json"
    WAL_SH = WAL_CACHE / "colors.sh"


# ══════════════════════════════════════════════════════════════════════════════
# Поведение
# ══════════════════════════════════════════════════════════════════════════════


class Settings:
    # Задержка перед reload EWW (секунд)
    EWW_RELOAD_DELAY: float = 0.2

    # Имя дефолтной темы — создаётся автоматически при первом apply
    DEFAULT_THEME_NAME: str = "default"

    # Бекенд обоев: "swww" | "swaybg" | "feh" | "nitrogen" | "xwallpaper"
    # Если не задан явно — определяется автоматически
    WALLPAPER_BACKEND: str = "swww"

    # Параметры swww
    SWWW_FLAGS: str = "--transition-type fade --transition-fps 60"

    # Параметры feh
    FEH_FLAGS: str = "--bg-scale"

    # Имя темы Zed (отображается в UI)
    ZED_THEME_NAME: str = "Wal Dynamic"


# ══════════════════════════════════════════════════════════════════════════════
# Автоопределение инструментов
# ══════════════════════════════════════════════════════════════════════════════


class Tools:
    """Определяет, какие инструменты установлены в системе."""

    @staticmethod
    def available(name: str) -> bool:
        return shutil.which(name) is not None

    @classmethod
    def has_eww(cls) -> bool:
        return cls.available("eww")

    @classmethod
    def has_rofi(cls) -> bool:
        return cls.available("rofi")

    @classmethod
    def has_kitty(cls) -> bool:
        return cls.available("kitty")

    @classmethod
    def has_wal(cls) -> bool:
        return cls.available("wal")

    @classmethod
    def has_swww(cls) -> bool:
        return cls.available("swww")

    @classmethod
    def has_swaybg(cls) -> bool:
        return cls.available("swaybg")

    @classmethod
    def has_feh(cls) -> bool:
        return cls.available("feh")

    @classmethod
    def has_zed(cls) -> bool:
        return cls.available("zed") or Paths.ZED_DIR.exists()

    @classmethod
    def has_firefox(cls) -> bool:
        return cls.available("firefox") or Paths.FIREFOX_PROFILES_DIR.exists()

    @classmethod
    def has_obsidian(cls) -> bool:
        return bool(Paths.OBSIDIAN_VAULTS)

    @classmethod
    def has_swaync(cls) -> bool:
        return cls.available("swaync")

    @classmethod
    def detect_wallpaper_backend(cls) -> str | None:
        """Первый найденный бекенд обоев или None."""
        for backend in ("swww", "swaybg", "feh", "nitrogen", "xwallpaper"):
            if cls.available(backend):
                return backend
        return None

    @classmethod
    def summary(cls) -> dict[str, bool]:
        return {
            "wal": cls.has_wal(),
            "eww": cls.has_eww(),
            "rofi": cls.has_rofi(),
            "zed": cls.has_zed(),
            "firefox": cls.has_firefox(),
            "obsidian": cls.has_obsidian(),
            "swaync": cls.has_swaync(),
            "kitty": cls.has_kitty(),
            "swww": cls.has_swww(),
            "swaybg": cls.has_swaybg(),
            "feh": cls.has_feh(),
        }
