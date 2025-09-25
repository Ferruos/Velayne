"""
Generic exchange adapter for ccxt-supported exchanges.

Эта обёртка позволяет использовать одну и ту же логику для разных бирж (Bybit, Binance и т.д.).
Тестовая среда задаётся флагом `testnet`: для Bybit она автоматически активирует отдельный API-домен.
"""

from typing import Any, Dict, List, Optional
import ccxt  # type: ignore


class ExchangeAdapter:
    """Единый интерфейс для работы с биржами через ccxt."""

    def __init__(self, name: str = "bybit", api_key: Optional[str] = None,
                 api_secret: Optional[str] = None, *, testnet: bool = True) -> None:
        # Пустые строки вместо None, чтобы ccxt не ругался
        api_key = api_key or ""
        api_secret = api_secret or ""

        # Проверяем, что такая биржа вообще есть в ccxt
        try:
            exchange_class = getattr(ccxt, name)
        except AttributeError:
            raise ValueError(f"Unsupported exchange: {name}")

        # Дополнительные опции для отдельных бирж
        options: Dict[str, Any] = {}
        if name == "bybit":
            # Bybit делит API для спота и фьючерсов; по умолчанию используем спотовый
            options.update({"defaultType": "spot", "testnet": testnet})
        elif name == "binance":
            options.update({"defaultType": "spot"})

        # Инициализируем конкретный класс ccxt
        self.exchange = exchange_class({
            "apiKey": api_key,
            "secret": api_secret,
            "enableRateLimit": True,
            "options": options,
        })

    def get_historical_data(self, symbol: str, *, timeframe: str = "1h",
                            limit: int = 500) -> Dict[str, List[float]]:
        """
        Загружает OHLCV и возвращает словарь с ценами закрытия.

        :param symbol: Тикер, например 'BTC/USDT'
        :param timeframe: Интервал свечей (1m, 1h, 1d и т.д.)
        :param limit: Число свечей
        :return: Dict с ключом 'close' и списком цен закрытия
        """
        ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        closes = [entry[4] for entry in ohlcv]
        return {"close": closes}

    def create_order(self, symbol: str, side: str, amount: float,
                     *, price: Optional[float] = None,
                     order_type: str = "market") -> Any:
        """
        Размещает маркет‑или лимит‑ордер.

        :param symbol: Пара (например 'BTC/USDT')
        :param side: 'buy' или 'sell'
        :param amount: Количество
        :param price: Цена для лимит‑ордера; игнорируется для маркет‑ордера
        :param order_type: 'market' или 'limit'
        :return: результат вызова ccxt
        """
        side = side.lower()
        if order_type.lower() == "market":
            return self.exchange.create_order(symbol, "market", side, amount)
        return self.exchange.create_order(symbol, "limit", side, amount, price)
