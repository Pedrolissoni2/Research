import cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import csv
import html
import os

scraper = cloudscraper.create_scraper()


def start_agb_reports(days, key_words, date_limit, path_output, url_list, stats, proxies=None):
    data_list = []
    page = 1
    while True:
        print(f"agb page {page}")
        posts = request_api(page)
        if not posts:
            break
        has_more = process_response(posts, date_limit, key_words, url_list, data_list, path_output)
        if has_more:
            page += 1
        else:
            break
    save_data(data_list, path_output)
    stats.append({
        "source": "AGB",
        "news_count": len(data_list)
    })
    return stats


def request_api(page):
    url = f"https://agbrief.com/wp-json/wp/v2/posts?per_page=100&page={page}&_fields=id,title,date,link"
    print(url)
    resp = scraper.get(url)
    if resp.status_code != 200:
        return []
    return resp.json()


def request_url(url):
    print(url)
    sitecontent = scraper.get(url).content.decode("utf-8", errors="ignore")
    obj_bs4 = BeautifulSoup(sitecontent, "html.parser")
    return obj_bs4


def process_response(posts, date_limit, key_words, url_list, data_list, path_output):
    for post in posts:
        news_date = datetime.fromisoformat(post["date"])
        news_date = news_date.replace(tzinfo=None)
        formatted_date = news_date.strftime("%Y-%m-%d %H:%M:%S")

        if news_date >= date_limit:
            new_url = post["link"]
            api_title = html.unescape(post["title"]["rendered"])
            has_keyword, category = process_response_details(new_url, key_words)
            data_json = {
                "website": "agb",
                "category": category,
                "date": formatted_date,
                "title": api_title,
                "url": new_url,
                "has_keywords": ", ".join(has_keyword),
            }
            if data_json["url"] not in url_list:
                data_list.append(data_json.copy())
                url_list.append(data_json["url"])
        else:
            return False
    return True


def process_response_details(url, key_words):
    has_keywords = []
    category = ""
    try:
        obj_bs4_details = request_url(url)

        category_bs4 = obj_bs4_details.select_one("a.td-post-category")
        category = category_bs4.text.strip() if category_bs4 else ""

        news_details_texts = obj_bs4_details.select("div.td-post-content p")
        for news_details in news_details_texts:
            news_details_text = news_details.text
            for key_word in key_words:
                if key_word in news_details_text.lower() and key_word not in has_keywords:
                    has_keywords.append(key_word)
    except Exception as e:
        print(f"  [WARN] agb detail failed for {url}: {e}")
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
