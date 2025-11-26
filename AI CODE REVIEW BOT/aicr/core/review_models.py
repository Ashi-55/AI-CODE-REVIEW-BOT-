from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class Category(str, Enum):
    bug = "bug"
    security = "security"
    performance = "performance"
    smell = "smell"
    style = "style"

class Severity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class ReviewItem(BaseModel):
    category: Category
    title: str
    description: str
    suggestion: Optional[str] = None
    severity: Severity = Severity.medium
    file: Optional[str] = None
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    tool: Optional[str] = None

class ReviewReport(BaseModel):
    items: List[ReviewItem] = Field(default_factory=list)
    summary: dict = Field(default_factory=dict)

    def add(self, item: ReviewItem):
        self.items.append(item)

    def compute_summary(self):
        by_category = {}
        by_severity = {}
        for it in self.items:
            by_category[it.category] = by_category.get(it.category, 0) + 1
            by_severity[it.severity] = by_severity.get(it.severity, 0) + 1
        self.summary = {"by_category": by_category, "by_severity": by_severity, "total": len(self.items)}
        return self.summary