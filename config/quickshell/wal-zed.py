import json, os
c = json.load(open(os.path.expanduser("~/.cache/wal/colors.json")))
bg = c["special"]["background"]
fg = c["special"]["foreground"]
c1 = c["colors"]["color1"]
c2 = c["colors"]["color2"]
c4 = c["colors"]["color4"]
c5 = c["colors"]["color5"]
c8 = c["colors"]["color8"]
os.makedirs(os.path.expanduser("~/.config/zed/themes"), exist_ok=True)
t = {
    "name": "wal",
    "author": "pywal",
    "themes": [{
        "name": "wal",
        "appearance": "dark",
        "style": {
            "background": bg,
            "editor.background": bg,
            "editor.foreground": fg,
            "terminal.background": bg,
            "terminal.foreground": fg,
            "tab_bar.background": bg,
            "toolbar.background": bg,
            "border": c8,
            "text": fg,
            "text.muted": c8,
            "syntax": {
                "keyword": {"color": c1},
                "string": {"color": c2},
                "function": {"color": c5},
                "type": {"color": c4},
                "comment": {"color": c8}
            }
        }
    }]
}
json.dump(t, open(os.path.expanduser("~/.config/zed/themes/wal.json"), "w"), indent=2)
print("Zed theme updated")
