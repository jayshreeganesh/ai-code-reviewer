from typing import List, Dict, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field

class ReviewCategory(str, Enum):
    BUG = "BUG"
    SECURITY = "SECURITY"
    PERFORMANCE = "PERFORMANCE"
    STYLE = "STYLE"
    DOCUMENTATION = "DOCUMENTATION"

class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"
    NITPICK = "NITPICK"

class PRVerdict(str, Enum):
    APPROVE = "APPROVE"
    COMMENT = "COMMENT"
    REQUEST_CHANGES = "REQUEST_CHANGES"

class InlineSuggestion(BaseModel):
    file_path: str = Field(..., description="Path to the file under review")
    line_number: Optional[int] = Field(None, description="Line number in the new/modified file")
    category: ReviewCategory = Field(..., description="Category of the finding")
    severity: Severity = Field(..., description="Severity level of the issue")
    title: str = Field(..., description="Brief one-line issue summary")
    description: str = Field(..., description="Detailed explanation of the flaw, bug, or vulnerability")
    original_code: Optional[str] = Field(None, description="Original problematic code snippet")
    suggested_code: Optional[str] = Field(None, description="Direct replacement code fix (GitHub suggestion compatible)")

class ReviewSummary(BaseModel):
    health_score: int = Field(..., ge=0, le=100, description="Overall Code Health Score (0 to 100)")
    verdict: PRVerdict = Field(..., description="Review outcome: APPROVE, COMMENT, or REQUEST_CHANGES")
    summary: str = Field(..., description="High-level executive overview of the changes and risks")
    total_files_analyzed: int
    total_issues_found: int
    critical_count: int
    warning_count: int
    info_count: int

class CodeReviewResponse(BaseModel):
    summary: ReviewSummary
    findings: List[InlineSuggestion]
    files_changed: List[str]
    processing_time_ms: float

class DiffReviewRequest(BaseModel):
    diff: str = Field(
        ...,
        min_length=10,
        description="Unified git diff or code patch to analyze.",
        examples=["""diff --git a/app.py b/app.py
index 83db48f..bf269f4 100644
--- a/app.py
+++ b/app.py
@@ -10,3 +10,4 @@ def get_user(user_id):
-    query = f"SELECT * FROM users WHERE id = '{user_id}'"
+    query = "SELECT * FROM users WHERE id = %s"
"""]
    )
    repository: Optional[str] = Field(None, description="Optional GitHub repo name (e.g. 'owner/repo')")
    pr_number: Optional[int] = Field(None, description="Optional Pull Request number")
    enable_security_scan: bool = Field(default=True, description="Enable static OWASP & secrets vulnerability checks")
    strictness: str = Field(default="balanced", description="Review strictness: 'permissive', 'balanced', or 'strict'")

class GitHubPRReviewRequest(BaseModel):
    pr_url: str = Field(
        ...,
        description="Public or private GitHub Pull Request URL.",
        examples=["https://github.com/fastapi/fastapi/pull/10000"]
    )
    github_token: Optional[str] = Field(None, description="Optional GitHub Personal Access Token for private repos or posting")
    post_comments: bool = Field(default=False, description="Whether to submit inline review comments back to GitHub PR")

class HealthResponse(BaseModel):
    status: str
    version: str
    llm_enabled: bool
    analyzers: List[str]
