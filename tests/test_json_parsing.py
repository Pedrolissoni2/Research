"""
Tests for the JSON-API scraper (igb_json.py).

igb_json.py differs from the HTML scrapers:
  - It calls a search API that returns JSON instead of HTML
  - Article category is inferred from the URL path, not from a page element
  - Date format is "%Y-%m-%d %H:%M:%S" (ISO-like, no timezone)

Covers:
  - URL-to-category conversion logic
  - Date filtering (within / beyond limit)
  - URL deduplication
  - Return value for pagination control
  - Output record structure
  - stats accumulation
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

import igb_json


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

DATE_LIMIT = datetime.now() - timedelta(days=7)
RECENT_DATE = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")
OLD_DATE = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")


def _make_json_result(url: str, date_str: str, title: str = "Test Article") -> dict:
    return {
        "url": {"raw": url},
        "timestamp": {"raw": date_str},
        "title": {"raw": title},
    }


def _make_json_response(results: list[dict]) -> dict:
    return {"results": results}


# ---------------------------------------------------------------------------
# URL → category parsing
# ---------------------------------------------------------------------------

class TestUrlToCategoryParsing:
    """
    The category is derived inline inside process_response by slicing the URL path.
    These tests validate that logic by calling process_response with known URLs
    and inspecting the category field written to data_list.
    """

    def _run(self, url: str) -> str:
        payload = _make_json_response([_make_json_result(url, RECENT_DATE)])
        data_list: list = []
        with patch("igb_json.process_response_details", return_value=[]):
            igb_json.process_response(payload, DATE_LIMIT, [], [], data_list, "/tmp")
        return data_list[0]["category"] if data_list else ""

    def test_single_word_segment(self):
        assert self._run("https://igamingbusiness.com/finance/article/") == "Finance"

    def test_hyphenated_segment_becomes_title_case(self):
        assert self._run("https://igamingbusiness.com/casino-games/article/") == "Casino Games"

    def test_multi_word_segment(self):
        assert self._run("https://igamingbusiness.com/tech-innovation/some-story/") == "Tech Innovation"

    def test_three_word_segment(self):
        assert self._run("https://igamingbusiness.com/legal-and-compliance/story/") == "Legal And Compliance"


# ---------------------------------------------------------------------------
# Date filtering
# ---------------------------------------------------------------------------

class TestIgbJsonDateFiltering:

    def test_recent_article_is_collected(self):
        payload = _make_json_response([
            _make_json_result("https://igamingbusiness.com/casino/win/", RECENT_DATE, "Big Win")
        ])
        data_list: list = []
        with patch("igb_json.process_response_details", return_value=["jackpot"]):
            igb_json.process_response(payload, DATE_LIMIT, ["jackpot"], [], data_list, "/tmp")
        assert len(data_list) == 1
        assert data_list[0]["title"] == "Big Win"

    def test_old_article_is_excluded(self):
        payload = _make_json_response([
            _make_json_result("https://igamingbusiness.com/casino/old/", OLD_DATE, "Old News")
        ])
        data_list: list = []
        with patch("igb_json.process_response_details", return_value=[]):
            igb_json.process_response(payload, DATE_LIMIT, [], [], data_list, "/tmp")
        assert len(data_list) == 0

    def test_returns_false_when_past_date_limit(self):
        payload = _make_json_response([
            _make_json_result("https://igamingbusiness.com/casino/old/", OLD_DATE)
        ])
        with patch("igb_json.process_response_details", return_value=[]):
            result = igb_json.process_response(payload, DATE_LIMIT, [], [], [], "/tmp")
        assert result is False

    def test_returns_true_when_all_within_date_limit(self):
        payload = _make_json_response([
            _make_json_result("https://igamingbusiness.com/casino/new/", RECENT_DATE)
        ])
        with patch("igb_json.process_response_details", return_value=[]):
            result = igb_json.process_response(payload, DATE_LIMIT, [], [], [], "/tmp")
        assert result is True

    def test_empty_results_list_returns_true(self):
        """An empty page is not 'past the date limit', so pagination could theoretically continue."""
        payload = _make_json_response([])
        result = igb_json.process_response(payload, DATE_LIMIT, [], [], [], "/tmp")
        # in_limit is True when the loop body never executes
        assert result is True


# ---------------------------------------------------------------------------
# URL deduplication
# ---------------------------------------------------------------------------

class TestIgbJsonDeduplication:

    def test_duplicate_url_not_added_again(self):
        url = "https://igamingbusiness.com/casino/seen/"
        payload = _make_json_response([_make_json_result(url, RECENT_DATE)])
        data_list: list = []
        url_list = [url]
        with patch("igb_json.process_response_details", return_value=[]):
            igb_json.process_response(payload, DATE_LIMIT, [], url_list, data_list, "/tmp")
        assert len(data_list) == 0

    def test_new_url_is_added_to_url_list(self):
        url = "https://igamingbusiness.com/casino/new/"
        payload = _make_json_response([_make_json_result(url, RECENT_DATE)])
        url_list: list = []
        with patch("igb_json.process_response_details", return_value=[]):
            igb_json.process_response(payload, DATE_LIMIT, [], url_list, [], "/tmp")
        assert url in url_list


# ---------------------------------------------------------------------------
# Output record structure
# ---------------------------------------------------------------------------

class TestIgbJsonRecordStructure:

    def test_record_has_all_required_fields(self):
        url = "https://igamingbusiness.com/casino/article/"
        payload = _make_json_response([_make_json_result(url, RECENT_DATE, "Test")])
        data_list: list = []
        with patch("igb_json.process_response_details", return_value=["jackpot"]):
            igb_json.process_response(payload, DATE_LIMIT, ["jackpot"], [], data_list, "/tmp")
        record = data_list[0]
        for field in ("website", "category", "date", "title", "url", "has_keywords"):
            assert field in record, f"Missing field: {field}"

    def test_website_field_is_igb(self):
        payload = _make_json_response([
            _make_json_result("https://igamingbusiness.com/casino/a/", RECENT_DATE)
        ])
        data_list: list = []
        with patch("igb_json.process_response_details", return_value=[]):
            igb_json.process_response(payload, DATE_LIMIT, [], [], data_list, "/tmp")
        assert data_list[0]["website"] == "igb"

    def test_has_keywords_is_comma_separated(self):
        payload = _make_json_response([
            _make_json_result("https://igamingbusiness.com/casino/a/", RECENT_DATE)
        ])
        data_list: list = []
        with patch("igb_json.process_response_details", return_value=["jackpot", "online casino"]):
            igb_json.process_response(payload, DATE_LIMIT, [], [], data_list, "/tmp")
        assert data_list[0]["has_keywords"] == "jackpot, online casino"


# ---------------------------------------------------------------------------
# Stats accumulation
# ---------------------------------------------------------------------------

class TestIgbJsonStats:

    def test_stats_appended_by_start_function(self, tmp_path):
        """start_igb_json_reports() appends a stats dict with source and news_count."""
        stats: list = []
        payload = _make_json_response([
            _make_json_result("https://igamingbusiness.com/casino/a/", RECENT_DATE, "Article 1"),
            _make_json_result("https://igamingbusiness.com/casino/b/", RECENT_DATE, "Article 2"),
        ])

        with patch("igb_json.request_url", return_value=payload), \
             patch("igb_json.process_response_details", return_value=[]):
            # Patch process_response to return False immediately (stop after first "page")
            with patch("igb_json.process_response", return_value=False) as mock_pr:
                mock_pr.return_value = False
                igb_json.start_igb_json_reports(
                    days=7,
                    key_words=[],
                    date_limit=DATE_LIMIT,
                    path_output=str(tmp_path),
                    url_list=[],
                    stats=stats,
                )

        assert len(stats) == 1
        assert stats[0]["source"] == "IGB"
        assert "news_count" in stats[0]
