from typing import List, Optional
from unidiff import PatchSet

class ChangedFile:
    def __init__(self, path: str):
        self.path = path
        self.added_lines = []  # List[tuple[int, str]]
        self.removed_lines = []  # List[tuple[int, str]]
        self.hunks = []  # List[dict]

    def to_dict(self):
        return {
            "path": self.path,
            "added_lines": self.added_lines,
            "removed_lines": self.removed_lines,
            "hunks": self.hunks,
        }


def parse_diff_text(diff_text: str) -> List[ChangedFile]:
    ps = PatchSet(diff_text)
    changed: List[ChangedFile] = []
    for patched_file in ps:
        cf = ChangedFile(path=patched_file.path or patched_file.target_file)
        for h in patched_file:
            hunk_info = {
                "source_start": h.source_start,
                "source_length": h.source_length,
                "target_start": h.target_start,
                "target_length": h.target_length,
            }
            cf.hunks.append(hunk_info)
            for l in h:
                if l.is_added:
                    cf.added_lines.append((l.target_line_no, l.value.rstrip("\n")))
                elif l.is_removed:
                    cf.removed_lines.append((l.source_line_no, l.value.rstrip("\n")))
        changed.append(cf)
    return changed


def summarize_diff(diff_text: str, max_chars: int = 15000) -> str:
    """Return a truncated diff for LLM prompts."""
    if len(diff_text) <= max_chars:
        return diff_text
    head = diff_text[: max_chars // 2]
    tail = diff_text[-max_chars // 2 :]
    return head + "\n...\n" + tail