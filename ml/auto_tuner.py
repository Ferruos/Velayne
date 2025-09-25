import schedule, threading, time

def auto_tune_blend(blend_manager, historical_data, strategy_classes):
    """
    Автоматическое переобучение blend раз в сутки, публикация новой версии.
    """
    def job():
        from ml.blend_optimizer import optimize_blend
        best = optimize_blend(historical_data, strategy_classes)
        blend_manager.publish_blend({**best, "version": str(int(time.time()))})
    schedule.every().day.at("00:30").do(job)
    threading.Thread(target=lambda: [schedule.run_pending() or time.sleep(60)]).start()