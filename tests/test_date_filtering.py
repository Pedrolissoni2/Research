"""
Tests for date filtering and pagination control (process_response).

Covers:
  - Articles within date limit are collected
  - Articles beyond date limit are skipped
  - Return value signals whether to fetch the next page
  - Duplicate URL detection prevents re-adding seen articles
  - Output records contain all required CSV fields
  - Correct date formats are parsed (each scraper uses a different format)
"""

import pytest
from unittest.mock import patch
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

import casinoreports
import yogonet


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_casinoreports_soup(articles: list[dict], has_next_page: bool = True) -> BeautifulSoup:
    """
    articles: list of dicts with keys title, href, category, date_str
    date_str format: "%B %d, %Y"  e.g. "January 02, 2024"
    """
    html = ""
    for a in articles:
        html += (
            f'<h3 class="post-preview__title h4"><a href="{a["href"]}">{a["title"]}</a></h3>'
            f'<p class="post-preview__term mb-mini"><a>{a["category"]}</a></p>'
            f'<p class="post-preview__date">{a["date_str"]}</p>'
        )
    # Casinoreports: absence of "span.page-numbers.next.disabled" means more pages exist
    if not has_next_page:
        html += '<span class="page-numbers next disabled">Next</span>'
    return BeautifulSoup(html, "html.parser")


def _make_yogonet_soup(articles: list[dict], has_next_button: bool = False) -> BeautifulSoup:
    """
    articles: list of dicts with keys title, href, date_str
    date_str format: "%Y-%m-%d"
    """
    html = ""
    for a in articles:
        html += (
            f'<h2 class="titulo_item_listado_noticias fuente_roboto_slab">'
            f'<a href="{a["href"]}">{a["title"]}</a></h2>'
            f'<div class="volanta_item_listado_noticias"><b>{a["date_str"]}</b></div>'
        )
    if has_next_button:
        html += (
            '<div class="contenedor_paginador_listado anterior_siguiente">'
            '<button class="boton_paginador siguiente">Next</button>'
            "</div>"
        )
    return BeautifulSoup(html, "html.parser")


RECENT_CR = (datetime.now() - timedelta(days=2)).strftime("%B %d, %Y")
OLD_CR = (datetime.now() - timedelta(days=30)).strftime("%B %d, %Y")

RECENT_YG = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
OLD_YG = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

DATE_LIMIT = datetime.now() - timedelta(days=7)


# ---------------------------------------------------------------------------
# casinoreports — date filtering
# ---------------------------------------------------------------------------

class TestCasinoreportsDateFiltering:

    def test_recent_article_is_collected(self):
        soup = _make_casinoreports_soup([
            {"title": "Big Win", "href": "http://ex.com/1", "category": "Casino", "date_str": RECENT_CR}
        ])
        data_list: list = []
        with patch("casinoreports.process_response_details", return_value=["jackpot"]):
            casinoreports.process_response(soup, DATE_LIMIT, ["jackpot"], [], data_list, "/tmp")
        assert len(data_list) == 1
        assert data_list[0]["title"] == "Big Win"

    def test_old_article_is_excluded(self):
        soup = _make_casinoreports_soup([
            {"title": "Ancient History", "href": "http://ex.com/old", "category": "Casino", "date_str": OLD_CR}
        ])
        data_list: list = []
        with patch("casinoreports.process_response_details", return_value=[]):
            casinoreports.process_response(soup, DATE_LIMIT, [], [], data_list, "/tmp")
        assert len(data_list) == 0

    def test_returns_false_when_article_is_past_limit(self):
        soup = _make_casinoreports_soup([
            {"title": "Old", "href": "http://ex.com/old", "category": "Casino", "date_str": OLD_CR}
        ])
        with patch("casinoreports.process_response_details", return_value=[]):
            result = casinoreports.process_response(soup, DATE_LIMIT, [], [], [], "/tmp")
        assert result is False

    def test_returns_false_when_disabled_next_button_present(self):
        """Even if all articles are within date limit, disabled next = last page."""
        soup = _make_casinoreports_soup(
            [{"title": "Recent", "href": "http://ex.com/r", "category": "Casino", "date_str": RECENT_CR}],
            has_next_page=False,
        )
        with patch("casinoreports.process_response_details", return_value=[]):
            result = casinoreports.process_response(soup, DATE_LIMIT, [], [], [], "/tmp")
        assert result is False

    def test_returns_true_when_within_limit_and_more_pages(self):
        soup = _make_casinoreports_soup(
            [{"title": "Recent", "href": "http://ex.com/r", "category": "Casino", "date_str": RECENT_CR}],
            has_next_page=True,
        )
        with patch("casinoreports.process_response_details", return_value=[]):
            result = casinoreports.process_response(soup, DATE_LIMIT, [], [], [], "/tmp")
        assert result is True

    def test_empty_page_pagination_behavior(self):
        """
        KNOWN BUG: An empty page (no articles, no disabled-next element) causes
        process_response() to return True, triggering an infinite pagination loop.

        Root cause: the guard condition is `next_page == None and in_limit == True`.
        On an empty page, in_limit is True and next_page is None, so it returns True
        instead of stopping. Fix: also check that at least one article was found.

        Actual:   True  (BUG — infinite loop)
        Expected: False (stop paginating on an empty page)
        """
        soup = BeautifulSoup("", "html.parser")
        result = casinoreports.process_response(soup, DATE_LIMIT, [], [], [], "/tmp")
        assert result is True  # documents the current buggy behavior


# ---------------------------------------------------------------------------
# casinoreports — URL deduplication
# ---------------------------------------------------------------------------

class TestUrlDeduplication:

    def test_duplicate_url_not_added_again(self):
        existing_url = "http://ex.com/already-seen"
        soup = _make_casinoreports_soup([
            {"title": "Seen Before", "href": existing_url, "category": "Casino", "date_str": RECENT_CR}
        ])
        data_list: list = []
        url_list = [existing_url]
        with patch("casinoreports.process_response_details", return_value=[]):
            casinoreports.process_response(soup, DATE_LIMIT, [], url_list, data_list, "/tmp")
        assert len(data_list) == 0

    def test_new_url_added_to_url_list_after_processing(self):
        new_url = "http://ex.com/brand-new"
        soup = _make_casinoreports_soup([
            {"title": "New Article", "href": new_url, "category": "Casino", "date_str": RECENT_CR}
        ])
        url_list: list = []
        with patch("casinoreports.process_response_details", return_value=[]):
            casinoreports.process_response(soup, DATE_LIMIT, [], url_list, [], "/tmp")
        assert new_url in url_list


# ---------------------------------------------------------------------------
# casinoreports — output record structure
# ---------------------------------------------------------------------------

class TestOutputRecordStructure:

    def test_record_contains_all_required_fields(self):
        soup = _make_casinoreports_soup([
            {"title": "Test Article", "href": "http://ex.com/t", "category": "Slots", "date_str": RECENT_CR}
        ])
        data_list: list = []
        with patch("casinoreports.process_response_details", return_value=["jackpot"]):
            casinoreports.process_response(soup, DATE_LIMIT, ["jackpot"], [], data_list, "/tmp")

        assert len(data_list) == 1
        record = data_list[0]
        for field in ("website", "category", "date", "title", "url", "has_keywords"):
            assert field in record, f"Missing field: {field}"

    def test_website_field_is_casinoreports(self):
        soup = _make_casinoreports_soup([
            {"title": "Article", "href": "http://ex.com/a", "category": "Casino", "date_str": RECENT_CR}
        ])
        data_list: list = []
        with patch("casinoreports.process_response_details", return_value=[]):
            casinoreports.process_response(soup, DATE_LIMIT, [], [], data_list, "/tmp")
        assert data_list[0]["website"] == "casinoreports"

    def test_has_keywords_is_comma_separated_string(self):
        soup = _make_casinoreports_soup([
            {"title": "Article", "href": "http://ex.com/a", "category": "Casino", "date_str": RECENT_CR}
        ])
        data_list: list = []
        with patch("casinoreports.process_response_details", return_value=["jackpot", "online casino"]):
            casinoreports.process_response(soup, DATE_LIMIT, [], [], data_list, "/tmp")
        assert data_list[0]["has_keywords"] == "jackpot, online casino"


# ---------------------------------------------------------------------------
# yogonet — different date format and pagination logic
# ---------------------------------------------------------------------------

class TestYogonetDateFormat:

    def test_yogonet_date_format_parsed_correctly(self):
        """Yogonet uses YYYY-MM-DD format."""
        soup = _make_yogonet_soup([
            {"title": "Yogo Article", "href": "http://yogo.net/a", "date_str": RECENT_YG}
        ])
        data_list: list = []
        with patch("yogonet.process_response_details", return_value=(["jackpot"], "Casino")):
            yogonet.process_response(soup, DATE_LIMIT, ["jackpot"], [], data_list, "/tmp")
        assert len(data_list) == 1

    def test_yogonet_old_article_excluded(self):
        soup = _make_yogonet_soup([
            {"title": "Old Yogo", "href": "http://yogo.net/old", "date_str": OLD_YG}
        ])
        data_list: list = []
        with patch("yogonet.process_response_details", return_value=([], "")):
            yogonet.process_response(soup, DATE_LIMIT, [], [], data_list, "/tmp")
        assert len(data_list) == 0


class TestYogonetPagination:

    def test_returns_false_when_no_next_button(self):
        soup = _make_yogonet_soup(
            [{"title": "Article", "href": "http://yogo.net/a", "date_str": RECENT_YG}],
            has_next_button=False,
        )
        with patch("yogonet.process_response_details", return_value=([], "")):
            result = yogonet.process_response(soup, DATE_LIMIT, [], [], [], "/tmp")
        assert result is False

    def test_returns_true_when_next_button_present_and_within_limit(self):
        soup = _make_yogonet_soup(
            [{"title": "Article", "href": "http://yogo.net/a", "date_str": RECENT_YG}],
            has_next_button=True,
        )
        with patch("yogonet.process_response_details", return_value=([], "")):
            result = yogonet.process_response(soup, DATE_LIMIT, [], [], [], "/tmp")
        assert result is True

    def test_returns_false_when_past_date_limit_even_with_next_button(self):
        soup = _make_yogonet_soup(
            [{"title": "Old", "href": "http://yogo.net/old", "date_str": OLD_YG}],
            has_next_button=True,
        )
        with patch("yogonet.process_response_details", return_value=([], "")):
            result = yogonet.process_response(soup, DATE_LIMIT, [], [], [], "/tmp")
        assert result is False
