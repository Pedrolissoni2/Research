import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import csv
import json
import os
import xml

headers = {
  'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8,application/signed-exchange;v=b3;q=0.7',
  'accept-language': 'pt-BR,pt-PT;q=0.9,pt;q=0.8,en-US;q=0.7,en;q=0.6',
  'if-modified-since': 'Wed, 04 Dec 2024 22:05:38 GMT',
  'priority': 'u=0, i',
  'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Linux"',
  'sec-fetch-dest': 'document',
  'sec-fetch-mode': 'navigate',
  'sec-fetch-site': 'same-origin',
  'sec-fetch-user': '?1',
  'upgrade-insecure-requests': '1',
  'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
}


def start_europeangaming_reports(days, key_words, date_limit, path_output, url_list, stats, proxies=None):
    data_list = []
    page = 1
    while True:
        print(page)
        obj_bs4 = request_url(f"https://europeangaming.eu/portal/category/latest-news/page/{page}/", proxies=proxies)
        has_next_page = process_response(obj_bs4, date_limit, key_words, url_list, data_list, path_output, proxies=proxies)
        if has_next_page == True:
            page = page + 1
            # break
        else:
            break
    save_data(data_list, path_output)
    stats.append({
        "source": "Europeangaming",
        "news_count": len(data_list)
    })
    return stats

def request_url(url, proxies):
    global headers
    print(url)
    sitecontent = requests.get(url, proxies=proxies, headers=headers, verify=False).content
    obj_bs4 = BeautifulSoup(sitecontent, "html.parser")
    return obj_bs4


def process_response(obj_bs4: BeautifulSoup, date_limit, key_words, url_list, data_list, path_output, proxies):

    news = obj_bs4.select("li.mvp-blog-story-wrap.left.relative.infinite-post a")
    # categories = obj_bs4.select("div.td-ss-main-content a.td-post-category")
    in_limit = True

    # for new, category, date in zip(news, categories, dates):
    for new in news:
        has_keyword, formatted_date, news_date = process_response_details(new["href"], key_words, proxies=proxies)
        title_soup = new.select_one("h2")

        if news_date >= date_limit:
            data_json = {
                "website": "europeangaming",
                "category": "",
                "date": formatted_date,
                "title": title_soup.text.strip(),
                "url": new["href"],
                "has_keywords": ", ".join(has_keyword),
            }
            if data_json["url"] not in url_list:
                data_list.append(data_json.copy())
                url_list.append(data_json["url"])
        else:
            in_limit = False
            break

    next_page = obj_bs4.select_one('div.mvp-inf-more-wrap.left.relative a')

    if next_page != None and in_limit == True:
        return True
    return False


def process_response_details(url, key_words, proxies):
    has_keywords = []

    obj_bs4_details = request_url(url, proxies=proxies)
    date = obj_bs4_details.select_one("time.post-date.updated")
    news_date_str = date["datetime"]
    news_date = datetime.strptime(news_date_str, "%Y-%m-%d")
    formatted_date = news_date.strftime("%Y-%m-%d %H:%M:%S")
    news_details_texts = obj_bs4_details.select("div#mvp-content-main p")
    for news_details in news_details_texts:
        news_details_text = news_details.text
        for key_word in key_words:
            if key_word in news_details_text.lower() and key_word not in has_keywords:
                # print(news_details_text, key_word)
                has_keywords.append(key_word)
    return list(sorted(has_keywords)), formatted_date, news_date


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
