from pathlib import Path
import sys
import os

def project_root() -> Path:
    # Ищет requirements.txt или папку velayne
    here = Path(__file__).resolve().parent
    for p in [here, *here.parents]:
        if (p / "requirements.txt").exists() and (p / "velayne").is_dir():
            return p
    raise RuntimeError("Не удалось найти корень проекта (requirements.txt + velayne/)")

def data_dir() -> Path:
    d = os.getenv("DATA_DIR", str(project_root() / "data"))
    p = Path(d)
    p.mkdir(parents=True, exist_ok=True)
    return p

def logs_dir() -> Path:
    d = os.getenv("LOG_DIR", str(project_root() / "logs"))
    p = Path(d)
    p.mkdir(parents=True, exist_ok=True)
    return p

def ensure_utf8_stdio():
    # Для Windows: python может не печатать utf-8 по умолчанию
    if os.name == "nt":
        import sys
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')