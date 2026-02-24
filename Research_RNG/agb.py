"""
agb.py — AG Brief scraper.

Uses the WordPress RSS feed for article listing (avoids Cloudflare-protected
admin-ajax.php) and cloudscraper for individual article pages.
"""

import csv
import logging
import os

import cloudscraper
from bs4 import BeautifulSoup

from utils import fetch_rss

log = logging.getLogger(__name__)

# WordPress RSS supports pagination via ?paged=N
RSS_BASE = "https://agbrief.com/feed/"


def start_agb_reports(days, key_words, date_limit, path_output, url_list, stats, proxies=None):
    data_list = []
    scraper = cloudscraper.create_scraper()

    page = 1
    while True:
        feed_url = RSS_BASE if page == 1 else f"{RSS_BASE}?paged={page}"
        log.info("[agb] fetching RSS page %d", page)
        items = fetch_rss(feed_url, proxies=proxies)
        if not items:
            break

        in_limit = True
        for item in items:
            pub_date = item["pub_date"]
            if pub_date is None:
                continue

            if pub_date < date_limit:
                in_limit = False
                break

            url = item["url"]
            if url in url_list:
                continue

            category, has_keywords = _fetch_detail(scraper, url, key_words, proxies)

            data_list.append({
                "website": "agb",
                "category": category,
                "date": pub_date.strftime("%Y-%m-%d %H:%M:%S"),
                "title": item["title"],
                "url": url,
                "has_keywords": ", ".join(has_keywords),
            })
            url_list.append(url)

        if not in_limit:
            break
        page += 1

    save_data(data_list, path_output)
    stats.append({"source": "AGB", "news_count": len(data_list)})
    return stats


def _fetch_detail(scraper, url, key_words, proxies):
    """Fetch an article page and return (category, sorted_keywords)."""
    try:
        resp = scraper.get(url, proxies=proxies, verify=False, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "html.parser")
    except Exception as exc:
        log.warning("[agb] detail fetch failed for %s — %s", url, exc)
        return "", []

    cat_el = soup.select_one("a.td-post-category")
    category = cat_el.text.strip() if cat_el else ""

    paras = soup.select("div.td-post-content p")
    text = " ".join(p.text for p in paras).lower()
    has_keywords = sorted({kw for kw in key_words if kw in text})

    return category, has_keywords


def save_data(data_list, path_output):
    output_file = os.path.join(path_output, "news.csv")
    insert_header = "news.csv" not in os.listdir(path_output)

    with open(output_file, mode="a+", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["category", "date", "title", "url", "website", "has_keywords"],
        )
        if insert_header:
            writer.writeheader()
        writer.writerows(data_list)
