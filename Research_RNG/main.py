"""
Research_RNG — News Aggregation Hub
=====================================
Collects gambling-industry news from 17 sources and appends results to
data/news.csv.  Each scraper is isolated in its own module; a failure in
one source never stops the others.

Usage
-----
    python main.py

Environment variables (all optional)
-------------------------------------
    PROXY_USER   SmartProxy username
    PROXY_PASS   SmartProxy password
    PROXY_HOST   Proxy host:port  (default: unblock.smartproxy.com:60000)
    DAYS         How many days back to collect  (default: 10)
"""

import csv
import logging
import os
import time
from datetime import datetime, timedelta

# ── scraper imports ──────────────────────────────────────────────────────────
from casinoreports   import start_casinoreports_reports
from yogonet         import start_yogonet_reports
from igb_json        import start_igb_json_reports
from focusgn         import start_focusgn_reports
from next_io         import start_next_io_reports
from the_gamblest    import start_the_gamblest_reports
from cgn             import start_cgn_reports
from askgamblers     import start_askgamblers_reports
from bigwinboard     import start_bigwinboard_reports
from igamingfuture   import start_igamingfuture_reports
from casinobeats     import start_casinobeats_reports
from sbcnews         import start_sbcnews_reports
from guru_news       import start_guru_news_reports
from ig_brazil       import start_ig_brazil_reports
from gamblinginsider import start_gamblinginsider_reports
from agb             import start_agb_reports
from europeangaming  import start_europeangaming_reports
# from casino_org import start_casino_org_reports  # TODO: needs casino.org selectors

# ── logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ── paths ─────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
PATH_OUTPUT = os.path.join(BASE_DIR, "data")
os.makedirs(PATH_OUTPUT, exist_ok=True)

# ── proxy ─────────────────────────────────────────────────────────────────────
PROXY_USER = os.getenv("PROXY_USER", "U0000220625")
PROXY_PASS = os.getenv("PROXY_PASS", "PW_157253090bf79e2059523ddaa70824bac")
PROXY_HOST = os.getenv("PROXY_HOST", "unblock.smartproxy.com:60000")

proxies = None
if PROXY_HOST and PROXY_USER:
    _p = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}"
    proxies = {"http": _p, "https": _p}

# ── time window ───────────────────────────────────────────────────────────────
DAYS       = int(os.getenv("DAYS", "10"))
DATE_LIMIT = datetime.now() - timedelta(days=DAYS)

# ── keyword list ──────────────────────────────────────────────────────────────
KEY_WORDS = [
    "jackpot",
    "operator",
    "provider",
    "mystery jackpot",
    "community jackpot",
    "mega jackpot",
    "multi-level jackpot",
    "progressive jackpot",
    "must drop by",
    "must hit by",
    "daily jackpot",
    "super jackpot",
    "cross-game jackpot",
    "mini jackpot",
    "major jackpot",
    "local jackpot",
    "networked jackpot",
    "shared jackpot",
    "accumulative jackpot",
    "pooled jackpot",
    "random jackpot",
    "tiered jackpot",
    "trigger jackpot",
    "rolling jackpot",
    "guaranteed jackpot",
    "linked jackpot",
    "progression rate",
    "jackpot meter",
    "jackpot pool",
    "jackpot contribution",
    "jackpot prize",
    "jackpot drop",
    "must drop",
    "jackpot slot",
    "win cap",
    "bonus round jackpot",
    "jackpot pot",
    "online casino",
    "bovada",
    "bodog",
    "hotdrop",
    "million",
    "win",
    "bonus abuse",
    "non-regulated operators",
    "non-regulated, Brazil",
]

# ── load existing URLs so we don't re-scrape known articles ──────────────────
url_list = []
csv_path = os.path.join(PATH_OUTPUT, "news.csv")
if os.path.isfile(csv_path):
    with open(csv_path, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(
            f,
            fieldnames=["category", "date", "title", "url", "website", "has_keywords"],
        )
        for i, row in enumerate(reader):
            if i != 0:
                url_list.append(row["url"])
    log.info("Loaded %d existing URLs for deduplication", len(url_list))

# ── scraper registry ──────────────────────────────────────────────────────────
# Format: (display_label, function, extra_kwargs)
# Scrapers that need a proxy receive proxies=proxies; if proxies is None they
# will simply run without one (most sites accept direct connections too).
SCRAPERS = [
    # ── no proxy required ────────────────────────────────────────────────────
    ("CasinoReports",    start_casinoreports_reports,    {}),
    ("Yogonet",          start_yogonet_reports,          {}),
    ("IGB (JSON API)",   start_igb_json_reports,         {}),
    ("FocusGN",          start_focusgn_reports,          {}),
    ("The Gamblest",     start_the_gamblest_reports,     {}),
    ("CGN",              start_cgn_reports,              {}),
    ("BigWinBoard",      start_bigwinboard_reports,      {}),
    ("iGaming Future",   start_igamingfuture_reports,    {}),
    ("Guru News",        start_guru_news_reports,        {}),
    # ── proxy-assisted (also work without proxy, just may hit rate limits) ───
    ("AskGamblers",      start_askgamblers_reports,      {"proxies": proxies}),
    ("Next.io",          start_next_io_reports,          {"proxies": proxies}),
    ("CasinoBeats",      start_casinobeats_reports,      {"proxies": proxies}),
    ("SBC News",         start_sbcnews_reports,          {"proxies": proxies}),
    ("iGaming Brazil",   start_ig_brazil_reports,        {"proxies": proxies}),
    ("Gambling Insider", start_gamblinginsider_reports,  {"proxies": proxies}),
    ("AGB",              start_agb_reports,              {"proxies": proxies}),
    ("European Gaming",  start_europeangaming_reports,   {"proxies": proxies}),
    # ("Casino.org",     start_casino_org_reports,       {"proxies": proxies}),  # TODO
]

# ── run ───────────────────────────────────────────────────────────────────────
log.info("Starting run — last %d days  (since %s)", DAYS, DATE_LIMIT.strftime("%Y-%m-%d"))
log.info("Output: %s", csv_path)
log.info("Proxy:  %s", PROXY_HOST if proxies else "none (direct connection)")
log.info("%d scrapers queued", len(SCRAPERS))
print()

stats       = []
errors      = []
t_run_start = time.time()

for label, fn, extra in SCRAPERS:
    log.info(">>> %s", label)
    t0 = time.time()
    try:
        stats = fn(
            days=DAYS,
            key_words=KEY_WORDS,
            date_limit=DATE_LIMIT,
            path_output=PATH_OUTPUT,
            url_list=url_list,
            stats=stats,
            **extra,
        )
    except Exception as exc:
        elapsed = time.time() - t0
        log.error("FAILED  %s — %s  (%.1fs)", label, exc, elapsed)
        errors.append({"source": label, "error": str(exc)})
        continue

    elapsed = time.time() - t0
    count   = stats[-1]["news_count"] if stats else 0
    log.info("    done — %d new articles  (%.1fs)", count, elapsed)

# ── summary ───────────────────────────────────────────────────────────────────
total_elapsed  = time.time() - t_run_start
total_articles = sum(s["news_count"] for s in stats)

print()
print("=" * 58)
print(f"  RESULTS  |  {datetime.now().strftime('%Y-%m-%d %H:%M')}  |  last {DAYS} days")
print("=" * 58)
for s in stats:
    print(f"  {s['source']:<26}  {s['news_count']:>5} articles")
if not stats:
    print("  (no data collected — all scrapers failed)")
print("-" * 58)
print(f"  {'TOTAL':<26}  {total_articles:>5} articles")
print(f"  Runtime: {total_elapsed:.0f}s")
if errors:
    print()
    print(f"  {len(errors)} scraper(s) failed:")
    for e in errors:
        print(f"    x {e['source']}: {e['error']}")
print("=" * 58)
