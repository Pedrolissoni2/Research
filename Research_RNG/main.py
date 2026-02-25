import requests
import urllib3
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import csv
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import os
from casinoreports import start_casinoreports_reports
from yogonet import start_yogonet_reports
from igb_json import start_igb_json_reports
from focusgn import start_focusgn_reports
from next_io import start_next_io_reports
from the_gamblest import start_the_gamblest_reports
from cgn import start_cgn_reports
from askgamblers import start_askgamblers_reports
from bigwinboard import start_bigwinboard_reports
from igamingfuture import start_igamingfuture_reports
from casinobeats import start_casinobeats_reports
from sbcnews import start_sbcnews_reports
from guru_news import start_guru_news_reports
from ig_brazil import start_ig_brazil_reports
from gamblinginsider import start_gamblinginsider_reports
from agb import start_agb_reports
from europeangaming import start_europeangaming_reports

 
stats = []

username = 'U0000220625'
password = 'PW_157253090bf79e2059523ddaa70824bac'
proxy = f"http://{username}:{password}@unblock.smartproxy.com:60000"

proxies = {
    'http': proxy,
    'https': proxy
}


days = 10
date_limit = datetime.now() - timedelta(days=days)
print(date_limit)
key_words = [
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
    "non-regulated, Brazil"
]


url_list = []
path_output = "C:\\Users\\pedro\\OneDrive\\Área de Trabalho\\Research_RNG\\data"


if "news.csv" in os.listdir(path_output):
    output_file = os.path.join(path_output, "news.csv")
    with open(output_file, mode="r", newline="", encoding="utf-8-sig") as file:
        file_reader = csv.DictReader(
            file,
            fieldnames=[
                "category",
                "date",
                "title",
                "url",
                "website",
                "has_keywords",
            ],
        )
        for line, row in enumerate(file_reader):
            if line != 0:
                url_list.append(row["url"])

def fix_mojibake(text):
    """Repair text incorrectly decoded as Windows-1252 instead of UTF-8.
    E.g. 'â€"' -> '—',  'Ã—' -> '×'
    """
    if not text:
        return text
    try:
        return text.encode('cp1252').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text


def fix_encoding_in_csv():
    output_file = os.path.join(path_output, "news.csv")
    if not os.path.exists(output_file):
        return
    fieldnames = ["category", "date", "title", "url", "website", "has_keywords"]
    with open(output_file, encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))
    fixed = 0
    for row in rows:
        for field in ('title', 'category', 'has_keywords'):
            original = row.get(field, '')
            repaired = fix_mojibake(original)
            if repaired != original:
                row[field] = repaired
                fixed += 1
    with open(output_file, mode='w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    if fixed:
        print(f"  Fixed {fixed} encoding issues in CSV.")
    else:
        print("  Encoding check done. CSV saved with UTF-8 BOM for Excel compatibility.")


errors = []

def run(name, fn, *args):
    try:
        return fn(*args)
    except Exception as e:
        errors.append({"source": name, "error": str(e)})
        print(f"[ERROR] {name}: {e}")
        return stats

stats = run("casinoreports",   start_casinoreports_reports,   days, key_words, date_limit, path_output, url_list, stats)
stats = run("yogonet",         start_yogonet_reports,         days, key_words, date_limit, path_output, url_list, stats)
stats = run("igb_json",        start_igb_json_reports,        days, key_words, date_limit, path_output, url_list, stats)
stats = run("focusgn",         start_focusgn_reports,         days, key_words, date_limit, path_output, url_list, stats)
stats = run("the_gamblest",    start_the_gamblest_reports,    days, key_words, date_limit, path_output, url_list, stats)
stats = run("cgn",             start_cgn_reports,             days, key_words, date_limit, path_output, url_list, stats)
stats = run("bigwinboard",     start_bigwinboard_reports,     days, key_words, date_limit, path_output, url_list, stats)
stats = run("igamingfuture",   start_igamingfuture_reports,   days, key_words, date_limit, path_output, url_list, stats)
stats = run("askgamblers",     start_askgamblers_reports,     days, key_words, date_limit, path_output, url_list, stats, proxies)
stats = run("next_io",         start_next_io_reports,         days, key_words, date_limit, path_output, url_list, stats, proxies)
stats = run("casinobeats",     start_casinobeats_reports,     days, key_words, date_limit, path_output, url_list, stats, proxies)
stats = run("sbcnews",         start_sbcnews_reports,         days, key_words, date_limit, path_output, url_list, stats, proxies)
stats = run("guru_news",       start_guru_news_reports,       days, key_words, date_limit, path_output, url_list, stats)
stats = run("ig_brazil",       start_ig_brazil_reports,       days, key_words, date_limit, path_output, url_list, stats)
stats = run("gamblinginsider", start_gamblinginsider_reports, days, key_words, date_limit, path_output, url_list, stats, proxies)
stats = run("europeangaming",  start_europeangaming_reports,  days, key_words, date_limit, path_output, url_list, stats, proxies)
stats = run("agb", start_agb_reports, days, key_words, date_limit, path_output, url_list, stats)


fix_encoding_in_csv()

print()
print("=== SUMMARY ===")
for stat in stats:
    print(f"  {stat['source']} - {stat['news_count']} news")

if errors:
    print()
    print("=== ERRORS ===")
    for err in errors:
        print(f"  {err['source']}: {err['error']}")
else:
    print()
    print("All sources completed successfully.")