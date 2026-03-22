#!/bin/bash
cp ~/.cache/wal/colors-kitty.conf ~/.config/kitty/wal-colors.conf 2>/dev/null
pkill -USR1 kitty 2>/dev/null
python3 ~/.config/quickshell/wal-zed.py 2>/dev/null
