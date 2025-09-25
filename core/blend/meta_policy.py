"""
MetaPolicy: переключение blend-схем в зависимости от режима рынка.

Режимы: trend, range, panic, custom
"""
class MetaPolicy:
    def __init__(self, blends_by_mode: dict):
        self.blends_by_mode = blends_by_mode

    def select_blend(self, market_mode: str) -> dict:
        """Вернуть blend-конфиг для текущего режима рынка."""
        return self.blends_by_mode.get(
            market_mode, self.blends_by_mode.get("default")
        )