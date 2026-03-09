# CLAUDE.md

## Project Overview

F1 Insight AI — F1 뉴스/인터뷰 자동 수집, LLM 요약(영문+한국어 번역), 웹 서비스 제공. Mac Mini에서 Docker Compose로 운영.

## Architecture

**Data flow:** Scraper → MongoDB (raw) → Elasticsearch (search index) → LLM summary/translation → Frontend

- **Backend** (`backend/`): Python 3.12+ FastAPI. Entry: `backend/app/main.py`. Modules: `api/`, `scraper/`, `scheduler/`, `llm/`, `models/`, `services/`
- **Frontend** (`frontend/`): Next.js 15 App Router, TypeScript, Tailwind CSS v4. API client: `frontend/src/lib/api.ts`
- **Infra**: Docker Compose — MongoDB 7, Elasticsearch 8.17, backend, frontend. Healthchecks gate startup order.

## Commands

### Backend
```bash
cd backend
pip install -e ".[dev]"          # Install with dev deps
uvicorn app.main:app --reload    # Dev server (port 8000)
ruff check . && ruff format .    # Lint + format
pytest                           # All tests
pytest tests/test_foo.py -k name # Single test
```

### Frontend
```bash
cd frontend
npm install && npm run dev       # Dev server (port 3000)
npm run build                    # Production build
npm run lint                     # ESLint
```

### Docker
```bash
docker compose up -d                          # All services
docker compose up mongodb elasticsearch -d    # DB only
docker compose down                           # Stop all
```

## Code Conventions

### Backend (Python)
- **Linter**: Ruff — rules E, F, I, W. Line length 100. Target py312.
- **Async**: async everywhere — Motor (MongoDB), async elasticsearch, httpx.
- **Models**: Pydantic v2 for validation + MongoDB document schemas.
- **Typing**: Type hints required on all public functions.
- **Errors**: Raise `HTTPException` with specific status codes. Never return bare dicts for errors.

### Frontend (TypeScript)
- **Strict mode**: TypeScript strict enabled.
- **Styling**: Tailwind CSS v4, no CSS modules.
- **Routing**: Next.js App Router (`src/app/`).
- **Imports**: Always use `@/*` alias.
- **Components**: Server Components by default. Add `'use client'` only when needed.

### General
- **Language**: Code/comments in English. UI text bilingual (EN + KR).
- **Commits**: Conventional commits (feat/fix/refactor/docs/chore).
- **Tests**: Write tests for business logic. Use pytest (backend), vitest (frontend).
- **No dead code**: Remove unused imports, variables, functions immediately.

## Workflow: 작업 완료 후 자동 커밋/푸시

모든 작업(feature, fix, refactor 등)이 끝나면 아래 순서를 **반드시** 따른다:

1. **Lint**: `ruff check . && ruff format .` (backend) / `npm run lint` (frontend)
2. **Test**: `pytest` (backend) / `npm run build` (frontend)
3. **모두 통과하면** → `git add` → `git commit` (conventional commit) → `git push`
4. **실패하면** → 수정 후 1번부터 재시도. 테스트 통과 전까지 커밋/푸시하지 않는다.

## Environment

Copy `.env.example` → `.env`. Key vars: `MONGODB_URI`, `ELASTICSEARCH_URL`, `OLLAMA_BASE_URL`, `NEXT_PUBLIC_API_URL`.

## Task Tracking

See `docs/plan/tasks.md` for phased implementation plan. See `docs/project-overview.md` for full architecture.

## Claude Code Configuration

### Slash Commands (`.claude/commands/`)
- **`/auto-tasks`** — 자동으로 tasks.md의 태스크를 순서대로 실행 (multi-agent orchestrator)
- **`/next-task`** — 다음 하나의 태스크만 실행
- **`/task-status`** — 현재 태스크 진행 상황 표시
- `/code-review` — Full code review with severity ratings
- `/python-review` — Python-specific code review
- `/plan` — Create implementation plan for a feature
- `/verify` — Verify changes work correctly
- `/build-fix` — Diagnose and fix build errors
- `/tdd` — Test-driven development workflow
- `/test-coverage` — Analyze and improve test coverage
- `/quality-gate` — Run quality checks
- `/checkpoint` — Save progress checkpoint
- `/refactor-clean` — Clean up and refactor code
- `/update-docs` — Update documentation

### Agents (`.claude/agents/`)
**task-executor** (태스크 자동 실행), architect, planner, code-reviewer, python-reviewer, security-reviewer, database-reviewer, build-error-resolver, refactor-cleaner, doc-updater, tdd-guide

### Skills (`.claude/skills/`)
python-patterns, python-testing, frontend-patterns, api-design, docker-patterns, backend-patterns, coding-standards, security-review, tdd-workflow, deployment-patterns, database-migrations, e2e-testing, search-first, verification-loop

### Rules (`.claude/rules/`)
- `common/` — General coding style, git workflow, security, testing, performance
- `python/` — Python-specific patterns, security, testing
- `typescript/` — TypeScript-specific patterns, security, testing
