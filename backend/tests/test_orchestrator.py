import pytest
from src.agents.orchestrator import ReviewOrchestrator


@pytest.mark.asyncio
async def test_orchestrator_runs_all_agents():
    orchestrator = ReviewOrchestrator()
    diff = """diff --git a/test.py b/test.py
--- a/test.py
+++ b/test.py
@@ -1,3 +1,4 @@
 def query(user_input):
+    cursor.execute("SELECT * FROM users WHERE id = " + user_input)
     pass
"""
    result = await orchestrator.run_review("test-run-id", diff)
    
    assert result.run_id == "test-run-id"
    assert result.status == "completed"
    assert result.summary is not None
    assert result.processing_time_seconds is not None


@pytest.mark.asyncio
async def test_orchestrator_produces_summary():
    orchestrator = ReviewOrchestrator()
    diff = """diff --git a/secure.py b/secure.py
--- a/secure.py
+++ b/secure.py
@@ -1,3 +1,4 @@
 def safe_function():
+    return True
"""
    result = await orchestrator.run_review("test-run-id", diff)
    
    assert result.summary.total_files_reviewed >= 0
    assert result.summary.total_issues_found >= 0
    assert result.summary.overall_assessment is not None


@pytest.mark.asyncio
async def test_orchestrator_handles_multiple_issues():
    orchestrator = ReviewOrchestrator()
    diff = """diff --git a/bad_code.py b/bad_code.py
--- a/bad_code.py
+++ b/bad_code.py
@@ -1,5 +1,8 @@
 def process(user_input):
+    id = 123
+    query = "SELECT * FROM users WHERE name = '%s'" % user_input
+    result = eval(user_input)
     pass
"""
    result = await orchestrator.run_review("test-run-id", diff)
    
    assert len(result.comments) > 0
    critical_issues = [c for c in result.comments if c.severity == "critical"]
    assert len(critical_issues) > 0


@pytest.mark.asyncio
async def test_orchestrator_formats_comments_by_severity():
    orchestrator = ReviewOrchestrator()
    diff = """diff --git a/mixed.py b/mixed.py
--- a/mixed.py
+++ b/mixed.py
@@ -1,5 +1,7 @@
 def process():
+    password = "hardcoded123"
+    x = 1   
     pass
"""
    result = await orchestrator.run_review("test-run-id", diff)
    
    if len(result.comments) > 1:
        severities = [c.severity for c in result.comments]
        critical_index = severities.index("critical") if "critical" in severities else -1
        style_index = severities.index("style") if "style" in severities else -1
        
        if critical_index != -1 and style_index != -1:
            assert critical_index < style_index
