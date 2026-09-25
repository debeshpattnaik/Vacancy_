"""
Main orchestrator for Legal Vacancy Tracker.
"""
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

from app.config import setup_logging, DB_PATH, REPORT_PATH_MD, REPORT_PATH_HTML, DATA_DIR
from app.scraper import scrape_all
from app.database import VacancyDB
from app.reporter import generate_markdown_report, generate_html_report

def main():
    parser = argparse.ArgumentParser(description="Legal Vacancy Tracker")
    parser.add_argument('--sources', type=str, default=None, help='Path to sources.json')
    parser.add_argument('--report-only', action='store_true', help='Generate reports without scraping')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('--dry-run', action='store_true', help='Scrape but do not update database')
    args = parser.parse_args()

    logger = setup_logging(verbose=args.verbose)
    logger.info("Starting Legal Vacancy Tracker v2.0.0...")

    # Load sources
    if args.sources:
        sources_path = Path(args.sources)
    else:
        sources_path = DATA_DIR / 'sources.json'
    
    if not sources_path.exists():
        logger.error(f"Sources file not found at {sources_path}")
        sys.exit(1)

    try:
        with open(sources_path, 'r', encoding='utf-8') as f:
            sources = json.load(f)
            # Handle potential dictionary wrappers
            if isinstance(sources, dict) and 'sources' in sources:
                sources = sources['sources']
    except Exception as e:
        logger.error(f"Failed to load sources: {e}")
        sys.exit(1)

    # Initialize DB
    db = VacancyDB(DB_PATH)
    
    run_timestamp = datetime.utcnow().isoformat()
    errors = []
    
    if not args.report_only:
        logger.info(f"Loaded {len(sources)} sources for scraping.")
        
        all_vacancies, errors = scrape_all(sources)
        logger.info(f"Scrape completed. Found {len(all_vacancies)} vacancies total. Errors: {len(errors)}")

        if not args.dry_run:
            new_count = 0
            # Insert into database
            for vac in all_vacancies:
                is_new = db.insert_vacancy(vac)
                if is_new:
                    new_count += 1
            
            # Expire old records
            expired = db.mark_expired(older_than_days=30)
            logger.info(f"Inserted {new_count} new vacancies. Marked {expired} as expired.")
            
            # Log run
            stats = db.get_stats()
            db.log_scrape_run(
                sources_checked=len(sources),
                sources_succeeded=len(sources) - len(errors),
                sources_failed=len(errors),
                new_vacancies=new_count,
                total_active=stats['active'],
                errors=errors
            )
        else:
            logger.info("DRY RUN: Database not updated.")

    # Generate Reports
    logger.info("Generating reports...")
    
    stats = db.get_stats()
    # If not dry run, fetch newly inserted. If dry run, assume all found today are new for the sake of the report?
    # Better to just use the DB's actual state
    # We'll fetch new vacancies from the past 24 hours approximately
    yesterday = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    new_vacs_db = db.get_new_vacancies(since_iso=yesterday)
    all_active = db.get_all_active()
    
    generate_markdown_report(new_vacs_db, all_active, stats, errors, run_timestamp, REPORT_PATH_MD)
    generate_html_report(new_vacs_db, all_active, stats, errors, run_timestamp, REPORT_PATH_HTML)
    
    logger.info(f"Reports saved to {REPORT_PATH_MD} and {REPORT_PATH_HTML}")
    
    if errors:
        sys.exit(2) # Warning state
    sys.exit(0)

if __name__ == '__main__':
    main()
