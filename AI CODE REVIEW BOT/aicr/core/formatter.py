from typing import List
from rich.table import Table
from rich.console import Console
from rich.text import Text
from .review_models import ReviewReport, ReviewItem, Severity

SEVERITY_COLOR = {
    Severity.low: "green",
    Severity.medium: "yellow",
    Severity.high: "red",
}


def render_report_table(report: ReviewReport, console: Console):
    report.compute_summary()
    table = Table(title="AI Code Review Report", show_lines=True)
    table.add_column("Severity")
    table.add_column("Category")
    table.add_column("Title")
    table.add_column("Location")
    table.add_column("Suggestion")
    for item in report.items:
        sev = Text(item.severity.value.upper(), style=SEVERITY_COLOR.get(item.severity, "white"))
        loc = f"{item.file or ''}:{item.start_line or ''}".strip(":")
        table.add_row(
            sev,
            item.category.value,
            item.title,
            loc,
            (item.suggestion or "").strip(),
        )
    console.print(table)
    # Print summary
    console.print("\nSummary:")
    for cat, count in report.summary.get("by_category", {}).items():
        console.print(f"- {cat}: {count}")
    for sev, count in report.summary.get("by_severity", {}).items():
        console.print(f"- {sev}: {count}")
    console.print(f"Total: {report.summary.get('total', 0)}")


def report_to_markdown(report: ReviewReport) -> str:
    report.compute_summary()
    lines: List[str] = []
    lines.append("# AI Code Review Report")
    lines.append("")
    lines.append("## Findings")
    lines.append("")
    for item in report.items:
        sev = item.severity.value.upper()
        loc = f"{item.file or ''}:{item.start_line or ''}".strip(":")
        lines.append(f"### [{sev}] {item.category.value} – {item.title}")
        lines.append("")
        lines.append("**Location:** " + (loc or "(unknown)"))
        lines.append("")
        lines.append("**Description:**")
        lines.append(item.description)
        lines.append("")
        if item.suggestion:
            lines.append("**Suggestion:**")
            lines.append(item.suggestion)
            lines.append("")
        if item.tool:
            lines.append(f"_Detected by: {item.tool}_")
            lines.append("")
    lines.append("## Summary")
    lines.append("")
    for cat, count in report.summary.get("by_category", {}).items():
        lines.append(f"- {cat}: {count}")
    for sev, count in report.summary.get("by_severity", {}).items():
        lines.append(f"- {sev}: {count}")
    lines.append(f"- Total: {report.summary.get('total', 0)}")
    return "\n".join(lines)