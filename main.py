import sqlite3
from datetime import datetime
from urllib.parse import urlparse, urlunparse
import feedparser

FEEDS = [
    {"name": "Українська Правда", "url": "https://www.pravda.com.ua/rss"},
    {"name": "Суспільне", "url": "https://suspilne.media/rss/all.rss"},
    {"name": "ТСН", "url": "https://tsn.ua/rss"},
    {"name": "МЕЖА", "url": "https://mezha.ua/feed/"},
    {"name": "r/reddit_ukr", "url": "https://www.reddit.com/r/reddit_ukr.rss"},
]

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36'

def init_db(conn):
    conn.execute("""
    CREATE TABLE IF NOT EXISTS articles (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            title        TEXT NOT NULL,
            summary      TEXT,
            url          TEXT UNIQUE NOT NULL,
            source       TEXT,
            published_at TEXT,
            created_at   TEXT DEFAULT CURRENT_TIMESTAMP
        ) 
    """)
    conn.commit()

def fetch_articles_from_feed(feed):
    parsed = feedparser.parse(feed['url'])
    articles = []
    for entry in parsed['entries']:
        articles.append({
            'title': entry.get('title', '').strip(),
            'summary': entry.get('summary', '').strip(),
            'url': clean_url(entry.get('link', '').strip()),
            'source': entry.get('source', '').strip(),
            'published_at': entry.get('published_at', str(datetime.now())),
        })
    return articles

def save_articles(conn, articles):
    new_count = 0
    for article in articles:
        cursor = conn.execute("""
            INSERT OR IGNORE INTO articles (title, summary, url, source, published_at)
                    VALUES (:title, :summary, :url, :source, :published_at)
                              """, article)
        if cursor.rowcount == 1:
            new_count += 1
    conn.commit()
    return new_count

def clean_url(url):
    parsed = urlparse(url)
    return urlunparse(parsed._replace(query="", fragment=""))

def main():
    conn = sqlite3.connect('personews.db')
    init_db(conn)

    for feed in FEEDS:
        articles = fetch_articles_from_feed(feed)
        new_count = save_articles(conn, articles)
        print(f"{feed['name']}: fetched {len(articles)}, saved {new_count} new")

    conn.close()

if __name__ == "__main__":
    main()
