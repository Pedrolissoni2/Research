import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import csv
import json
import os



def start_igb_json_reports(days, key_words, date_limit, path_output, url_list, stats):
    data_list = []
    page = 1
    while True:
        print(page)
        json_content = request_url(
            method="POST",
            url="https://clus1-dcs1.synotiosearch.net/api/as/v1/engines/igamingbusiness-com/search.json",
            data={
                "query": "",
                "page": {"size": 1000, "current": page},
                "sort": {"date": "desc"},
                "facets": {
                    "category": {"type": "value", "size": 100},
                    "content_type": {"type": "value", "size": 100},
                    "region": {"type": "value", "size": 100},
                    "post_tag": {"type": "value", "size": 100},
                },
                "filters": {
                    "all": [
                        {"blog_id": "1"},
                        {"object_type": ["post", "company_news", "brand_view"]},
                        {"is_visible": "true"},
                        {"is_private": "false"},
                    ]
                },
            },
            parse="json",
            headers={"authorization": "Bearer search-2t8y4cc8ej9yh9cufhujes9v"},
        )

        has_next_page = process_response(json_content, date_limit, key_words, url_list, data_list, path_output)
        if has_next_page == True:
            page = page + 1
        else:
            break
    save_data(data_list, path_output)
    stats.append({
        "source": "IGB",
        "news_count": len(data_list)
    })
    return stats

def request_url(method, url, data, headers, parse):
    print(url)

    sitecontent = requests.request(method=method, url=url, json=data, headers=headers)
    if parse == "bs4":
        obj_bs4 = BeautifulSoup(sitecontent.content, "html.parser")
        return obj_bs4
    else:
        return sitecontent.json()


def process_response(json_content, date_limit, key_words, url_list, data_list, path_output):
    in_limit = True

    for new in json_content["results"]:
        string = new["url"]["raw"]
        string_replace = string.replace("https://igamingbusiness.com/", "")
        string_split = string_replace.split("/")[0]
        string_category = string_split.replace("-", " ").title()

        news_date_str = new["timestamp"]["raw"]
        news_date = datetime.strptime(news_date_str, "%Y-%m-%d %H:%M:%S")
        formatted_date = news_date.strftime("%Y-%m-%d %H:%M:%S")

        if news_date >= date_limit:
            has_keyword = process_response_details(new["url"]["raw"], key_words)
            data_json = {
                "website": "igb",
                "category": string_category,
                "date": formatted_date,
                "title": new["title"]["raw"],
                "url": new["url"]["raw"],
                "has_keywords": ", ".join(has_keyword),
            }
            if data_json["url"] not in url_list:
                data_list.append(data_json.copy())
                url_list.append(data_json["url"])
        else:
            in_limit = False
            break

    return in_limit


def process_response_details(url, key_words):
    has_keywords = []

    obj_bs4_details = request_url(
        method="GET", url=url, data={}, headers={}, parse="bs4"
    )
    news_details_texts = obj_bs4_details.select(
        "article.o-single-template__content div p"
    )
    for news_details in news_details_texts:
        news_details_text = news_details.text
        for key_word in key_words:
            if key_word in news_details_text.lower() and key_word not in has_keywords:
                # print(news_details_text, key_word)
                has_keywords.append(key_word)
    return has_keywords


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
