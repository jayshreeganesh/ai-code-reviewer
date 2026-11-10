import os
import json
import re
from typing import List, Dict, Any, Optional

from app.schemas import (
    InlineSuggestion,
    ReviewSummary,
    CodeReviewResponse,
    ReviewCategory,
    Severity,
    PRVerdict
)
from app.services.diff_parser import FileChange, diff_parser_service
from app.services.security_scanner import security_scanner_service

class AIReviewer:
    """
    Multi-pass code review engine combining deterministic static analysis,
    OWASP security auditing, algorithmic performance heuristics,
    and Gemini 2.0 Flash deep reasoning.
    """

    HEURISTIC_RULES = [
        # Mutable default argument in Python
        {
            "regex": r"def\s+[a-zA-Z0-9_]+\s*\([^)]*?=\s*(?:\[\]|\{\}|set\(\))",
            "category": ReviewCategory.BUG,
            "severity": Severity.WARNING,
            "title": "Mutable Default Argument in Function Definition",
            "desc": "Default parameter values are evaluated once when the function is defined, not each time it is called. Using mutable types ([] or {}) shares state across all calls, causing subtle data leakage bugs.",
            "fix": "def my_func(items: Optional[List] = None):\n    if items is None:\n        items = []"
        },
        # Bare except block catching SystemExit / KeyboardInterrupt
        {
            "regex": r"except\s*:",
            "category": ReviewCategory.BUG,
            "severity": Severity.WARNING,
            "title": "Bare 'except:' Clause Masks Critical Exceptions",
            "desc": "A bare `except:` catches `KeyboardInterrupt` and `SystemExit`, preventing clean process termination and masking programming errors like NameError or TypeError. Catch specific exceptions or `except Exception:`.",
            "fix": "except Exception as e:\n    logger.error(f'Operation failed: {e}')"
        },
        # Silent exception suppression
        {
            "regex": r"except\s+Exception.*:\s*\n\s*pass",
            "category": ReviewCategory.BUG,
            "severity": Severity.WARNING,
            "title": "Silent Exception Suppression (Swallowed Error)",
            "desc": "Silently suppressing exceptions with `except ...: pass` hides database failures, networking errors, and corrupted state, making production outages impossible to debug.",
            "fix": "except Exception as e:\n    logger.warning(f'Suppressed non-fatal warning: {e}')"
        },
        # N+1 Database query pattern inside loops
        {
            "regex": r"for\s+[a-zA-Z0-9_]+\s+in\s+[a-zA-Z0-9_]+:\s*\n\s*.*?(?:\.query|\.filter|\.get|cursor\.execute|db\.)",
            "category": ReviewCategory.PERFORMANCE,
            "severity": Severity.WARNING,
            "title": "Potential N+1 Database Query Anti-Pattern",
            "desc": "Executing individual database queries inside a loop produces N+1 query overhead. Batch the query using SQL `IN (...)` or prefetch related records via ORM joins/select_related.",
            "fix": "# Batch query using IN operator outside the loop\nrecords = db.query(Model).filter(Model.id.in_(ids)).all()"
        },
        # Missing resource management with open()
        {
            "regex": r"=\s*open\s*\([^)]+\)(?!\s*as\b)",
            "category": ReviewCategory.PERFORMANCE,
            "severity": Severity.INFO,
            "title": "File Resource Opened Without Context Manager",
            "desc": "Opening files without a `with` statement risks file descriptor leaks if an unhandled exception occurs before `.close()`. Always use `with open(...) as f:`.",
            "fix": "with open(file_path, 'r', encoding='utf-8') as f:\n    data = f.read()"
        },
        # Console log left in production code
        {
            "regex": r"(?:console\.log|print)\s*\(",
            "category": ReviewCategory.STYLE,
            "severity": Severity.NITPICK,
            "title": "Development Print/Logging Statement in Production",
            "desc": "Direct `print()` or `console.log()` statements pollute standard output and bypass configured log formatters. Use structured logging.",
            "fix": "logger.info('Structured log message')"
        }
    ]

    def _run_heuristic_scan(self, file_changes: List[FileChange]) -> List[InlineSuggestion]:
        findings: List[InlineSuggestion] = []
        for fc in file_changes:
            full_patch = fc.raw_patch

            # Line by line checks
            for added in fc.added_lines:
                line_no = added.get("line_no")
                content = added.get("content", "")

                for rule in self.HEURISTIC_RULES:
                    if re.search(rule["regex"], content):
                        findings.append(InlineSuggestion(
                            file_path=fc.file_path,
                            line_number=line_no,
                            category=rule["category"],
                            severity=rule["severity"],
                            title=rule["title"],
                            description=rule["desc"],
                            original_code=content.strip(),
                            suggested_code=rule["fix"]
                        ))

            # Multi-line pattern checks (like N+1 queries across loops)
            for rule in self.HEURISTIC_RULES:
                matches = list(re.finditer(rule["regex"], full_patch, re.MULTILINE))
                for m in matches:
                    # Avoid duplicate if already caught in line-by-line
                    matched_text = m.group(0).strip()
                    if not any(f.original_code and matched_text in f.original_code for f in findings):
                        findings.append(InlineSuggestion(
                            file_path=fc.file_path,
                            line_number=fc.added_lines[0]["line_no"] if fc.added_lines else 1,
                            category=rule["category"],
                            severity=rule["severity"],
                            title=rule["title"],
                            description=rule["desc"],
                            original_code=matched_text[:80] + ("..." if len(matched_text) > 80 else ""),
                            suggested_code=rule["fix"]
                        ))

        return findings

    async def _run_gemini_analysis(self, diff_text: str, file_changes: List[FileChange]) -> List[InlineSuggestion]:
        """
        Invokes Gemini 2.0 Flash to detect nuanced architectural flaws, logic bugs,
        and generate context-aware inline replacement code blocks.
        """
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            return []

        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=api_key)

            prompt = f"""You are an elite Staff Software Engineer and AppSec Reviewer reviewing a Pull Request.
Analyze the following Git Diff and identify bugs, security vulnerabilities, performance bottlenecks, and architectural flaws.

For every issue found, return a JSON object with:
- file_path: the relative file path
- line_number: integer line number in the new/modified file where the issue resides
- category: one of ["BUG", "SECURITY", "PERFORMANCE", "STYLE", "DOCUMENTATION"]
- severity: one of ["CRITICAL", "WARNING", "INFO", "NITPICK"]
- title: concise one-line headline
- description: clear explanation of the defect and why it matters
- original_code: the specific problematic lines
- suggested_code: the exact replacement code fix ready for a GitHub suggestion block

GIT DIFF:
```diff
{diff_text[:12000]}
```

Respond ONLY with a valid JSON array of objects. Do not include markdown code fences or conversational text."""

            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    response_mime_type="application/json"
                )
            )

            raw_text = response.text.strip()
            data = json.loads(raw_text)

            ai_findings: List[InlineSuggestion] = []
            if isinstance(data, list):
                for item in data:
                    try:
                        ai_findings.append(InlineSuggestion(
                            file_path=item.get("file_path", "unknown"),
                            line_number=item.get("line_number"),
                            category=ReviewCategory(item.get("category", "BUG").upper()),
                            severity=Severity(item.get("severity", "WARNING").upper()),
                            title=item.get("title", "Code Issue Detected"),
                            description=item.get("description", ""),
                            original_code=item.get("original_code"),
                            suggested_code=item.get("suggested_code")
                        ))
                    except Exception:
                        continue
            return ai_findings

        except Exception as e:
            print(f"[AI Reviewer] Gemini API skipped or error: {e}")
            return []

    def calculate_health_and_summary(
        self,
        findings: List[InlineSuggestion],
        total_files: int
    ) -> ReviewSummary:
        """
        Calculates Code Health Score (0-100) and PR Verdict (APPROVE, COMMENT, REQUEST_CHANGES).
        """
        score = 100
        critical_count = sum(1 for f in findings if f.severity == Severity.CRITICAL)
        warning_count = sum(1 for f in findings if f.severity == Severity.WARNING)
        info_count = sum(1 for f in findings if f.severity in (Severity.INFO, Severity.NITPICK))

        score -= (critical_count * 25)
        score -= (warning_count * 8)
        score -= (info_count * 2)
        score = max(0, min(100, score))

        # Determine Verdict
        if critical_count > 0 or score < 65:
            verdict = PRVerdict.REQUEST_CHANGES
            summary_msg = (
                f"🚨 **Changes Requested**: {critical_count} critical security/logic flaw(s) detected. "
                "Immediate resolution required before merging to protect production integrity."
            )
        elif warning_count > 0 or score < 85:
            verdict = PRVerdict.COMMENT
            summary_msg = (
                f"⚠️ **Review Comments**: Code is generally sound but has {warning_count} warning(s) "
                "regarding error handling, performance, or best practices."
            )
        else:
            verdict = PRVerdict.APPROVE
            summary_msg = (
                "✅ **Approved**: Excellent code quality. No security vulnerabilities or critical defects identified. "
                "Ready for merge."
            )

        return ReviewSummary(
            health_score=score,
            verdict=verdict,
            summary=summary_msg,
            total_files_analyzed=total_files,
            total_issues_found=len(findings),
            critical_count=critical_count,
            warning_count=warning_count,
            info_count=info_count
        )

    async def review_diff(self, diff_text: str, enable_security: bool = True) -> CodeReviewResponse:
        import time
        start_time = time.perf_counter()

        # Step 1: Parse diff
        file_changes = diff_parser_service.parse(diff_text)
        files_changed = [fc.file_path for fc in file_changes]

        # Step 2: Deterministic Static Scans
        all_findings: List[InlineSuggestion] = []

        if enable_security:
            sec_findings = security_scanner_service.scan_diff(file_changes)
            all_findings.extend(sec_findings)

        heuristic_findings = self._run_heuristic_scan(file_changes)
        all_findings.extend(heuristic_findings)

        # Step 3: LLM Deep Reasoning (if API key available)
        llm_findings = await self._run_gemini_analysis(diff_text, file_changes)
        if llm_findings:
            # Deduplicate similar findings by line and category
            for lf in llm_findings:
                is_duplicate = any(
                    f.file_path == lf.file_path and f.line_number == lf.line_number and f.category == lf.category
                    for f in all_findings
                )
                if not is_duplicate:
                    all_findings.append(lf)

        # Step 4: Health scoring and verdict
        summary = self.calculate_health_and_summary(all_findings, len(files_changed))
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return CodeReviewResponse(
            summary=summary,
            findings=all_findings,
            files_changed=files_changed,
            processing_time_ms=duration_ms
        )

ai_reviewer_service = AIReviewer()
