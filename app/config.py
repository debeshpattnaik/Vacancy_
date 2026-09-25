"""
Configuration for the Legal Vacancy Tracker project.
"""
import os
import re
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

# Path Configuration
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / 'data'
DB_PATH = DATA_DIR / 'vacancies.db'
REPORT_PATH_MD = DATA_DIR / 'daily_report.md'
REPORT_PATH_HTML = DATA_DIR / 'daily_report.html'
LOG_DIR = ROOT / 'logs'

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# HTTP Settings
TIMEOUT = int(os.getenv('LVT_TIMEOUT', '15'))
MAX_RETRIES = int(os.getenv('LVT_MAX_RETRIES', '3'))
RETRY_BACKOFF = float(os.getenv('LVT_RETRY_BACKOFF', '0.5'))
RATE_LIMIT_DELAY = float(os.getenv('LVT_RATE_LIMIT_DELAY', '2.0'))

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.47'
]

# Regex Patterns
_LEGAL_TERMS = r'\b(legal|law|advocate|counsel|judicial|compliance|company secretary|legal officer|legal advisor|law officer|legal consultant|legal assistant|arbitration|litigation|legal associate|legal manager|para-legal|legal head|general counsel|CLO|legal department|jurisprudence|legal executive|solicitor|notary|attorney|prosecutor|standing counsel|legal aid|panel advocate|district judge|civil judge|magistrate|additional judge|registrar \(judicial\))\b'
_VACANCY_TERMS = r'\b(recruitment|career|vacancy|vacancies|job|jobs|notification|advertisement|engagement|appointment|hiring|apply|application|consultant|walk-in|interview|selection|empanelment|panel|deputation|contractual|outsource|tender|eoi|expression of interest|rfp|circular|office order|notice|opening)\b'

LEGAL_PATTERN = re.compile(_LEGAL_TERMS, re.IGNORECASE)
VACANCY_PATTERN = re.compile(_VACANCY_TERMS, re.IGNORECASE)

def setup_logging(verbose: bool = False) -> logging.Logger:
    """Configures and returns the application logger."""
    level = logging.DEBUG if verbose else logging.INFO
    logger = logging.getLogger('lvt')
    
    if logger.handlers:
        return logger

    logger.setLevel(level)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # File handler
    log_file = LOG_DIR / 'tracker.log'
    fh = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3)
    fh.setLevel(level)
    fh.setFormatter(formatter)
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger
