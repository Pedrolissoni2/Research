import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import csv
import json
import os


days = 3
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
]

data_list = []
url_list = []
path_output = "C:\\Users\\pedro\\OneDrive\\Área de Trabalho\\Research_RNG\\data"


def start_crawler(days, key_words):
    global url_list

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

    page = 1
    while True:
        print(page)
        obj_bs4 = request_url(f"https://www.casinoreports.com/page/{page}/?s")
        has_next_page = process_response(obj_bs4)
        if has_next_page == True:
            page = page + 1
        else:
            break
    save_data(data_list, path_output)


def request_url(url):
    print(url)
    sitecontent = requests.get(url).content
    obj_bs4 = BeautifulSoup(sitecontent, "html.parser")
    return obj_bs4


def process_response(obj_bs4: BeautifulSoup):
    global path_output, data_list

    news = obj_bs4.select("h3.post-preview__title.h4 a")
    categories = obj_bs4.select("p.post-preview__term.mb-mini a")
    dates = obj_bs4.select("p.post-preview__date")
    in_limit = True

    for new, category, date in zip(news, categories, dates):
        # for new, date in zip(news, dates):
        news_date_str = date.text.strip()
        news_date = datetime.strptime(news_date_str, "%B %d, %Y")
        formatted_date = news_date.strftime("%Y-%m-%d %H:%M:%S")

        if news_date >= date_limit:
            has_keyword = process_response_details(new["href"])
            data_json = {
                "website": "casinoreports",
                "category": category.text.strip(),
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
            # break

    next_page = obj_bs4.select_one("span.page-numbers.next.disabled")

    if next_page == None and in_limit == True:
        return True
    return False


def process_response_details(url):
    global key_words
    has_keywords = []

    obj_bs4_details = request_url(url)
    news_details_texts = obj_bs4_details.select("article.content p")
    for news_details in news_details_texts:
        news_details_text = news_details.text
        for key_word in key_words:
            if key_word in news_details_text.lower() and key_word not in has_keywords:
                # print(news_details_text, key_word)
                has_keywords.append(key_word)
    return list(sorted(has_keywords))


def save_data(data_list, path_output):
    output_file = os.path.join(path_output, "news.csv")
    insert_header = False
    if "news.csv" not in os.listdir(path_output):
        insert_header = True

    with open(output_file, mode="a+", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["category", "date", "title", "url", "website", "has_keywords"],
        )
        if insert_header == True:
            writer.writeheader()
        writer.writerows(data_list)


start_crawler(days, key_words)
