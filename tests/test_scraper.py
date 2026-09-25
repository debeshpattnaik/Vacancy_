"""Comprehensive tests for Legal Vacancy Tracker."""
import pytest
import re
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from app.config import LEGAL_PATTERN, VACANCY_PATTERN, USER_AGENTS, setup_logging
from app.scraper import VacancyScraper
from app.database import VacancyDB
from app.reporter import generate_markdown_report, generate_html_report


# ─── Config Tests ─────────────────────────────────────────────────────────────

class TestConfig:
    def test_legal_pattern_matches_basic_terms(self):
        terms = ["legal", "law", "advocate", "counsel", "judicial", "compliance",
                 "company secretary", "legal officer", "legal advisor"]
        for term in terms:
            assert LEGAL_PATTERN.search(term), f"LEGAL_PATTERN should match '{term}'"

    def test_legal_pattern_case_insensitive(self):
        assert LEGAL_PATTERN.search("LEGAL OFFICER")
        assert LEGAL_PATTERN.search("Legal Advisor")
        assert LEGAL_PATTERN.search("Advocate")

    def test_legal_pattern_no_false_positive(self):
        assert not LEGAL_PATTERN.search("engineer")
        assert not LEGAL_PATTERN.search("accountant")

    def test_vacancy_pattern_matches_basic_terms(self):
        terms = ["recruitment", "career", "vacancy", "vacancies", "job",
                 "notification", "appointment", "hiring", "empanelment"]
        for term in terms:
            assert VACANCY_PATTERN.search(term), f"VACANCY_PATTERN should match '{term}'"

    def test_vacancy_pattern_no_false_positive(self):
        assert not VACANCY_PATTERN.search("annual report")
        assert not VACANCY_PATTERN.search("about us")

    def test_user_agents_list_populated(self):
        assert len(USER_AGENTS) >= 5
        for ua in USER_AGENTS:
            assert "Mozilla" in ua or "Chrome" in ua

    def test_setup_logging_returns_logger(self):
        import logging
        logger = setup_logging(verbose=False)
        assert isinstance(logger, logging.Logger)
        assert logger.name == "lvt"


# ─── Scraper Tests ────────────────────────────────────────────────────────────

class TestScraper:
    def test_scraper_creates_session(self):
        scraper = VacancyScraper()
        assert scraper.session is not None

    def test_extract_links_finds_legal_vacancies(self, sample_html, sample_source):
        scraper = VacancyScraper()
        links = scraper.extract_links(sample_html, "https://example.gov.in/", sample_source)
        # Should find legal-related vacancy links (legal officer, advocate, company secretary, compliance, law officer)
        assert len(links) >= 3, f"Expected >= 3 legal vacancy links, got {len(links)}: {[l['title'] for l in links]}"

    def test_extract_links_detects_pdf(self, sample_html, sample_source):
        scraper = VacancyScraper()
        links = scraper.extract_links(sample_html, "https://example.gov.in/", sample_source)
        pdf_links = [l for l in links if l.get("is_pdf")]
        assert len(pdf_links) >= 1, "Should detect at least one PDF link"

    def test_extract_links_non_legal_source_filters(self, sample_html, sample_non_legal_source):
        scraper = VacancyScraper()
        links = scraper.extract_links(sample_html, "https://example.gov.in/", sample_non_legal_source)
        # Non-legal source: only links with legal keywords in TEXT should match
        for link in links:
            assert LEGAL_PATTERN.search(link["title"]), \
                f"Non-legal source should only return links with legal terms: '{link['title']}'"

    def test_extract_links_returns_proper_structure(self, sample_html, sample_source):
        scraper = VacancyScraper()
        links = scraper.extract_links(sample_html, "https://example.gov.in/", sample_source)
        for link in links:
            assert "title" in link
            assert "url" in link
            assert "source_name" in link
            assert "source_type" in link
            assert "is_pdf" in link
            assert link["url"].startswith("http")

    def test_extract_links_resolves_relative_urls(self, sample_html, sample_source):
        scraper = VacancyScraper()
        links = scraper.extract_links(sample_html, "https://example.gov.in/", sample_source)
        for link in links:
            assert link["url"].startswith("https://example.gov.in/")

    def test_rate_limiter(self):
        import time
        scraper = VacancyScraper()
        scraper.last_request_time = time.time()
        start = time.time()
        scraper._rate_limit()
        # Should have waited approximately RATE_LIMIT_DELAY seconds
        elapsed = time.time() - start
        assert elapsed >= 1.0  # At least some rate limiting happened


# ─── Database Tests ───────────────────────────────────────────────────────────

class TestDatabase:
    def test_db_creates_tables(self, temp_db):
        with temp_db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = {row[0] for row in cursor.fetchall()}
            assert "vacancies" in tables
            assert "scrape_log" in tables

    def test_insert_new_vacancy(self, temp_db, sample_vacancy):
        result = temp_db.insert_vacancy(sample_vacancy)
        assert result is True  # New vacancy

    def test_insert_duplicate_vacancy(self, temp_db, sample_vacancy):
        temp_db.insert_vacancy(sample_vacancy)
        result = temp_db.insert_vacancy(sample_vacancy)
        assert result is False  # Already exists

    def test_get_all_active(self, temp_db, sample_vacancy):
        temp_db.insert_vacancy(sample_vacancy)
        active = temp_db.get_all_active()
        assert len(active) == 1
        assert active[0]["url"] == sample_vacancy["url"]
        assert active[0]["status"] == "active"

    def test_get_stats(self, temp_db, sample_vacancy):
        temp_db.insert_vacancy(sample_vacancy)
        stats = temp_db.get_stats()
        assert stats["active"] == 1
        assert stats["total"] == 1

    def test_mark_expired(self, temp_db):
        # Insert a vacancy with an old last_seen date
        old_vacancy = {
            "title": "Old Vacancy",
            "url": "https://example.gov.in/old",
            "source_name": "Test",
            "source_type": "Test",
            "date_text": None,
            "is_pdf": False
        }
        temp_db.insert_vacancy(old_vacancy)
        # Manually backdate last_seen
        with temp_db.get_connection() as conn:
            conn.execute("UPDATE vacancies SET last_seen = datetime('now', '-60 days') WHERE url = ?",
                        (old_vacancy["url"],))
            conn.commit()
        expired = temp_db.mark_expired(older_than_days=30)
        assert expired == 1

    def test_log_scrape_run(self, temp_db):
        temp_db.log_scrape_run(
            sources_checked=10,
            sources_succeeded=8,
            sources_failed=2,
            new_vacancies=5,
            total_active=20,
            errors=[{"source": "Test", "error": "timeout"}]
        )
        with temp_db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scrape_log")
            logs = cursor.fetchall()
            assert len(logs) == 1

    def test_get_new_vacancies_since(self, temp_db, sample_vacancy):
        temp_db.insert_vacancy(sample_vacancy)
        # Get vacancies from before today — should include it
        yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()
        new = temp_db.get_new_vacancies(since_iso=yesterday)
        assert len(new) == 1

    def test_multiple_vacancies(self, temp_db):
        for i in range(5):
            temp_db.insert_vacancy({
                "title": f"Legal Officer {i}",
                "url": f"https://example.gov.in/vacancy-{i}",
                "source_name": "Ministry",
                "source_type": "Department",
                "date_text": None,
                "is_pdf": False
            })
        stats = temp_db.get_stats()
        assert stats["active"] == 5
        assert stats["total"] == 5


# ─── Reporter Tests ──────────────────────────────────────────────────────────

class TestReporter:
    def test_markdown_report_empty(self, tmp_path):
        out = tmp_path / "test_report.md"
        generate_markdown_report([], [], {"active": 0, "total": 0}, [], "2026-09-25T00:00:00", out)
        content = out.read_text()
        assert "Legal Vacancy Tracker Report" in content
        assert "No new vacancies" in content

    def test_markdown_report_with_vacancies(self, tmp_path):
        out = tmp_path / "test_report.md"
        vacancies = [
            {"source": "SEBI", "source_type": "Regulator", "title": "Legal Officer", "url": "https://sebi.gov.in/jobs/1", "is_pdf": False}
        ]
        generate_markdown_report(vacancies, vacancies, {"active": 1, "total": 1}, [], "2026-09-25T00:00:00", out)
        content = out.read_text()
        assert "SEBI" in content
        assert "Legal Officer" in content

    def test_markdown_report_with_errors(self, tmp_path):
        out = tmp_path / "test_report.md"
        errors = [{"source": "Test", "error": "Connection timeout"}]
        generate_markdown_report([], [], {"active": 0, "total": 0}, errors, "2026-09-25T00:00:00", out)
        content = out.read_text()
        assert "Connection timeout" in content

    def test_html_report_generates_valid_html(self, tmp_path):
        out = tmp_path / "test_report.html"
        generate_html_report([], [], {"active": 0, "total": 0}, [], "2026-09-25T00:00:00", out)
        content = out.read_text()
        assert "<html" in content
        assert "</html>" in content
        assert "Legal Vacancy Tracker Report" in content

    def test_html_report_with_vacancies(self, tmp_path):
        out = tmp_path / "test_report.html"
        vacancies = [
            {"source": "RBI", "source_type": "Regulator", "title": "Counsel", "url": "https://rbi.org.in/jobs/1", "is_pdf": True}
        ]
        generate_html_report(vacancies, vacancies, {"active": 1, "total": 1}, [], "2026-09-25T00:00:00", out)
        content = out.read_text()
        assert "RBI" in content
        assert "PDF" in content
