from typing import List, Optional
from pydantic import BaseModel, Field


class ReviewComment(BaseModel):
    file_path: str
    line_number: Optional[int] = None
    severity: str = Field(..., pattern="^(critical|warning|info|style)$")
    category: str
    message: str
    suggestion: Optional[str] = None


class ReviewSummary(BaseModel):
    total_files_reviewed: int
    total_issues_found: int
    critical_issues: int
    warnings: int
    info_items: int
    style_issues: int
    overall_assessment: str


class ReviewResult(BaseModel):
    run_id: str
    status: str
    summary: Optional[ReviewSummary] = None
    comments: List[ReviewComment] = []
    processing_time_seconds: Optional[float] = None


class PRReviewRequest(BaseModel):
    repo_owner: str
    repo_name: str
    pr_number: int


class DiffReviewRequest(BaseModel):
    diff_content: str
    repo_context: Optional[str] = None
