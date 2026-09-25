"""
Reporting functionality for Legal Vacancy Tracker.
"""
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

def generate_markdown_report(new_vacancies: List[Dict], all_active: List[Dict], 
                             stats: Dict[str, Any], errors: List[Dict], run_time: str, out_path: Path):
    """Generate a markdown report and write it to disk."""
    lines = [
        f"# Legal Vacancy Tracker Report",
        f"**Generated:** {run_time}",
        f"**Active Vacancies:** {stats.get('active', 0)} | **Total Monitored:** {stats.get('total', 0)}",
        "",
        "## New Vacancies"
    ]
    
    if not new_vacancies:
        lines.append("*No new vacancies found in this run.*")
    else:
        lines.append("| Source | Title | Link |")
        lines.append("|---|---|---|")
        for v in new_vacancies:
            link = f"[Link]({v['url']})"
            is_pdf = " *(PDF)*" if v.get('is_pdf') else ""
            lines.append(f"| {v['source']} ({v['source_type']}) | {v['title'].replace('|', '-')} | {link}{is_pdf} |")
    
    lines.append("\n## System Errors")
    if not errors:
        lines.append("*No errors in this run.*")
    else:
        for err in errors:
            lines.append(f"- **{err['source']}**: {err['error']}")
            
    out_path.write_text("\n".join(lines), encoding='utf-8')


def generate_html_report(new_vacancies: List[Dict], all_active: List[Dict], 
                         stats: Dict[str, Any], errors: List[Dict], run_time: str, out_path: Path):
    """Generate an HTML report and write it to disk."""
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Legal Vacancy Tracker Report</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 1200px; margin: 0 auto; padding: 20px; }}
            h1, h2 {{ color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
            .stats {{ display: flex; gap: 20px; margin-bottom: 20px; background: #f8f9fa; padding: 15px; border-radius: 8px; }}
            .stat-box {{ background: #fff; padding: 15px; border: 1px solid #ddd; border-radius: 5px; flex: 1; text-align: center; }}
            .stat-box strong {{ font-size: 1.5em; display: block; color: #3498db; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f2f2f2; font-weight: bold; }}
            tr:hover {{ background-color: #f5f5f5; }}
            a {{ color: #3498db; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            .error-list {{ color: #e74c3c; background: #fadbd8; padding: 15px; border-radius: 5px; }}
            .pdf-badge {{ font-size: 0.8em; background: #e74c3c; color: white; padding: 2px 6px; border-radius: 3px; margin-left: 5px; }}
        </style>
    </head>
    <body>
        <h1>Legal Vacancy Tracker Report</h1>
        <p><strong>Generated:</strong> {run_time}</p>
        
        <div class="stats">
            <div class="stat-box"><strong>{len(new_vacancies)}</strong> New Vacancies</div>
            <div class="stat-box"><strong>{stats.get('active', 0)}</strong> Active Vacancies</div>
            <div class="stat-box"><strong>{len(errors)}</strong> Errors</div>
        </div>
        
        <h2>New Vacancies</h2>
    """
    
    if not new_vacancies:
        html += "<p><em>No new vacancies found in this run.</em></p>"
    else:
        html += """
        <table>
            <thead>
                <tr>
                    <th>Source</th>
                    <th>Type</th>
                    <th>Title</th>
                    <th>Link</th>
                </tr>
            </thead>
            <tbody>
        """
        for v in new_vacancies:
            pdf_badge = "<span class='pdf-badge'>PDF</span>" if v.get('is_pdf') else ""
            html += f"""
                <tr>
                    <td>{v['source']}</td>
                    <td>{v.get('source_type', '')}</td>
                    <td>{v['title']}</td>
                    <td><a href="{v['url']}" target="_blank">View Details</a>{pdf_badge}</td>
                </tr>
            """
        html += "</tbody></table>"

    html += "<h2>System Errors</h2>"
    if not errors:
        html += "<p><em>No errors in this run.</em></p>"
    else:
        html += "<ul class='error-list'>"
        for err in errors:
            html += f"<li><strong>{err['source']}</strong>: {err['error']}</li>"
        html += "</ul>"
        
    html += """
    </body>
    </html>
    """
    
    out_path.write_text(html, encoding='utf-8')
