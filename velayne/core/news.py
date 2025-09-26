import feedparser
from datetime import datetime

RSS_FEEDS = [
    "https://cryptonews.com/news/feed",
    "https://cointelegraph.com/rss"
]

_news_cache = []

async def fetch_news():
    global _news_cache
    news = []
    for url in RSS_FEEDS:
        try:
            d = feedparser.parse(url)
            for entry in d.entries[:5]:
                news.append({
                    "title": entry.title,
                    "link": entry.link,
                    "dt": entry.published[:16] if hasattr(entry, "published") else ""
                })
        except Exception:
            continue
    _news_cache = news

async def get_latest_news(n=5):
    if not _news_cache:
        await fetch_news()
    return _news_cache[:n]