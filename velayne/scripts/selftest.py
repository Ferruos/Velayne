import sys
import traceback
import asyncio

def printc(msg, color="green"):
    c = {"red": "\033[91m", "green": "\033[92m", "reset": "\033[0m"}
    print(f"{c.get(color,'')}{msg}{c['reset']}")

async def main_async():
    print("== SELFTEST ==")
    # Import all main modules
    try:
        import velayne.run
        import velayne.bot.main
        import velayne.bot.user
        import velayne.bot.ui
        import velayne.bot.middlewares
        import velayne.infra.db
        import velayne.core.engine
        import velayne.core.ml
        import velayne.core.news
        import velayne.infra.perf
        printc("All modules imported OK", "green")
    except Exception as e:
        printc(f"SELFTEST FAIL: Import error: {e}", "red")
        traceback.print_exc()
        return False

    # Check DB API
    try:
        db = velayne.infra.db
        assert hasattr(db, "init_db_and_bootstrap")
        assert hasattr(db, "get_or_create_user")
        assert hasattr(db, "set_user_consent")
        assert hasattr(db, "get_users_count")
        assert hasattr(db, "get_user_active_subscription")
        assert hasattr(db, "upsert_subscription_for_test_trial")
        assert hasattr(db, "expire_old_subscriptions")
        assert hasattr(db, "get_next_expiring_subscriptions")
        assert hasattr(db, "upsert_strategy_pref")
        assert hasattr(db, "get_global_mode")
        assert hasattr(db, "set_global_mode")
        printc("DB API OK", "green")
    except Exception as e:
        printc(f"SELFTEST FAIL: DB API error: {e}", "red")
        traceback.print_exc()
        return False

    # Check perf API symbols
    try:
        perf = velayne.infra.perf
        assert hasattr(perf, "DATAIO_BUFFERS")
        assert hasattr(perf, "get_dataio_buffer")
        assert hasattr(perf, "flush_all_dataio_buffers")
        assert hasattr(perf, "ORDER_TOKEN_BUCKET")
        assert hasattr(perf, "CIRCUIT_BREAKERS")
        assert hasattr(perf, "perf_summary")
        buf = perf.get_dataio_buffer("trades")
        buf.append({"user_id": 1, "dt": "now", "symbol": "BTC"})
        perf.flush_all_dataio_buffers()
        printc("Perf API OK", "green")
    except Exception as e:
        printc(f"SELFTEST FAIL: perf API error: {e}", "red")
        traceback.print_exc()
        return False

    # get_or_create_user
    try:
        user = await velayne.infra.db.get_or_create_user(999999)
        printc(f"User create/get OK: {user.id if user else 'None'}", "green")
    except Exception as e:
        printc("SELFTEST FAIL: get_or_create_user error: " + str(e), "red")
        traceback.print_exc()
        return False

    # upsert_strategy_pref
    try:
        await velayne.infra.db.upsert_strategy_pref(999999, "ema_crossover", True)
        printc("upsert_strategy_pref OK", "green")
    except Exception as e:
        printc("SELFTEST FAIL: upsert_strategy_pref error: " + str(e), "red")
        traceback.print_exc()
        return False

    # Check start_bot callable
    try:
        from velayne.bot.main import start_bot
        assert callable(start_bot)
        printc("start_bot is callable", "green")
    except Exception as e:
        printc("SELFTEST FAIL: start_bot not callable: " + str(e), "red")
        traceback.print_exc()
        return False

    # Single sandbox tick and flush
    try:
        if hasattr(velayne.core.engine, "start_sandbox_service"):
            await velayne.core.engine.start_sandbox_service()
        perf.flush_all_dataio_buffers()
        printc("Sandbox tick and flush OK", "green")
    except Exception as e:
        printc("SELFTEST FAIL: sandbox error: " + str(e), "red")
        traceback.print_exc()
        return False

    printc("SELFTEST OK", "green")
    return True

def main():
    try:
        res = asyncio.run(main_async())
        if res:
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        printc("SELFTEST FAIL: Exception: " + str(e), "red")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()