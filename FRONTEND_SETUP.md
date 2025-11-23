# Frontend Setup Guide

This Next.js frontend provides a modern UI for the GitHub PR Review Agent backend.

## Environment Variables

All sensitive configuration is stored in environment variables to prevent hardcoded secrets.

### Setup

1. Copy the example environment file:
   ```bash
   cp .env.local.example .env.local
   ```

2. Configure the backend API URL in `.env.local`:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

### Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL | `http://localhost:8000` |

**Note:** The `NEXT_PUBLIC_` prefix makes the variable accessible in the browser. Only use this prefix for non-sensitive configuration like API URLs.

## Security Best Practices

### ✅ What We Do

- **No Hardcoded Tokens**: GitHub tokens are input by users through the UI or configured on the backend
- **Environment Variables**: All configuration uses environment variables
- **Optional Token Field**: Users can optionally provide their own GitHub token for private repos
- **Password Input**: GitHub token field uses `type="password"` to hide sensitive input
- **Server-Side Default**: Backend uses its own configured token when user doesn't provide one

### Backend Integration

The frontend connects to three backend endpoints:

1. **POST /review/pr** - Submit a PR for review
   - Requires: `repo_full_name`, `pr_number`
   - Optional: `github_token` (uses backend token if not provided)

2. **POST /review/diff** - Submit a diff for review
   - Requires: `diff_text`
   - No GitHub token needed (manual diff analysis)

3. **GET /review/{run_id}** - Check review status
   - Returns structured review results

## Running the Frontend

### Development
```bash
npm run dev
# or
bun dev
```

### Production
```bash
npm run build
npm start
# or
bun run build
bun start
```

## Token Security

### For Users
- **Public Repos**: Leave token field empty (backend uses its configured token)
- **Private Repos**: Provide your personal access token
- **Token Scope**: Only `repo` scope needed for PR access

### For Deployment
- Store backend GitHub token in backend `.env` file
- Never commit `.env.local` or `.env` files to version control
- Use secure secret management for production deployments

## CORS Configuration

If the frontend runs on a different domain than the backend, configure CORS in the backend FastAPI app:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
