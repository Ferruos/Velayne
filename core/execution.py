import time

class Executor:
    def __init__(self, exchange_adapter, portfolio_manager):
        self.exchange = exchange_adapter
        self.portfolio = portfolio_manager
        self.open_orders = []

    def drain_positions(self):
        print("Дренаж: закрываю все ордера.")
        for order in self.open_orders:
            # В реальном мире здесь нужно закрыть позицию.
            print(f"Закрываю позицию: {order}")
        self.open_orders = []

    def cancel_all_orders(self):
        print("Отмена всех активных ордеров.")
        self.open_orders = []

    def execute_order(self, symbol, order):
        """
        Отправляет ордер на биржу через ExchangeAdapter.
        :param symbol: торгуемая пара, например 'BTC/USDT'
        :param order: словарь {'action': buy/sell/hold/stop, 'amount': float}
        """
        action = order.get("action")
        amount = order.get("amount", 0.0)
        if action == "stop":
            self.drain_positions()
            return
        if action in ("hold", None) or amount <= 0:
            print("Нет действия (hold/zero).")
            return
        # Выполняем ордер на бирже
        try:
            result = self.exchange.create_order(symbol, action, amount)
            print(f"Отправил ордер: {action} {amount} {symbol} → {result}")
            self.open_orders.append({"symbol": symbol, "action": action, "amount": amount})
        except Exception as e:
            print(f"Ошибка размещения ордера: {e}")
