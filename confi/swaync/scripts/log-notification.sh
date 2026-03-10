#!/usr/bin/env bash
# ~/.config/swaync/scripts/log-notification.sh
# Логирует все уведомления в ~/.local/share/swaync/history.log
# Использование: log-notification.sh APP SUMMARY BODY URGENCY

APP="${1:-unknown}"
SUMMARY="${2:-}"
BODY="${3:-}"
URGENCY="${4:-normal}"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
LOG_DIR="$HOME/.local/share/swaync"
LOG_FILE="$LOG_DIR/history.log"

mkdir -p "$LOG_DIR"

# Ограничить лог до 1000 строк
if [[ -f "$LOG_FILE" ]]; then
  LINE_COUNT=$(wc -l < "$LOG_FILE")
  if (( LINE_COUNT > 1000 )); then
    tail -n 800 "$LOG_FILE" > "${LOG_FILE}.tmp" && mv "${LOG_FILE}.tmp" "$LOG_FILE"
  fi
fi

printf '[%s] [%-8s] [%-20s] %s — %s\n' \
  "$TIMESTAMP" "$URGENCY" "$APP" "$SUMMARY" "$BODY" >> "$LOG_FILE"
