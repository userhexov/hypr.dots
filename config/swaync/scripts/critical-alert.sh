#!/usr/bin/env bash
# ~/.config/swaync/scripts/critical-alert.sh
# Запускается при критических уведомлениях: звук + flash экрана

SUMMARY="${1:-Критическое уведомление}"
BODY="${2:-}"

# Громкий системный звук
paplay /usr/share/sounds/freedesktop/stereo/bell.oga 2>/dev/null || \
  pw-play /usr/share/sounds/freedesktop/stereo/bell.oga 2>/dev/null

# Flash экрана через hyprctl (если доступен)
if command -v hyprctl &>/dev/null; then
  hyprctl keyword "decoration:screen_shader" "" 2>/dev/null
fi

# Логируем критическое
LOG_FILE="$HOME/.local/share/swaync/critical.log"
mkdir -p "$(dirname "$LOG_FILE")"
printf '[%s] CRITICAL: %s — %s\n' \
  "$(date '+%Y-%m-%d %H:%M:%S')" "$SUMMARY" "$BODY" >> "$LOG_FILE"
