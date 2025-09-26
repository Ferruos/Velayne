import os
import sys
import subprocess
import signal
from pathlib import Path
from datetime import datetime
from velayne.infra.logger import logger

WORKER_LOGS_DIR = Path("logs/workers")
WORKER_LOGS_DIR.mkdir(parents=True, exist_ok=True)

def _worker_script(user_id):
    # Запуск воркера через отдельный процесс (python -m velayne.core.engine ...args)
    return [
        sys.executable,
        "-m",
        "velayne.core.engine",
        "--live",
        f"--user_id={user_id}"
    ]

def _safe_kill(pid):
    """Кроссплатформенный kill"""
    try:
        if os.name == "nt":
            import ctypes
            PROCESS_TERMINATE = 1
            handle = ctypes.windll.kernel32.OpenProcess(PROCESS_TERMINATE, False, pid)
            if handle:
                ctypes.windll.kernel32.TerminateProcess(handle, -1)
                ctypes.windll.kernel32.CloseHandle(handle)
                return True
            return False
        else:
            os.kill(pid, signal.SIGTERM)
            return True
    except Exception as e:
        logger.warning(f"Kill error for pid={pid}: {e}")
        return False

def start_live_worker(user_id):
    log_path = WORKER_LOGS_DIR / f"live_{user_id}.log"
    with open(log_path, "a", encoding="utf-8") as f:
        proc = subprocess.Popen(
            _worker_script(user_id),
            stdout=f,
            stderr=subprocess.STDOUT,
            cwd=os.getcwd()
        )
        logger.info(f"Started live worker for user {user_id}, pid={proc.pid}")
        return proc.pid

def stop_live_worker(user_id):
    from velayne.infra.db import Worker, SessionLocal
    session = SessionLocal()
    obj = session.query(Worker).filter_by(user_id=user_id, mode="live").first()
    if not obj or not obj.pid:
        return False
    try:
        ok = _safe_kill(obj.pid)
        if ok:
            obj.status = "stopped"
            session.commit()
            logger.info(f"Stopped live worker for user {user_id}")
            return True
        else:
            return False
    except Exception as e:
        logger.warning(f"Failed to stop worker: {e}")
        return False

def restart_live_worker(user_id):
    stop_live_worker(user_id)
    return start_live_worker(user_id)

def status_live_worker(user_id):
    from velayne.infra.db import Worker, SessionLocal
    session = SessionLocal()
    obj = session.query(Worker).filter_by(user_id=user_id, mode="live").first()
    if not obj:
        return {"status": "not_found"}
    uptime = None
    if obj.last_heartbeat:
        delta = datetime.utcnow() - obj.last_heartbeat
        uptime = int(delta.total_seconds())
    return {
        "user_id": obj.user_id,
        "status": obj.status,
        "pid": obj.pid,
        "last_heartbeat": obj.last_heartbeat,
        "logs_path": obj.logs_path,
        "uptime": uptime,
    }

def list_live_workers():
    from velayne.infra.db import Worker, SessionLocal
    session = SessionLocal()
    objs = session.query(Worker).filter_by(mode="live").all()
    rows = []
    for obj in objs:
        uptime = None
        if obj.last_heartbeat:
            delta = datetime.utcnow() - obj.last_heartbeat
            uptime = int(delta.total_seconds())
        rows.append({
            "user_id": obj.user_id,
            "pid": obj.pid,
            "status": obj.status,
            "last_heartbeat": obj.last_heartbeat,
            "logs_path": obj.logs_path,
            "uptime": uptime,
        })
    return rows

def kill_live_worker(user_id: int) -> bool:
    return stop_live_worker(user_id)

def kill_all_live_workers():
    rows = list_live_workers()
    results = {}
    for row in rows:
        user_id = row["user_id"]
        if not row["pid"]:
            results[user_id] = "not_running"
            continue
        try:
            ok = _safe_kill(row["pid"])
            if ok:
                results[user_id] = "ok"
            else:
                results[user_id] = "error"
        except Exception:
            results[user_id] = "error"
    return results