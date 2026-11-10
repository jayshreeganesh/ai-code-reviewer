import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.github_service import github_service
from app.services.ai_reviewer import ai_reviewer_service
from app.schemas import Severity, PRVerdict

client = TestClient(app)

VULNERABLE_DIFF = """diff --git a/services/auth.py b/services/auth.py
index 1111111..2222222 100644
--- a/services/auth.py
+++ b/services/auth.py
@@ -5,6 +5,9 @@ def authenticate_and_log(user_id):
+    AWS_KEY = "AKIA1234567890ABCDEF"
+    query = f"SELECT * FROM secrets WHERE id = '{user_id}'"
+    cursor.execute(query)
+    eval(user_id)
"""

CLEAN_DIFF = """diff --git a/utils/math.py b/utils/math.py
index 3333333..4444444 100644
--- a/utils/math.py
+++ b/utils/math.py
@@ -10,3 +10,5 @@ def add(a: int, b: int) -> int:
+    \"\"\"Calculates sum of two integers.\"\"\"
+    return a + b
"""

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert len(data["analyzers"]) >= 3

@pytest.mark.asyncio
async def test_reviewer_catches_critical_vulnerabilities():
    res = await ai_reviewer_service.review_diff(VULNERABLE_DIFF)
    assert res.summary.critical_count >= 2
    assert res.summary.verdict == PRVerdict.REQUEST_CHANGES
    assert res.summary.health_score < 60

    titles = [f.title for f in res.findings]
    assert any("AWS" in t for t in titles)
    assert any("SQL Injection" in t for t in titles)
    assert any("eval" in t for t in titles)

@pytest.mark.asyncio
async def test_reviewer_approves_clean_diff():
    res = await ai_reviewer_service.review_diff(CLEAN_DIFF)
    assert res.summary.critical_count == 0
    assert res.summary.verdict == PRVerdict.APPROVE
    assert res.summary.health_score >= 90

def test_api_review_diff_endpoint():
    response = client.post("/api/v1/review/diff", json={
        "diff": VULNERABLE_DIFF,
        "enable_security_scan": True
    })
    assert response.status_code == 200
    data = response.json()
    assert data["summary"]["verdict"] == "REQUEST_CHANGES"
    assert len(data["findings"]) >= 2
    assert "services/auth.py" in data["files_changed"]

def test_api_validation_too_short():
    response = client.post("/api/v1/review/diff", json={"diff": "short"})
    assert response.status_code == 422

def test_github_url_parser():
    owner, repo, pr_no = github_service.parse_pr_url("https://github.com/fastapi/fastapi/pull/10500")
    assert owner == "fastapi"
    assert repo == "fastapi"
    assert pr_no == 10500

def test_github_url_parser_invalid():
    with pytest.raises(ValueError):
        github_service.parse_pr_url("https://invalid-url.com/something")
