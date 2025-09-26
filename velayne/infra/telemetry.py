import json
import time
from pathlib import Path
from threading import Lock
import asyncio

class Telemetry:
    def __init__(self, path="logs/telemetry.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(exist_ok=True)
        self._lock = Lock()
        self.metrics = {}
        self.last_alerts = {}
        self.admin_notify = None

    def record(self, key, value, extra=None):
        ts = int(time.time())
        row = {"ts": ts, "key": key, "value": value}
        if extra:
            row["extra"] = extra
        with self._lock:
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        self.metrics[key] = value
        self.check_alert(key, value)

    def check_alert(self, key, value):
        # Пример критов: latency, errors, disk, circuit_breaker
        crits = {
            "latency_ms": lambda v: v > 1500,
            "error_rate": lambda v: v > 0.1,
            "disk_free_gb": lambda v: v < 1.0,
            "circuit_breaker": lambda v: v,
        }
        if key in crits and crits[key](value):
            # Не алертить чаще, чем раз в 5 мин по ключу
            now = time.time()
            if now - self.last_alerts.get(key, 0) > 300:
                self.last_alerts[key] = now
                if self.admin_notify:
                    asyncio.create_task(self.admin_notify(f"ALERT: {key} = {value}"))

    def get_summary(self):
        return dict(self.metrics)

    def tail_logs(self, n=50):
        # Быстрый tail -n
        try:
            with self.path.open("rb") as f:
                f.seek(0, 2)
                size = f.tell()
                buf = bytearray()
                lines = []
                pos = size
                while len(lines) < n and pos > 0:
                    read = min(4096, pos)
                    pos -= read
                    f.seek(pos)
                    chunk = f.read(read)
                    buf = chunk + buf
                    lines = buf.split(b"\n")
                lines = [l.decode("utf-8") for l in lines if l.strip()]
                return lines[-n:]
        except Exception:
            return []

TELEMETRY = Telemetry()

# FastAPI mini-dashboard (optional)
try:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse, PlainTextResponse
    import uvicorn

    app = FastAPI()

    @app.get("/health")
    def health():
        return {"status": "ok", "ts": int(time.time())}

    @app.get("/metrics/summary")
    def metrics_summary():
        return JSONResponse(TELEMETRY.get_summary())

    @app.get("/logs/tail")
    def logs_tail(n: int = 50):
        return PlainTextResponse("\n".join(TELEMETRY.tail_logs(n)))

    def run_dashboard(host="127.0.0.1", port=8686):
        uvicorn.run(app, host=host, port=port)
except ImportError:
    app = None
    def run_dashboard(*a, **k): print("FastAPI/uvicorn not installed")