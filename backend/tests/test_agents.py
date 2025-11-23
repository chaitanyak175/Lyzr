import pytest
from src.agents.diff_parser import DiffParserAgent
from src.agents.ast_agent import ASTAgent
from src.agents.security import SecurityAgent
from src.agents.performance import PerformanceAgent
from src.agents.style import StyleAgent
from src.agents.readability import ReadabilityAgent


@pytest.mark.asyncio
async def test_diff_parser_parses_simple_diff():
    agent = DiffParserAgent()
    diff = """diff --git a/test.py b/test.py
--- a/test.py
+++ b/test.py
@@ -1,3 +1,4 @@
 def hello():
+    print('world')
     pass
"""
    context = {"diff_content": diff}
    await agent.analyze(context)
    
    assert "parsed_files" in context
    assert len(context["parsed_files"]) == 1
    assert context["parsed_files"][0]["path"] == "test.py"


@pytest.mark.asyncio
async def test_diff_parser_handles_binary_files():
    agent = DiffParserAgent()
    diff = """diff --git a/image.png b/image.png
Binary files a/image.png and b/image.png differ
"""
    context = {"diff_content": diff}
    await agent.analyze(context)
    
    assert context["parsed_files"][0]["is_binary"] is True


@pytest.mark.asyncio
async def test_ast_agent_detects_shadowing():
    agent = ASTAgent()
    diff = """diff --git a/test.py b/test.py
--- a/test.py
+++ b/test.py
@@ -1,3 +1,4 @@
 def process():
+    id = 123
     pass
"""
    context = {"diff_content": diff, "parsed_files": []}
    parser = DiffParserAgent()
    await parser.analyze(context)
    
    comments = await agent.analyze(context)
    
    assert len(comments) > 0
    assert any("shadow" in c.message.lower() for c in comments)
    assert any(c.severity == "warning" for c in comments)


@pytest.mark.asyncio
async def test_security_agent_detects_sql_injection():
    agent = SecurityAgent()
    diff = """diff --git a/database.py b/database.py
--- a/database.py
+++ b/database.py
@@ -1,3 +1,4 @@
 def query_user(username):
+    cursor.execute("SELECT * FROM users WHERE name = '%s'" % username)
     pass
"""
    context = {"diff_content": diff, "parsed_files": []}
    parser = DiffParserAgent()
    await parser.analyze(context)
    
    comments = await agent.analyze(context)
    
    assert len(comments) > 0
    assert any("sql injection" in c.message.lower() for c in comments)
    assert any(c.severity == "critical" for c in comments)


@pytest.mark.asyncio
async def test_security_agent_detects_hardcoded_secrets():
    agent = SecurityAgent()
    diff = """diff --git a/config.py b/config.py
--- a/config.py
+++ b/config.py
@@ -1,3 +1,4 @@
 def setup():
+    api_key = "sk_live_abc123def456ghi789"
     pass
"""
    context = {"diff_content": diff, "parsed_files": []}
    parser = DiffParserAgent()
    await parser.analyze(context)
    
    comments = await agent.analyze(context)
    
    assert len(comments) > 0
    assert any("secret" in c.message.lower() or "key" in c.message.lower() for c in comments)


@pytest.mark.asyncio
async def test_security_agent_detects_eval_usage():
    agent = SecurityAgent()
    diff = """diff --git a/utils.py b/utils.py
--- a/utils.py
+++ b/utils.py
@@ -1,3 +1,4 @@
 def process(code):
+    result = eval(code)
     pass
"""
    context = {"diff_content": diff, "parsed_files": []}
    parser = DiffParserAgent()
    await parser.analyze(context)
    
    comments = await agent.analyze(context)
    
    assert len(comments) > 0
    assert any("eval" in c.message.lower() for c in comments)


@pytest.mark.asyncio
async def test_performance_agent_detects_nested_loops():
    agent = PerformanceAgent()
    diff = """diff --git a/algorithm.py b/algorithm.py
--- a/algorithm.py
+++ b/algorithm.py
@@ -1,3 +1,5 @@
 def process(items):
     for i in items:
+        for j in items:
+            pass
"""
    context = {"diff_content": diff, "parsed_files": []}
    parser = DiffParserAgent()
    await parser.analyze(context)
    
    comments = await agent.analyze(context)
    
    assert len(comments) > 0
    assert any("nested loop" in c.message.lower() or "complexity" in c.message.lower() for c in comments)


@pytest.mark.asyncio
async def test_style_agent_detects_trailing_whitespace():
    agent = StyleAgent()
    diff = """diff --git a/code.py b/code.py
--- a/code.py
+++ b/code.py
@@ -1,3 +1,4 @@
 def hello():
+    print('test')   
     pass
"""
    context = {"diff_content": diff, "parsed_files": []}
    parser = DiffParserAgent()
    await parser.analyze(context)
    
    comments = await agent.analyze(context)
    
    assert len(comments) > 0
    assert any("trailing whitespace" in c.message.lower() for c in comments)


@pytest.mark.asyncio
async def test_readability_agent_detects_long_lines():
    agent = ReadabilityAgent()
    long_line = "x = " + "a" * 150
    diff = f"""diff --git a/code.py b/code.py
--- a/code.py
+++ b/code.py
@@ -1,3 +1,4 @@
 def hello():
+    {long_line}
     pass
"""
    context = {"diff_content": diff, "parsed_files": []}
    parser = DiffParserAgent()
    await parser.analyze(context)
    
    comments = await agent.analyze(context)
    
    assert len(comments) > 0
    assert any("line exceeds" in c.message.lower() or "length" in c.message.lower() for c in comments)


@pytest.mark.asyncio
async def test_binary_files_are_skipped():
    parser = DiffParserAgent()
    diff = """diff --git a/image.png b/image.png
Binary files a/image.png and b/image.png differ
"""
    context = {"diff_content": diff}
    await parser.analyze(context)
    
    security_agent = SecurityAgent()
    comments = await security_agent.analyze(context)
    
    assert len(comments) == 0
