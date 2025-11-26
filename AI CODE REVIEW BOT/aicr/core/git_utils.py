import subprocess
from typing import Optional
import requests
from pathlib import Path


def get_repo_root() -> Optional[str]:
    try:
        out = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], stderr=subprocess.STDOUT)
        return out.decode().strip()
    except Exception:
        return None


def get_diff_between_refs(repo_root: str, base: str, head: str) -> str:
    cmd = ["git", "-C", repo_root, "diff", f"{base}..{head}"]
    out = subprocess.check_output(cmd)
    return out.decode("utf-8", errors="ignore")


def fetch_pr_diff(repo: str, pr_number: int, token: str) -> str:
    owner_repo = repo
    url = f"https://api.github.com/repos/{owner_repo}/pulls/{pr_number}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3.diff",
        "User-Agent": "aicr-bot",
    }
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    return r.text