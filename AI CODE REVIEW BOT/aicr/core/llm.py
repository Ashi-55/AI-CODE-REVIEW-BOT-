import os
from typing import List, Optional
from openai import OpenAI

from .review_models import ReviewItem, ReviewReport, Category, Severity
from .diff_parser import summarize_diff

SYSTEM_PROMPT = (
    "You are a senior software architect and code reviewer. "
    "Given a git diff, produce a structured review focusing on bugs, security vulnerabilities, performance issues, code smells, and style violations. "
    "Return JSON with a list of items, each with: category, title, description, suggestion, severity, file, start_line, end_line."
)

MODEL = os.environ.get("AICR_MODEL", "gpt-4o-mini")


def _client() -> OpenAI:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is required")
    return OpenAI(api_key=api_key)


def llm_review(diff_text: str) -> List[ReviewItem]:
    # Gracefully skip if no API key is configured
    if not os.environ.get("OPENAI_API_KEY"):
        return []
    client = _client()
    prompt = SYSTEM_PROMPT + "\n\nDiff:\n" + summarize_diff(diff_text)
    resp = client.responses.create(
        model=MODEL,
        input=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
    )
    try:
        content_text = resp.output_text
    except Exception:
        content_text = "[]"

    import json
    items: List[ReviewItem] = []
    try:
        parsed = json.loads(content_text)
        for d in parsed:
            items.append(
                ReviewItem(
                    category=Category(d.get("category", "smell")),
                    title=d.get("title", "Issue"),
                    description=d.get("description", ""),
                    suggestion=d.get("suggestion"),
                    severity=Severity(d.get("severity", "medium")),
                    file=d.get("file"),
                    start_line=d.get("start_line"),
                    end_line=d.get("end_line"),
                    tool="llm",
                )
            )
    except Exception:
        # If the model returns markdown, try to coerce (fallback)
        items.append(
            ReviewItem(
                category=Category.smell,
                title="LLM response parsing error",
                description="Could not parse model output as JSON",
                severity=Severity.low,
                tool="llm",
            )
        )
    return items