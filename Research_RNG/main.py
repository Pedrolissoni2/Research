import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import csv
import json
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
    with open(output_file, mode="r", newline="", encoding="utf-8") as file:
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

# stats = start_casinoreports_reports(days, key_words, date_limit, path_output, url_list, stats)
# stats = start_yogonet_reports(days, key_words, date_limit, path_output, url_list, stats)
# stats = start_igb_json_reports(days, key_words, date_limit, path_output, url_list, stats)
# stats = start_focusgn_reports(days, key_words, date_limit, path_output, url_list, stats)
# stats = start_the_gamblest_reports(days, key_words, date_limit, path_output, url_list, stats)
# stats = start_cgn_reports(days, key_words, date_limit, path_output, url_list, stats)
# stats = start_bigwinboard_reports(days, key_words, date_limit, path_output, url_list, stats)
# stats = start_igamingfuture_reports(days, key_words, date_limit, path_output, url_list, stats)
# stats = start_askgamblers_reports(days, key_words, date_limit, path_output, url_list, stats, proxies)
# stats = start_next_io_reports(days, key_words, date_limit, path_output, url_list, stats, proxies)
# stats = start_casinobeats_reports(days, key_words, date_limit, path_output, url_list, stats, proxies)
# stats = start_sbcnews_reports(days, key_words, date_limit, path_output, url_list, stats, proxies)
# stats = start_guru_news_reports(days, key_words, date_limit, path_output, url_list, stats)
# stats = start_ig_brazil_reports(days, key_words, date_limit, path_output, url_list, stats)
# stats = start_gamblinginsider_reports(days, key_words, date_limit, path_output, url_list, stats, proxies)
# stats = start_europeangaming_reports(days, key_words, date_limit, path_output, url_list, stats, proxies)
# start_agb_reports(days, key_words, date_limit, path_output, url_list)


print()
for stat in stats:
    print(stat["source"], "-", stat["news_count"])