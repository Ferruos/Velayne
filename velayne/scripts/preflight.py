import sys
import os
import traceback

def printc(text, color="green"):
    c = {"red": "\033[91m", "green": "\033[92m", "reset": "\033[0m"}
    print(f"{c.get(color,'')}{text}{c['reset']}")

def main():
    verbose = "--verbose" in sys.argv
    ok = True

    def vprint(*args):
        if verbose:
            print(*args)

    # 1. Python >= 3.11
    vprint("Проверка Python >= 3.11 ...")
    if sys.version_info < (3, 11):
        printc("Требуется Python 3.11+", "red")
        ok = False

    # 2. Импорт pydantic_settings
    try:
        import pydantic_settings
        import pydantic
        vprint(f"pydantic: {pydantic.__version__}, pydantic_settings: {pydantic_settings.__version__}")
        if not hasattr(pydantic_settings, "BaseSettings"):
            raise ImportError("BaseSettings moved")
    except Exception:
        printc("Ошибка: Не найден pydantic-settings (pip install pydantic-settings)", "red")
        printc("pip install pydantic-settings pydantic>=2.7", "red")
        ok = False

    # 3. Импорт onnx и onnxruntime
    try:
        import onnx
        import onnxruntime
        vprint(f"onnx: {onnx.__version__}, onnxruntime: {onnxruntime.__version__}")
    except Exception:
        printc("Ошибка: Не найден onnx/onnxruntime. pip install onnx onnxruntime", "red")
        ok = False

    # 4. requirements.txt
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    req = os.path.join(root, "requirements.txt")
    vprint(f"Путь к requirements.txt: {req}")
    if not os.path.isfile(req):
        printc(f"Не найден requirements.txt по пути {req}", "red")
        ok = False

    # 5. Импорт velayne
    try:
        import velayne
        vprint("Импорт velayne: OK")
    except Exception as e:
        printc("Ошибка импорта velayne: " + str(e), "red")
        ok = False

    # 6. Логи и дата
    try:
        from velayne.infra.paths import data_dir, logs_dir, ensure_utf8_stdio
        d = data_dir()
        l = logs_dir()
        vprint(f"data_dir: {d}, logs_dir: {l}")
        ensure_utf8_stdio()
    except Exception as e:
        printc("Ошибка создания папок data/logs: " + str(e), "red")
        ok = False

    # 7. Проверка mode_switch_message
    try:
        from velayne.bot import ui
        assert hasattr(ui, "mode_switch_message")
        vprint("mode_switch_message: OK")
    except Exception:
        printc("Ошибка: Не найдена функция mode_switch_message в velayne/bot/ui.py", "red")
        ok = False

    if ok:
        printc("Префлайт успешно пройден", "green")
        sys.exit(0)
    else:
        printc("Префлайт провалился. Исправьте ошибки выше.", "red")
        sys.exit(1)

if __name__ == "__main__":
    main()