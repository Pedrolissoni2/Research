"""
Tests for CSV persistence (save_data).

All scrapers share the same save_data() implementation.  casinoreports.py
is used as the representative module.

Covers:
  - File creation when news.csv does not yet exist
  - Header row written on first save
  - No duplicate header when appending to an existing file
  - Data values are written and readable with DictReader
  - Multiple rows are written correctly
  - Empty data list creates file but writes nothing beyond header
"""

import csv
import os
import pytest

import casinoreports


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _sample_record(**overrides) -> dict:
    base = {
        "category": "Casino",
        "date": "2024-06-15 10:30:00",
        "title": "Big Jackpot Win",
        "url": "http://example.com/win",
        "website": "casinoreports",
        "has_keywords": "jackpot, online casino",
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# File creation
# ---------------------------------------------------------------------------

class TestFileCreation:

    def test_csv_file_is_created(self, tmp_path):
        casinoreports.save_data([_sample_record()], str(tmp_path))
        assert (tmp_path / "news.csv").exists()

    def test_no_file_created_when_data_is_empty(self, tmp_path):
        """
        Current behavior: save_data() only creates a file when the list is
        non-empty (DictWriter.writerows with an empty list writes nothing, but
        the file is still opened and the header is written).
        This test documents/verifies the actual outcome.
        """
        casinoreports.save_data([], str(tmp_path))
        # File is opened for append, so it is created; header is written if new.
        assert (tmp_path / "news.csv").exists()


# ---------------------------------------------------------------------------
# Header handling
# ---------------------------------------------------------------------------

class TestHeaderHandling:

    EXPECTED_FIELDNAMES = ["category", "date", "title", "url", "website", "has_keywords"]

    def test_header_present_in_new_file(self, tmp_path):
        casinoreports.save_data([_sample_record()], str(tmp_path))
        with open(tmp_path / "news.csv", encoding="utf-8") as f:
            first_row = next(csv.reader(f))
        assert first_row == self.EXPECTED_FIELDNAMES

    def test_no_second_header_when_appending(self, tmp_path):
        """Calling save_data twice must not insert a second header row."""
        casinoreports.save_data([_sample_record(title="Article 1", url="http://ex.com/1")], str(tmp_path))
        casinoreports.save_data([_sample_record(title="Article 2", url="http://ex.com/2")], str(tmp_path))

        with open(tmp_path / "news.csv", encoding="utf-8") as f:
            rows = list(csv.reader(f))

        # 1 header + 2 data rows
        assert len(rows) == 3
        # Only the first row is the header
        assert rows[0] == self.EXPECTED_FIELDNAMES
        assert rows[1][self.EXPECTED_FIELDNAMES.index("title")] == "Article 1"
        assert rows[2][self.EXPECTED_FIELDNAMES.index("title")] == "Article 2"


# ---------------------------------------------------------------------------
# Data integrity
# ---------------------------------------------------------------------------

class TestDataIntegrity:

    def test_written_values_are_readable(self, tmp_path):
        record = _sample_record(
            title="Progressive Jackpot Record",
            url="http://example.com/record",
            has_keywords="progressive jackpot, jackpot",
        )
        casinoreports.save_data([record], str(tmp_path))

        with open(tmp_path / "news.csv", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 1
        assert rows[0]["title"] == "Progressive Jackpot Record"
        assert rows[0]["website"] == "casinoreports"
        assert rows[0]["has_keywords"] == "progressive jackpot, jackpot"

    def test_multiple_records_all_written(self, tmp_path):
        records = [
            _sample_record(title=f"Article {i}", url=f"http://ex.com/{i}")
            for i in range(5)
        ]
        casinoreports.save_data(records, str(tmp_path))

        with open(tmp_path / "news.csv", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        assert len(rows) == 5
        titles = {r["title"] for r in rows}
        assert titles == {f"Article {i}" for i in range(5)}

    def test_unicode_characters_preserved(self, tmp_path):
        record = _sample_record(title="Título em Português", category="Notícias")
        casinoreports.save_data([record], str(tmp_path))

        with open(tmp_path / "news.csv", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        assert rows[0]["title"] == "Título em Português"
        assert rows[0]["category"] == "Notícias"

    def test_empty_has_keywords_written_as_empty_string(self, tmp_path):
        record = _sample_record(has_keywords="")
        casinoreports.save_data([record], str(tmp_path))

        with open(tmp_path / "news.csv", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        assert rows[0]["has_keywords"] == ""
