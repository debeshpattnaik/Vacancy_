# 🏛️ Legal Vacancy Tracker

[![Daily Check](https://github.com/debeshpattnaik/Vacancy_/actions/workflows/daily.yml/badge.svg)](https://github.com/debeshpattnaik/Vacancy_/actions/workflows/daily.yml)
[![Tests](https://github.com/debeshpattnaik/Vacancy_/actions/workflows/test.yml/badge.svg)](https://github.com/debeshpattnaik/Vacancy_/actions/workflows/test.yml)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Automated tracker for legal/law vacancies across 100+ Indian government organizations, PSUs, regulatory bodies, tribunals, and courts.**

Never miss a legal vacancy notification again. This tool scrapes official career pages twice daily and produces structured reports of all legal recruitment opportunities.

---

## ✨ Features

- 📡 **118+ Sources** — Ministries, regulators (SEBI, RBI, CCI), tribunals (NCLT, NGT), PSUs, banks, courts, NLUs
- 🔍 **Smart Detection** — Two-pass matching with 40+ legal terms and 30+ vacancy terms
- 📄 **PDF Detection** — Automatically identifies downloadable PDF notifications
- 🗄️ **SQLite Database** — Persistent storage with vacancy lifecycle tracking (active/expired)
- 📊 **Dual Reports** — Professional Markdown + standalone HTML reports
- ⏰ **Auto-scheduled** — GitHub Actions runs twice daily (09:00 & 15:00 IST)
- 🔄 **Auto-retry** — HTTP retry with exponential backoff, rate limiting, User-Agent rotation
- 📝 **Scrape Logging** — Complete audit trail of every run
- 🐳 **Docker Support** — Containerized deployment option

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/debeshpattnaik/Vacancy_.git
cd Vacancy_

# 2. Install
pip install -r requirements.txt

# 3. Run
python -m app.tracker
```

Reports are generated at:
- `data/daily_report.md` — Markdown report
- `data/daily_report.html` — HTML report (open in browser)
- `data/vacancies.db` — SQLite database

## 📋 Usage

```bash
# Standard run
python -m app.tracker

# Verbose logging
python -m app.tracker --verbose

# Dry run (scrape but don't save)
python -m app.tracker --dry-run

# Report only (from existing DB)
python -m app.tracker --report-only

# Custom sources file
python -m app.tracker --sources path/to/custom_sources.json
```

## ⚙️ Configuration

Copy `.env.example` to `.env` and customize:

```ini
LVT_TIMEOUT=15              # HTTP timeout (seconds)
LVT_MAX_RETRIES=3           # Retry attempts per request
LVT_RATE_LIMIT_DELAY=2.0    # Delay between requests (seconds)
LVT_EXPIRY_DAYS=30          # Days before marking vacancy as expired
```

## 🏗️ Architecture

```
legal-vacancy-tracker/
├── app/
│   ├── config.py       # Configuration, paths, regex patterns, logging
│   ├── scraper.py      # VacancyScraper with retry, rate-limit, UA rotation
│   ├── database.py     # VacancyDB with SQLite, lifecycle management
│   ├── reporter.py     # Markdown + HTML report generation
│   └── tracker.py      # Main orchestrator with CLI
├── data/
│   ├── sources.json    # 118+ source configurations
│   ├── vacancies.db    # SQLite database (auto-generated)
│   ├── daily_report.md # Latest report (auto-generated)
│   └── daily_report.html
├── tests/              # Pytest test suite
├── docker/             # Docker deployment
├── .github/workflows/  # CI/CD (daily scrape + test pipeline)
├── pyproject.toml      # Project metadata & tool config
└── requirements.txt    # Dependencies
```

## 📡 Source Categories (118+ Sources)

| Category | Count | Examples |
|---|---|---|
| Central Government | 24 | Ministry of Law, DoPT, MeitY, MHA |
| Regulators | 20 | SEBI, RBI, IRDAI, CCI, IBBI, TRAI |
| Tribunals & Courts | 16 | NCLT, NCLAT, SAT, NGT, High Courts, Supreme Court |
| PSUs | 27 | ONGC, NTPC, BHEL, SAIL, Coal India, IOC |
| PSU Banks & Insurance | 13 | SBI, PNB, BOB, LIC, GIC |
| Autonomous Bodies & NLUs | 12 | NALSA, Law Commission, NLSIU, NALSAR |
| Job Aggregator Portals | 8 | NCS, UPSC, SSC, FreeJobAlert |

## 🔄 GitHub Actions (Auto-scheduled)

Once pushed to GitHub, the tracker runs automatically:

1. **Daily scrape** — Twice daily at 09:00 IST and 15:00 IST
2. **Auto-commit** — Updates database and reports
3. **Auto-issue** — Creates GitHub Issue on failure
4. **Manual trigger** — Run anytime via `workflow_dispatch`

## 🧪 Testing

```bash
# Install dev dependencies
pip install pytest pytest-cov ruff mypy

# Run tests
pytest tests/ -v --cov=app

# Lint
ruff check app/ tests/

# Type check
mypy app/
```

## 🐳 Docker

```bash
docker build -t legal-vacancy-tracker -f docker/Dockerfile .
docker run --rm -v $(pwd)/data:/app/data legal-vacancy-tracker
```

## ➕ Adding New Sources

Edit `data/sources.json` and add an entry:

```json
{
  "name": "Organization Name",
  "type": "Category",
  "url": "https://main-website.com",
  "career_url": "https://main-website.com/careers",
  "is_legal_org": false
}
```

Set `is_legal_org: true` for organizations whose **all** vacancies are legal-relevant (courts, law departments).

See [`data/README.md`](data/README.md) for the complete source schema guide.

## ⚠️ Disclaimer

This tool monitors **publicly accessible** official government and corporate career pages. Some organizations use JavaScript rendering, CAPTCHAs, PDFs, or separate application portals that may not be fully captured by HTML scraping. Always verify vacancy details on the official website.

## 📄 License

[MIT License](LICENSE) — free to use, modify, and distribute.

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Priority areas:
- Adding more sources with correct career page URLs
- JavaScript-rendered page support (Playwright/Selenium)
- Email/Telegram notification integration
- Advanced date parsing from vacancy text
