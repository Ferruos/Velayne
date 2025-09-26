import asyncio
import time
import json
from pathlib import Path
from collections import defaultdict, deque
import statistics

# === Async semaphore for heavy sections (ML, IO) ===
ML_SEMAPHORE = asyncio.BoundedSemaphore(2)
IO_SEMAPHORE = asyncio.BoundedSemaphore(4)

PERF_LOG = Path("logs/perf.jsonl")
PERF_LOG.parent.mkdir(exist_ok=True)

# --- Token Bucket ---
class TokenBucket:
    def __init__(self, rate, capacity):
        self.rate = rate  # tokens/sec
        self.capacity = capacity
        self.tokens = capacity
        self.last = time.time()
        self._lock = asyncio.Lock()

    async def get(self, n=1):
        async with self._lock:
            now = time.time()
            elapsed = now - self.last
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.last = now
            if self.tokens >= n:
                self.tokens -= n
                return True
            else:
                return False

    async def wait(self, n=1):
        while True:
            if await self.get(n):
                return
            await asyncio.sleep(0.01)

# --- Circuit breaker (per exchange/user) ---
class CircuitBreaker:
    def __init__(self, error_threshold=5, reset_timeout=30, admin_notify_cb=None):
        self.error_count = 0
        self.tripped = False
        self.last_error = 0
        self.error_threshold = error_threshold
        self.reset_timeout = reset_timeout
        self.last_trip = 0
        self.admin_notify_cb = admin_notify_cb

    def on_error(self, exc=None):
        self.error_count += 1
        self.last_error = time.time()
        if self.error_count >= self.error_threshold and not self.tripped:
            self.tripped = True
            self.last_trip = time.time()
            if self.admin_notify_cb:
                try:
                    self.admin_notify_cb(f"Circuit breaker TRIPPED: {exc}")
                except Exception:
                    pass

    def on_success(self):
        self.error_count = 0
        if self.tripped and time.time() - self.last_trip > self.reset_timeout:
            self.tripped = False

    def is_tripped(self):
        if self.tripped:
            if time.time() - self.last_trip > self.reset_timeout:
                self.tripped = False
                self.error_count = 0
                return False
            return True
        return False

# --- Latency histograms ---
class LatencyStats:
    def __init__(self, maxlen=1200):
        self.samples = defaultdict(lambda: deque(maxlen=maxlen))

    def add(self, key, value):
        self.samples[key].append(value)

    def percentiles(self, key):
        arr = list(self.samples[key])
        if not arr:
            return {"p50": None, "p90": None, "p99": None}
        arr.sort()
        return {
            "p50": arr[int(len(arr)*0.50)] if len(arr) else None,
            "p90": arr[int(len(arr)*0.90)] if len(arr) else None,
            "p99": arr[int(len(arr)*0.99)] if len(arr) else None,
            "count": len(arr)
        }

LATENCY_STATS = LatencyStats()
QUEUE_PRESSURE = defaultdict(int)
CIRCUIT_BREAKERS = {}  # key: (exchange, user_id)

def update_latency(key, value):
    LATENCY_STATS.add(key, value)

def flush_perf_log():
    # Write summary with percentiles for main paths
    summary = {}
    for key in ["inference", "place_order", "fetch_news"]:
        summary[key] = LATENCY_STATS.percentiles(key)
    summary['ts'] = int(time.time())
    with open(PERF_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(summary) + "\n")

def get_perf_summary():
    data = {}
    for key in ["inference", "place_order", "fetch_news"]:
        p = LATENCY_STATS.percentiles(key)
        data[key] = {k:v for k,v in p.items()}
    # Очереди
    data["order_queues"] = dict(QUEUE_PRESSURE)
    # Circuit breakers
    data["circuit_breakers"] = {
        k: dict(tripped=cb.is_tripped(), err=cb.error_count, last_trip=cb.last_trip)
        for k, cb in CIRCUIT_BREAKERS.items()
    }
    return data

def get_circuit_breaker(exchange, user_id, notify_admin=None):
    key = (exchange, user_id)
    if key not in CIRCUIT_BREAKERS:
        CIRCUIT_BREAKERS[key] = CircuitBreaker(admin_notify_cb=notify_admin)
    return CIRCUIT_BREAKERS[key]