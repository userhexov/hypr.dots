#!/usr/bin/env python3
"""
menu.py — интерактивное TUI меню управления темами.

Навигация:
  ↑↓ / j k  — перемещение
  Enter       — выбрать
  Esc / q     — назад / выход
"""

import curses
import math
import subprocess
from pathlib import Path

import main
from config import Paths, Tools

# ══════════════════════════════════════════════════════════════════════════════
# Константы сетки тем
# ══════════════════════════════════════════════════════════════════════════════

BOX_W        = 22
BOX_H        = 8
BOXES_PER_ROW = 4
PREVIEW_W    = 18
PREVIEW_H    = 4
PAD_X        = 2    # отступ превью внутри бокса по X
PAD_Y        = 1    # отступ превью внутри бокса по Y

# ══════════════════════════════════════════════════════════════════════════════
# Цветовые пары (инициализируются в init_colors)
# ══════════════════════════════════════════════════════════════════════════════

CP_NORMAL   = 1   # обычный текст
CP_SELECTED = 2   # выбранный элемент
CP_HEADER   = 3   # заголовок
CP_HINT     = 4   # подсказки
CP_OK       = 5   # успех (зелёный)
CP_ERR      = 6   # ошибка (красный)
CP_DIM      = 7   # приглушённый


def init_colors() -> None:
    curses.start_color()
    curses.use_default_colors()

    curses.init_pair(CP_NORMAL,   curses.COLOR_WHITE,  -1)
    curses.init_pair(CP_SELECTED, curses.COLOR_BLACK,  curses.COLOR_CYAN)
    curses.init_pair(CP_HEADER,   curses.COLOR_CYAN,   -1)
    curses.init_pair(CP_HINT,     curses.COLOR_BLACK,  -1)
    curses.init_pair(CP_OK,       curses.COLOR_GREEN,  -1)
    curses.init_pair(CP_ERR,      curses.COLOR_RED,    -1)
    curses.init_pair(CP_DIM,      curses.COLOR_WHITE,  -1)


# ══════════════════════════════════════════════════════════════════════════════
# Kitty preview
# ══════════════════════════════════════════════════════════════════════════════

def clear_previews() -> None:
    if Tools.has_kitty():
        subprocess.run("kitty +kitten icat --clear", shell=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def kitty_preview(image_path: str, x: int, y: int) -> None:
    if not Tools.has_kitty() or not Path(image_path).exists():
        return
    cmd = (
        f"kitty +kitten icat --transfer-mode file "
        f"--place {PREVIEW_W}x{PREVIEW_H}@{x}x{y} '{image_path}'"
    )
    subprocess.run(cmd, shell=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# ══════════════════════════════════════════════════════════════════════════════
# Вспомогательные функции отрисовки
# ══════════════════════════════════════════════════════════════════════════════

def safe_addstr(stdscr, y: int, x: int, text: str, attr: int = 0) -> None:
    """addstr без выхода за границы экрана."""
    h, w = stdscr.getmaxyx()
    if y < 0 or y >= h or x < 0 or x >= w:
        return
    max_len = w - x
    try:
        stdscr.addstr(y, x, text[:max_len], attr)
    except curses.error:
        pass


def draw_header(stdscr, title: str) -> None:
    """Рисует верхний заголовок на всю ширину."""
    h, w = stdscr.getmaxyx()
    bar = f"  {title}  ".center(w)
    safe_addstr(stdscr, 0, 0, bar, curses.color_pair(CP_HEADER) | curses.A_BOLD)


def draw_footer(stdscr, hints: str) -> None:
    """Рисует нижнюю строку с подсказками по клавишам."""
    h, w = stdscr.getmaxyx()
    bar = f"  {hints}  ".ljust(w)
    safe_addstr(stdscr, h - 1, 0, bar,
                curses.color_pair(CP_HINT) | curses.A_REVERSE | curses.A_DIM)


def draw_status(stdscr, msg: str, is_error: bool = False) -> None:
    """Рисует сообщение статуса в предпоследней строке."""
    h, w = stdscr.getmaxyx()
    attr = curses.color_pair(CP_ERR if is_error else CP_OK) | curses.A_BOLD
    safe_addstr(stdscr, h - 2, 2, msg.ljust(w - 4), attr)


def draw_box(
    stdscr,
    top: int,
    left: int,
    width: int,
    height: int,
    label: str = "",
    selected: bool = False,
) -> None:
    """Рисует рамку бокса с подписью снизу."""
    attr_border = (
        curses.color_pair(CP_SELECTED) | curses.A_BOLD
        if selected
        else curses.color_pair(CP_NORMAL)
    )
    attr_label = (
        curses.color_pair(CP_SELECTED) | curses.A_BOLD
        if selected
        else curses.color_pair(CP_NORMAL) | curses.A_BOLD
    )

    inner = width - 2

    # Рамка
    safe_addstr(stdscr, top,             left, f"╭{'─' * inner}╮", attr_border)
    for i in range(1, height - 1):
        safe_addstr(stdscr, top + i,     left, f"│{' ' * inner}│", attr_border)
    safe_addstr(stdscr, top + height - 1, left, f"╰{'─' * inner}╯", attr_border)

    # Подпись (центрирована, нижняя внутренняя строка)
    label_row = top + height - 2
    label_col = left + 1 + max(0, (inner - len(label)) // 2)
    safe_addstr(stdscr, label_row, label_col, label[:inner], attr_label)


def draw_menu_item(
    stdscr,
    y: int,
    x: int,
    text: str,
    selected: bool,
) -> None:
    """Рисует один пункт вертикального меню в рамке."""
    inner = len(text) + 2
    if selected:
        attr_box   = curses.color_pair(CP_SELECTED) | curses.A_BOLD
        attr_text  = curses.color_pair(CP_SELECTED) | curses.A_BOLD
    else:
        attr_box   = curses.color_pair(CP_NORMAL)
        attr_text  = curses.color_pair(CP_NORMAL)

    safe_addstr(stdscr, y,     x, f"╭{'─' * inner}╮", attr_box)
    safe_addstr(stdscr, y + 1, x, f"│ {text} │",       attr_text)
    safe_addstr(stdscr, y + 2, x, f"╰{'─' * inner}╯", attr_box)


# ══════════════════════════════════════════════════════════════════════════════
# Сетка тем
# ══════════════════════════════════════════════════════════════════════════════

def draw_theme_grid(
    stdscr,
    themes: list[str],
    selected_idx: int,
    status: str = "",
    status_error: bool = False,
) -> None:
    """Отрисовывает сетку тем с превью."""
    stdscr.erase()

    draw_header(stdscr, "  Темы оформления")
    draw_footer(stdscr, "↑↓←→ / hjkl  навигация  │  Enter  выбрать  │  Esc  назад")

    if status:
        draw_status(stdscr, status, status_error)

    clear_previews()

    for idx, name in enumerate(themes):
        row = idx // BOXES_PER_ROW
        col = idx % BOXES_PER_ROW
        top  = 2 + row * (BOX_H + 1)
        left = 2 + col * (BOX_W + 2)

        draw_box(stdscr, top, left, BOX_W, BOX_H,
                 label=name, selected=(idx == selected_idx))

        img_file = Paths.EWW_THEMES_DIR / f"{name}.theme"
        if img_file.exists():
            kitty_preview(
                img_file.read_text().strip(),
                x=left + PAD_X,
                y=top  + PAD_Y,
            )

    stdscr.refresh()


def theme_grid_menu(stdscr, action: str = "load") -> str | None:
    """
    Интерактивная сетка тем.
    action: "load" | "delete"
    Возвращает имя выбранной темы или None при отмене.
    """
    themes = sorted(t.stem for t in Paths.EWW_THEMES_DIR.glob("*.theme"))
    if not themes:
        stdscr.erase()
        draw_header(stdscr, "Темы оформления")
        safe_addstr(stdscr, 3, 4, "Нет сохранённых тем.",
                    curses.color_pair(CP_ERR) | curses.A_BOLD)
        draw_footer(stdscr, "Esc  назад")
        stdscr.refresh()
        stdscr.getch()
        return None

    idx     = 0
    status  = ""
    is_err  = False

    while True:
        draw_theme_grid(stdscr, themes, idx, status, is_err)
        status = ""

        key = stdscr.getch()

        if key in (curses.KEY_UP, ord("k")):
            idx = max(0, idx - BOXES_PER_ROW)

        elif key in (curses.KEY_DOWN, ord("j")):
            idx = min(len(themes) - 1, idx + BOXES_PER_ROW)

        elif key in (curses.KEY_LEFT, ord("h")):
            idx = max(0, idx - 1)

        elif key in (curses.KEY_RIGHT, ord("l")):
            idx = min(len(themes) - 1, idx + 1)

        elif key in (curses.KEY_ENTER, ord("\n")):
            name = themes[idx]

            if action == "load":
                clear_previews()
                main.load(name)
                return name

            elif action == "delete":
                clear_previews()
                curses.endwin()
                confirm = input(
                    f"\nУдалить тему '{name}'? [y/N]: "
                ).strip().lower()
                if confirm == "y":
                    main.delete(name)
                    themes.pop(idx)
                    idx = min(idx, len(themes) - 1)
                    if not themes:
                        return None
                stdscr = curses.initscr()
                init_colors()
                curses.curs_set(0)

        elif key in (27, ord("q")):   # Esc или q
            clear_previews()
            return None


# ══════════════════════════════════════════════════════════════════════════════
# Главное меню
# ══════════════════════════════════════════════════════════════════════════════

MENU_ITEMS = [
    ("Применить тему",    "Выбрать изображение и применить"),
    ("Загрузить тему",    "Выбрать из сохранённых тем"),
    ("Сохранить тему",    "Сохранить текущую тему"),
    ("Удалить тему",      "Удалить сохранённую тему"),
    ("Информация",        "Показать установленные инструменты"),
    ("Выход",             ""),
]


def draw_main_menu(stdscr, selected_idx: int, status: str = "", is_err: bool = False) -> None:
    stdscr.erase()
    draw_header(stdscr, "  Менеджер тем")
    draw_footer(stdscr, "↑↓ / jk  навигация  │  Enter  выбрать  │  q  выход")

    if status:
        draw_status(stdscr, status, is_err)

    for idx, (title, subtitle) in enumerate(MENU_ITEMS):
        y = 2 + idx * 3
        draw_menu_item(stdscr, y, 4, title, selected=(idx == selected_idx))

        if subtitle:
            safe_addstr(stdscr, y + 1, 4 + len(title) + 6, subtitle,
                        curses.color_pair(CP_DIM) | curses.A_DIM)

    stdscr.refresh()


def main_menu(stdscr) -> None:
    init_colors()
    curses.curs_set(0)

    idx    = 0
    status = ""
    is_err = False

    while True:
        draw_main_menu(stdscr, idx, status, is_err)
        status = ""
        is_err = False

        key = stdscr.getch()

        if key in (curses.KEY_UP, ord("k")):
            idx = (idx - 1) % len(MENU_ITEMS)

        elif key in (curses.KEY_DOWN, ord("j")):
            idx = (idx + 1) % len(MENU_ITEMS)

        elif key in (curses.KEY_ENTER, ord("\n")):
            choice = MENU_ITEMS[idx][0]

            if choice == "Применить тему":
                curses.endwin()
                path = input("\nПуть к изображению: ").strip()
                if path:
                    ok_result = main.apply(Path(path))
                    status = f"Тема применена: {path}" if ok_result else f"Ошибка при применении"
                    is_err = not ok_result
                stdscr = curses.initscr()
                init_colors()
                curses.curs_set(0)

            elif choice == "Загрузить тему":
                name = theme_grid_menu(stdscr, action="load")
                if name:
                    status = f"Тема '{name}' загружена"

            elif choice == "Сохранить тему":
                curses.endwin()
                name = input("\nИмя темы: ").strip()
                if name:
                    ok_result = main.save(name)
                    status = f"Тема '{name}' сохранена" if ok_result else "Ошибка при сохранении"
                    is_err = not ok_result
                stdscr = curses.initscr()
                init_colors()
                curses.curs_set(0)

            elif choice == "Удалить тему":
                theme_grid_menu(stdscr, action="delete")
                status = "Тема удалена"

            elif choice == "Информация":
                curses.endwin()
                main.info()
                input("Нажми Enter для продолжения...")
                stdscr = curses.initscr()
                init_colors()
                curses.curs_set(0)

            elif choice == "Выход":
                clear_previews()
                break

        elif key in (27, ord("q")):
            clear_previews()
            break


# ══════════════════════════════════════════════════════════════════════════════
# Точка входа
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    curses.wrapper(main_menu)
