"""
casinobeats.py — Casino Beats scraper.

Uses the WordPress RSS feed for article listing and fetch_html_tiered
for individual article detail pages.
"""
import csv
import logging
import os

from bs4 import BeautifulSoup

from utils import fetch_html_tiered, fetch_rss

log = logging.getLogger(__name__)

RSS_BASE = "https://casinobeats.com/feed/"


def start_casinobeats_reports(days, key_words, date_limit, path_output, url_list, stats, proxies=None):
    data_list = []

    page = 1
    while True:
        feed_url = RSS_BASE if page == 1 else f"{RSS_BASE}?paged={page}"
        log.info("[casinobeats] fetching RSS page %d", page)
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

            has_keywords, category = _fetch_detail(url, key_words, proxies)

            data_list.append({
                "website": "casinobeats",
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
    stats.append({"source": "Casinobeats", "news_count": len(data_list)})
    return stats


def _fetch_detail(url, key_words, proxies):
    """Fetch article page and return (sorted_keywords, category)."""
    soup = fetch_html_tiered(url, proxies=proxies) or BeautifulSoup("", "html.parser")

    category_soup = soup.select('a.entry-crumb')
    category = category_soup[-1].text.strip() if category_soup else ""

    paras = soup.select("div.td-post-content.tagdiv-type p")
    text = " ".join(p.text for p in paras).lower()
    has_keywords = sorted({kw for kw in key_words if kw in text})

    return has_keywords, category


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
