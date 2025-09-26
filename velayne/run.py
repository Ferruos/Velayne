import asyncio
import logging
import sys
import signal
from velayne.infra.config import get_settings
from velayne.infra.logger import setup_logging
from velayne.infra.db import init_db
settings = get_settings()

def main():
    active_log = setup_logging()
    print(f"[ЛОГИ] Лог пишется в: {active_log}")

    async def real_main():
        await init_db()
        from velayne.infra.scheduler import start_scheduler_async
        from velayne.core.engine import start_sandbox_service
        from velayne.bot.main import start_bot
        # Watchdog
        async def watchdog_task(coro_factory, name, max_restarts=5, restart_delay=3):
            restarts = 0
            while restarts <= max_restarts:
                try:
                    logging.info(f"[WATCHDOG] Запуск {name} (рестарт #{restarts})")
                    await coro_factory()
                    logging.warning(f"[WATCHDOG] {name} завершился нормально (рестарт #{restarts})")
                    break
                except Exception as e:
                    restarts += 1
                    logging.error(f"[WATCHDOG] {name} аварийно завершился: {e} (рестарт {restarts}/{max_restarts})")
                    if restarts > max_restarts:
                        logging.error(f"[WATCHDOG] {name} достиг лимита рестартов ({max_restarts}).")
                        break
                    await asyncio.sleep(restart_delay)
        tasks = [
            asyncio.create_task(watchdog_task(start_scheduler_async, "scheduler")),
            asyncio.create_task(watchdog_task(start_sandbox_service, "sandbox")),
            asyncio.create_task(watchdog_task(start_bot, "bot"))
        ]
        loop = asyncio.get_event_loop()
        stop_event = asyncio.Event()
        def shutdown(*_):
            print("[ИНФО] Корректное завершение...")
            stop_event.set()
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, shutdown)
            except Exception:
                pass
        await stop_event.wait()
        for t in tasks:
            t.cancel()
        await asyncio.sleep(0.2)
        print("[ИНФО] Velayne остановлен.")

    asyncio.run(real_main())

if __name__ == "__main__":
    main()