# Примитивный news_cache для примера (должен быть thread-safe при concurrency!)
from collections import deque

class NewsCache:
    def __init__(self, maxlen=50):
        self._cache = deque(maxlen=maxlen)
    def add(self, item):
        self._cache.appendleft(item)
    def get_latest(self, n=5):
        return list(self._cache)[:n]

news_cache = NewsCache()
# Пример добавления новости:
# news_cache.add({'title': 'BTC вырос', 'link': 'https://...'})