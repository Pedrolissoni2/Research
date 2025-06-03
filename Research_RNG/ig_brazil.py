import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import csv
import json
import os
import xml

headers = {
  'accept': '*/*',
  'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
  'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
  'cookie': '_ga=GA1.1.2099774829.1730486800; noticeVisibility=noticeVisibility; _pk_ref.381965.3ad5=%5B%22%22%2C%22%22%2C1734474159%2C%22https%3A%2F%2Fwww.google.com%2F%22%5D; _pk_ses.381965.3ad5=*; _clck=ksuyg3%7C2%7Cfrs%7C0%7C1766; __cf_bm=9ZpwJQukaxmGzXBJcgnEU58vEyYq8POA7jqr6k_L5dE-1734474159-1.0.1.1-JKQVd_UkyYQsurFnSfghUZc.eNgEwc39ETm0sv3Hxjod6uDwT.BZ3.oXmpW2eqFqCned1N1ljJ5NsvDZJr7pJg; cf_clearance=EWJPwmFXm2ZvH52k0s83oZ6GOQ39ouGrVkmYfVcSjYo-1734474383-1.2.1.1-6T36nKNumOxMrF6IsBTvoTDxO3DylTmtkftJ7dMq9NI3FEXQF1HjcvjbW38n9acZQMSluTiH2hIHY.DTN3qj6OrJuMgCw2vZUrWhyXzgFCobLwP7TFp2aJdEqqHH1hZwJJ.3OBjQz69.4ziaJP_Q3ykE0__Zeuvj5YUgbKZ.6vQpSmah7ac0VwpkmzvwBkZludKjFcvEvn82nVU1uH1VV8ACe0IDO42l7hcDlh0XyQ3JezYcLgvo_FRz3k_sJqsZsvPDCDbRv72h2NqREe3xeBtZXNeG_hBaI17DnmxPJQjlkJ375Q2fHohCh..9nVzlJS8rfXa1ugsXvOF0_NwHlo8nyZq1OsGgldNTWdGdn2IEgB0MrZ6KeKFs1SXIFYOp4ALgeOmb1IbhNpqesrpR6Q; _pk_id.381965.3ad5=ae87800eff9dc674.1730486803.11.1734474483.1734474159.; _ga_0ZE0VS1EEW=GS1.1.1734474158.11.1.1734474483.45.0.0; _ga_TP6SECCV43=GS1.1.1734474158.11.1.1734474487.41.0.0; _clsk=an0qbv%7C1734474970459%7C5%7C1%7Cu.clarity.ms%2Fcollect; __cf_bm=L7Mn6m8raIc1pMcWFEQmdBHHG_ZsFct2JDnWRos.4lA-1734647508-1.0.1.1-Uj.VDbqrLnQsqoPG_a_cJjv2HkprxSxdmHwzaKHxFrnI1XfcXA9t.RMWlnQdzY8rki6fD0gkG3mFMWehjKFFKA',
  'origin': 'https://igamingbrazil.com',
  'priority': 'u=1, i',
  'referer': 'https://igamingbrazil.com/en/all-the-news/',
  'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Opera";v="114"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 OPR/114.0.0.0',
  'x-requested-with': 'XMLHttpRequest'
}


def start_ig_brazil_reports(days, key_words, date_limit, path_output, url_list, stats, proxies=None):
    data_list = []
    page = 1
    while True:
        print(page)
        obj_bs4 = request_api("https://igamingbrazil.com/wp-admin/admin-ajax.php?td_theme_name=Newspaper&v=9.2.2", page, proxies=proxies)
        has_next_page = process_response(obj_bs4, date_limit, key_words, url_list, data_list, path_output, proxies=proxies)
        if has_next_page == True:
            page = page + 1
            # break
        else:
            break
    save_data(data_list, path_output)
    stats.append({
        "source": "IG_Brazil",
        "news_count": len(data_list)
    })
    return stats

def request_api(url, page, proxies):
    global headers
    print(url)
    payload = f"action=td_ajax_block&td_atts=%7B%22limit%22%3A%22100%22%2C%22ajax_pagination%22%3A%22infinite%22%2C%22m1_tl%22%3A%2230%22%2C%22td_ajax_preloading%22%3A%22preload_all%22%2C%22separator%22%3A%22%22%2C%22custom_title%22%3A%22%22%2C%22custom_url%22%3A%22%22%2C%22block_template_id%22%3A%22%22%2C%22post_ids%22%3A%22%22%2C%22category_id%22%3A%22%22%2C%22category_ids%22%3A%22%22%2C%22tag_slug%22%3A%22%22%2C%22autors_id%22%3A%22%22%2C%22installed_post_types%22%3A%22%22%2C%22sort%22%3A%22%22%2C%22offset%22%3A%22%22%2C%22el_class%22%3A%22%22%2C%22td_ajax_filter_type%22%3A%22%22%2C%22td_ajax_filter_ids%22%3A%22%22%2C%22td_filter_default_txt%22%3A%22All%22%2C%22f_header_font_header%22%3A%22%22%2C%22f_header_font_title%22%3A%22Block+header%22%2C%22f_header_font_settings%22%3A%22%22%2C%22f_header_font_family%22%3A%22%22%2C%22f_header_font_size%22%3A%22%22%2C%22f_header_font_line_height%22%3A%22%22%2C%22f_header_font_style%22%3A%22%22%2C%22f_header_font_weight%22%3A%22%22%2C%22f_header_font_transform%22%3A%22%22%2C%22f_header_font_spacing%22%3A%22%22%2C%22f_header_%22%3A%22%22%2C%22f_ajax_font_title%22%3A%22Ajax+categories%22%2C%22f_ajax_font_settings%22%3A%22%22%2C%22f_ajax_font_family%22%3A%22%22%2C%22f_ajax_font_size%22%3A%22%22%2C%22f_ajax_font_line_height%22%3A%22%22%2C%22f_ajax_font_style%22%3A%22%22%2C%22f_ajax_font_weight%22%3A%22%22%2C%22f_ajax_font_transform%22%3A%22%22%2C%22f_ajax_font_spacing%22%3A%22%22%2C%22f_ajax_%22%3A%22%22%2C%22f_more_font_title%22%3A%22Load+more+button%22%2C%22f_more_font_settings%22%3A%22%22%2C%22f_more_font_family%22%3A%22%22%2C%22f_more_font_size%22%3A%22%22%2C%22f_more_font_line_height%22%3A%22%22%2C%22f_more_font_style%22%3A%22%22%2C%22f_more_font_weight%22%3A%22%22%2C%22f_more_font_transform%22%3A%22%22%2C%22f_more_font_spacing%22%3A%22%22%2C%22f_more_%22%3A%22%22%2C%22m1f_title_font_header%22%3A%22%22%2C%22m1f_title_font_title%22%3A%22Article+title%22%2C%22m1f_title_font_settings%22%3A%22%22%2C%22m1f_title_font_family%22%3A%22%22%2C%22m1f_title_font_size%22%3A%22%22%2C%22m1f_title_font_line_height%22%3A%22%22%2C%22m1f_title_font_style%22%3A%22%22%2C%22m1f_title_font_weight%22%3A%22%22%2C%22m1f_title_font_transform%22%3A%22%22%2C%22m1f_title_font_spacing%22%3A%22%22%2C%22m1f_title_%22%3A%22%22%2C%22m1f_cat_font_title%22%3A%22Article+category+tag%22%2C%22m1f_cat_font_settings%22%3A%22%22%2C%22m1f_cat_font_family%22%3A%22%22%2C%22m1f_cat_font_size%22%3A%22%22%2C%22m1f_cat_font_line_height%22%3A%22%22%2C%22m1f_cat_font_style%22%3A%22%22%2C%22m1f_cat_font_weight%22%3A%22%22%2C%22m1f_cat_font_transform%22%3A%22%22%2C%22m1f_cat_font_spacing%22%3A%22%22%2C%22m1f_cat_%22%3A%22%22%2C%22m1f_meta_font_title%22%3A%22Article+meta+info%22%2C%22m1f_meta_font_settings%22%3A%22%22%2C%22m1f_meta_font_family%22%3A%22%22%2C%22m1f_meta_font_size%22%3A%22%22%2C%22m1f_meta_font_line_height%22%3A%22%22%2C%22m1f_meta_font_style%22%3A%22%22%2C%22m1f_meta_font_weight%22%3A%22%22%2C%22m1f_meta_font_transform%22%3A%22%22%2C%22m1f_meta_font_spacing%22%3A%22%22%2C%22m1f_meta_%22%3A%22%22%2C%22ajax_pagination_infinite_stop%22%3A%22%22%2C%22css%22%3A%22%22%2C%22tdc_css%22%3A%22%22%2C%22td_column_number%22%3A3%2C%22header_color%22%3A%22%22%2C%22color_preset%22%3A%22%22%2C%22border_top%22%3A%22%22%2C%22class%22%3A%22td_uid_11_6761e672e35a2_rand%22%2C%22tdc_css_class%22%3A%22td_uid_11_6761e672e35a2_rand%22%2C%22tdc_css_class_style%22%3A%22td_uid_11_6761e672e35a2_rand_style%22%7D&td_block_id=td_uid_11_6761e672e35a2&td_column_number=3&td_current_page={page}&block_type=td_block_3&td_filter_value=&td_user_action="
 
    sitecontent = requests.post(url, data=payload, proxies=proxies, headers=headers).json()
    sitecontent = sitecontent["td_data"]
    obj_bs4 = BeautifulSoup(sitecontent, "html.parser")
    return obj_bs4    

def request_url(url, proxies):
    global headers
    print(url)
    sitecontent = requests.get(url, proxies=proxies, headers=headers).content
    obj_bs4 = BeautifulSoup(sitecontent, "html.parser")
    return obj_bs4


def process_response(obj_bs4: BeautifulSoup, date_limit, key_words, url_list, data_list, path_output, proxies):

    news = obj_bs4.select("h3.entry-title.td-module-title a")
    dates = obj_bs4.select("time.entry-date.updated.td-module-date")
    in_limit = True

    # for new, category, date in zip(news, categories, dates):
    for new, date in zip(news, dates):
        news_date_str = date["datetime"]
        news_date = datetime.fromisoformat(news_date_str)
        news_date = news_date.replace(tzinfo=None)
        formatted_date = news_date.strftime("%Y-%m-%d %H:%M:%S")

        if news_date >= date_limit:
            new_url = new["href"]
            new_url = new_url.replace("igamingbrazil.com/", "igamingbrazil.com/en/")
            has_keyword, title, category = process_response_details(new_url, key_words, proxies=proxies)
            data_json = {
                "website": "ig_brazil",
                "category": category,
                "date": formatted_date,
                "title": title,
                "url": new_url,
                "has_keywords": ", ".join(has_keyword),
            }
            if data_json["url"] not in url_list:
                data_list.append(data_json.copy())
                url_list.append(data_json["url"])
        else:
            in_limit = False
            break

    if in_limit == True:
        return True
    return False


def process_response_details(url, key_words, proxies):
    has_keywords = []

    obj_bs4_details = request_url(url, proxies=proxies)
    title_bs4 = obj_bs4_details.select_one("header.td-post-title h1")
    title = title_bs4.text.strip()
    
    category_bs4 = obj_bs4_details.select_one("li.entry-category a")
    category = category_bs4.text.strip()

    news_details_texts = obj_bs4_details.select("div.td-post-content p")
    for news_details in news_details_texts:
        news_details_text = news_details.text
        for key_word in key_words:
            if key_word in news_details_text.lower() and key_word not in has_keywords:
                # print(news_details_text, key_word)
                has_keywords.append(key_word)
    return list(sorted(has_keywords)), title, category


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
