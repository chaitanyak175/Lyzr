# Usage Guide

Complete guide for using the PR Review Agent in various scenarios.

## Table of Contents
- [Quick Start](#quick-start)
- [API Usage](#api-usage)
- [Example Scenarios](#example-scenarios)
- [Integration Patterns](#integration-patterns)
- [Troubleshooting](#troubleshooting)

## Quick Start

### 1. Setup and Run

```bash
cd backend
cp .env.example .env
# Edit .env with your GITHUB_TOKEN
docker-compose up -d
```

### 2. Verify Installation

```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy"}
```

### 3. Submit Your First Review

```bash
curl -X POST http://localhost:8000/review/diff \
  -H "Content-Type: application/json" \
  -d '{
    "diff_content": "diff --git a/test.py b/test.py\n--- a/test.py\n+++ b/test.py\n@@ -1,3 +1,4 @@\n def hello():\n+    id = 123\n     pass"
  }'
```

### 4. Check Results

```bash
# Use run_id from previous response
curl http://localhost:8000/review/{run_id}
```

## API Usage

### Review a GitHub Pull Request

**Endpoint**: `POST /review/pr`

**Request**:
```json
{
  "repo_owner": "facebook",
  "repo_name": "react",
  "pr_number": 12345
}
```

**Response**:
```json
{
  "run_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "Review started. Use GET /review/{run_id} to check progress."
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/review/pr \
  -H "Content-Type: application/json" \
  -d '{
    "repo_owner": "octocat",
    "repo_name": "Hello-World",
    "pr_number": 1
  }'
```

### Review a Diff Directly

**Endpoint**: `POST /review/diff`

**Request**:
```json
{
  "diff_content": "diff --git a/app.py b/app.py\n...",
  "repo_context": "optional-context-info"
}
```

**Response**: Same as PR review

**Example**:
```bash
curl -X POST http://localhost:8000/review/diff \
  -H "Content-Type: application/json" \
  -d @examples/sql_injection.diff
```

### Get Review Results

**Endpoint**: `GET /review/{run_id}`

**Response (Pending)**:
```json
{
  "run_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "comments": []
}
```

**Response (Completed)**:
```json
{
  "run_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "summary": {
    "total_files_reviewed": 3,
    "total_issues_found": 7,
    "critical_issues": 2,
    "warnings": 3,
    "info_items": 1,
    "style_issues": 1,
    "overall_assessment": "CRITICAL: 2 critical security issues must be addressed"
  },
  "comments": [
    {
      "file_path": "app/database.py",
      "line_number": 45,
      "severity": "critical",
      "category": "security",
      "message": "Potential SQL injection vulnerability detected",
      "suggestion": "Use parameterized queries or ORM methods"
    }
  ],
  "processing_time_seconds": 2.34
}
```

## Example Scenarios

### Scenario 1: SQL Injection Detection

**Input** (`examples/sql_injection.diff`):
```python
# Added lines in diff:
query = "SELECT * FROM users WHERE name = '%s'" % username
cursor.execute(query)
```

**Expected Output**:
- **Severity**: critical
- **Category**: security
- **Message**: Potential SQL injection vulnerability detected
- **Suggestion**: Use parameterized queries or ORM methods

**Test It**:
```bash
curl -X POST http://localhost:8000/review/diff \
  -H "Content-Type: application/json" \
  --data-binary @examples/sql_injection.diff
```

### Scenario 2: Variable Shadowing

**Input** (`examples/naming_shadowing.diff`):
```python
# Added lines:
list = []
dict = {}
id = 0
type = item.get('category')
```

**Expected Output**:
- **Severity**: warning
- **Category**: naming
- **Message**: Variable name shadows a built-in
- **Suggestion**: Consider renaming to avoid shadowing

**Test It**:
```bash
curl -X POST http://localhost:8000/review/diff \
  -H "Content-Type: application/json" \
  --data-binary @examples/naming_shadowing.diff
```

### Scenario 3: Performance Issues

**Input** (`examples/performance_issues.diff`):
```python
# Nested loops:
for i in range(len(items)):
    for j in range(len(items)):
        if items[i] == items[j]:
            duplicates.append(items[i])

# String concatenation in loop:
while i < len(data):
    report += str(data[i])
    i += 1
```

**Expected Output**:
- **Severity**: warning
- **Category**: performance
- **Message**: Nested loop detected - potential O(n²) complexity
- **Suggestion**: Consider using list comprehensions or more efficient algorithms

### Scenario 4: Style Violations

**Input** (`examples/style_violations.diff`):
```python
# Added lines:
def ProcessUser(user):   # Trailing whitespace
    userName = user.name  # camelCase instead of snake_case
    result = {"name": userName, 'email': email}  # Mixed quotes

class userHandler:  # lowercase class name
    def AddUser(self):  # PascalCase for method
        pass
```

**Expected Output**:
- Multiple style issues detected
- Trailing whitespace warnings
- Naming convention violations

### Scenario 5: Binary Files

**Input** (`examples/binary_files.diff`):
```
Binary files a/logo.png and b/logo.png differ
```

**Expected Output**:
- Binary files skipped
- Only code changes reviewed
- No false positives on binary data

## Integration Patterns

### CI/CD Integration (GitHub Actions)

Create `.github/workflows/pr-review.yml`:

```yaml
name: Automated PR Review

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - name: Review PR
        run: |
          RESPONSE=$(curl -X POST https://your-api.com/review/pr \
            -H "Content-Type: application/json" \
            -d "{
              \"repo_owner\": \"${{ github.repository_owner }}\",
              \"repo_name\": \"${{ github.event.repository.name }}\",
              \"pr_number\": ${{ github.event.pull_request.number }}
            }")
          
          RUN_ID=$(echo $RESPONSE | jq -r '.run_id')
          
          # Poll for results
          for i in {1..30}; do
            RESULT=$(curl https://your-api.com/review/$RUN_ID)
            STATUS=$(echo $RESULT | jq -r '.status')
            
            if [ "$STATUS" = "completed" ]; then
              echo "Review completed"
              echo $RESULT | jq '.summary'
              break
            fi
            
            sleep 2
          done
```

### Pre-commit Hook

Create `.git/hooks/pre-push`:

```bash
#!/bin/bash

DIFF=$(git diff origin/main...HEAD)

RESPONSE=$(curl -X POST http://localhost:8000/review/diff \
  -H "Content-Type: application/json" \
  -d "{\"diff_content\": $(echo $DIFF | jq -Rs .)}")

RUN_ID=$(echo $RESPONSE | jq -r '.run_id')

sleep 3

RESULT=$(curl http://localhost:8000/review/$RUN_ID)
CRITICAL=$(echo $RESULT | jq -r '.summary.critical_issues')

if [ "$CRITICAL" -gt 0 ]; then
  echo "❌ Critical issues found! Review required."
  echo $RESULT | jq '.comments[] | select(.severity=="critical")'
  exit 1
fi

echo "✅ No critical issues found"
```

### Python SDK Example

```python
import requests
import time

class PRReviewClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def review_pr(self, owner, repo, pr_number):
        response = requests.post(
            f"{self.base_url}/review/pr",
            json={
                "repo_owner": owner,
                "repo_name": repo,
                "pr_number": pr_number
            }
        )
        return response.json()["run_id"]
    
    def get_results(self, run_id, timeout=60):
        start = time.time()
        while time.time() - start < timeout:
            response = requests.get(f"{self.base_url}/review/{run_id}")
            result = response.json()
            
            if result["status"] == "completed":
                return result
            
            time.sleep(2)
        
        raise TimeoutError("Review timed out")

client = PRReviewClient()
run_id = client.review_pr("facebook", "react", 12345)
results = client.get_results(run_id)

print(f"Found {results['summary']['total_issues_found']} issues")
for comment in results['comments']:
    if comment['severity'] == 'critical':
        print(f"🚨 {comment['file_path']}:{comment['line_number']}")
        print(f"   {comment['message']}")
```

### Webhook Integration

```python
from fastapi import FastAPI, Request
import requests

app = FastAPI()

@app.post("/github-webhook")
async def handle_webhook(request: Request):
    payload = await request.json()
    
    if payload["action"] in ["opened", "synchronize"]:
        pr = payload["pull_request"]
        
        response = requests.post(
            "http://pr-review-agent:8000/review/pr",
            json={
                "repo_owner": payload["repository"]["owner"]["login"],
                "repo_name": payload["repository"]["name"],
                "pr_number": pr["number"]
            }
        )
        
        return {"status": "review_started", "run_id": response.json()["run_id"]}
```

## Troubleshooting

### Issue: "Review stuck in pending"

**Cause**: Celery worker not running or crashed

**Solution**:
```bash
docker-compose logs celery_worker
docker-compose restart celery_worker
```

### Issue: "GitHub API rate limit"

**Cause**: Too many requests to GitHub API

**Solution**:
- Use authenticated token (increases limit to 5000/hour)
- Implement caching for PR diffs
- Add delay between requests

### Issue: "No issues detected on bad code"

**Possible Causes**:
1. Binary file (skipped by design)
2. Non-Python file (limited analysis)
3. Issue pattern not in detection rules

**Debug**:
```bash
# Check parsed files
curl http://localhost:8000/review/{run_id} | jq '.comments'

# Check agent logs
docker-compose logs app | grep -i "agent"
```

### Issue: "Database connection failed"

**Solution**:
```bash
# Check database is running
docker-compose ps db

# Verify connection string
docker-compose exec app env | grep DATABASE_URL

# Test connection
docker-compose exec app python -c "from src.database import engine; print(engine.url)"
```

### Issue: "Import errors in tests"

**Solution**:
```bash
# Ensure PYTHONPATH includes src
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or use installed package mode
pip install -e .
```

## Advanced Usage

### Custom Agent Execution

Run specific agents only:

```python
from src.agents.security import SecurityAgent
from src.agents.diff_parser import DiffParserAgent

parser = DiffParserAgent()
security = SecurityAgent()

context = {"diff_content": diff_text}
await parser.analyze(context)
issues = await security.analyze(context)

print(f"Found {len(issues)} security issues")
```

### Batch Processing

Process multiple PRs:

```python
prs = [
    ("org1", "repo1", 10),
    ("org1", "repo1", 11),
    ("org2", "repo2", 5),
]

run_ids = []
for owner, repo, pr_num in prs:
    response = requests.post(
        "http://localhost:8000/review/pr",
        json={"repo_owner": owner, "repo_name": repo, "pr_number": pr_num}
    )
    run_ids.append(response.json()["run_id"])

# Wait and collect results
results = [client.get_results(rid) for rid in run_ids]
```

### Custom Reporting

Generate custom reports:

```python
def generate_report(results):
    report = {
        "critical_count": results["summary"]["critical_issues"],
        "files_with_issues": set(),
        "most_common_category": None
    }
    
    categories = {}
    for comment in results["comments"]:
        report["files_with_issues"].add(comment["file_path"])
        cat = comment["category"]
        categories[cat] = categories.get(cat, 0) + 1
    
    report["most_common_category"] = max(categories, key=categories.get)
    
    return report
```

## Performance Tips

1. **Use diff review for faster processing** (skips GitHub API)
2. **Batch similar requests** to same repository
3. **Cache results** for unchanged file hashes
4. **Scale Celery workers** horizontally for high volume
5. **Use Redis cluster** for distributed deployments

## Best Practices

1. **Always check health endpoint** before submitting reviews
2. **Implement retry logic** with exponential backoff
3. **Store run_ids** for audit trails
4. **Monitor processing times** for performance degradation
5. **Set reasonable timeouts** (30-60 seconds typical)
6. **Handle all response statuses** (pending, processing, completed, failed)
7. **Parse and display issues** by severity for prioritization
