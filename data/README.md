# Data Sources Guide

## Source Schema

Each entry in `sources.json` follows this schema:

```json
{
  "name": "Organization Name",
  "type": "Category (Ministry/Department, Regulator, Tribunal, PSU, etc.)",
  "url": "https://main-website.com",
  "career_url": "https://main-website.com/careers",
  "is_legal_org": true,
  "search_patterns": ["optional additional patterns"],
  "notes": "any special notes"
}
```

### Fields

| Field | Required | Description |
|---|---|---|
| `name` | ✅ | Display name of the organization |
| `type` | ✅ | Category for grouping in reports |
| `url` | ✅ | Main website URL |
| `career_url` | ❌ | Direct link to careers/recruitment page (preferred over homepage) |
| `is_legal_org` | ❌ | Set `true` for organizations whose ALL vacancies are legal-relevant (courts, law ministries, NALSA, etc.). This bypasses the legal keyword check. |
| `notes` | ❌ | Internal notes for maintainers |

## Source Categories

- **Ministry/Department** — Central government bodies
- **Regulator** — SEBI, RBI, IRDAI, CCI, etc.
- **Tribunal** — NCLT, NCLAT, SAT, NGT, CAT, etc.
- **Judiciary** — High Courts, Supreme Court
- **PSU** — Public Sector Undertakings
- **PSU Bank** — State-owned banks
- **Financial Institution** — NABARD, SIDBI, EXIM Bank, etc.
- **Autonomous Body** — NITI Aayog, UGC, NLUs, etc.
- **Job Aggregator** — NCS, UPSC, SSC portals

## Tips for Adding Sources

1. **Use the actual career/recruitment page URL** as `career_url` — not just the homepage
2. **Government sites** use `.gov.in` or `.nic.in` domains
3. **PSU career pages** are often at `/careers`, `/career`, or `/recruitment`
4. **Set `is_legal_org: true`** only for organizations where legal work IS the core mandate
5. **Test URLs manually** before adding — some government sites may be temporarily down

## Generated Files

| File | Description |
|---|---|
| `vacancies.db` | SQLite database with all scraped vacancies and scrape history |
| `daily_report.md` | Markdown report of latest run |
| `daily_report.html` | HTML report (standalone, shareable) |
