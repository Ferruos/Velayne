import os
import json
from pathlib import Path
from datetime import datetime
import feedparser

CACHE_PATH = Path("data/news_cache.json")
os.makedirs(CACHE_PATH.parent, exist_ok=True)

FEEDS = [
    ("CoinDesk", "https://www.coindesk.com/arc/outboundfeeds/rss/"),
    ("CoinTelegraph", "https://cointelegraph.com/rss"),
    ("Binance", "https://www.binance.com/en/support/announcement/c-48?navId=48&type=1"),  # Not a true RSS, but placeholder
]

TRIGGERS = {
    "FOMC": 1,
    "CPI": 1,
    "SEC": 1,
    "sanction": 1,
    "hack": 1,
    "exploit": 1,
    "delisting": 1,
    "FUD": 1,
    "court": 1,
    "fine": 1,
    "liquidation": 1,
    "SECURITY": 1,
    "stablecoin": 1,
    "lawsuit": 1,
    "regulation": 1,
}

T1 = 2  # sum >= T1 → CAUTION
T2 = 4  # sum >= T2 → RED

def fetch_news(max_items=100) -> list:
    items = []
    try:
        for source, url in FEEDS:
            d = feedparser.parse(url)
            for entry in d.entries[:max_items]:
                items.append({
                    "title": entry.title,
                    "link": entry.link,
                    "published": entry.get("published", ""),
                    "source": source,
                })
        # Кэшируем
        with open(CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(items, f)
        return items
    except Exception:
        # Нет сети — читаем кэш
        if CACHE_PATH.exists():
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                items = json.load(f)
            return items
        return []

def classify_news(items) -> dict:
    score = 0
    tags = {}
    for item in items:
        text = item["title"].lower()
        for key, val in TRIGGERS.items():
            if key.lower() in text:
                score += val
                tags[key] = tags.get(key, 0) + 1
    level = "NONE"
    if score >= T2:
        level = "RED"
    elif score >= T1:
        level = "CAUTION"
    return {
        "level": level,
        "score": score,
        "tags": tags,
        "count": len(items)
    }

def news_guard():
    """Вернуть (level, пояснение)"""
    items = []
    try:
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            items = json.load(f)
    except Exception:
        pass
    result = classify_news(items)
    level = result.get("level", "NONE")
    tags = result.get("tags", {})
    explain = "Нет тревожных новостей"
    if level == "CAUTION":
        explain = "Внимание: важные новости (" + ", ".join(tags.keys()) + ")"
    elif level == "RED":
        explain = "Критические новости (" + ", ".join(tags.keys()) + ")"
    return level, {"explain": explain, **result}