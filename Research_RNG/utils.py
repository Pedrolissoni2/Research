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
