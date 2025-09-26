import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.triggers.interval import IntervalTrigger
from velayne.infra.config import get_settings
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

settings = get_settings()

sched = None

async def ensure_jobs():
    global sched
    if sched:
        return
    jobstore = SQLAlchemyJobStore(url=settings.DB_URL)
    sched = AsyncIOScheduler(jobstores={"default": jobstore})
    sched.add_job(expire_subs, trigger=IntervalTrigger(hours=1), id="expire_subs", replace_existing=True)
    sched.add_job(heartbeat, trigger=IntervalTrigger(seconds=30), id="heartbeat", replace_existing=True)
    sched.start()
    logging.info("[SCHEDULER] Запуск APScheduler с SQLite jobstore.")

async def expire_subs():
    # Деактивация истёкших подписок
    engine = create_async_engine(settings.DB_URL, echo=False, future=True)
    async with engine.begin() as conn:
        await conn.execute(
            text("UPDATE users SET sub_until=NULL WHERE sub_until IS NOT NULL AND sub_until < CURRENT_TIMESTAMP")
        )
        await conn.commit()
    logging.info("[SCHEDULER] Проверка подписок завершена.")

async def heartbeat():
    logging.info("[SCHEDULER] сервис жив")

async def start_scheduler_async():
    await ensure_jobs()
    while True:
        await asyncio.sleep(60)