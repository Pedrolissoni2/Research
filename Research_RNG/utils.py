"""
utils.py — Shared helpers for the Research_RNG scraper hub.

All 20 scraper modules contain identical copies of save_data().
New scrapers should import from here instead of duplicating the function.
Existing scrapers keep their local copies for now; a future refactor can
switch them over in one pass.
"""

import csv
import os
import time
import logging
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

import cloudscraper
import requests
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

DEFAULT_HEADERS = {
    "accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,image/apng,*/*;q=0.8"
    ),
    "accept-language": "en-US,en;q=0.9",
    "user-agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
}

# HTTP status codes that indicate bot/rate-limit blocking
_BLOCKED_STATUSES = {403, 429, 503}


def fetch_html(url, proxies=None, headers=None, retries=3, backoff=2, timeout=30):
    """GET a URL and return a BeautifulSoup object, or None on failure.

    Retries up to *retries* times with exponential backoff.
    SSL verification is disabled because several gambling-news sites have
    misconfigured or self-signed certificates.
    """
    h = headers or DEFAULT_HEADERS
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, proxies=proxies, headers=h, verify=False, timeout=timeout)
            resp.raise_for_status()
            return BeautifulSoup(resp.content, "html.parser")
        except Exception as exc:
            log.warning("[fetch_html] attempt %d/%d failed for %s — %s", attempt, retries, url, exc)
            if attempt < retries:
                time.sleep(backoff ** attempt)
    return None


def fetch_html_tiered(url, proxies=None, headers=None, retries=3, backoff=2, timeout=30):
    """GET a URL using a two-tier strategy.

    Tier 1: plain requests.  If the response is 403/429/503 (bot block) it
    immediately falls through to Tier 2 without further retries.

    Tier 2: cloudscraper, which handles Cloudflare JS challenges
    automatically.

    Returns a BeautifulSoup object, or None if both tiers fail.
    """
    h = headers or DEFAULT_HEADERS

    # Tier 1 — plain requests
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, proxies=proxies, headers=h, verify=False, timeout=timeout)
            if resp.status_code in _BLOCKED_STATUSES:
                log.info(
                    "[fetch_html_tiered] status %d for %s — switching to cloudscraper",
                    resp.status_code, url,
                )
                break  # skip remaining Tier 1 retries
            resp.raise_for_status()
            return BeautifulSoup(resp.content, "html.parser")
        except requests.exceptions.HTTPError:
            break
        except Exception as exc:
            log.warning(
                "[fetch_html_tiered] plain attempt %d/%d failed for %s — %s",
                attempt, retries, url, exc,
            )
            if attempt < retries:
                time.sleep(backoff ** attempt)

    # Tier 2 — cloudscraper
    log.info("[fetch_html_tiered] using cloudscraper for %s", url)
    for attempt in range(1, retries + 1):
        try:
            scraper = cloudscraper.create_scraper()
            resp = scraper.get(url, proxies=proxies, verify=False, timeout=timeout)
            resp.raise_for_status()
            return BeautifulSoup(resp.content, "html.parser")
        except Exception as exc:
            log.warning(
                "[fetch_html_tiered] cloudscraper attempt %d/%d failed for %s — %s",
                attempt, retries, url, exc,
            )
            if attempt < retries:
                time.sleep(backoff ** attempt)
    return None


def fetch_rss(url, proxies=None, timeout=30):
    """Fetch an RSS 2.0 feed and return a list of item dicts.

    Each dict has keys:
      'title'       – article title (str)
      'url'         – article link (str)
      'pub_date'    – publication datetime (datetime, tz-naive UTC) or None
      'description' – excerpt/summary text (str, may contain HTML)
      'categories'  – list of category strings

    Returns an empty list on network or parse failure.
    """
    try:
        resp = requests.get(
            url, proxies=proxies, headers=DEFAULT_HEADERS, verify=False, timeout=timeout
        )
        resp.raise_for_status()
    except Exception as exc:
        log.warning("[fetch_rss] failed to fetch %s — %s", url, exc)
        return []

    try:
        root = ET.fromstring(resp.content)
    except ET.ParseError as exc:
        log.warning("[fetch_rss] XML parse error for %s — %s", url, exc)
        return []

    channel = root.find("channel")
    if channel is None:
        return []

    items = []
    for item in channel.findall("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub_date_str = (item.findtext("pubDate") or "").strip()
        description = (item.findtext("description") or "").strip()
        categories = [c.text.strip() for c in item.findall("category") if c.text]

        pub_date = None
        if pub_date_str:
            try:
                pub_date = parsedate_to_datetime(pub_date_str).replace(tzinfo=None)
            except Exception:
                pass

        items.append({
            "title": title,
            "url": link,
            "pub_date": pub_date,
            "description": description,
            "categories": categories,
        })
    return items


def fetch_json_post(url, payload, headers, proxies=None, retries=3, backoff=2, timeout=30):
    """POST *payload* to *url* and return parsed JSON, or None on failure."""
    for attempt in range(1, retries + 1):
        try:
            resp = requests.post(url, data=payload, headers=headers, proxies=proxies,
                                 verify=False, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            log.warning("[fetch_json_post] attempt %d/%d failed for %s — %s", attempt, retries, url, exc)
            if attempt < retries:
                time.sleep(backoff ** attempt)
    return None


# ---------------------------------------------------------------------------
# Keyword matching
# ---------------------------------------------------------------------------

def find_keywords(text, key_words):
    """Return a sorted list of keywords that appear in *text* (case-insensitive)."""
    text_lower = text.lower()
    return sorted({kw for kw in key_words if kw in text_lower})


# ---------------------------------------------------------------------------
# CSV persistence
# ---------------------------------------------------------------------------

CSV_FIELDNAMES = ["category", "date", "title", "url", "website", "has_keywords"]


def save_data(data_list, path_output):
    """Append *data_list* to news.csv in *path_output*, creating the file if needed."""
    output_file = os.path.join(path_output, "news.csv")
    insert_header = not os.path.isfile(output_file)
    with open(output_file, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES, extrasaction="ignore")
        if insert_header:
            writer.writeheader()
        writer.writerows(data_list)


def load_existing_urls(path_output):
    """Read news.csv and return a list of all previously scraped URLs."""
    csv_path = os.path.join(path_output, "news.csv")
    if not os.path.isfile(csv_path):
        return []
    urls = []
    with open(csv_path, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, fieldnames=CSV_FIELDNAMES)
        for i, row in enumerate(reader):
            if i != 0:  # skip header row
                urls.append(row["url"])
    return urls
