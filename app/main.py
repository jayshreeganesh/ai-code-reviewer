import os
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app import __version__
from app.schemas import (
    DiffReviewRequest,
    GitHubPRReviewRequest,
    CodeReviewResponse,
    HealthResponse
)
from app.services.ai_reviewer import ai_reviewer_service
from app.services.github_service import github_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"[CodeReviewer] Initializing AI Code Review Bot v{__version__}...")
    llm_active = bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))
    print(f"[CodeReviewer] Engine ready. Gemini LLM enabled: {llm_active}.")
    yield
    print("[CodeReviewer] Shutting down AI Code Review Bot.")

app = FastAPI(
    title="AI Code Review Bot API",
    description=(
        "Autonomous Pull Request Reviewer & DevSecOps Auditing Microservice. "
        "Evaluates Git diffs, catches logic bugs, scans for OWASP vulnerabilities & hardcoded secrets, "
        "generates inline GitHub code suggestions, and computes code health scores."
    ),
    version=__version__,
    lifespan=lifespan
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", summary="Interactive Web Playground", include_in_schema=False)
async def serve_playground():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "AI Code Review Bot API is running. Visit /docs for OpenAPI documentation."}

@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Health & System Capabilities"
)
async def health_check():
    llm_active = bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))
    return HealthResponse(
        status="healthy",
        version=__version__,
        llm_enabled=llm_active,
        analyzers=[
            "OWASP Top 10 Security & Secrets Scanner",
            "Heuristic Bug & Logic Flaw Detector",
            "Performance & Resource Leak Analyzer",
            "Gemini 2.0 Flash Deep Architectural Reviewer"
        ]
    )

@app.post(
    "/api/v1/review/diff",
    response_model=CodeReviewResponse,
    tags=["Code Review"],
    summary="Review Raw Git Diff or Unified Patch"
)
async def review_diff(payload: DiffReviewRequest):
    try:
        result = await ai_reviewer_service.review_diff(
            diff_text=payload.diff,
            enable_security=payload.enable_security_scan
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Diff review failed: {str(e)}"
        )

@app.post(
    "/api/v1/review/pr",
    response_model=CodeReviewResponse,
    tags=["Code Review"],
    summary="Fetch & Review GitHub Pull Request by URL"
)
async def review_github_pr(payload: GitHubPRReviewRequest):
    try:
        # Step 1: Parse PR URL
        owner, repo, pr_number = github_service.parse_pr_url(payload.pr_url)

        # Step 2: Fetch PR diff
        diff_text = await github_service.fetch_pr_diff(
            owner=owner,
            repo=repo,
            pull_number=pr_number,
            token=payload.github_token
        )

        if not diff_text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Pull Request {owner}/{repo}#{pr_number} contains no diff changes."
            )

        # Step 3: Run review
        review_result = await ai_reviewer_service.review_diff(diff_text=diff_text)

        # Step 4: Optionally submit comments back to GitHub PR
        if payload.post_comments and payload.github_token:
            await github_service.post_review_to_pr(
                owner=owner,
                repo=repo,
                pull_number=pr_number,
                review_result=review_result,
                token=payload.github_token
            )

        return review_result

    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PR review failed: {str(e)}"
        )

@app.post(
    "/api/v1/webhook",
    tags=["Automation & Webhooks"],
    summary="GitHub Pull Request Webhook Handler"
)
async def github_webhook(request: Request):
    """
    Automated webhook handler for GitHub App or Repository Webhooks.
    Triggers code reviews on pull_request 'opened' and 'synchronize' events.
    """
    event = request.headers.get("X-GitHub-Event")
    if event != "pull_request":
        return {"status": "ignored", "reason": f"Event '{event}' is not a pull_request event"}

    payload = await request.json()
    action = payload.get("action")

    if action not in ["opened", "synchronize", "reopened"]:
        return {"status": "ignored", "reason": f"Action '{action}' does not require review"}

    pr = payload.get("pull_request", {})
    pr_url = pr.get("html_url")
    if not pr_url:
        return {"status": "error", "message": "Missing pull_request.html_url"}

    # Run review in background
    token = os.environ.get("GITHUB_TOKEN")
    try:
        owner, repo, pr_number = github_service.parse_pr_url(pr_url)
        diff_text = await github_service.fetch_pr_diff(owner, repo, pr_number, token)
        review = await ai_reviewer_service.review_diff(diff_text)

        if token:
            await github_service.post_review_to_pr(owner, repo, pr_number, review, token)

        return {
            "status": "success",
            "pr": f"{owner}/{repo}#{pr_number}",
            "health_score": review.summary.health_score,
            "verdict": review.summary.verdict.value,
            "findings_count": len(review.findings)
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}
