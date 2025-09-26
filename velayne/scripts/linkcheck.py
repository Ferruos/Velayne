import ast
import os
import sys
from pathlib import Path
import logging
import shutil

PKG = "velayne"
IGNORED = ["__init__.py", "tests", "migrations"]

def find_py_files(root: Path):
    pyfiles = []
    for p in root.rglob("*.py"):
        if any(ig in str(p) for ig in IGNORED):
            continue
        pyfiles.append(p)
    return pyfiles

def find_imports(pyfile: Path):
    with open(pyfile, encoding="utf-8") as f:
        src = f.read()
    try:
        tree = ast.parse(src, filename=str(pyfile))
    except Exception:
        return []
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith(PKG):
                for n in node.names:
                    imports.append((node.module, n.name, pyfile))
    return imports

def has_symbol(pyfile: Path, symbol: str) -> bool:
    with open(pyfile, encoding="utf-8") as f:
        src = f.read()
    # crude: look for def or class at root
    for line in src.splitlines():
        if line.strip().startswith(f"def {symbol}(") or line.strip().startswith(f"class {symbol}("):
            return True
        if line.strip().startswith(f"async def {symbol}("):
            return True
    return False

def append_stub_ui(pyfile: Path, name: str):
    with open(pyfile, encoding="utf-8") as f:
        src = f.read()
    stub = f"\ndef {name}(*args, **kwargs):\n    return \"<{name} placeholder (auto-generated)>\"\n"
    if stub in src:
        return False
    shutil.copy2(pyfile, str(pyfile) + ".bak")
    with open(pyfile, "a", encoding="utf-8") as f:
        f.write(stub)
    logging.warning(f"[STUB] Added stub UI func: {name} in {pyfile}")
    return True

def append_stub_db(pyfile: Path, name: str):
    with open(pyfile, encoding="utf-8") as f:
        src = f.read()
    stub = (
        f"\nimport logging\n"
        f"async def {name}(*args, **kwargs):\n"
        f"    logging.warning('[STUB] DB func {name} called')\n"
        f"    return None\n"
    )
    if f"def {name}(" in src or f"async def {name}(" in src:
        return False
    shutil.copy2(pyfile, str(pyfile) + ".bak")
    with open(pyfile, "a", encoding="utf-8") as f:
        f.write(stub)
    logging.warning(f"[STUB] Added stub DB func: {name} in {pyfile}")
    return True

def append_stub_generic(pyfile: Path, name: str):
    with open(pyfile, encoding="utf-8") as f:
        src = f.read()
    stub = (
        f"\nimport logging\n"
        f"def {name}(*args, **kwargs):\n"
        f"    logging.warning('[STUB] Generic func {name} called')\n"
        f"    return None\n"
    )
    if f"def {name}(" in src or f"async def {name}(" in src:
        return False
    shutil.copy2(pyfile, str(pyfile) + ".bak")
    with open(pyfile, "a", encoding="utf-8") as f:
        f.write(stub)
    logging.warning(f"[STUB] Added stub generic func: {name} in {pyfile}")
    return True

def main():
    logging.basicConfig(level=logging.INFO)
    root = Path(__file__).parent.parent / PKG
    pyfiles = find_py_files(root)
    created = []
    for pyfile in pyfiles:
        imports = find_imports(pyfile)
        for mod, symbol, usefile in imports:
            modfile = root / Path(*mod.split("."))  # velayne/bot/ui.py
            modfile = modfile.with_suffix(".py")
            if not modfile.exists():
                continue
            if has_symbol(modfile, symbol):
                continue
            if mod == "velayne.bot.ui":
                append_stub_ui(modfile, symbol)
                created.append((mod, symbol, modfile))
            elif mod == "velayne.infra.db":
                append_stub_db(modfile, symbol)
                created.append((mod, symbol, modfile))
            else:
                append_stub_generic(modfile, symbol)
                created.append((mod, symbol, modfile))
    if created:
        print("CREATED STUBS:")
        for mod, symbol, modfile in created:
            print(f"  {mod}.{symbol} in {modfile}")
    else:
        print("No missing imports detected.")
    sys.exit(0)

if __name__ == "__main__":
    main()