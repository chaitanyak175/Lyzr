# Design Documentation

## System Architecture

The PR Review Agent is built on a **multi-agent architecture** where specialized agents independently analyze different aspects of code changes. This design promotes modularity, extensibility, and parallel processing capabilities.

## Core Principles

### 1. Agent Independence
Each agent operates independently with no direct dependencies on other agents. They receive a shared context dictionary and contribute their findings without affecting others.

### 2. Self-Documenting Code
All source code is written to be self-explanatory through:
- Clear, descriptive variable names
- Expressive function/class names
- Logical code structure
- Type hints throughout
- **Zero comments or docstrings in source files**

All explanatory text resides in documentation markdown files (like this one).

### 3. Extensibility
New agents can be added without modifying existing code. Simply:
1. Extend `BaseAgent`
2. Implement `analyze()` method
3. Register in orchestrator
4. Add corresponding tests

### 4. Asynchronous Processing
Reviews run asynchronously via Celery workers to prevent blocking API requests. Users poll for results using run IDs.

## Agent Pipeline

### Phase 1: Parsing
**DiffParserAgent** transforms raw git diffs into structured data:
- Extracts file paths, hunks, line numbers
- Identifies binary files
- Parses added/removed/context lines
- Stores parsed structure in shared context

### Phase 2: Analysis
Specialized agents run concurrently, each focusing on specific concerns:

**ASTAgent**
- Parses Python code into Abstract Syntax Trees
- Detects variable shadowing (builtin/common names)
- Identifies structural anti-patterns
- Only processes Python files

**StaticAnalysisAgent**
- Detects unused variables
- Identifies unreachable code
- Finds potential logic errors
- Language-agnostic pattern matching

**SecurityAgent**
- SQL injection detection (string formatting in queries)
- Hardcoded secrets and API keys
- Dangerous functions (eval, exec)
- Critical severity for security issues

**PerformanceAgent**
- Nested loop detection (O(n²) complexity)
- Repeated computations in loops
- Inefficient string concatenation
- Performance anti-patterns

**ReadabilityAgent**
- Line length violations (>100 chars)
- Complex nested expressions
- Magic numbers without context
- Cognitive complexity markers

**StyleAgent**
- Trailing whitespace
- Quote consistency (single vs double)
- Naming convention violations
- PEP 8 style issues

**TestCoverageAgent**
- Detects new functions without tests
- Suggests test file locations
- Correlates production code with test files
- Warns on missing test coverage

### Phase 3: Aggregation
**SummarizerAgent**
- Counts issues by severity
- Calculates total files reviewed
- Generates overall assessment
- Produces structured summary

**CommentFormatterAgent**
- Sorts comments by severity/file/line
- Deduplicates redundant comments
- Formats for human readability
- Prepares final output structure

### Phase 4: Orchestration
**ReviewOrchestrator**
- Manages agent execution order
- Maintains shared context
- Collects all agent outputs
- Times the entire process
- Returns structured ReviewResult

## Data Flow

```
GitHub PR/Diff → API Endpoint → Celery Task → Orchestrator
                                                    ↓
                                              Context Dict
                                                    ↓
                    ┌──────────────────────────────┼─────────────────┐
                    │                              │                 │
              DiffParser                     Other Agents      Test Coverage
                    │                              │                 │
                    └──────────────────────────────┼─────────────────┘
                                                    ↓
                                            All Comments List
                                                    ↓
                                    ┌───────────────┴───────────────┐
                              Summarizer                      Formatter
                                    │                               │
                                    └───────────────┬───────────────┘
                                                    ↓
                                            ReviewResult Object
                                                    ↓
                                        Database + JSON Response
```

## Database Schema

**ReviewRun Table**
- `id`: Primary key (integer)
- `run_id`: Unique UUID for API lookups
- `repo_owner`: GitHub repository owner
- `repo_name`: Repository name
- `pr_number`: Pull request number (optional)
- `status`: Enum (pending, processing, completed, failed)
- `result_data`: JSON string of ReviewResult
- `error_message`: Error details if failed
- `created_at`: Timestamp
- `completed_at`: Timestamp (when finished)

## API Design

### RESTful Endpoints

**POST /review/pr**
- Input: `{repo_owner, repo_name, pr_number}`
- Creates ReviewRun with pending status
- Queues Celery task
- Returns: `{run_id, status, message}`
- Non-blocking (returns immediately)

**POST /review/diff**
- Input: `{diff_content, repo_context?}`
- For direct diff submission
- Creates ReviewRun
- Queues Celery task
- Returns: `{run_id, status, message}`

**GET /review/{run_id}**
- Retrieves review status and results
- Returns pending/processing if not complete
- Returns full ReviewResult when done
- Returns 404 if run_id not found
- Returns 500 if review failed

## Celery Task Architecture

**review_pr_task**
- Fetches PR diff via GitHub API
- Delegates to orchestrator
- Updates database on completion/failure
- Handles all exceptions gracefully

**review_diff_task**
- Directly processes provided diff
- Same flow as PR task minus GitHub API
- Used for testing and direct integrations

## Error Handling Strategy

### Agent-Level
- Each agent catches its own exceptions
- Failed agents don't block others
- Errors logged but don't propagate
- Partial results better than total failure

### Task-Level
- Celery tasks catch all exceptions
- Database updated with error status
- Error message stored for debugging
- Failed tasks don't retry (by design)

### API-Level
- 404 for missing resources
- 500 for internal errors with details
- Validation errors return 422
- All errors return JSON structure

## Comment Structure

Each comment contains:
- `file_path`: Where the issue occurs
- `line_number`: Specific line (or null for file-level)
- `severity`: critical/warning/info/style
- `category`: Issue classification
- `message`: Human-readable description
- `suggestion`: Actionable recommendation (optional)

## Severity Levels

**critical**: Security vulnerabilities, dangerous patterns
- SQL injection
- Hardcoded secrets
- eval/exec usage

**warning**: Significant issues that should be addressed
- Performance problems
- Missing tests
- Shadowing builtins

**info**: Suggestions for improvement
- Readability concerns
- Magic numbers
- Long lines

**style**: Cosmetic/formatting issues
- Trailing whitespace
- Quote inconsistency
- Naming conventions

## GitHub Integration

**GitHubClient**
- Authenticates via personal access token
- Fetches PR metadata and diff
- Can post review comments (future feature)
- Handles rate limiting gracefully

**Diff Retrieval**
- Fetches individual file patches
- Reconstructs unified diff format
- Handles binary files appropriately
- Preserves line number accuracy

## Extensibility Points

### Adding New Detection Rules

**In Existing Agent**
1. Add method to agent class (e.g., `_check_new_pattern`)
2. Call from `check_*_issues()` method
3. Return additional ReviewComments
4. Add corresponding test

**As New Agent**
1. Create `src/agents/new_agent.py`
2. Extend BaseAgent
3. Implement `async def analyze(self, context)`
4. Register in `ReviewOrchestrator.__init__()`
5. Add test file `tests/test_new_agent.py`

### Custom Severity Levels
Modify `ReviewComment.severity` field pattern in `src/schemas.py`

### Alternative Storage Backends
Implement alternative to `get_session()` in `src/database.py`

### Custom GitHub Workflows
Extend `GitHubClient` with additional methods

## Performance Considerations

### Optimization Strategies
- Agents run concurrently (async)
- Parsing happens once, all agents use result
- Binary files skipped early
- Database indexed on run_id
- Redis for fast task queueing

### Scalability
- Horizontal scaling: Add more Celery workers
- Vertical scaling: Increase worker concurrency
- Database pooling for connections
- Stateless design enables load balancing

## Testing Strategy

### Unit Tests
- Each agent tested independently
- Mock GitHub API responses
- In-memory SQLite for database tests
- Async test support via pytest-asyncio

### Integration Tests
- Full pipeline tests via orchestrator
- API endpoint tests with TestClient
- Example diffs for real scenarios

### Test Coverage
- All agents covered
- All API endpoints covered
- Example diffs for each issue type
- Edge cases (binary files, empty diffs)

## Configuration Management

**Environment Variables**
- Loaded via pydantic-settings
- Validated on startup
- Type-safe access via `settings` object
- .env file for local development
- Environment variables for production

**Deployment Environments**
- development: Debug mode, verbose logging
- testing: In-memory databases, mocked externals
- production: Optimized, secure, monitored

## Security Considerations

### API Security
- CORS middleware for web clients
- Secret key for session management
- GitHub token stored securely
- No sensitive data in logs

### Code Execution
- No eval/exec in agent code
- AST parsing instead of code execution
- Static analysis only
- Sandboxed Celery workers

### Dependency Security
- Regular dependency updates
- Bandit security scanning in CI
- Safety checks for known vulnerabilities
- Pinned versions in requirements.txt

## Future Enhancements

### Planned Features
1. Direct PR comment posting via GitHub API
2. Configurable severity thresholds
3. Custom rule configuration files
4. Multi-language support (JavaScript, Go, etc.)
5. Machine learning for pattern detection
6. Webhook integration for auto-reviews
7. Review history and analytics
8. Team-specific coding standards

### Architecture Extensions
- Plugin system for community agents
- Rule marketplace/repository
- Distributed tracing for debugging
- Real-time review progress updates
- Cached analysis for unchanged files

## Troubleshooting Guide

**Review stuck in processing**
- Check Celery worker logs
- Verify Redis connection
- Confirm database accessibility
- Review task timeout settings

**No issues detected**
- Verify agents are registered
- Check diff parsing output
- Confirm file types supported
- Review agent detection thresholds

**GitHub API errors**
- Validate token permissions
- Check rate limit status
- Verify repository access
- Confirm PR number exists

**Database connection failures**
- Check DATABASE_URL format
- Verify PostgreSQL is running
- Confirm network connectivity
- Review connection pool settings
