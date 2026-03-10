#!/bin/bash

# Директории с темами
THEMES_DIR="$HOME/.config/eww/themes"
WALLPAPERS_DIR="$HOME/Pictures/Wallpapers"

# Создаем директорию если её нет
mkdir -p "$THEMES_DIR"
mkdir -p "$WALLPAPERS_DIR"

# Начинаем JSON массив
echo -n "["

first=true

# Функция добавления темы в JSON
add_theme() {
    local name="$1"
    local path="$2"
    local preview="$3"
    
    if [ "$first" = true ]; then
        first=false
    else
        echo -n ","
    fi
    
    echo -n "{\"name\":\"$name\",\"path\":\"$path\",\"preview\":\"$preview\"}"
}

# 1. Загружаем сохраненные темы из ~/.config/eww/themes/*.theme
for theme_file in "$THEMES_DIR"/*.theme; do
    [ -e "$theme_file" ] || continue
    
    theme_name=$(basename "$theme_file" .theme)
    wallpaper_path=$(cat "$theme_file")
    
    # Проверяем существование файла обоев
    if [ -f "$wallpaper_path" ]; then
        add_theme "$theme_name" "$wallpaper_path" "$wallpaper_path"
    fi
done

# 2. Загружаем обои из ~/Pictures/Wallpapers (если их еще нет в темах)
for img in "$WALLPAPERS_DIR"/*.{jpg,jpeg,png,webp}; do
    [ -e "$img" ] || continue
    
    filename=$(basename "$img")
    name="${filename%.*}"
    
    # Проверяем, не существует ли уже тема с таким именем
    if [ ! -f "$THEMES_DIR/${name}.theme" ]; then
        add_theme "$name" "$img" "$img"
    fi
done

echo "]"
