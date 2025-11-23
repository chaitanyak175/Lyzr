# Automated GitHub Pull Request Review Agent

A production-ready, multi-agent system that analyzes GitHub pull requests and produces human-quality code review comments. Built with FastAPI, Celery, and a modular agent architecture.

## 🚀 Features

- **Multi-Agent Architecture**: 10 specialized agents for comprehensive code analysis
- **Security Detection**: SQL injection, hardcoded secrets, eval/exec usage
- **Performance Analysis**: Nested loops, repeated computations, inefficient patterns
- **Code Quality**: AST analysis, naming conventions, shadowing detection
- **Style Checking**: Trailing whitespace, quote consistency, naming conventions
- **Test Coverage**: Identifies missing test files for new code
- **Binary File Handling**: Skips binary files gracefully
- **Async Processing**: Celery workers for non-blocking reviews
- **REST API**: FastAPI endpoints for easy integration
- **Production Ready**: Docker, CI/CD, comprehensive tests

## 📋 Prerequisites

- Python 3.11+
- Docker & Docker Compose (recommended)
- PostgreSQL 16
- Redis 7
- GitHub Personal Access Token

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Application                      │
│  POST /review/pr  │  POST /review/diff  │  GET /review/{id} │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
         ┌───────────────┐
         │ Celery Worker │
         └───────┬───────┘
                 │
                 ▼
    ┌────────────────────────┐
    │  Review Orchestrator   │
    └────────┬───────────────┘
             │
    ┌────────┴────────────────────────────────────────┐
    │                                                  │
    ▼         ▼         ▼         ▼         ▼         ▼
┌────────┐ ┌────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────┐
│  Diff  │ │AST │ │Security│ │ Perf.  │ │ Style  │ │Test│
│ Parser │ │    │ │        │ │        │ │        │ │Cov.│
└────────┘ └────┘ └────────┘ └────────┘ └────────┘ └────┘
                     │
                     ▼
            ┌────────────────┐
            │  Summarizer &  │
            │   Formatter    │
            └────────────────┘
                     │
                     ▼
              ┌─────────────┐
              │   Results   │
              │  (JSON/DB)  │
              └─────────────┘
```

## 🛠️ Installation

### Option 1: Docker (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd backend
```

2. Copy environment file:
```bash
cp .env.example .env
```

3. Edit `.env` and set your GitHub token:
```bash
GITHUB_TOKEN=ghp_your_token_here
SECRET_KEY=your-secure-secret-key
```

4. Build and start services:
```bash
make build
make up
```

5. Verify services are running:
```bash
docker-compose ps
curl http://localhost:8000/health
```

### Option 2: Local Development

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up PostgreSQL and Redis locally, then configure `.env`

4. Initialize database:
```bash
make migrate
```

5. Run services:
```bash
# Terminal 1: API Server
make dev

# Terminal 2: Celery Worker
make celery-worker
```

## 🎯 Usage

### Quick Start

1. Start the application:
```bash
docker-compose up -d
```

2. Submit a PR for review:
```bash
curl -X POST http://localhost:8000/review/pr \
  -H "Content-Type: application/json" \
  -d '{
    "repo_owner": "octocat",
    "repo_name": "Hello-World",
    "pr_number": 1
  }'
```

3. Get review results:
```bash
curl http://localhost:8000/review/{run_id}
```

### Review a Diff Directly

```bash
curl -X POST http://localhost:8000/review/diff \
  -H "Content-Type: application/json" \
  -d '{
    "diff_content": "diff --git a/file.py b/file.py\n..."
  }'
```

### Example with Test Diff

```bash
curl -X POST http://localhost:8000/review/diff \
  -H "Content-Type: application/json" \
  -d @examples/sql_injection.diff
```

## 🧪 Testing

Run all tests:
```bash
make test
```

Run with coverage:
```bash
make test-cov
```

Run specific test file:
```bash
pytest tests/test_agents.py -v
```

Test with example diffs:
```bash
pytest tests/ -v -k "sql_injection"
```

## 🔍 Linting & Formatting

Format code:
```bash
make format
```

Run linters:
```bash
make lint
```

Type checking:
```bash
make type-check
```

Security scan:
```bash
make security-scan
```

## 📊 Monitoring

View application logs:
```bash
make logs
```

View specific service logs:
```bash
make docker-logs-app
make docker-logs-celery
```

Access Celery Flower (task monitoring):
```bash
make celery-flower
# Visit http://localhost:5555
```

## 🔧 Development

### Project Structure

```
backend/
├── src/
│   ├── agents/              # Multi-agent modules
│   │   ├── base.py
│   │   ├── diff_parser.py
│   │   ├── ast_agent.py
│   │   ├── security.py
│   │   ├── performance.py
│   │   ├── readability.py
│   │   ├── style.py
│   │   ├── test_coverage.py
│   │   ├── summarizer.py
│   │   ├── comment_formatter.py
│   │   └── orchestrator.py
│   ├── main.py              # FastAPI application
│   ├── tasks.py             # Celery tasks
│   ├── models.py            # Database models
│   ├── schemas.py           # Pydantic schemas
│   ├── config.py            # Configuration
│   ├── database.py          # Database setup
│   ├── github_client.py     # GitHub API client
│   └── celery_app.py        # Celery configuration
├── tests/                   # Test suite
├── examples/                # Example diffs
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── README.md
```

### Adding a New Agent

1. Create `src/agents/new_agent.py` extending `BaseAgent`
2. Implement `async def analyze(self, context)` method
3. Register in `src/agents/orchestrator.py`
4. Add tests in `tests/test_agents.py`

See DESIGN.md for detailed architecture documentation.

## 🚢 Deployment

### Docker Production Build

```bash
docker build -t pr-review-agent:latest .
docker run -p 8000:8000 \
  -e DATABASE_URL=<url> \
  -e REDIS_URL=<url> \
  -e GITHUB_TOKEN=<token> \
  pr-review-agent:latest
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| DATABASE_URL | PostgreSQL connection string | Yes |
| REDIS_URL | Redis connection string | Yes |
| GITHUB_TOKEN | GitHub Personal Access Token | Yes |
| SECRET_KEY | Application secret key | Yes |
| ENVIRONMENT | deployment environment | No |

## 📖 API Documentation

Once running, visit:
- Interactive API docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Endpoints

**POST /review/pr**
- Submit a GitHub PR for review
- Returns: `{run_id, status, message}`

**POST /review/diff**
- Submit a diff directly for review
- Returns: `{run_id, status, message}`

**GET /review/{run_id}**
- Get review results
- Returns: Full review with comments and summary

**GET /health**
- Health check endpoint
- Returns: `{status: "healthy"}`

## 🤝 Contributing

1. Install pre-commit hooks: `make install`
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes with self-documenting code (no comments!)
4. Run tests: `make test`
5. Run linters: `make format && make lint`
6. Commit changes: `git commit -m "Add amazing feature"`
7. Push branch: `git push origin feature/amazing-feature`
8. Open Pull Request

## 📝 License

This project is proprietary. All rights reserved.

## 🙏 Acknowledgments

Built with FastAPI, Celery, SQLModel, PostgreSQL, and Redis.

## 📞 Support

For issues and questions, see USAGE.md and DESIGN.md for detailed documentation.
