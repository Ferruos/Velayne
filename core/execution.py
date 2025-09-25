import time

class Executor:
    def __init__(self, exchange_adapter, portfolio_manager):
        self.exchange = exchange_adapter
        self.portfolio = portfolio_manager
        self.open_orders = []

    def drain_positions(self):
        print("Дренаж: закрываю все ордера.")
        for order in self.open_orders:
            # Отправить на биржу закрывающий ордер
            print(f"Закрываю позицию: {order}")
        self.open_orders = []

    def cancel_all_orders(self):
        print("Отмена всех активных ордеров (mock).")
        self.open_orders = []

    def execute_order(self, symbol, order):
        # Защита: если action=stop — дренировать, если hold — ничего
        if order["action"] == "stop":
            self.drain_positions()
            return
        if order["action"] == "hold" or order["amount"] == 0:
            print("Нет действия (hold/zero).")
            return
        # Отправить ордер на биржу (mock)
        print(f"Ордер: {order['action']} {order['amount']} {symbol}")
        self.open_orders.append(order)
        # Эмуляция случайной задержки/ошибки
        time.sleep(0.1)
        if False:  # тут можно эмулировать ошибки
            raise Exception("Биржа недоступна")