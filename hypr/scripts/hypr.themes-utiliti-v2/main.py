#!/usr/bin/env python3
"""
main.py — ядро управления темами.

Команды:
  main.py <image>       — применить тему из изображения
  main.py save <name>   — сохранить текущую тему
  main.py load <name>   — загрузить тему
  main.py list          — список тем
  main.py delete <name> — удалить тему
  main.py info          — информация об установленных инструментах
"""

import shutil
import sys
from pathlib import Path

import swaync

import eww
import firefox
import obsidian
import rofi
import wal
import zed
from config import Paths, Settings, Tools
from utils import ensure_dir, err, ok, require_arg, warn

# Гарантируем наличие директории тем при импорте модуля
ensure_dir(Paths.EWW_THEMES_DIR)


# ══════════════════════════════════════════════════════════════════════════════
# Основные операции
# ══════════════════════════════════════════════════════════════════════════════


def apply(image: Path) -> bool:
    """
    Применяет тему из изображения:
      1. pywal генерирует цвета
      2. EWW получает colors-dynamic.scss
      3. Rofi получает colors.rasi
      4. Zed получает wal-dynamic.json + settings.json обновляется
      5. Firefox получает userChrome.css
      6. Obsidian получает CSS сниппет
      7. EWW перезагружается

    Ошибка в любом модуле не прерывает остальные.
    Возвращает True при успехе.
    """
    if not image.exists():
        err(f"Файл не найден: {image}")
        return False

    try:
        colors = wal.apply(image)
    except (FileNotFoundError, RuntimeError) as e:
        err(str(e))
        return False

    # Сохраняем путь к текущему изображению
    Paths.EWW_CURRENT_IMG.write_text(str(image.resolve()))

    # Обновляем все конфиги — каждый модуль сам проверяет наличие инструмента
    eww.generate_scss(colors)
    rofi.generate_colors(colors)
    zed.generate_theme(colors)
    firefox.generate_colors(colors)
    obsidian.generate_snippet(colors)
    swaync.generate_style(colors)

    # Перезагружаем EWW последним
    eww.reload()

    ok(f"Тема применена: {image.name}")
    return True


def save(name: str) -> bool:
    """
    Сохраняет текущую тему под именем name.
    Копирует scss, rasi и путь к изображению.
    """
    if not Paths.EWW_CURRENT_IMG.exists():
        err("Нет активной темы. Сначала примени изображение.")
        return False

    image_path = Paths.EWW_CURRENT_IMG.read_text().strip()

    (Paths.EWW_THEMES_DIR / f"{name}.theme").write_text(image_path)

    if Paths.EWW_COLORS.exists():
        shutil.copy(Paths.EWW_COLORS, Paths.EWW_THEMES_DIR / f"{name}.scss")

    if Paths.ROFI_COLORS.exists():
        shutil.copy(Paths.ROFI_COLORS, Paths.EWW_THEMES_DIR / f"{name}.rasi")

    ok(f"Тема '{name}' сохранена")
    return True


def load(name: str) -> bool:
    """
    Загружает сохранённую тему.
    Если изображение доступно — полный apply через pywal.
    Если нет — восстанавливает цвета из сохранённых файлов.
    """
    theme_file = Paths.EWW_THEMES_DIR / f"{name}.theme"
    scss_file = Paths.EWW_THEMES_DIR / f"{name}.scss"
    rasi_file = Paths.EWW_THEMES_DIR / f"{name}.rasi"

    if not theme_file.exists():
        err(f"Тема '{name}' не найдена")
        return False

    image = Path(theme_file.read_text().strip())

    if image.exists():
        return apply(image)

    # Изображение недоступно — восстанавливаем из файлов
    warn(f"Изображение не найдено: {image}")
    warn("Восстанавливаем цвета из сохранённых файлов...")

    restored = False

    if scss_file.exists():
        shutil.copy(scss_file, Paths.EWW_COLORS)
        eww.reload()
        restored = True

    if rasi_file.exists():
        shutil.copy(rasi_file, Paths.ROFI_COLORS)
        restored = True

    if restored:
        ok(f"Тема '{name}' загружена (без обоев)")
    else:
        err(f"Нет файлов для восстановления темы '{name}'")

    return restored


def list_themes() -> list[str]:
    """Выводит и возвращает список сохранённых тем."""
    themes = sorted(t.stem for t in Paths.EWW_THEMES_DIR.glob("*.theme"))

    if not themes:
        print("  (нет сохранённых тем)")
        return []

    for name in themes:
        marker = " ★" if name == Settings.DEFAULT_THEME_NAME else ""
        print(f"  • {name}{marker}")

    return themes


def delete(name: str) -> bool:
    """Удаляет все файлы темы (.theme, .scss, .rasi)."""
    removed = False
    for ext in ("theme", "scss", "rasi"):
        f = Paths.EWW_THEMES_DIR / f"{name}.{ext}"
        if f.exists():
            f.unlink()
            removed = True

    if removed:
        ok(f"Тема '{name}' удалена")
    else:
        warn(f"Тема '{name}' не найдена")

    return removed


def info() -> None:
    """Выводит информацию об установленных инструментах и текущей теме."""
    print("\n  Инструменты:")
    for tool, installed in Tools.summary().items():
        status = "✓" if installed else "✗"
        print(f"    {status}  {tool}")

    print(f"\n  Текущая тема: ", end="")
    if Paths.EWW_CURRENT_IMG.exists():
        print(Paths.EWW_CURRENT_IMG.read_text().strip())
    else:
        print("не задана")
    print()


# ══════════════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════════════

HELP = """\
Использование:
  main.py <image>       — применить тему из изображения
  main.py save <name>   — сохранить текущую тему
  main.py load <name>   — загрузить тему
  main.py list          — список сохранённых тем
  main.py delete <name> — удалить тему
  main.py info          — информация об установленных инструментах
"""


def main() -> None:
    if len(sys.argv) < 2:
        print(HELP)
        return

    cmd = sys.argv[1]

    if cmd == "save":
        save(require_arg(sys.argv, 2, "имя темы"))
    elif cmd == "load":
        load(require_arg(sys.argv, 2, "имя темы"))
    elif cmd == "list":
        list_themes()
    elif cmd in ("delete", "remove"):
        delete(require_arg(sys.argv, 2, "имя темы"))
    elif cmd == "info":
        info()
    elif cmd in ("-h", "--help"):
        print(HELP)
    else:
        apply(Path(cmd))


if __name__ == "__main__":
    main()
