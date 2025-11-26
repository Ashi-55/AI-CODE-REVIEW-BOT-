import json
import os
from pathlib import Path
from typing import Optional, List

import typer
from rich.console import Console
from rich.panel import Panel

from .core.reviewer import Reviewer
from .core.formatter import render_report_table, report_to_markdown
from .core.git_utils import get_repo_root, get_diff_between_refs, fetch_pr_diff

app = typer.Typer(add_completion=False, help="AI Code Review Bot CLI")
console = Console()

@app.callback()
def main():
    """AI Code Review Bot – analyze diffs or PRs and produce structured review."""

review_app = typer.Typer(help="Run code review on different inputs")
app.add_typer(review_app, name="review")

@review_app.command("diff-file")
def review_diff_file(
    diff_path: Path = typer.Argument(..., help="Path to a unified diff file"),
    repo: Optional[Path] = typer.Option(None, "--repo", help="Path to local git repository"),
    output: Optional[Path] = typer.Option(None, "--output", help="Path to write JSON report"),
    markdown: Optional[Path] = typer.Option(None, "--markdown", help="Path to write Markdown summary"),
    github_summary: bool = typer.Option(False, "--github-summary", help="Also write to GitHub Actions job summary if available"),
    fail_on_severity: Optional[str] = typer.Option(None, "--fail-on-severity", help="Fail (non-zero exit) if any issue >= given severity [low|medium|high]")
):
    if not diff_path.exists():
        raise typer.BadParameter(f"Diff file not found: {diff_path}")
    diff_text = diff_path.read_text(encoding="utf-8", errors="ignore")
    reviewer = Reviewer(repo_root=str(repo or get_repo_root()))
    report = reviewer.review_diff_text(diff_text)

    render_report_table(report, console)

    if output:
        output.write_text(json.dumps(report.model_dump(), indent=2), encoding="utf-8")
        console.print(Panel.fit(f"JSON report written to {output}", title="Output", border_style="green"))
    md = report_to_markdown(report)
    if markdown:
        markdown.write_text(md, encoding="utf-8")
        console.print(Panel.fit(f"Markdown summary written to {markdown}", title="Output", border_style="green"))
    if github_summary:
        summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary_path:
            Path(summary_path).write_text(md, encoding="utf-8")
            console.print(Panel.fit("GitHub Actions job summary written", title="GitHub", border_style="blue"))

    if fail_on_severity:
        if reviewer.should_fail(report, fail_on_severity):
            raise typer.Exit(code=2)

@review_app.command("git")
def review_git(
    base: str = typer.Option(..., "--base", help="Base ref (e.g., origin/main)"),
    head: str = typer.Option("HEAD", "--head", help="Head ref (default HEAD)"),
    repo: Optional[Path] = typer.Option(None, "--repo", help="Path to local git repository"),
    output: Optional[Path] = typer.Option(None, "--output", help="Path to write JSON report"),
    markdown: Optional[Path] = typer.Option(None, "--markdown", help="Path to write Markdown summary"),
    github_summary: bool = typer.Option(False, "--github-summary", help="Also write to GitHub Actions job summary if available"),
    fail_on_severity: Optional[str] = typer.Option(None, "--fail-on-severity", help="Fail (non-zero exit) if any issue >= given severity [low|medium|high]")
):
    repo_root = str(repo or get_repo_root())
    diff_text = get_diff_between_refs(repo_root, base, head)
    reviewer = Reviewer(repo_root=repo_root)
    report = reviewer.review_diff_text(diff_text)

    render_report_table(report, console)

    if output:
        output.write_text(json.dumps(report.model_dump(), indent=2), encoding="utf-8")
        console.print(Panel.fit(f"JSON report written to {output}", title="Output", border_style="green"))
    md = report_to_markdown(report)
    if markdown:
        markdown.write_text(md, encoding="utf-8")
        console.print(Panel.fit(f"Markdown summary written to {markdown}", title="Output", border_style="green"))
    if github_summary:
        summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary_path:
            Path(summary_path).write_text(md, encoding="utf-8")
            console.print(Panel.fit("GitHub Actions job summary written", title="GitHub", border_style="blue"))

    if fail_on_severity:
        if reviewer.should_fail(report, fail_on_severity):
            raise typer.Exit(code=2)

@review_app.command("pr")
def review_pr(
    repo: str = typer.Option(..., "--repo", help="<owner>/<repo>"),
    pr_number: int = typer.Option(..., "--pr", help="Pull request number"),
    token: Optional[str] = typer.Option(None, "--token", help="GitHub token; defaults to GITHUB_TOKEN env"),
    output: Optional[Path] = typer.Option(None, "--output", help="Path to write JSON report"),
    markdown: Optional[Path] = typer.Option(None, "--markdown", help="Path to write Markdown summary"),
    github_summary: bool = typer.Option(False, "--github-summary", help="Also write to GitHub Actions job summary if available"),
    fail_on_severity: Optional[str] = typer.Option(None, "--fail-on-severity", help="Fail (non-zero exit) if any issue >= given severity [low|medium|high]")
):
    gh_token = token or os.environ.get("GITHUB_TOKEN")
    if not gh_token:
        raise typer.BadParameter("GitHub token is required (pass --token or set GITHUB_TOKEN)")
    diff_text = fetch_pr_diff(repo, pr_number, gh_token)
    reviewer = Reviewer(repo_root=None)  # No local repo guaranteed
    report = reviewer.review_diff_text(diff_text)

    render_report_table(report, console)

    if output:
        output.write_text(json.dumps(report.model_dump(), indent=2), encoding="utf-8")
        console.print(Panel.fit(f"JSON report written to {output}", title="Output", border_style="green"))
    md = report_to_markdown(report)
    if markdown:
        markdown.write_text(md, encoding="utf-8")
        console.print(Panel.fit(f"Markdown summary written to {markdown}", title="Output", border_style="green"))
    if github_summary:
        summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary_path:
            Path(summary_path).write_text(md, encoding="utf-8")
            console.print(Panel.fit("GitHub Actions job summary written", title="GitHub", border_style="blue"))

    if fail_on_severity:
        if reviewer.should_fail(report, fail_on_severity):
            raise typer.Exit(code=2)