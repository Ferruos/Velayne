import threading
import time
from collections import defaultdict, deque
from typing import Any, Callable

__all__ = [
    "DATAIO_BUFFERS",
    "get_dataio_buffer",
    "flush_all_dataio_buffers",
    "ORDER_TOKEN_BUCKET",
    "CIRCUIT_BREAKERS",
    "perf_summary",
]

# --- DataIO write-behind buffer ---

class WriteBehindBuffer:
    def __init__(self, name, flush_every_secs=5, flush_every_records=500):
        self.name = name
        self._records = []
        self._lock = threading.Lock()
        self._last_flush = time.monotonic()
        self._flush_every_secs = flush_every_secs
        self._flush_every_records = flush_every_records

    def append(self, record: dict):
        with self._lock:
            self._records.append(record)
            now = time.monotonic()
            if (
                len(self._records) >= self._flush_every_records
                or (now - self._last_flush) >= self._flush_every_secs
            ):
                self.flush()

    def pop_all(self):
        with self._lock:
            items = list(self._records)
            self._records.clear()
            return items

    def flush(self):
        # Actual disk write is handled in dataio; here we just pop and return records.
        recs = self.pop_all()
        self._last_flush = time.monotonic()
        return recs

DATAIO_BUFFERS: dict[str, WriteBehindBuffer] = {}

def get_dataio_buffer(name: str) -> WriteBehindBuffer:
    if name not in DATAIO_BUFFERS:
        DATAIO_BUFFERS[name] = WriteBehindBuffer(name)
    return DATAIO_BUFFERS[name]

def flush_all_dataio_buffers():
    for buf in DATAIO_BUFFERS.values():
        buf.flush()

# --- Order token bucket ---

class TokenBucket:
    def __init__(self, capacity=10, refill_rate=1.0):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.monotonic()
        self._lock = threading.Lock()

    def try_consume(self, n=1):
        with self._lock:
            now = time.monotonic()
            elapsed = now - self.last_refill
            refill = elapsed * self.refill_rate
            self.tokens = min(self.capacity, self.tokens + refill)
            self.last_refill = now
            if self.tokens >= n:
                self.tokens -= n
                return True
            return False

ORDER_TOKEN_BUCKET = TokenBucket(capacity=10, refill_rate=1.0)

# --- Circuit breakers ---

class CircuitBreaker:
    def __init__(self, fail_max=5, reset_timeout=30):
        self.fail_max = fail_max
        self.reset_timeout = reset_timeout
        self.failures = 0
        self.last_failure = 0
        self.open = False

    def record_success(self):
        self.failures = 0
        self.open = False

    def record_failure(self):
        self.failures += 1
        self.last_failure = time.monotonic()
        if self.failures >= self.fail_max:
            self.open = True

    def is_open(self):
        if self.open:
            if (time.monotonic() - self.last_failure) > self.reset_timeout:
                self.reset()
                return False
            return True
        return False

    def reset(self):
        self.failures = 0
        self.open = False

CIRCUIT_BREAKERS: dict[str, CircuitBreaker] = {
    "exchange": CircuitBreaker(),
    "news": CircuitBreaker(),
}

# --- Perf summary ---

PERF_METRICS = defaultdict(lambda: deque(maxlen=200))

def record_perf(metric: str, dt: float):
    PERF_METRICS[metric].append(dt)

def percentile(vals, p):
    if not vals:
        return None
    vals = sorted(vals)
    k = int(len(vals) * (p / 100.0))
    k = min(len(vals) - 1, max(0, k))
    return vals[k]

def perf_summary():
    result = {}
    for k, v in PERF_METRICS.items():
        result[k] = {
            "p50": percentile(v, 50),
            "p90": percentile(v, 90),
            "p99": percentile(v, 99),
            "count": len(v),
        }
    # token bucket/circuit breakers state
    result["order_token_bucket"] = {
        "tokens": getattr(ORDER_TOKEN_BUCKET, "tokens", None),
        "capacity": getattr(ORDER_TOKEN_BUCKET, "capacity", None),
    }
    result["circuit_breakers"] = {
        name: {"open": cb.is_open(), "failures": cb.failures}
        for name, cb in CIRCUIT_BREAKERS.items()
    }
    return result