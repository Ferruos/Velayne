import ccxt
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import logging
import asyncio
import time
from velayne.infra.config import settings

logger = logging.getLogger("velayne.live")

EXCHANGE_MAP = {
    "binance": ccxt.binance,
    "bybit": ccxt.bybit,
    "okx": ccxt.okx,
}

def create_client(exchange, key, secret, passphrase=None, testnet=None):
    if exchange not in EXCHANGE_MAP:
        raise ValueError("Unknown exchange: " + str(exchange))
    params = {"apiKey": key, "secret": secret}
    if exchange == "okx" and passphrase:
        params["password"] = passphrase
    client = EXCHANGE_MAP[exchange](params)
    # Тестнет поддержка
    if testnet is None:
        testnet = settings.EXCHANGE_TESTNET
    if exchange == "binance":
        client.options["defaultType"] = "future"
        if testnet:
            client.set_sandbox_mode(True)
            client.urls['api'] = client.urls['test']
    elif exchange == "bybit":
        if testnet:
            client.urls['api'] = 'https://api-testnet.bybit.com'
    elif exchange == "okx":
        if testnet:
            client.urls['api'] = 'https://www.okx.com'
            client.options['sandbox'] = True
    return client

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, max=4), retry=retry_if_exception_type(Exception))
def validate_keys(exchange, key, secret, passphrase=None, testnet=None):
    try:
        client = create_client(exchange, key, secret, passphrase, testnet)
        if hasattr(client, "fetch_balance"):
            client.fetch_balance()
        else:
            client.fetch_time()
        return True
    except Exception as e:
        logger.warning(f"Key validation fail: {e}")
        return False

class OrderQueue:
    def __init__(self, max_parallel: int, max_per_sec: int):
        self.max_parallel = max_parallel
        self.max_per_sec = max_per_sec
        self._sem = asyncio.BoundedSemaphore(max_parallel)
        self._last_times = []
        self._lock = asyncio.Lock()
        self._queue = asyncio.Queue()

    async def enqueue(self, func, *args, **kwargs):
        async with self._lock:
            now = time.time()
            self._last_times = [t for t in self._last_times if now-t < 1]
            if len(self._last_times) >= self.max_per_sec:
                logger.warning("OrderQueue: RPS limit hit; backpressure applied")
                await asyncio.sleep(1)
            self._last_times.append(now)
        async with self._sem:
            return await func(*args, **kwargs)

order_queues = {}

def get_order_queue(user_id):
    if user_id not in order_queues:
        from velayne.infra.config import settings
        order_queues[user_id] = OrderQueue(settings.ORDER_QUEUE_MAX_PARALLEL, settings.ORDER_QUEUE_MAX_PER_SEC)
    return order_queues[user_id]

async def place_order(client, user_id, symbol, side, qty, type="market", price=None, params=None):
    queue = get_order_queue(user_id)
    async def _do_order():
        try:
            # --- Реалистичная комиссия и слippage ---
            order_type = type
            # Получить биржевые данные для расчёта комиссии и спреда
            market = client.market(symbol)
            taker_fee = getattr(market, "taker", 0.0005)
            maker_fee = getattr(market, "maker", 0.0002)
            spread = None
            try:
                ticker = client.fetch_ticker(symbol)
                spread = abs(ticker.get("ask", 0) - ticker.get("bid", 0))
            except Exception:
                spread = 0.0

            # Проскальзывание: зависит от qty
            slippage_pct = min(0.0005 + abs(qty) * 0.0003, 0.005)
            base_price = ticker["ask"] if side == "buy" else ticker["bid"]
            exec_price = base_price * (1 + slippage_pct) if side == "buy" else base_price * (1 - slippage_pct)

            # Комиссия
            fee = abs(qty * exec_price) * (taker_fee if order_type == "market" else maker_fee)

            # Создаём ордер (боевой)
            if order_type == "market":
                order = client.create_market_order(symbol, side, qty, params or {})
            else:
                order = client.create_limit_order(symbol, side, qty, price, params or {})
            # Добавить инфу про комиссию, проскальзывание и спред
            order["fee_calc"] = fee
            order["slippage_pct"] = slippage_pct
            order["spread"] = spread
            order["exec_price"] = exec_price
            return order
        except Exception as e:
            logger.error(f"Order error: {e}")
            raise
    return await queue.enqueue(_do_order)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, max=4), retry=retry_if_exception_type(Exception))
def cancel_order(client, order_id, symbol=None):
    try:
        if symbol:
            return client.cancel_order(order_id, symbol)
        else:
            return client.cancel_order(order_id)
    except Exception as e:
        logger.error(f"Cancel order error: {e}")
        return False

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, max=4), retry=retry_if_exception_type(Exception))
def get_balance(client):
    return client.fetch_balance()

@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=0.5, max=2), retry=retry_if_exception_type(Exception))
def get_ticker(client, symbol):
    return client.fetch_ticker(symbol)

# --- Для ML фичей: cost aware ---
def enrich_features_with_cost(features: dict, order, fee, slippage, spread):
    features = dict(features)
    features['last_fee'] = fee
    features['last_slippage'] = slippage
    features['last_spread'] = spread
    return features