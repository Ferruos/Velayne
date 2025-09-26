import sys
import traceback
import asyncio

print("== QUICK SELFTEST ==")

try:
    import velayne.core.engine
    import velayne.infra.scheduler
    import velayne.bot.main
    import velayne.bot.ui
except Exception as e:
    print("[FAIL] Import error:", repr(e))
    traceback.print_exc()
    sys.exit(1)

async def test_sandbox():
    try:
        # Try to run sandbox with single_step or just create/cancel
        if hasattr(velayne.core.engine, "run_sandbox_loop"):
            coro = velayne.core.engine.run_sandbox_loop(0, single_step=True)
            await coro
        elif hasattr(velayne.core.engine, "start_sandbox_service"):
            # Start and then cancel
            task = asyncio.create_task(velayne.core.engine.start_sandbox_service())
            await asyncio.sleep(1)
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        else:
            print("[WARN] No sandbox coroutine found.")
    except Exception as e:
        print("[FAIL] Sandbox error:", repr(e))
        traceback.print_exc()
        sys.exit(1)

try:
    asyncio.run(test_sandbox())
except Exception as e:
    print("[FAIL] Asyncio run error:", repr(e))
    traceback.print_exc()
    sys.exit(1)

print("QUICK SELFTEST OK")
sys.exit(0)