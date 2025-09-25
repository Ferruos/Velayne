import os

MODE_FILE = "trade_mode.txt"

def set_mode(mode):
    with open(MODE_FILE, "w") as f:
        f.write(mode)

def get_mode():
    if not os.path.exists(MODE_FILE):
        return "sandbox"
    with open(MODE_FILE) as f:
        return f.read().strip()