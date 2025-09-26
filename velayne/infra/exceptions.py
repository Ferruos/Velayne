class ConfigError(Exception):
    """Ошибка конфигурации приложения"""

class DependencyError(Exception):
    """Зависимость не найдена или не может быть импортирована"""

class ModeError(Exception):
    """Ошибка режима работы"""

class PaymentError(Exception):
    """Ошибка при обработке оплаты"""

class ExchangeError(Exception):
    """Ошибка при работе с биржей/рынком"""