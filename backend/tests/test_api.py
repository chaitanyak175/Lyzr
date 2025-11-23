import pytest
from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "PR Review Agent"
    assert "endpoints" in data


def test_health_check(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_review_diff_endpoint_creates_review(client: TestClient):
    diff_content = """diff --git a/test.py b/test.py
--- a/test.py
+++ b/test.py
@@ -1,3 +1,4 @@
 def hello():
+    print('world')
     pass
"""
    response = client.post(
        "/review/diff",
        json={"diff_content": diff_content}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "run_id" in data
    assert data["status"] == "pending"


def test_review_pr_endpoint_creates_review(client: TestClient):
    response = client.post(
        "/review/pr",
        json={
            "repo_owner": "testuser",
            "repo_name": "testrepo",
            "pr_number": 123
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "run_id" in data
    assert data["status"] == "pending"


def test_get_review_returns_404_for_nonexistent(client: TestClient):
    response = client.get("/review/nonexistent-id")
    assert response.status_code == 404


def test_get_review_returns_pending_status(client: TestClient):
    create_response = client.post(
        "/review/diff",
        json={"diff_content": "diff --git a/test.py b/test.py"}
    )
    run_id = create_response.json()["run_id"]
    
    response = client.get(f"/review/{run_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["run_id"] == run_id
    assert data["status"] in ["pending", "processing"]
