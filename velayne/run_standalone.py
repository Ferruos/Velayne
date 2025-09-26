import asyncio
import os
import sys
import traceback
import signal

print("=== RUN_STANDALONE ENTRY ===", flush=True)

def flush_dataio_buffers():
    try:
        from velayne.infra.perf import flush_all_dataio_buffers
        flush_all_dataio_buffers()
    except Exception:
        pass

async def main():
    try:
        from velayne.core.engine import start_sandbox_service
    except Exception as e:
        print("[FATAL] Failed to import start_sandbox_service:", repr(e), flush=True)
        traceback.print_exc()
        return 1

    try:
        from velayne.infra.scheduler import start_scheduler
    except Exception as e:
        print("[WARN] Failed to import start_scheduler:", repr(e), flush=True)
        traceback.print_exc()
        start_scheduler = None

    try:
        from velayne.bot.main import start_bot
    except Exception as e:
        print("[WARN] Failed to import start_bot (bot will be disabled):", repr(e), flush=True)
        traceback.print_exc()
        start_bot = None

    try:
        from velayne.infra.config import settings
        tg_token = os.environ.get("TG_TOKEN") or getattr(settings, "TG_TOKEN", None)
    except Exception as e:
        print("[WARN] Failed to get TG_TOKEN from settings:", repr(e), flush=True)
        traceback.print_exc()
        tg_token = None

    if tg_token:
        print("[INFO] TG_TOKEN is set, bot will start.", flush=True)
    else:
        print("[INFO] TG_TOKEN is empty, bot will NOT start.", flush=True)

    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def stop_signal(*_):
        print("[SIGNAL] Stop requested", flush=True)
        try:
            flush_dataio_buffers()
        except Exception:
            pass
        stop_event.set()

    try:
        loop.add_signal_handler(signal.SIGINT, stop_signal)
        loop.add_signal_handler(signal.SIGTERM, stop_signal)
    except Exception:
        pass

    tasks = []

    tasks.append(asyncio.create_task(start_sandbox_service(), name="sandbox"))

    if start_scheduler is not None:
        tasks.append(asyncio.create_task(start_scheduler(), name="scheduler"))

    if tg_token and start_bot is not None:
        tasks.append(asyncio.create_task(start_bot(), name="bot"))
    else:
        print("[INFO] Bot disabled (no TG_TOKEN or import failed)", flush=True)

    async def heartbeat():
        while not stop_event.is_set():
            print("[HEARTBEAT] alive", flush=True)
            await asyncio.sleep(5)
    tasks.append(asyncio.create_task(heartbeat(), name="heartbeat"))

    async def watcher():
        while not stop_event.is_set():
            done, pending = await asyncio.wait(tasks, timeout=1.0, return_when=asyncio.FIRST_EXCEPTION)
            for d in done:
                exc = d.exception()
                if exc:
                    print(f"[TASK-CRASH] {d.get_name()}: {repr(exc)}", flush=True)
                    traceback.print_exc()
            await asyncio.sleep(1)
    watch_task = asyncio.create_task(watcher(), name="watcher")

    await stop_event.wait()
    for t in tasks:
        t.cancel()
    watch_task.cancel()
    try:
        flush_dataio_buffers()
    except Exception:
        pass
    print("[EXIT] graceful shutdown", flush=True)
    return 0

if __name__ == "__main__":
    try:
        rc = asyncio.run(main())
    except Exception as e:
        print("[FATAL] Top-level crash:", repr(e), flush=True)
        traceback.print_exc()
        rc = 1
    print(f"[EXIT CODE] {rc}", flush=True)
    sys.exit(rc)