from pathlib import Path
from typing import Optional, List

from .diff_parser import parse_diff_text
from .review_models import ReviewReport, ReviewItem, Severity, Category
from .analyzers import run_pylint, run_bandit, run_radon
from .llm import llm_review

class Reviewer:
    def __init__(self, repo_root: Optional[str]):
        self.repo_root = repo_root

    def review_diff_text(self, diff_text: str) -> ReviewReport:
        changed_files = parse_diff_text(diff_text)
        report = ReviewReport(items=[])

        # Static analyzers on changed files
        file_paths: List[Path] = []
        for cf in changed_files:
            p = Path(cf.path)
            if self.repo_root and not p.is_absolute():
                p = Path(self.repo_root) / p
            if p.exists():
                file_paths.append(p)

        report.items.extend(run_pylint(file_paths))
        report.items.extend(run_bandit(file_paths))
        report.items.extend(run_radon(file_paths))

        # LLM analysis
        llm_items = llm_review(diff_text)
        report.items.extend(llm_items)

        report.compute_summary()
        return report

    def should_fail(self, report: ReviewReport, fail_on_severity: str) -> bool:
        sev = Severity(fail_on_severity)
        ranks = {Severity.low: 1, Severity.medium: 2, Severity.high: 3}
        threshold = ranks[sev]
        return any(ranks[it.severity] >= threshold for it in report.items)