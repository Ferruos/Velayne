import asyncio
import signal
import json
from loguru import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from velayne.infra.db import expire_old_subscriptions, get_next_expiring_subscriptions
from velayne.core.news import fetch_news, classify_news, news_guard
from velayne.core.ml import auto_optimize, train_from_logs, suggest_strategy_mix
from velayne.infra import health
from velayne.infra import retention

NEWS_STATE_PATH = "data/news_state.json"
ML_STATE_PATH = "data/models/meta.json"
STRATEGY_MIX_PATH = "data/models/strategy_mix.json"
PNL_LOG_PATH = "logs/sandbox_pnl.log"
HEALTH_PATH = "logs/health.jsonl"

async def expire_subscriptions():
    expired_count = await expire_old_subscriptions()
    if expired_count:
        logger.info(f"Планировщик: Статус 'expired' установлен для {expired_count} подписок.")

async def remind_expiring():
    subs = await get_next_expiring_subscriptions(limit=10)
    now = datetime.utcnow()
    for sub in subs:
        delta = sub.expires_at - now
        hours_left = delta.total_seconds() / 3600
        if any(abs(hours_left - th) < 0.5 for th in [24, 3, 1]):
            logger.info(
                f"Планировщик: Напоминание о скором завершении подписки user_id={sub.user_id}, plan={sub.plan}, expires_at={sub.expires_at}"
            )

async def daily_maintenance():
    logger.info("Планировщик: daily_maintenance — ротация логов, статистика, ...")
    news_level, news_meta = news_guard()
    try:
        with open(PNL_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"{datetime.utcnow().isoformat()} News: {news_level} Tags: {json.dumps(news_meta.get('tags', {}))}\n")
    except Exception:
        pass

async def fetch_and_classify_news_job():
    items = fetch_news(100)
    result = classify_news(items)
    with open(NEWS_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump({"last_classification": result, "timestamp": datetime.utcnow().isoformat()}, f)
    logger.info(f"News fetched. Level: {result['level']}, Tags: {result['tags']}")

async def ml_auto_optimize_job():
    auto_optimize()
    logger.info("ML auto_optimize запущена.")

async def healthcheck_job():
    snap = health.health_snapshot()
    with open(HEALTH_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(snap) + "\n")

async def train_from_logs_job():
    # отдельные метрики по источникам + общая
    sources = ['sandbox', 'live']
    weights = {'sandbox': 0.5, 'live': 1.0}
    meta = train_from_logs(sources=sources, weights=weights)
    if meta:
        logger.info(f"ML Train (общая): Версия={meta.get('version')} AUC={meta.get('auc'):.3f} Acc={meta.get('accuracy'):.3f} F1={meta.get('f1'):.3f} Порог={meta.get('best_thresh'):.2f}")
        for src, m in meta.get('sources', {}).items():
            logger.info(f"ML Train src={src}: AUC={m['auc']:.3f} Acc={m['accuracy']:.3f} F1={m['f1']:.3f} N={m['count']}")
    else:
        logger.info("ML Train: Недостаточно данных для обучения.")
    mix = suggest_strategy_mix()
    logger.info(f"StrategyMix: {mix.get('recommendations')}")

async def retention_job():
    stats = retention.retention_summary()
    logger.info(f"Retention: {json.dumps(stats, ensure_ascii=False, indent=2)}")

async def start_retention_now():
    stats = retention.retention_summary()
    logger.info(f"Retention (manual): {json.dumps(stats, ensure_ascii=False, indent=2)}")
    return stats

async def start_scheduler():
    snap = health.health_snapshot()
    logger.info(f"Health snapshot: {snap}")
    heal_res = health.self_heal()
    logger.info(f"Self-heal: {heal_res}")

    scheduler = AsyncIOScheduler()
    scheduler.add_job(lambda: asyncio.create_task(expire_subscriptions()), "interval", minutes=10, id="expire_subs")
    scheduler.add_job(lambda: asyncio.create_task(remind_expiring()), "interval", minutes=30, id="remind_exp")
    scheduler.add_job(lambda: asyncio.create_task(daily_maintenance()), "cron", hour=3, id="daily_maint")
    scheduler.add_job(lambda: asyncio.create_task(fetch_and_classify_news_job()), "interval", minutes=15, id="fetch_news")
    scheduler.add_job(lambda: asyncio.create_task(ml_auto_optimize_job()), "interval", hours=12, id="ml_optimize")
    scheduler.add_job(lambda: asyncio.create_task(healthcheck_job()), "interval", minutes=5, id="healthcheck")
    scheduler.add_job(lambda: asyncio.create_task(train_from_logs_job()), "interval", hours=6, id="ml_train_from_logs")
    scheduler.add_job(lambda: asyncio.create_task(retention_job()), "cron", hour=4, id="retention_daily")

    scheduler.start()
    logger.info("Планировщик запущен.")

    stop_event = asyncio.Event()

    def shutdown_handler(*_):
        logger.warning("Получен сигнал завершения (SIGINT/SIGTERM), останавливаем планировщик...")
        stop_event.set()
        scheduler.shutdown(wait=False)

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    try:
        while not stop_event.is_set():
            await asyncio.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Планировщик остановлен.")
        scheduler.shutdown()