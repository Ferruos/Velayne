import feedparser
from transformers import pipeline

FEEDS = [
    "https://www.coindesk.com/arc/outboundfeeds/rss/?outputType=xml",
    "https://cryptopanic.com/news/rss/",
    "https://news.ycombinator.com/rss"
]

nlp = pipeline("sentiment-analysis", model="yiyanghkust/finbert-tone")

def fetch_news():
    news = []
    for url in FEEDS:
        d = feedparser.parse(url)
        for entry in d.entries[:5]:
            news.append({
                "title": entry.title,
                "summary": getattr(entry, "summary", entry.title),
                "link": entry.link
            })
    return news

def analyze_news(news_items):
    for n in news_items:
        try:
            sentiment = nlp(n["summary"][:512])[0]
            n["sentiment"] = sentiment["label"]
            n["score"] = sentiment["score"]
        except Exception:
            n["sentiment"] = "unknown"
            n["score"] = 0.0
    return news_items

def get_analyzed_news():
    news = fetch_news()
    analyzed = analyze_news(news)
    return analyzed