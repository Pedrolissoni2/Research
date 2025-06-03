import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import csv
import json
import os



def start_focusgn_reports(days, key_words, date_limit, path_output, url_list, stats):
    data_list = []
    page = 1
    while True:
        print(page)
        obj_bs4 = request_url(f"https://focusgn.com/page/{page}/?s=")
        has_next_page = process_response(obj_bs4, date_limit, key_words, url_list, data_list, path_output)
        if has_next_page == True:
            page = page + 1
        else:
            break
    save_data(data_list, path_output)
    stats.append({
        "source": "Focusgn",
        "news_count": len(data_list)
    })
    return stats


def request_url(url):
    print(url)
    sitecontent = requests.get(url).content
    obj_bs4 = BeautifulSoup(sitecontent, "html.parser")
    return obj_bs4


def process_response(obj_bs4: BeautifulSoup, date_limit, key_words, url_list, data_list, path_output):

    news = obj_bs4.select("article.br-10.grid-article.bg-w a")
    # categories = obj_bs4.select("h1.page-title.text-primary.font-light.category-header a")
    dates = obj_bs4.select("div.article-date.text-primary.font-light.bg-w")
    in_limit = True

    # for new, category, date in zip(news, categories, dates):
    for new, date in zip(news, dates):
        news_date_str = date.text.strip()
        news_date = datetime.strptime(news_date_str, "%m/%d/%y")
        formatted_date = news_date.strftime("%Y-%m-%d %H:%M:%S")

        if news_date >= date_limit:
            has_keyword, category = process_response_details(new["href"], key_words)
            title_soup = new.select_one("h3")
            data_json = {
                "website": "focus_gn",
                "category": category,
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
            # break

    next_page = obj_bs4.select_one("div.nav-links a.next.page-numbers")

    if next_page != None and in_limit == True:
        return True
    return False


def process_response_details(url, key_words):
    has_keywords = []

    obj_bs4_details = request_url(url)
    category_soup = obj_bs4_details.select_one("span.section a")
    if category_soup != None:
        category = category_soup.text.strip()
    else:
        category = ""
    news_details_texts = obj_bs4_details.select("div.article-content p")
    for news_details in news_details_texts:
        news_details_text = news_details.text
        for key_word in key_words:
            if key_word in news_details_text.lower() and key_word not in has_keywords:
                # print(news_details_text, key_word)
                has_keywords.append(key_word)
    return list(sorted(has_keywords)), category


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
