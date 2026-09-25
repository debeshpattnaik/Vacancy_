"""
Database layer for Legal Vacancy Tracker.
"""
import sqlite3
import json
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager
from typing import List, Dict, Any, Optional

class VacancyDB:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the database schema."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS vacancies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    source_type TEXT,
                    title TEXT NOT NULL,
                    url TEXT UNIQUE NOT NULL,
                    detail_url TEXT,
                    is_pdf BOOLEAN DEFAULT 0,
                    date_posted TEXT,
                    first_seen TEXT NOT NULL,
                    last_seen TEXT NOT NULL,
                    status TEXT DEFAULT 'active'
                )
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_vacancies_status ON vacancies(status)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_vacancies_url ON vacancies(url)
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scrape_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_timestamp TEXT NOT NULL,
                    sources_checked INTEGER,
                    sources_succeeded INTEGER,
                    sources_failed INTEGER,
                    new_vacancies INTEGER,
                    total_active INTEGER,
                    errors_json TEXT
                )
            ''')
            conn.commit()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def insert_vacancy(self, vacancy: Dict[str, Any]) -> bool:
        """Insert a vacancy. Returns True if it is newly added, False if it already existed."""
        now = datetime.utcnow().isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if exists
            cursor.execute("SELECT id FROM vacancies WHERE url = ?", (vacancy.get('url'),))
            row = cursor.fetchone()
            
            if row:
                # Update last_seen and status if previously inactive
                cursor.execute("""
                    UPDATE vacancies 
                    SET last_seen = ?, status = 'active'
                    WHERE url = ?
                """, (now, vacancy.get('url')))
                conn.commit()
                return False
            else:
                # Insert new
                cursor.execute("""
                    INSERT INTO vacancies 
                    (source, source_type, title, url, detail_url, is_pdf, date_posted, first_seen, last_seen, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')
                """, (
                    vacancy.get('source_name'),
                    vacancy.get('source_type', 'unknown'),
                    vacancy.get('title'),
                    vacancy.get('url'),
                    vacancy.get('detail_url'),
                    vacancy.get('is_pdf', False),
                    vacancy.get('date_text'),
                    now,
                    now
                ))
                conn.commit()
                return True

    def update_last_seen(self, urls: List[str]):
        """Bulk update last_seen for given URLs."""
        if not urls:
            return
        now = datetime.utcnow().isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(
                "UPDATE vacancies SET last_seen = ?, status = 'active' WHERE url = ?",
                [(now, url) for url in urls]
            )
            conn.commit()

    def get_new_vacancies(self, since_iso: str) -> List[Dict]:
        """Get vacancies first seen since the given ISO timestamp."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM vacancies WHERE first_seen >= ? ORDER BY first_seen DESC", (since_iso,))
            return [dict(row) for row in cursor.fetchall()]

    def get_all_active(self) -> List[Dict]:
        """Get all currently active vacancies."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM vacancies WHERE status = 'active' ORDER BY first_seen DESC")
            return [dict(row) for row in cursor.fetchall()]

    def mark_expired(self, older_than_days: int) -> int:
        """Mark vacancies as expired if they haven't been seen recently."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE vacancies 
                SET status = 'expired' 
                WHERE status = 'active' 
                AND last_seen < datetime('now', '-{older_than_days} days')
            """)
            updated = cursor.rowcount
            conn.commit()
            return updated

    def log_scrape_run(self, sources_checked: int, sources_succeeded: int, sources_failed: int, 
                       new_vacancies: int, total_active: int, errors: List[Dict]):
        """Log a complete scrape run."""
        now = datetime.utcnow().isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO scrape_log 
                (run_timestamp, sources_checked, sources_succeeded, sources_failed, new_vacancies, total_active, errors_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                now, sources_checked, sources_succeeded, sources_failed, 
                new_vacancies, total_active, json.dumps(errors)
            ))
            conn.commit()
            
    def get_stats(self) -> Dict[str, Any]:
        """Return basic database stats."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) FROM vacancies WHERE status = 'active'")
            active = cursor.fetchone()[0]
            cursor.execute("SELECT count(*) FROM vacancies")
            total = cursor.fetchone()[0]
            return {"active": active, "total": total}
