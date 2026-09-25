"""
Production scraper module for Legal Vacancy Tracker.
"""
import time
import random
import logging
from typing import List, Dict, Any, Tuple
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup

from app.config import (
    TIMEOUT, MAX_RETRIES, RETRY_BACKOFF, RATE_LIMIT_DELAY,
    USER_AGENTS, LEGAL_PATTERN, VACANCY_PATTERN
)

logger = logging.getLogger('lvt.scraper')

class VacancyScraper:
    def __init__(self):
        self.session = self._create_session()
        self.last_request_time = 0.0

    def _create_session(self) -> requests.Session:
        """Create a robust requests session with retries."""
        session = requests.Session()
        retry = Retry(
            total=MAX_RETRIES,
            backoff_factor=RETRY_BACKOFF,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
        
    def _rate_limit(self):
        """Simple rate limiting to avoid getting blocked."""
        elapsed = time.time() - self.last_request_time
        if elapsed < RATE_LIMIT_DELAY:
            time.sleep(RATE_LIMIT_DELAY - elapsed)
        self.last_request_time = time.time()

    def fetch_url(self, url: str) -> Tuple[str, str]:
        """Fetch a URL, returning HTML content and the final redirected URL."""
        self._rate_limit()
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        
        try:
            response = self.session.get(url, headers=headers, timeout=TIMEOUT)
            response.raise_for_status()
            return response.text, response.url
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch {url}: {e}")
            raise

    def scrape_source(self, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scrape a single source configuration and return found vacancies."""
        logger.info(f"Scraping source: {source.get('name')}")
        vacancies = []
        
        url_to_scrape = source.get('career_url') or source.get('url')
        if not url_to_scrape:
            logger.error(f"Source {source.get('name')} missing URL")
            return vacancies

        try:
            html, final_url = self.fetch_url(url_to_scrape)
            extracted = self.extract_links(html, final_url, source)
            vacancies.extend(extracted)
            
            # Check for sub-pages to follow one level deep
            soup = BeautifulSoup(html, 'html.parser')
            for a in soup.find_all('a', href=True):
                text = a.get_text(strip=True)
                if len(text) < 50 and VACANCY_PATTERN.search(text):
                    sub_url = urljoin(final_url, a['href'])
                    # Basic check to avoid re-scraping the same or external huge pages
                    if sub_url != final_url and sub_url.startswith(source.get('url', '')):
                        logger.debug(f"Following sub-page: {sub_url}")
                        try:
                            sub_html, sub_final_url = self.fetch_url(sub_url)
                            sub_extracted = self.extract_links(sub_html, sub_final_url, source)
                            vacancies.extend(sub_extracted)
                        except Exception as e:
                            logger.warning(f"Failed sub-page {sub_url}: {e}")
                            
        except Exception as e:
            logger.error(f"Error scraping {source.get('name')}: {e}")
            raise

        # Remove duplicates
        unique_vacancies = {v['url']: v for v in vacancies}.values()
        return list(unique_vacancies)

    def extract_links(self, html: str, base_url: str, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract legal vacancies from HTML using a Two-Pass approach."""
        soup = BeautifulSoup(html, 'html.parser')
        vacancies = []
        
        # Determine if the entire source is inherently legal
        is_legal_source = source.get('is_legal_org', False)
        
        for a in soup.find_all('a', href=True):
            text = a.get_text(separator=" ", strip=True)
            href = a['href']
            url = urljoin(base_url, href)
            
            # Include 'title' or 'aria-label' if text is empty or small
            title_attr = a.get('title', '')
            if len(text) < 5:
                text = f"{text} {title_attr}".strip()
                
            # If still no meaningful text, check parent row (common in tables)
            if len(text) < 10:
                parent_tr = a.find_parent('tr')
                if parent_tr:
                    text = parent_tr.get_text(separator=" ", strip=True)

            if not text:
                continue

            # TWO-PASS STRATEGY
            # Pass 1: Broad check for Vacancy/Recruitment terms
            if VACANCY_PATTERN.search(text) or '.pdf' in href.lower() or 'notification' in text.lower():
                
                # Pass 2: Check for Legal relevance (either by source config or text regex)
                if is_legal_source or LEGAL_PATTERN.search(text):
                    
                    is_pdf = href.lower().endswith('.pdf')
                    
                    vacancies.append({
                        'title': text[:200],  # Truncate overly long text
                        'url': url,
                        'source_name': source.get('name', 'Unknown'),
                        'source_type': source.get('type', 'Unknown'),
                        'date_text': None,  # Advanced date parsing could be added here
                        'is_pdf': is_pdf
                    })
                    
        return vacancies

def scrape_all(sources: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Orchestrates scraping of all sources and collects errors."""
    scraper = VacancyScraper()
    all_vacancies = []
    errors = []
    
    for source in sources:
        try:
            vacs = scraper.scrape_source(source)
            all_vacancies.extend(vacs)
        except Exception as e:
            errors.append({
                'source': source.get('name'),
                'url': source.get('url'),
                'error': str(e)
            })
            
    return all_vacancies, errors
