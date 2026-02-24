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
  'cookie': '_clck=1gfpr9d%7C2%7Cfsd%7C0%7C1833; _pk_ref.2.a157=%5B%22%22%2C%22%22%2C1736285970%2C%22https%3A%2F%2Fwww.google.com%2F%22%5D; _pk_id.2.a157=e94a563902912f5a.1736285970.; _pk_ses.2.a157=1; _gid=GA1.2.824224517.1736285973; moove_gdpr_popup=%7B%22strict%22%3A%221%22%2C%22thirdparty%22%3A%221%22%2C%22advanced%22%3A%221%22%7D; cf_clearance=bfbCLvNkf4NkNxGj8Fe8bhnnxyHP4DBos52WUju6YiE-1736286004-1.2.1.1-MClbx7_qIHMmgqN0Mpyv_1QMg..ctmjVyO76dqOSMIJosXYnTH3zR_B5R0p1YfE.U2wVokVWVTAoqxqpMZ7_WYWqZCB.ftWOuYEAQt7KWyI8TVC_KcVrkPlIaxe41wPL2WcdYM7c17phFvUw8pymR5KS8ZxW6kaA7WJZ.C1PVJityHmGwSYtsbmh8gRV3sbX2cO0tmYDs6SmGCJcaYXfDZMGenGvNZ4aA0KSLFZo44O625EDhybS8OANdppl0BbiFOMXhu2W4v.9Hyy9UV9Sd42l5PeqXFzpTeI9p97zDMLxOZkU_00WZ9kKEAbuzdBVJWkTPfOMLmJlKy5UrzM8OKW6Z_07FxucUvQFHO8N5E194QzNaFd9luTlbS7BlX5YRJYOEg98jUHSTyvFzec6koIKJPykckac27vGReryLjzoOR2OK5x5eb0QRLhuVsly; _ga=GA1.1.655792128.1736285970; _clsk=43me86%7C1736287636336%7C15%7C1%7Cr.clarity.ms%2Fcollect; _ga_Y1ENPPYP59=GS1.1.1736285970.1.1.1736287648.39.0.0',
  'origin': 'https://agbrief.com',
  'priority': 'u=1, i',
  'referer': 'https://agbrief.com/headlines/',
  'sec-ch-ua': '"Chromium";v="130", "Opera";v="115", "Not?A_Brand";v="99"',
  'sec-ch-ua-arch': '"x86"',
  'sec-ch-ua-bitness': '"64"',
  'sec-ch-ua-full-version': '"115.0.5322.119"',
  'sec-ch-ua-full-version-list': '"Chromium";v="130.0.6723.170", "Opera";v="115.0.5322.119", "Not?A_Brand";v="99.0.0.0"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-model': '""',
  'sec-ch-ua-platform': '"Windows"',
  'sec-ch-ua-platform-version': '"15.0.0"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 OPR/115.0.0.0',
  'x-requested-with': 'XMLHttpRequest'
}


def start_agb_reports(days, key_words, date_limit, path_output, url_list, stats, proxies=None):
    data_list = []
    page = 1
    while True:
        print(page)
        obj_bs4 = request_api("https://agbrief.com/wp-admin/admin-ajax.php?td_theme_name=Newspaper&v=12.6.6", page, proxies=proxies)
        if obj_bs4 is None:
            break
        has_next_page = process_response(obj_bs4, date_limit, key_words, url_list, data_list, path_output, proxies=proxies)
        if has_next_page == True:
            page = page + 1
        else:
            break
    save_data(data_list, path_output)
    stats.append({
        "source": "AGB",
        "news_count": len(data_list)
    })
    return stats

def request_api(url, page, proxies):
    global headers
    print(url)
    payload = f"action=td_ajax_block&td_atts=%7B%22ajax_pagination%22%3A%22load_more%22%2C%22category_id%22%3A%22%22%2C%22time_ago%22%3A%22yes%22%2C%22td_ajax_preloading%22%3A%22preload%22%2C%22limit%22%3A%2210%22%2C%22image_width%22%3A%22%22%2C%22image_floated%22%3A%22%22%2C%22meta_padding%22%3A%22%22%2C%22image_radius%22%3A%22%22%2C%22image_height%22%3A%2267%22%2C%22meta_info_horiz%22%3A%22%22%2C%22modules_category%22%3A%22image%22%2C%22modules_category_margin%22%3A%22%22%2C%22hide_image%22%3A%22%22%2C%22show_excerpt%22%3A%22none%22%2C%22show_btn%22%3A%22none%22%2C%22f_title_font_size%22%3A%2216%22%2C%22f_title_font_weight%22%3A%22600%22%2C%22all_modules_space%22%3A%2220%22%2C%22h_effect%22%3A%22shadow%22%2C%22f_meta_font_weight%22%3A%22600%22%2C%22tag_slug%22%3A%22latest-news%22%2C%22meta_info_align%22%3A%22%22%2C%22meta_margin%22%3A%220px+0px+0px+0px%22%2C%22art_title%22%3A%22-10px+0px+4px+0px%22%2C%22tdc_css%22%3A%22eyJhbGwiOnsiZGlzcGxheSI6IiJ9fQ%3D%3D%22%2C%22f_title_font_line_height%22%3A%221.4%22%2C%22custom_title%22%3A%22LATEST+NEWS%22%2C%22custom_url%22%3A%22https%3A%2F%2Fagbrief.com%2Fcategory%2Fnews%2F%22%2C%22block_template_id%22%3A%22td_block_template_8%22%2C%22border_color%22%3A%22%23ce472c%22%2C%22header_text_color%22%3A%22%23000000%22%2C%22show_com%22%3A%22none%22%2C%22f_header_font_weight%22%3A%22700%22%2C%22block_type%22%3A%22td_flex_block_1%22%2C%22separator%22%3A%22%22%2C%22title_tag%22%3A%22%22%2C%22mc1_tl%22%3A%22%22%2C%22mc1_title_tag%22%3A%22%22%2C%22mc1_el%22%3A%22%22%2C%22post_ids%22%3A%22%22%2C%22taxonomies%22%3A%22%22%2C%22category_ids%22%3A%22%22%2C%22in_all_terms%22%3A%22%22%2C%22autors_id%22%3A%22%22%2C%22installed_post_types%22%3A%22%22%2C%22include_cf_posts%22%3A%22%22%2C%22exclude_cf_posts%22%3A%22%22%2C%22sort%22%3A%22%22%2C%22popular_by_date%22%3A%22%22%2C%22linked_posts%22%3A%22%22%2C%22favourite_only%22%3A%22%22%2C%22offset%22%3A%22%22%2C%22open_in_new_window%22%3A%22%22%2C%22show_modified_date%22%3A%22%22%2C%22time_ago_add_txt%22%3A%22ago%22%2C%22time_ago_txt_pos%22%3A%22%22%2C%22review_source%22%3A%22%22%2C%22el_class%22%3A%22%22%2C%22td_query_cache%22%3A%22%22%2C%22td_query_cache_expiration%22%3A%22%22%2C%22td_ajax_filter_type%22%3A%22%22%2C%22td_ajax_filter_ids%22%3A%22%22%2C%22td_filter_default_txt%22%3A%22All%22%2C%22container_width%22%3A%22%22%2C%22modules_on_row%22%3A%22100%25%22%2C%22modules_gap%22%3A%22%22%2C%22m_padding%22%3A%22%22%2C%22modules_border_size%22%3A%22%22%2C%22modules_border_style%22%3A%22%22%2C%22modules_border_color%22%3A%22%23eaeaea%22%2C%22modules_border_radius%22%3A%22%22%2C%22modules_divider%22%3A%22%22%2C%22modules_divider_color%22%3A%22%23eaeaea%22%2C%22image_size%22%3A%22%22%2C%22image_alignment%22%3A%2250%22%2C%22show_favourites%22%3A%22%22%2C%22fav_size%22%3A%222%22%2C%22fav_space%22%3A%22%22%2C%22fav_ico_color%22%3A%22%22%2C%22fav_ico_color_h%22%3A%22%22%2C%22fav_bg%22%3A%22%22%2C%22fav_bg_h%22%3A%22%22%2C%22fav_shadow_shadow_header%22%3A%22%22%2C%22fav_shadow_shadow_title%22%3A%22Shadow%22%2C%22fav_shadow_shadow_size%22%3A%22%22%2C%22fav_shadow_shadow_offset_horizontal%22%3A%22%22%2C%22fav_shadow_shadow_offset_vertical%22%3A%22%22%2C%22fav_shadow_shadow_spread%22%3A%22%22%2C%22fav_shadow_shadow_color%22%3A%22%22%2C%22video_icon%22%3A%22%22%2C%22video_popup%22%3A%22yes%22%2C%22video_rec%22%3A%22%22%2C%22spot_header%22%3A%22%22%2C%22video_rec_title%22%3A%22%22%2C%22video_rec_color%22%3A%22%22%2C%22video_rec_disable%22%3A%22%22%2C%22autoplay_vid%22%3A%22yes%22%2C%22show_vid_t%22%3A%22block%22%2C%22vid_t_margin%22%3A%22%22%2C%22vid_t_padding%22%3A%22%22%2C%22video_title_color%22%3A%22%22%2C%22video_title_color_h%22%3A%22%22%2C%22video_bg%22%3A%22%22%2C%22video_overlay%22%3A%22%22%2C%22vid_t_color%22%3A%22%22%2C%22vid_t_bg_color%22%3A%22%22%2C%22f_vid_title_font_header%22%3A%22%22%2C%22f_vid_title_font_title%22%3A%22Video+pop-up+article+title%22%2C%22f_vid_title_font_settings%22%3A%22%22%2C%22f_vid_title_font_family%22%3A%22%22%2C%22f_vid_title_font_size%22%3A%22%22%2C%22f_vid_title_font_line_height%22%3A%22%22%2C%22f_vid_title_font_style%22%3A%22%22%2C%22f_vid_title_font_weight%22%3A%22%22%2C%22f_vid_title_font_transform%22%3A%22%22%2C%22f_vid_title_font_spacing%22%3A%22%22%2C%22f_vid_title_%22%3A%22%22%2C%22f_vid_time_font_title%22%3A%22Video+duration+text%22%2C%22f_vid_time_font_settings%22%3A%22%22%2C%22f_vid_time_font_family%22%3A%22%22%2C%22f_vid_time_font_size%22%3A%22%22%2C%22f_vid_time_font_line_height%22%3A%22%22%2C%22f_vid_time_font_style%22%3A%22%22%2C%22f_vid_time_font_weight%22%3A%22%22%2C%22f_vid_time_font_transform%22%3A%22%22%2C%22f_vid_time_font_spacing%22%3A%22%22%2C%22f_vid_time_%22%3A%22%22%2C%22meta_width%22%3A%22%22%2C%22meta_space%22%3A%22%22%2C%22art_btn%22%3A%22%22%2C%22meta_info_border_size%22%3A%22%22%2C%22meta_info_border_style%22%3A%22%22%2C%22meta_info_border_color%22%3A%22%23eaeaea%22%2C%22meta_info_border_radius%22%3A%22%22%2C%22modules_category_padding%22%3A%22%22%2C%22modules_cat_border%22%3A%22%22%2C%22modules_category_radius%22%3A%220%22%2C%22show_cat%22%3A%22inline-block%22%2C%22modules_extra_cat%22%3A%22%22%2C%22show_author%22%3A%22inline-block%22%2C%22author_photo%22%3A%22%22%2C%22author_photo_size%22%3A%22%22%2C%22author_photo_space%22%3A%22%22%2C%22author_photo_radius%22%3A%22%22%2C%22show_date%22%3A%22inline-block%22%2C%22show_review%22%3A%22inline-block%22%2C%22review_space%22%3A%22%22%2C%22review_size%22%3A%222.5%22%2C%22review_distance%22%3A%22%22%2C%22art_excerpt%22%3A%22%22%2C%22excerpt_col%22%3A%221%22%2C%22excerpt_gap%22%3A%22%22%2C%22excerpt_middle%22%3A%22%22%2C%22excerpt_inline%22%3A%22%22%2C%22show_audio%22%3A%22block%22%2C%22hide_audio%22%3A%22%22%2C%22art_audio%22%3A%22%22%2C%22art_audio_size%22%3A%221.5%22%2C%22btn_title%22%3A%22%22%2C%22btn_margin%22%3A%22%22%2C%22btn_padding%22%3A%22%22%2C%22btn_border_width%22%3A%22%22%2C%22btn_radius%22%3A%22%22%2C%22pag_space%22%3A%22%22%2C%22pag_padding%22%3A%22%22%2C%22pag_border_width%22%3A%22%22%2C%22pag_border_radius%22%3A%22%22%2C%22prev_tdicon%22%3A%22%22%2C%22next_tdicon%22%3A%22%22%2C%22pag_icons_size%22%3A%22%22%2C%22f_header_font_header%22%3A%22%22%2C%22f_header_font_title%22%3A%22Block+header%22%2C%22f_header_font_settings%22%3A%22%22%2C%22f_header_font_family%22%3A%22%22%2C%22f_header_font_size%22%3A%22%22%2C%22f_header_font_line_height%22%3A%22%22%2C%22f_header_font_style%22%3A%22%22%2C%22f_header_font_transform%22%3A%22%22%2C%22f_header_font_spacing%22%3A%22%22%2C%22f_header_%22%3A%22%22%2C%22f_ajax_font_title%22%3A%22Ajax+categories%22%2C%22f_ajax_font_settings%22%3A%22%22%2C%22f_ajax_font_family%22%3A%22%22%2C%22f_ajax_font_size%22%3A%22%22%2C%22f_ajax_font_line_height%22%3A%22%22%2C%22f_ajax_font_style%22%3A%22%22%2C%22f_ajax_font_weight%22%3A%22%22%2C%22f_ajax_font_transform%22%3A%22%22%2C%22f_ajax_font_spacing%22%3A%22%22%2C%22f_ajax_%22%3A%22%22%2C%22f_more_font_title%22%3A%22Load+more+button%22%2C%22f_more_font_settings%22%3A%22%22%2C%22f_more_font_family%22%3A%22%22%2C%22f_more_font_size%22%3A%22%22%2C%22f_more_font_line_height%22%3A%22%22%2C%22f_more_font_style%22%3A%22%22%2C%22f_more_font_weight%22%3A%22%22%2C%22f_more_font_transform%22%3A%22%22%2C%22f_more_font_spacing%22%3A%22%22%2C%22f_more_%22%3A%22%22%2C%22f_title_font_header%22%3A%22%22%2C%22f_title_font_title%22%3A%22Article+title%22%2C%22f_title_font_settings%22%3A%22%22%2C%22f_title_font_family%22%3A%22%22%2C%22f_title_font_style%22%3A%22%22%2C%22f_title_font_transform%22%3A%22%22%2C%22f_title_font_spacing%22%3A%22%22%2C%22f_title_%22%3A%22%22%2C%22f_cat_font_title%22%3A%22Article+category+tag%22%2C%22f_cat_font_settings%22%3A%22%22%2C%22f_cat_font_family%22%3A%22%22%2C%22f_cat_font_size%22%3A%22%22%2C%22f_cat_font_line_height%22%3A%22%22%2C%22f_cat_font_style%22%3A%22%22%2C%22f_cat_font_weight%22%3A%22%22%2C%22f_cat_font_transform%22%3A%22%22%2C%22f_cat_font_spacing%22%3A%22%22%2C%22f_cat_%22%3A%22%22%2C%22f_meta_font_title%22%3A%22Article+meta+info%22%2C%22f_meta_font_settings%22%3A%22%22%2C%22f_meta_font_family%22%3A%22%22%2C%22f_meta_font_size%22%3A%22%22%2C%22f_meta_font_line_height%22%3A%22%22%2C%22f_meta_font_style%22%3A%22%22%2C%22f_meta_font_transform%22%3A%22%22%2C%22f_meta_font_spacing%22%3A%22%22%2C%22f_meta_%22%3A%22%22%2C%22f_ex_font_title%22%3A%22Article+excerpt%22%2C%22f_ex_font_settings%22%3A%22%22%2C%22f_ex_font_family%22%3A%22%22%2C%22f_ex_font_size%22%3A%22%22%2C%22f_ex_font_line_height%22%3A%22%22%2C%22f_ex_font_style%22%3A%22%22%2C%22f_ex_font_weight%22%3A%22%22%2C%22f_ex_font_transform%22%3A%22%22%2C%22f_ex_font_spacing%22%3A%22%22%2C%22f_ex_%22%3A%22%22%2C%22f_btn_font_title%22%3A%22Article+read+more+button%22%2C%22f_btn_font_settings%22%3A%22%22%2C%22f_btn_font_family%22%3A%22%22%2C%22f_btn_font_size%22%3A%22%22%2C%22f_btn_font_line_height%22%3A%22%22%2C%22f_btn_font_style%22%3A%22%22%2C%22f_btn_font_weight%22%3A%22%22%2C%22f_btn_font_transform%22%3A%22%22%2C%22f_btn_font_spacing%22%3A%22%22%2C%22f_btn_%22%3A%22%22%2C%22mix_color%22%3A%22%22%2C%22mix_type%22%3A%22%22%2C%22fe_brightness%22%3A%221%22%2C%22fe_contrast%22%3A%221%22%2C%22fe_saturate%22%3A%221%22%2C%22mix_color_h%22%3A%22%22%2C%22mix_type_h%22%3A%22%22%2C%22fe_brightness_h%22%3A%221%22%2C%22fe_contrast_h%22%3A%221%22%2C%22fe_saturate_h%22%3A%221%22%2C%22m_bg%22%3A%22%22%2C%22color_overlay%22%3A%22%22%2C%22shadow_shadow_header%22%3A%22%22%2C%22shadow_shadow_title%22%3A%22Module+Shadow%22%2C%22shadow_shadow_size%22%3A%22%22%2C%22shadow_shadow_offset_horizontal%22%3A%22%22%2C%22shadow_shadow_offset_vertical%22%3A%22%22%2C%22shadow_shadow_spread%22%3A%22%22%2C%22shadow_shadow_color%22%3A%22%22%2C%22title_txt%22%3A%22%22%2C%22title_txt_hover%22%3A%22%22%2C%22all_underline_height%22%3A%22%22%2C%22all_underline_color%22%3A%22%22%2C%22cat_bg%22%3A%22%22%2C%22cat_bg_hover%22%3A%22%22%2C%22cat_txt%22%3A%22%22%2C%22cat_txt_hover%22%3A%22%22%2C%22cat_border%22%3A%22%22%2C%22cat_border_hover%22%3A%22%22%2C%22meta_bg%22%3A%22%22%2C%22author_txt%22%3A%22%22%2C%22author_txt_hover%22%3A%22%22%2C%22date_txt%22%3A%22%22%2C%22ex_txt%22%3A%22%22%2C%22com_bg%22%3A%22%22%2C%22com_txt%22%3A%22%22%2C%22rev_txt%22%3A%22%22%2C%22audio_btn_color%22%3A%22%22%2C%22audio_time_color%22%3A%22%22%2C%22audio_bar_color%22%3A%22%22%2C%22audio_bar_curr_color%22%3A%22%22%2C%22shadow_m_shadow_header%22%3A%22%22%2C%22shadow_m_shadow_title%22%3A%22Meta+info+shadow%22%2C%22shadow_m_shadow_size%22%3A%22%22%2C%22shadow_m_shadow_offset_horizontal%22%3A%22%22%2C%22shadow_m_shadow_offset_vertical%22%3A%22%22%2C%22shadow_m_shadow_spread%22%3A%22%22%2C%22shadow_m_shadow_color%22%3A%22%22%2C%22btn_bg%22%3A%22%22%2C%22btn_bg_hover%22%3A%22%22%2C%22btn_txt%22%3A%22%22%2C%22btn_txt_hover%22%3A%22%22%2C%22btn_border%22%3A%22%22%2C%22btn_border_hover%22%3A%22%22%2C%22pag_text%22%3A%22%22%2C%22pag_h_text%22%3A%22%22%2C%22pag_bg%22%3A%22%22%2C%22pag_h_bg%22%3A%22%22%2C%22pag_border%22%3A%22%22%2C%22pag_h_border%22%3A%22%22%2C%22ajax_pagination_next_prev_swipe%22%3A%22%22%2C%22ajax_pagination_infinite_stop%22%3A%22%22%2C%22css%22%3A%22%22%2C%22td_column_number%22%3A1%2C%22header_color%22%3A%22%22%2C%22color_preset%22%3A%22%22%2C%22border_top%22%3A%22%22%2C%22class%22%3A%22tdi_75%22%2C%22tdc_css_class%22%3A%22tdi_75%22%2C%22tdc_css_class_style%22%3A%22tdi_75_rand_style%22%7D&td_block_id=tdi_75&td_column_number=1&td_current_page={page}&block_type=td_flex_block_1&td_filter_value=&td_user_action=&td_magic_token=db09dd8334"
 
    try:
        response = requests.post(url, data=payload, proxies=proxies, headers=headers, verify=False, timeout=30)
        response.raise_for_status()
        data = response.json()
        html = data["td_data"]
    except Exception as exc:
        print(f"[agb] request_api failed: {exc}")
        return None
    obj_bs4 = BeautifulSoup(html, "html.parser")
    return obj_bs4

def request_url(url, proxies):
    global headers
    print(url)
    sitecontent = requests.get(url, proxies=proxies, headers=headers, verify=False).content
    obj_bs4 = BeautifulSoup(sitecontent, "html.parser")
    return obj_bs4


def process_response(obj_bs4: BeautifulSoup, date_limit, key_words, url_list, data_list, path_output, proxies):

    news = obj_bs4.select("h3.entry-title.td-module-title a")
    categories = obj_bs4.select("a.td-post-category")
    dates = obj_bs4.select("time.entry-date.updated.td-module-date")
    in_limit = True

    for new, category, date in zip(news, categories, dates):
    # for new, date in zip(news, dates):
        news_date_str = date["datetime"]
        news_date = datetime.fromisoformat(news_date_str)
        news_date = news_date.replace(tzinfo=None)
        formatted_date = news_date.strftime("%Y-%m-%d %H:%M:%S")
        category = category.text.strip()

        if news_date >= date_limit:
            has_keyword = process_response_details(new["href"], key_words, proxies=proxies)
            data_json = {
                "website": "agb",
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
            break

    if in_limit == True:
        return True
    return False


def process_response_details(url, key_words, proxies):
    has_keywords = []

    obj_bs4_details = request_url(url, proxies=proxies)
    news_details_texts = obj_bs4_details.select("div.td-post-content p")
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
