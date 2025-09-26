import asyncio
import signal
import sys
from velayne.infra.logger import setup_logging, logger

def _print_menu():
    print("\n[Velayne] Меню управления:")
    print("[Q]uit  [R]estart Sandbox  [D]iagnostics  [S]elftest  [P]erf summary\n")

async def menu_input(sandbox_restart, show_diag, run_selftest, show_perf, shutdown_flag):
    import threading
    def input_thread():
        while not shutdown_flag["stop"]:
            try:
                cmd = input().strip().lower()
                if cmd == "q":
                    shutdown_flag["stop"] = True
                elif cmd == "r":
                    sandbox_restart()
                elif cmd == "d":
                    show_diag()
                elif cmd == "s":
                    run_selftest()
                elif cmd == "p":
                    show_perf()
            except EOFError:
                break
    th = threading.Thread(target=input_thread, daemon=True)
    th.start()

async def selftest():
    from velayne.scripts import preflight
    import time

    print("[SELFTEST] Префлайт...")
    try:
        preflight.main()
    except SystemExit as e:
        if e.code != 0:
            print("[SELFTEST] Preflight FAILED")
            return {"ok": False, "step": "preflight", "error": "preflight fail"}
    except Exception as e:
        print(f"[SELFTEST] Preflight exception: {e}")
        return {"ok": False, "step": "preflight", "error": str(e)}

    print("[SELFTEST] Sandbox тик...")
    try:
        from velayne.core.engine import run_sandbox_loop, stop_sandbox_service
        async def quick_sandbox():
            task = asyncio.create_task(run_sandbox_loop(0))
            await asyncio.sleep(3)
            await stop_sandbox_service()
            return True
        await quick_sandbox()
    except Exception as e:
        print(f"[SELFTEST] Sandbox FAIL: {e}")
        return {"ok": False, "step": "sandbox", "error": str(e)}

    print("[SELFTEST] Scheduler...")
    try:
        from velayne.infra.scheduler import start_scheduler
        async def check_sched():
            task = asyncio.create_task(start_scheduler())
            await asyncio.sleep(2)
            task.cancel()
            return True
        await check_sched()
    except Exception as e:
        print(f"[SELFTEST] Scheduler FAIL: {e}")
        return {"ok": False, "step": "scheduler", "error": str(e)}

    print("[SELFTEST] TG_TOKEN/init...")
    try:
        from velayne.infra.config import get_settings
        tg_token = get_settings().TG_TOKEN
        if tg_token:
            from aiogram import Bot
            bot = Bot(token=tg_token)
            me = await bot.get_me()
            print(f"[SELFTEST] TG OK: @{me.username}")
        else:
            print("[SELFTEST] TG_TOKEN не задан — бот не проверяется.")
    except Exception as e:
        print(f"[SELFTEST] Bot FAIL: {e}")
        return {"ok": False, "step": "tg", "error": str(e)}

    print("SELFTEST OK")
    return {"ok": True, "step": "all"}

def show_perf_summary():
    from velayne.infra.perf import get_perf_summary
    import pprint
    print("\n=== PERF SUMMARY ===")
    pprint.pprint(get_perf_summary())

async def main():
    import importlib

    setup_logging()
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--selftest', action='store_true')
    args = parser.parse_args()

    if args.selftest:
        res = await selftest()
        if res["ok"]:
            print("SELFTEST OK")
            sys.exit(0)
        else:
            print(f"SELFTEST FAIL: {res}")
            sys.exit(1)

    print("\n=== Velayne Service Unified Launcher ===")
    _print_menu()

    # Preflight
    import velayne.scripts.preflight
    try:
        velayne.scripts.preflight.main()
    except SystemExit as e:
        if e.code != 0:
            logger.error("Preflight check failed. Исправьте ошибки и перезапустите.")
            sys.exit(1)

    import velayne.bot.main
    import velayne.infra.scheduler
    import velayne.core.engine

    shutdown_flag = {"stop": False}
    tasks = {}

    async def start_bot_task():
        from velayne.infra.config import get_settings
        tg_token = get_settings().TG_TOKEN
        if not tg_token:
            logger.warning("TG_TOKEN пуст — бот не запущен.")
            return
        await velayne.bot.main.start_bot()

    async def start_scheduler_task():
        await velayne.infra.scheduler.start_scheduler()

    async def start_sandbox_task():
        await velayne.core.engine.start_sandbox_service()

    async def shutdown():
        shutdown_flag["stop"] = True
        logger.info("[SHUTDOWN] Stopping all tasks...")
        for name, task in tasks.items():
            if not task.done():
                task.cancel()
        await asyncio.gather(*[task for task in tasks.values()], return_exceptions=True)
        try:
            from velayne.core import dataio
            await dataio.flush_all()
        except Exception:
            pass
        try:
            await velayne.core.engine.stop_sandbox_service()
        except Exception:
            pass
        logger.info("[SHUTDOWN] All services stopped.")

    from velayne.infra import health

    def show_diag():
        snap = health.health_snapshot()
        print("\n[DIAGNOSTICS]:")
        for k, v in snap.items():
            if k == "details":
                for dk, dv in v.items():
                    print(f"  {dk}: {dv}")
            else:
                print(f"  {k}: {v}")

    async def sandbox_restart():
        logger.warning("[ADMIN] Sandbox restart requested.")
        await velayne.core.engine.restart_sandbox_service()
        print("[INFO] Sandbox сервис перезапущен.")

    def menu_sandbox_restart():
        asyncio.run_coroutine_threadsafe(sandbox_restart(), loop)

    def menu_show_diag():
        show_diag()

    def menu_run_selftest():
        async def runner():
            res = await selftest()
            print("[SELFTEST] result:", res)
        asyncio.run_coroutine_threadsafe(runner(), loop)

    def menu_show_perf():
        show_perf_summary()

    import threading
    menu_thread = threading.Thread(
        target=lambda: asyncio.run(menu_input(menu_sandbox_restart, menu_show_diag, menu_run_selftest, menu_show_perf, shutdown_flag)),
        daemon=True
    )
    menu_thread.start()

    async def task_runner(name, coro_func):
        backoff = 1
        while not shutdown_flag["stop"]:
            try:
                await coro_func()
                logger.warning(f"[{name}] Завершён (неожиданно).")
                break
            except asyncio.CancelledError:
                logger.info(f"[{name}] Cancelled.")
                break
            except Exception as e:
                logger.error(f"[{name}] Exception: {e}")
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 30)
        logger.info(f"[{name}] Loop exited.")

    loop = asyncio.get_running_loop()
    def sig_handler(*_):
        shutdown_flag["stop"] = True
        print("\n[SHUTDOWN] SIGINT/SIGTERM получен, завершаем...")
        asyncio.run_coroutine_threadsafe(shutdown(), loop)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tasks["bot"] = asyncio.create_task(task_runner("Bot", start_bot_task))
    tasks["scheduler"] = asyncio.create_task(task_runner("Scheduler", start_scheduler_task))
    tasks["sandbox"] = asyncio.create_task(task_runner("Sandbox", start_sandbox_task))

    while not shutdown_flag["stop"]:
        await asyncio.sleep(1)
    await shutdown()
    print("[Velayne] Остановлено. До свидания.")

if __name__ == "__main__":
    import asyncio
    try:
        import uvloop
        uvloop.install()
    except ImportError:
        pass
    asyncio.run(main())