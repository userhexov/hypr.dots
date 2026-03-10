#!/bin/bash

# Директория с обоями
WALLPAPERS_DIR="$HOME/Pictures/Wallpapers"

# Проверяем существование директории с обоями
if [ ! -d "$WALLPAPERS_DIR" ]; then
    mkdir -p "$WALLPAPERS_DIR"
    echo "[]"
    exit 0
fi

# Начинаем JSON массив
echo -n "["

first=true

# Поддерживаемые форматы
for img in "$WALLPAPERS_DIR"/*.{jpg,jpeg,png,webp}; do
    # Проверяем, существует ли файл (glob может не найти совпадений)
    [ -e "$img" ] || continue

    filename=$(basename "$img")
    name="${filename%.*}"  # имя без расширения

    # Добавляем запятую перед всеми элементами кроме первого
    if [ "$first" = true ]; then
        first=false
    else
        echo -n ","
    fi

    # Используем сам файл как превью (EWW сам уменьшит)
    echo -n "{\"name\":\"$name\",\"path\":\"$img\",\"preview\":\"$img\"}"
done

echo "]"
