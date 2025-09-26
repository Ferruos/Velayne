import sys
import os
import argparse
import importlib
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()
    verbose = args.verbose

    from velayne.infra.logger import setup_logging
    setup_logging()

    status = []
    ok = True

    # Python version
    if sys.version_info < (3, 11):
        status.append(("python", False, f"Python >=3.11 required, found {sys.version}"))
        ok = False
    else:
        status.append(("python", True, f"{sys.version}"))

    # pydantic-settings
    try:
        from pydantic_settings import BaseSettings
        _ = BaseSettings()
        status.append(("pydantic-settings", True, "OK (v2)"))
    except Exception as e:
        status.append(("pydantic-settings", False, f"Import error: {e}"))
        ok = False

    # onnx/onnxruntime
    try:
        import onnx
        import onnxruntime
        status.append(("onnx", True, f"OK ({onnx.__version__})"))
        status.append(("onnxruntime", True, f"OK ({onnxruntime.__version__})"))
    except Exception as e:
        status.append(("onnx/onnxruntime", False, f"Missing: {e}. Run: pip install onnx==1.18 onnxruntime==1.18"))
        ok = False

    # TG_TOKEN
    from velayne.infra.config import get_settings
    settings = get_settings()
    token_status = "OK" if settings.TG_TOKEN else "пусто"
    status.append(("TG_TOKEN", True, token_status))

    # LOG_DIR/DATA_DIR
    for d in [settings.LOG_DIR, settings.DATA_DIR]:
        try:
            Path(d).mkdir(parents=True, exist_ok=True)
            status.append((f"dir:{d}", True, "OK"))
        except Exception as e:
            status.append((f"dir:{d}", False, f"Cannot create: {e}"))
            ok = False

    # onnx model presence
    model_path = Path(settings.DATA_DIR) / "models" / "signal.onnx"
    need_model_build = False
    if not model_path.exists():
        need_model_build = True
        status.append(("ML model", False, f"Not found: {model_path}"))
    else:
        status.append(("ML model", True, str(model_path)))

    # UI mode_switch_message
    try:
        ui = importlib.import_module("velayne.bot.ui")
        if not hasattr(ui, "mode_switch_message"):
            raise ImportError("mode_switch_message not found")
        status.append(("ui.mode_switch_message", True, "OK"))
    except Exception as e:
        status.append(("ui.mode_switch_message", False, f"Import error: {e}"))
        ok = False

    # Verbose output
    if verbose:
        print("=== Velayne Preflight Diagnostics ===")
        for name, isok, detail in status:
            print(f"{'[OK]' if isok else '[FAIL]'} {name}: {detail}")
        if need_model_build:
            print("ML model отсутствует: будет создан автоматически при первом запуске.")
        print("TG_TOKEN:", token_status)
        print("=====================================")

    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()