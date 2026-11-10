import re
from typing import Dict, Any, Optional, Tuple, List
import httpx
from app.schemas import CodeReviewResponse, InlineSuggestion, PRVerdict

class GitHubService:
    """
    Interacts with GitHub REST API to fetch PR diffs, extract metadata,
    and post structured inline code reviews.
    """

    def parse_pr_url(self, pr_url: str) -> Tuple[str, str, int]:
        """
        Parses a URL like https://github.com/owner/repo/pull/123 into (owner, repo, pr_number).
        """
        match = re.search(r"github\.com/([^/]+)/([^/]+)/pull/(\d+)", pr_url)
        if not match:
            raise ValueError(f"Invalid GitHub PR URL format: {pr_url}. Expected https://github.com/owner/repo/pull/123")
        return match.group(1), match.group(2), int(match.group(3))

    async def fetch_pr_diff(self, owner: str, repo: str, pull_number: int, token: Optional[str] = None) -> str:
        """
        Fetches the unified git diff of a GitHub Pull Request.
        """
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}"
        headers = {
            "Accept": "application/vnd.github.v3.diff",
            "User-Agent": "AI-Code-Reviewer-Bot/1.0"
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"

        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.get(url, headers=headers)
            if res.status_code == 404:
                raise ValueError(f"Pull Request not found on GitHub: {owner}/{repo}#{pull_number}. If private, provide a GitHub Token.")
            elif res.status_code == 403:
                raise ValueError("GitHub API rate limit exceeded. Please provide a GitHub Personal Access Token.")
            res.raise_for_status()
            return res.text

    async def post_review_to_pr(
        self,
        owner: str,
        repo: str,
        pull_number: int,
        review_result: CodeReviewResponse,
        token: str
    ) -> Dict[str, Any]:
        """
        Posts review comments and verdict back to the GitHub Pull Request.
        """
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/reviews"
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "AI-Code-Reviewer-Bot/1.0"
        }

        # Build Markdown summary body
        s = review_result.summary
        score_emoji = "🟢" if s.health_score >= 85 else ("🟡" if s.health_score >= 65 else "🔴")
        verdict_event = "APPROVE" if s.verdict == PRVerdict.APPROVE else ("REQUEST_CHANGES" if s.verdict == PRVerdict.REQUEST_CHANGES else "COMMENT")

        body = f"""## 🤖 AI Code Review Summary

**Code Health Score:** {score_emoji} **{s.health_score} / 100**
**Verdict:** `{s.verdict.value}`

{s.summary}

### 📊 Review Metrics
- **Files Analyzed:** {s.total_files_analyzed}
- **Total Issues Found:** {s.total_issues_found} (🚨 {s.critical_count} Critical, ⚠️ {s.warning_count} Warnings, ℹ️ {s.info_count} Info)
- **Processing Time:** {review_result.processing_time_ms} ms

---
*Reviewed autonomously by [AI Code Reviewer Bot](https://github.com/jayshreeganesh/ai-code-reviewer).*
"""

        # Format inline comments
        comments_payload: List[Dict[str, Any]] = []
        for finding in review_result.findings:
            if finding.line_number and finding.file_path:
                comment_text = f"### [{finding.severity.value}] {finding.title}\n\n{finding.description}\n"
                if finding.suggested_code:
                    comment_text += f"\n```suggestion\n{finding.suggested_code}\n```"

                comments_payload.append({
                    "path": finding.file_path,
                    "line": finding.line_number,
                    "side": "RIGHT",
                    "body": comment_text
                })

        payload = {
            "body": body,
            "event": verdict_event,
            "comments": comments_payload[:25]  # Limit to 25 inline comments to respect GitHub payload size
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            res = await client.post(url, headers=headers, json=payload)
            res.raise_for_status()
            return res.json()

github_service = GitHubService()
