# casino_org.py
#
# STATUS: PLACEHOLDER — NOT integrated in main.py
#
# This file was originally a copy of the old sbcnews scraper.  It was renamed
# casino_org.py but was never updated with actual casino.org selectors or URL.
#
# TODO to activate:
#   1. Set BASE_URL to the casino.org news section (e.g. https://www.casino.org/news/)
#   2. Update the CSS selectors in process_response() and process_response_details()
#      to match casino.org's HTML structure
#   3. Uncomment the import + entry in SCRAPERS inside main.py

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import csv
import os

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'accept-language': 'en-US,en;q=0.9',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
}

BASE_URL = "https://www.casino.org/news/page/{page}/"  # TODO: verify this URL


def start_casino_org_reports(days, key_words, date_limit, path_output, url_list, stats, proxies=None):
    data_list = []
    page = 1
    while True:
        print(page)
        obj_bs4 = request_url(BASE_URL.format(page=page), proxies=proxies)
        has_next_page = process_response(obj_bs4, date_limit, key_words, url_list, data_list, path_output, proxies=proxies)
        if has_next_page:
            page += 1
        else:
            break
    save_data(data_list, path_output)
    stats.append({
        "source": "Casino.org",
        "news_count": len(data_list)
    })
    return stats


def request_url(url, proxies=None):
    global headers
    print(url)
    sitecontent = requests.get(url, proxies=proxies, headers=headers, verify=False).content
    return BeautifulSoup(sitecontent, "html.parser")


def process_response(obj_bs4: BeautifulSoup, date_limit, key_words, url_list, data_list, path_output, proxies):
    # TODO: update selectors for casino.org HTML structure
    news = obj_bs4.select("h2.post-box-title a")
    dates = obj_bs4.select("span.tie-date")
    in_limit = True

    for new, date in zip(news, dates):
        news_date_str = date.text.strip()
        try:
            news_date = datetime.strptime(news_date_str, "%B %d, %Y")
        except ValueError:
            continue
        formatted_date = news_date.strftime("%Y-%m-%d %H:%M:%S")

        if news_date >= date_limit:
            has_keyword, category = process_response_details(new["href"], key_words, proxies=proxies)
            data_json = {
                "website": "casino_org",
                "category": category,
                "date": formatted_date,
                "title": new.text.strip(),
                "url": new["href"],
                "has_keywords": ", ".join(has_keyword),
            }
            if data_json["url"] not in url_list:
                data_list.append(data_json.copy())
                url_list.append(data_json["url"])
        else:
            in_limit = False

    next_page = obj_bs4.select_one('span.tie-next-page a')
    return next_page is not None and in_limit


def process_response_details(url, key_words, proxies=None):
    has_keywords = []
    obj_bs4_details = request_url(url, proxies=proxies)
    # TODO: update selectors for casino.org article pages
    cat_tags = obj_bs4_details.select('span.post-cats a')
    category = cat_tags[-1].text.strip() if cat_tags else ""
    news_details_texts = obj_bs4_details.select("div.entry p")
    for news_details in news_details_texts:
        news_details_text = news_details.text
        for key_word in key_words:
            if key_word in news_details_text.lower() and key_word not in has_keywords:
                has_keywords.append(key_word)
    return list(sorted(has_keywords)), category


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
