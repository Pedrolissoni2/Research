"""
Tests for keyword matching logic (process_response_details).

All scrapers share the same pattern:
  - Fetch article HTML via request_url()
  - Select paragraph elements with a CSS selector
  - Check if each keyword is present in the text (case-insensitive)
  - Return a sorted, deduplicated list of matched keywords

casinoreports.py is used as the representative module.
"""

import pytest
from unittest.mock import patch
from bs4 import BeautifulSoup

import casinoreports


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_article_soup(paragraphs: list[str]) -> BeautifulSoup:
    """Return a BeautifulSoup simulating a casinoreports article detail page."""
    p_tags = "".join(f"<p>{p}</p>" for p in paragraphs)
    html = f"<article class='content'>{p_tags}</article>"
    return BeautifulSoup(html, "html.parser")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestKeywordFound:
    def test_single_keyword_detected(self):
        soup = _make_article_soup(["This article discusses a progressive jackpot."])
        with patch("casinoreports.request_url", return_value=soup):
            result = casinoreports.process_response_details("http://example.com", ["jackpot"])
        assert "jackpot" in result

    def test_multiple_keywords_all_detected(self):
        soup = _make_article_soup([
            "The online casino launched a new jackpot.",
            "A leading provider announced the feature.",
        ])
        key_words = ["jackpot", "online casino", "provider"]
        with patch("casinoreports.request_url", return_value=soup):
            result = casinoreports.process_response_details("http://example.com", key_words)
        assert set(result) == {"jackpot", "online casino", "provider"}

    def test_keyword_split_across_paragraphs(self):
        """Each paragraph is scanned independently; keywords found in any paragraph count."""
        soup = _make_article_soup([
            "No relevant content here.",
            "This paragraph mentions a jackpot drop.",
        ])
        with patch("casinoreports.request_url", return_value=soup):
            result = casinoreports.process_response_details("http://example.com", ["jackpot drop"])
        assert "jackpot drop" in result


class TestCaseInsensitivity:
    def test_uppercase_keyword_in_text_is_matched(self):
        soup = _make_article_soup(["The JACKPOT was claimed."])
        with patch("casinoreports.request_url", return_value=soup):
            result = casinoreports.process_response_details("http://example.com", ["jackpot"])
        assert "jackpot" in result

    def test_mixed_case_keyword_in_text_is_matched(self):
        soup = _make_article_soup(["Winning the Online Casino prize."])
        with patch("casinoreports.request_url", return_value=soup):
            result = casinoreports.process_response_details("http://example.com", ["online casino"])
        assert "online casino" in result


class TestNoMatch:
    def test_keyword_absent_returns_empty_list(self):
        soup = _make_article_soup(["This is a sports news article about football."])
        with patch("casinoreports.request_url", return_value=soup):
            result = casinoreports.process_response_details("http://example.com", ["jackpot", "online casino"])
        assert result == []

    def test_empty_article_returns_empty_list(self):
        soup = BeautifulSoup("<article class='content'></article>", "html.parser")
        with patch("casinoreports.request_url", return_value=soup):
            result = casinoreports.process_response_details("http://example.com", ["jackpot"])
        assert result == []

    def test_empty_keyword_list_returns_empty_list(self):
        soup = _make_article_soup(["This article mentions jackpots and casinos."])
        with patch("casinoreports.request_url", return_value=soup):
            result = casinoreports.process_response_details("http://example.com", [])
        assert result == []


class TestDeduplication:
    def test_keyword_repeated_across_paragraphs_appears_once(self):
        soup = _make_article_soup([
            "The jackpot grew larger.",
            "Another jackpot mention in the second paragraph.",
            "And yet another jackpot reference.",
        ])
        with patch("casinoreports.request_url", return_value=soup):
            result = casinoreports.process_response_details("http://example.com", ["jackpot"])
        assert result.count("jackpot") == 1


class TestResultOrdering:
    def test_result_is_sorted_alphabetically(self):
        soup = _make_article_soup(["The provider runs an online casino jackpot game."])
        key_words = ["provider", "jackpot", "online casino"]
        with patch("casinoreports.request_url", return_value=soup):
            result = casinoreports.process_response_details("http://example.com", key_words)
        assert result == sorted(result)


class TestSubstringMatchBehavior:
    def test_keyword_as_substring_is_detected(self):
        """
        Documents current behavior: the implementation uses 'in' for matching,
        so 'jackpot' will match inside 'jackpots'.  This is intentional for
        broad recall, but means false positives are possible.
        """
        soup = _make_article_soup(["Multiple jackpots were awarded."])
        with patch("casinoreports.request_url", return_value=soup):
            result = casinoreports.process_response_details("http://example.com", ["jackpot"])
        # Substring match is the current behavior — assert it's consistent
        assert "jackpot" in result
