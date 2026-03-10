"""
color_utils.py — утилиты для работы с цветами.

Используется для подбора читаемых комбинаций цветов
в Rofi, Zed, Obsidian и других приложениях.
"""


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """#rrggbb → (r, g, b)"""
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02x}{g:02x}{b:02x}"


def luminance(hex_color: str) -> float:
    def channel(c: int) -> float:
        v = c / 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4

    r, g, b = hex_to_rgb(hex_color)
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def contrast_ratio(a: str, b: str) -> float:
    la, lb = luminance(a) + 0.05, luminance(b) + 0.05
    return max(la, lb) / min(la, lb)


def readable_fg(bg: str, light: str = "#ffffff", dark: str = "#1a1a1a") -> str:
    return light if contrast_ratio(bg, light) >= contrast_ratio(bg, dark) else dark


def darken(hex_color: str, amount: float = 0.15) -> str:
    r, g, b = hex_to_rgb(hex_color)
    f = 1 - amount
    return rgb_to_hex(int(r * f), int(g * f), int(b * f))


def lighten(hex_color: str, amount: float = 0.15) -> str:
    r, g, b = hex_to_rgb(hex_color)
    return rgb_to_hex(
        min(255, int(r + (255 - r) * amount)),
        min(255, int(g + (255 - g) * amount)),
        min(255, int(b + (255 - b) * amount)),
    )


def mix(a: str, b: str, ratio: float = 0.5) -> str:
    ra, ga, ba = hex_to_rgb(a)
    rb, gb, bb = hex_to_rgb(b)
    return rgb_to_hex(
        int(ra + (rb - ra) * ratio),
        int(ga + (gb - ga) * ratio),
        int(ba + (bb - ba) * ratio),
    )


def alpha_rgba(hex_color: str, opacity: float) -> str:
    """hex + opacity → rgba(r, g, b, alpha) для CSS/Firefox."""
    r, g, b = hex_to_rgb(hex_color)
    return f"rgba({r}, {g}, {b}, {opacity:.2f})"


def hex_add_alpha(hex_color: str, opacity: float) -> str:
    """
    hex + opacity → #rrggbbaa (формат Rofi).
    Rofi принимает rrggbbaa, НЕ aarrggbb и НЕ rgba().
    """
    r, g, b = hex_to_rgb(hex_color)
    a = int(opacity * 255)
    return f"#{r:02x}{g:02x}{b:02x}{a:02x}"


def saturation(hex_color: str) -> float:
    """Насыщенность (0.0–1.0) по модели HSL."""
    r, g, b = (c / 255.0 for c in hex_to_rgb(hex_color))
    cmax, cmin = max(r, g, b), min(r, g, b)
    delta = cmax - cmin
    if delta == 0:
        return 0.0
    lightness = (cmax + cmin) / 2
    return delta / (1 - abs(2 * lightness - 1))


def pick_darkest(colors: dict, candidates: list[str]) -> str:
    """Самый тёмный цвет из списка ключей."""
    return min(candidates, key=lambda k: luminance(colors[k]))


def pick_lightest(colors: dict, candidates: list[str]) -> str:
    """Самый светлый цвет из списка ключей."""
    return max(candidates, key=lambda k: luminance(colors[k]))


def pick_most_saturated(colors: dict, candidates: list[str]) -> str:
    """Наиболее насыщенный цвет из списка ключей."""
    return max(candidates, key=lambda k: saturation(colors[k]))


def pick_best_accent(colors: dict, bg_key: str = "background") -> str:
    """
    Лучший акцентный цвет из color1–color15:
    максимальная насыщенность + контраст к фону ≥ 3.0.
    """
    bg = colors[bg_key]
    candidates = [f"color{i}" for i in range(1, 16)]
    good = [k for k in candidates if contrast_ratio(colors[k], bg) >= 3.0]
    pool = good if good else candidates
    return colors[pick_most_saturated(colors, pool)]


def build_rofi_palette(colors: dict) -> dict:
    bg = darken(colors["color0"], 0.10)
    bg_alt = mix(colors["color0"], colors["color1"], 0.4)
    accent = colors["color4"]
    fg = colors["foreground"]
    if contrast_ratio(fg, bg) < 4.5:
        fg = readable_fg(bg)
    return {
        "bg": bg,
        "bg_alt": bg_alt,
        "fg": fg,
        "accent": accent,
        "fg_on_accent": readable_fg(accent),
        "border": accent,
        "urgent": colors.get("color1", "#ff5555"),
        "placeholder": mix(fg, bg, 0.5),
    }


def build_zed_palette(colors: dict) -> dict:
    bg = colors["color0"]
    fg = colors["foreground"]
    if contrast_ratio(fg, bg) < 4.5:
        fg = readable_fg(bg)
    accent = colors["color4"]
    return {
        "bg": bg,
        "bg_panel": mix(colors["color0"], colors["color1"], 0.5),
        "bg_elevated": lighten(bg, 0.08),
        "bg_selection": alpha(accent, 0.25),
        "fg": fg,
        "fg_muted": mix(fg, bg, 0.4),
        "accent": accent,
        "accent_text": readable_fg(accent),
        "border": mix(accent, bg, 0.6),
        "error": colors.get("color1", "#ff5555"),
        "warning": colors.get("color3", "#f1fa8c"),
        "success": colors.get("color2", "#50fa7b"),
        "string": colors.get("color2", "#50fa7b"),
        "keyword": colors.get("color5", "#bd93f9"),
        "comment": mix(fg, bg, 0.45),
        "constant": colors.get("color3", "#f1fa8c"),
        "function": colors.get("color4", "#8be9fd"),
        "type_": colors.get("color6", "#8be9fd"),
    }


def build_obsidian_palette(colors: dict) -> dict:
    bg = colors["color0"]
    accent = colors["color4"]
    fg = colors["foreground"]
    if contrast_ratio(fg, bg) < 4.5:
        fg = readable_fg(bg)
    return {
        "bg_primary": bg,
        "bg_secondary": lighten(bg, 0.05),
        "bg_tertiary": lighten(bg, 0.10),
        "fg_primary": fg,
        "fg_muted": mix(fg, bg, 0.4),
        "accent": accent,
        "accent_hover": lighten(accent, 0.12),
        "border": mix(accent, bg, 0.7),
        "link": colors.get("color4", "#8be9fd"),
        "tag": colors.get("color5", "#bd93f9"),
        "highlight": alpha(accent, 0.20),
    }
