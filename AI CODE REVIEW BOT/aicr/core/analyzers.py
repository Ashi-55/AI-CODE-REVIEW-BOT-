import subprocess
from pathlib import Path
from typing import List

from .review_models import ReviewItem, Severity, Category


def run_pylint(files: List[Path]) -> List[ReviewItem]:
    items: List[ReviewItem] = []
    if not files:
        return items
    try:
        cmd = ["pylint", "--output-format=json"] + [str(f) for f in files]
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        import json
        data = json.loads(out.decode("utf-8", errors="ignore"))
        for d in data:
            sev_map = {"convention": Severity.low, "refactor": Severity.low, "warning": Severity.medium, "error": Severity.high, "fatal": Severity.high}
            items.append(
                ReviewItem(
                    category=Category.style,
                    title=d.get("message", "pylint issue"),
                    description=f"{d.get('symbol')} ({d.get('message-id')})",
                    suggestion=f"{d.get('message')}",
                    severity=sev_map.get(d.get("type"), Severity.medium),
                    file=d.get("path"),
                    start_line=d.get("line"),
                    end_line=d.get("line"),
                    tool="pylint",
                )
            )
    except Exception:
        pass
    return items


def run_bandit(files: List[Path]) -> List[ReviewItem]:
    items: List[ReviewItem] = []
    py_files = [str(f) for f in files if f.suffix == ".py"]
    if not py_files:
        return items
    try:
        cmd = ["bandit", "-f", "json"] + ["-r"] + py_files
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        import json
        data = json.loads(out.decode("utf-8", errors="ignore"))
        for r in data.get("results", []):
            sev_map = {"LOW": Severity.low, "MEDIUM": Severity.medium, "HIGH": Severity.high}
            items.append(
                ReviewItem(
                    category=Category.security,
                    title=r.get("issue_text", "bandit issue"),
                    description=r.get("issue_text", ""),
                    suggestion=r.get("remediation", None),
                    severity=sev_map.get(r.get("issue_severity"), Severity.medium),
                    file=r.get("filename"),
                    start_line=r.get("line_number"),
                    end_line=r.get("line_number"),
                    tool="bandit",
                )
            )
    except Exception:
        pass
    return items


def run_radon(files: List[Path]) -> List[ReviewItem]:
    items: List[ReviewItem] = []
    py_files = [str(f) for f in files if f.suffix == ".py"]
    if not py_files:
        return items
    try:
        cmd = ["radon", "cc", "-j"] + py_files
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        import json
        data = json.loads(out.decode("utf-8", errors="ignore"))
        for filename, entries in data.items():
            for e in entries:
                grade = e.get("rank", "C")
                sev = Severity.low if grade in ("A", "B") else Severity.medium if grade == "C" else Severity.high
                items.append(
                    ReviewItem(
                        category=Category.smell,
                        title=f"Complexity rank {grade}",
                        description=f"Function {e.get('name')} has CC {e.get('complexity')}",
                        suggestion="Refactor to reduce complexity (split function, simplify logic)",
                        severity=sev,
                        file=filename,
                        start_line=e.get("lineno"),
                        end_line=e.get("endline"),
                        tool="radon",
                    )
                )
    except Exception:
        pass
    return items