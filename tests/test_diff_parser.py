import pytest
from app.services.diff_parser import diff_parser_service

SAMPLE_DIFF = """diff --git a/app.py b/app.py
index 83db48f..bf269f4 100644
--- a/app.py
+++ b/app.py
@@ -10,4 +10,5 @@ def get_user(user_id):
-    query = f"SELECT * FROM users WHERE id = '{user_id}'"
+    # Parameterized query
+    query = "SELECT * FROM users WHERE id = %s"
+    cursor.execute(query, (user_id,))
"""

def test_diff_parser_extracts_files():
    file_changes = diff_parser_service.parse(SAMPLE_DIFF)
    assert len(file_changes) == 1
    assert file_changes[0].file_path == "app.py"

def test_diff_parser_extracts_added_lines():
    file_changes = diff_parser_service.parse(SAMPLE_DIFF)
    added = file_changes[0].added_lines
    assert len(added) == 3
    contents = [a["content"] for a in added]
    assert any("SELECT * FROM users" in c for c in contents)
    assert any("cursor.execute" in c for c in contents)

def test_diff_parser_fallback_raw_code():
    raw_code = """
def authenticate_user(username, password):
    if username == "admin":
        return True
    return False
    """
    file_changes = diff_parser_service.parse(raw_code)
    assert len(file_changes) >= 1
    assert len(file_changes[0].added_lines) >= 4
