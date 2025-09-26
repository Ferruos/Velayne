import sys
import asyncio
import traceback
import os
from velayne.core.ml import (
    load_golden_dataset,
    simulate_strategy_on_data,
    train_meta_model,
    export_sklearn_to_onnx,
    run_quick_demo,
)

def printc(msg, color="green"):
    c = {"red": "\033[91m", "green": "\033[92m", "yellow": "\033[93m", "reset": "\033[0m"}
    print(f"{c.get(color,'')}{msg}{c['reset']}", flush=True)

async def main():
    print("== Velayne Selftest ==")

    # 1. Init config / DB
    try:
        from velayne.infra.db import init_db_and_bootstrap
        await init_db_and_bootstrap()
        printc("[DB] OK: init_db_and_bootstrap", "green")
    except Exception as e:
        printc(f"[DB] FAIL: {e}", "red")
        traceback.print_exc()
        sys.exit(4)

    # 2. Golden dataset
    try:
        df = load_golden_dataset()
        assert not df.empty, "Golden dataset is empty"
        printc(f"[DATA] OK: loaded {len(df)} bars", "green")
    except Exception as e:
        printc(f"[DATA] FAIL: {e}", "red")
        traceback.print_exc()
        sys.exit(4)

    # 3. Simulate strategy
    try:
        sim = simulate_strategy_on_data(df)
        for k in ["net_pnl", "sharpe", "equity_curve", "trades"]:
            if k not in sim:
                printc(f"[SIM] FAIL: key {k} missing", "red")
                sys.exit(4)
        printc(f"[SIM] OK: trades={sim['trades']} net_pnl={sim['net_pnl']:.2f} sharpe={sim['sharpe']:.2f}", "green")
    except Exception as e:
        printc(f"[SIM] FAIL: {e}", "red")
        traceback.print_exc()
        sys.exit(4)

    # 4. Meta-model
    try:
        meta = train_meta_model(df)
        acc = meta["acc"]
        if not (0.45 <= acc <= 0.65):
            printc(f"[META] WARN: acc={acc:.3f} (expected 0.45..0.65)", "yellow")
        else:
            printc(f"[META] OK: acc={acc:.3f}", "green")
    except Exception as e:
        printc(f"[META] FAIL: {e}", "red")
        traceback.print_exc()
        sys.exit(4)

    # 5. Export ONNX
    try:
        path = export_sklearn_to_onnx(meta["model"], meta["features"])
        if not os.path.exists(path):
            printc(f"[ONNX] FAIL: file not found {path}", "red")
            sys.exit(4)
        printc(f"[ONNX] OK: {path}", "green")
    except Exception as e:
        printc(f"[ONNX] FAIL: {e}", "red")
        traceback.print_exc()
        sys.exit(4)

    printc("[SELFTEST] SUCCESS", "green")
    sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())