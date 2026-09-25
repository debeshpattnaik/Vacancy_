"""Shared pytest fixtures for Legal Vacancy Tracker tests."""
import pytest
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

from app.database import VacancyDB


@pytest.fixture
def temp_db(tmp_path):
    """Create a temporary VacancyDB instance for testing."""
    db_path = tmp_path / "test_vacancies.db"
    db = VacancyDB(db_path)
    yield db


@pytest.fixture
def sample_html():
    """Sample HTML with a mix of legal and non-legal vacancy links."""
    return """
    <html>
        <body>
            <h1>Careers</h1>
            <table>
                <tr>
                    <td><a href="/notifications/legal-officer-recruitment-2026.pdf">Recruitment of Legal Officer - 2026</a></td>
                    <td>15-09-2026</td>
                </tr>
                <tr>
                    <td><a href="/notifications/advocate-empanelment.html">Empanelment of Advocates for Panel</a></td>
                    <td>10-09-2026</td>
                </tr>
                <tr>
                    <td><a href="/notifications/clerk-vacancy.html">Vacancy for Office Clerk</a></td>
                    <td>01-09-2026</td>
                </tr>
                <tr>
                    <td><a href="/notifications/company-secretary-appointment.pdf">Appointment of Company Secretary</a></td>
                    <td>05-09-2026</td>
                </tr>
                <tr>
                    <td><a href="/about.html">About Us</a></td>
                    <td></td>
                </tr>
                <tr>
                    <td><a href="/notifications/compliance-officer-hiring.html">Hiring of Compliance Officer</a></td>
                    <td>20-09-2026</td>
                </tr>
            </table>
            <a href="/careers">Career Opportunities</a>
            <a href="/notifications/law-officer-walk-in.pdf">Walk-in Interview for Law Officer</a>
        </body>
    </html>
    """


@pytest.fixture
def sample_source():
    """A sample source configuration."""
    return {
        "name": "Test Ministry of Law",
        "type": "Ministry/Department",
        "url": "https://example.gov.in/",
        "is_legal_org": True
    }


@pytest.fixture
def sample_non_legal_source():
    """A sample non-legal source configuration."""
    return {
        "name": "Test Department",
        "type": "Ministry/Department",
        "url": "https://example.gov.in/",
        "is_legal_org": False
    }


@pytest.fixture
def sample_sources():
    """Multiple sample sources for integration tests."""
    return [
        {"name": "Ministry of Law", "type": "Ministry/Department", "url": "https://law.gov.in/", "is_legal_org": True},
        {"name": "SEBI", "type": "Regulator", "url": "https://www.sebi.gov.in/"},
        {"name": "NCLT", "type": "Tribunal", "url": "https://nclt.gov.in/", "is_legal_org": True}
    ]


@pytest.fixture
def sample_vacancy():
    """A sample vacancy dict as returned by the scraper."""
    return {
        "title": "Recruitment of Legal Officer",
        "url": "https://example.gov.in/notifications/legal-officer-2026.pdf",
        "source_name": "Test Ministry",
        "source_type": "Ministry/Department",
        "date_text": None,
        "is_pdf": True
    }
