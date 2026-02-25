import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import csv
import json
import os


days = 15
date_limit = datetime.now() - timedelta(days=days)
print(date_limit)
key_words = ['jackpot', 'operator', 'provider', 'progressive jackpot', 'must drop by', 'must hit by', 'daily jackpot', 'super jackpot',
             'mystery jackpot', 'community jackpot', 'multi-level jackpot', 'cross-game jackpot', 'mega jackpot', 'mini jackpot', 
             'major jackpot', 'local jackpot', 'networked jackpot', 'shared jackpot', 'accumulative jackpot', 'pooled jackpot', 
             'random jackpot', 'tiered jackpot', 'trigger jackpot', 'rolling jackpot', 'guaranteed jackpot', 'linked jackpot', 
             'progression rate', 'jackpot meter', 'jackpot pool', 'jackpot contribution', 'jackpot prize', 'jackpot drop', 'must drop', 
             'jackpot slot', 'win cap', 'bonus round jackpot', 'jackpot pot', 'online casino',
]
topics = [
    # 'marketing-affiliates',
    # 'tech-innovation',
    # 'casino-games',
    'casino',
    # 'legal-compliance',
    # 'crypto-gambling',
    # 'sustainable-gambling',
    # 'sports-betting',
    # 'people',
    # 'esports',
    # 'finance',
    # 'gaming',
    # 'ice365',
    # 'lottery',
    # 'strategy',
    # 'money-laundering',
    # 'offshore-gaming',
    # 'uncategorized'
]


data_list = []
url_list = []
path_output = "C:\\Users\\pedro\\OneDrive\\Área de Trabalho\\Research_RNG\\data"


def start_crawler(days, key_words):
    global url_list
    
    if 'news.csv' in os.listdir(path_output):

        output_file = os.path.join(path_output, 'news.csv')
        with open (output_file, mode="r", newline='', encoding='utf-8') as file:
            file_reader = csv.DictReader(file, fieldnames=['category', 'date', 'title', 'url', 'website', 'has_keywords'])
            for line, row in enumerate(file_reader):
                if line != 0:
                    url_list.append(row['url'])

    for topic in topics:
        for content_type in ['news', 'in-depth']:
             
            page = 1
            while True:
                print(topic, page)
                obj_bs4 = request_url(f"https://igamingbusiness.com/subtopic/{topic}/{content_type}/page/{page}")
                has_next_page = process_response(obj_bs4, topic)
                if has_next_page == True:
                    page = page + 1
                else:
                    break
    save_data(data_list, path_output)
        
                
            

def request_url(url):
    print(url)
    sitecontent = requests.get(url).content.decode("utf-8", errors="ignore")
    obj_bs4 = BeautifulSoup(sitecontent, 'html.parser')
    return obj_bs4

def process_response(obj_bs4:BeautifulSoup, topic):
    global path_output, data_list
    
    news = obj_bs4.select("h2.c-card__title a")
    # categories = obj_bs4.select("div.c-card__tags a")
    dates = obj_bs4.select("span.c-card__date time")
    in_limit = True

    # for new, category, date in zip(news, categories, dates):
    for new, date in zip(news, dates):
        string = new['href']
        string_replace = string.replace("https://igamingbusiness.com/","")
        string_split = string_replace.split("/")[0]
        string_category = string_split.replace('-'," ").title()

        news_date_str = date['datetime']
        news_date = datetime.strptime(news_date_str, "%Y-%m-%d %H:%M:%S")
        formatted_date = news_date.strftime("%Y-%m-%d %H:%M:%S")

        if news_date >= date_limit:
            has_keyword = process_response_details(new['href'])
            data_json = {
                'website': "igb",
                'category': string_category,
                'date': formatted_date,
                'title': new.text.strip(),
                'url':new["href"],
                'has_keywords': ', '.join(has_keyword)

            }
            if data_json['url'] not in url_list:
                data_list.append(data_json.copy())
                url_list.append(data_json['url'])
        else:
            in_limit = False
            # break

    next_page = obj_bs4.select_one('a.nextpostslink')
    
    if next_page != None and in_limit == True:
        return True
    return False


def process_response_details(url):
    global key_words
    has_keywords = []

    obj_bs4_details = request_url(url)
    news_details_texts = obj_bs4_details.select('article.o-single-template__content div p')
    for news_details in news_details_texts:
        news_details_text = news_details.text
        for key_word in key_words:
           if key_word in news_details_text.lower() and key_word not in has_keywords:
            # print(news_details_text, key_word)
            has_keywords.append(key_word)
    return has_keywords   

def save_data(data_list, path_output):
    output_file = os.path.join(path_output, 'news.csv')
    insert_header = False
    if 'news.csv' not in os.listdir(path_output):
        insert_header = True

    with open(output_file, mode='a+', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['category', 'date', 'title', 'url', 'website', 'has_keywords'])
        if insert_header == True:
            writer.writeheader()
        writer.writerows(data_list)



start_crawler(days, key_words)
