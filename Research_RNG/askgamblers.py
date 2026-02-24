from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import csv
import os

from utils import fetch_html_tiered


def start_askgamblers_reports(days, key_words, date_limit, path_output, url_list, stats, proxies=None):
    data_list = []
    page = 1
    while True:
        print(page)
        obj_bs4 = request_url(f"https://www.askgamblers.com/gambling-news/{page}", proxies=proxies)
        has_next_page = process_response(obj_bs4, date_limit, key_words, url_list, data_list, path_output, proxies=proxies)
        if has_next_page == True:
            page = page + 1
        else:
            break
    save_data(data_list, path_output)
    stats.append({
        "source": "Askgamblers",
        "news_count": len(data_list)
    })
    return stats


def request_url(url, proxies):
    print(url)
    return fetch_html_tiered(url, proxies=proxies) or BeautifulSoup("", "html.parser")


def process_response(obj_bs4: BeautifulSoup, date_limit, key_words, url_list, data_list, path_output, proxies):
    news = obj_bs4.select("ul.card-list.group li a.card")
    dates = obj_bs4.select("p.card__status")
    in_limit = True

    for new, date in zip(news, dates):
        url = "https://www.askgamblers.com"+new["href"]
        news_date_str = date.text.strip()
        news_date = datetime.strptime(news_date_str, "%B %d, %Y")
        formatted_date = news_date.strftime("%Y-%m-%d %H:%M:%S")

        if news_date >= date_limit:
            has_keyword = process_response_details(url, key_words, proxies=proxies)
            title_soup = new.select_one("h3")
            data_json = {
                "website": "askgamblers",
                "category": "",
                "date": formatted_date,
                "title": title_soup.text.strip(),
                "url": url,
                "has_keywords": ", ".join(has_keyword),
            }
            if data_json["url"] not in url_list:
                data_list.append(data_json.copy())
                url_list.append(data_json["url"])
        else:
            in_limit = False
            break

    next_page = obj_bs4.select_one("span.icon.icon--chevron-right")

    if next_page != None and in_limit == True:
        return True
    return False


def process_response_details(url, key_words, proxies):
    has_keywords = []

    obj_bs4_details = request_url(url, proxies=proxies)
    news_details_texts = obj_bs4_details.select("div.single-post__content.post-content p")
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

