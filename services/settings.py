import os

SETTINGS_FILE = "settings.txt"

def set_mode(mode: str):
    with open(SETTINGS_FILE, "w") as f:
        f.write(f"mode={mode}\n")

def get_mode():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE) as f:
            for line in f:
                if line.startswith("mode="):
                    return line.split("=", 1)[1].strip()
    return "sandbox"