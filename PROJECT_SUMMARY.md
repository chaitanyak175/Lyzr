# Automated GitHub Pull Request Review Agent

## 🎯 Project Overview

A complete, production-ready **Python backend system** that automatically analyzes GitHub pull requests and produces human-quality code review comments. Built with a sophisticated multi-agent architecture for comprehensive code analysis.

## 📁 Project Structure

```
/
├── backend/                    # Complete Python backend application
│   ├── src/                   # Source code (100% comment-free)
│   │   ├── agents/           # 10 specialized review agents
│   │   ├── main.py           # FastAPI application
│   │   ├── tasks.py          # Celery async workers
│   │   ├── models.py         # Database models
│   │   ├── schemas.py        # API schemas
│   │   └── ...
│   ├── tests/                # Comprehensive test suite
│   ├── examples/             # Example diffs for testing
│   ├── Dockerfile            # Container configuration
│   ├── docker-compose.yml    # Multi-service orchestration
│   ├── Makefile              # Build automation
│   ├── README.md             # Setup & quick start
│   ├── DESIGN.md             # Architecture documentation
│   ├── USAGE.md              # Integration examples
│   └── RELEASE_NOTES.md      # Version history
│
└── src/                       # Next.js frontend (original)
    └── app/
        └── page.tsx
```

## 🚀 Quick Start

Navigate to the backend directory and follow the setup instructions:

```bash
cd backend

# Copy environment file
cp .env.example .env

# Edit .env and add your GitHub token
# GITHUB_TOKEN=ghp_your_token_here

# Start with Docker (recommended)
docker-compose up -d

# Or install locally
make install
make dev
```

## ✨ Key Features

### Multi-Agent Architecture
- **10 specialized agents** for comprehensive analysis
- **Security detection**: SQL injection, hardcoded secrets, eval/exec
- **Performance analysis**: Nested loops, inefficient patterns
- **Code quality**: AST analysis, naming, shadowing
- **Style checking**: Whitespace, quotes, conventions
- **Test coverage**: Missing test detection

### Production Ready
- **FastAPI** REST API with async processing
- **Celery** workers for non-blocking reviews
- **PostgreSQL** for persistent storage
- **Redis** for task queue and caching
- **Docker** complete containerization
- **CI/CD** GitHub Actions pipeline
- **100% type-hinted** Python codebase
- **Zero comments** self-documenting code

## 📖 Documentation

All documentation is in the `backend/` directory:

- **[README.md](backend/README.md)** - Installation, setup, testing, deployment
- **[DESIGN.md](backend/DESIGN.md)** - Architecture, agents, extensibility
- **[USAGE.md](backend/USAGE.md)** - API examples, integration patterns
- **[RELEASE_NOTES.md](backend/RELEASE_NOTES.md)** - Version history, features

## 🔧 Technology Stack

**Backend Framework**
- Python 3.11+
- FastAPI 0.115.0
- Celery 5.4.0
- SQLModel 0.0.22

**Infrastructure**
- PostgreSQL 16
- Redis 7
- Docker & Docker Compose

**Development**
- pytest (testing)
- black (formatting)
- ruff (linting)
- mypy (type checking)
- bandit (security)

## 🎯 API Endpoints

Once running (default: http://localhost:8000):

- `POST /review/pr` - Submit GitHub PR for review
- `POST /review/diff` - Submit raw diff for analysis
- `GET /review/{run_id}` - Get review results
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation

## 🧪 Example Usage

```bash
# Submit a PR review
curl -X POST http://localhost:8000/review/pr \
  -H "Content-Type: application/json" \
  -d '{
    "repo_owner": "facebook",
    "repo_name": "react",
    "pr_number": 12345
  }'

# Get results
curl http://localhost:8000/review/{run_id}
```

## 📊 What Gets Detected

✅ **Security Issues**
- SQL injection vulnerabilities
- Hardcoded secrets and API keys
- Dangerous eval/exec usage

✅ **Performance Problems**
- Nested loops (O(n²) complexity)
- Repeated computations
- Inefficient string operations

✅ **Code Quality**
- Variable shadowing
- Unused variables
- Complex expressions
- Magic numbers

✅ **Style Violations**
- Trailing whitespace
- Quote inconsistency
- Naming conventions
- Line length

✅ **Testing Gaps**
- Missing test files
- Uncovered new functions

## 🏗️ Architecture Highlights

### Multi-Agent System
Each agent independently analyzes code changes:
1. **DiffParserAgent** - Parses git diffs
2. **ASTAgent** - Python AST analysis
3. **SecurityAgent** - Security vulnerabilities
4. **PerformanceAgent** - Performance issues
5. **ReadabilityAgent** - Code readability
6. **StyleAgent** - Code style
7. **TestCoverageAgent** - Test coverage
8. **StaticAnalysisAgent** - Static checks
9. **SummarizerAgent** - Result aggregation
10. **CommentFormatterAgent** - Output formatting

### Async Processing
- FastAPI handles HTTP requests
- Celery workers process reviews asynchronously
- Results stored in PostgreSQL
- Status polling via run IDs

## 🔒 Code Quality Principles

### Self-Documenting Code
- **Zero comments or docstrings** in source files
- Clear, expressive variable/function names
- Logical code structure
- Type hints throughout
- All explanations in markdown docs

### Testing
- 45+ test cases
- >85% code coverage
- Unit and integration tests
- Example diffs for all scenarios

## 🚢 Deployment

### Docker (Recommended)
```bash
cd backend
docker-compose up -d
```

### Manual
```bash
cd backend
pip install -r requirements.txt
make migrate
make dev  # Terminal 1
make celery-worker  # Terminal 2
```

## 📝 Environment Variables

Required in `backend/.env`:
```bash
DATABASE_URL=postgresql://postgres:postgres@db:5432/prreview
REDIS_URL=redis://redis:6379/0
GITHUB_TOKEN=ghp_your_personal_access_token_here
SECRET_KEY=your-secure-secret-key-here
```

## 🧪 Testing

```bash
cd backend

# Run all tests
make test

# With coverage
make test-cov

# Lint and format
make format
make lint
```

## 📦 What's Included

### Complete Backend System
✅ 10 specialized review agents  
✅ FastAPI REST API  
✅ Celery async workers  
✅ PostgreSQL database  
✅ Redis caching  
✅ Docker infrastructure  
✅ GitHub Actions CI/CD  
✅ Pre-commit hooks  
✅ Comprehensive tests  
✅ Example diffs  
✅ Full documentation  

### Code Quality
✅ 100% type-hinted Python  
✅ Zero comments (self-documenting)  
✅ Black formatted  
✅ Ruff linted  
✅ MyPy type checked  
✅ Bandit security scanned  

## 🎓 Learning Resources

Start with these files in order:
1. `backend/README.md` - Setup and quick start
2. `backend/USAGE.md` - API usage examples
3. `backend/DESIGN.md` - Architecture deep dive
4. `backend/RELEASE_NOTES.md` - Feature details

## 🤝 Contributing

1. Follow self-documenting code style (no comments!)
2. Add tests for new features
3. Run `make format && make lint && make test`
4. Update documentation as needed

## 📞 Getting Help

- Check `backend/README.md` for setup issues
- See `backend/USAGE.md` for API examples
- Review `backend/DESIGN.md` for architecture
- Check example diffs in `backend/examples/`

## ⚡ Performance

- Average review time: 2-5 seconds
- Async processing (non-blocking)
- Horizontally scalable (add workers)
- Efficient single-pass parsing

## 🎯 Perfect For

- Code review automation
- CI/CD integration
- Pre-commit validation
- Team coding standards enforcement
- Security vulnerability detection
- Performance optimization guidance

---

**Navigate to `backend/` directory to get started!**

```bash
cd backend
cat README.md  # Read full setup instructions
```
