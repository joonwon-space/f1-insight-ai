# Auto Task Executor

You are a task orchestrator for the F1 Insight AI project. Your job is to automatically execute tasks from `docs/plan/tasks.md` one by one.

## Orchestration Process

### Step 1: Determine Current State
1. Read `docs/plan/tasks.md` to get the full task list.
2. Read `docs/analysis/project-analysis.md` to understand the current project state.
3. Run `git log --oneline` to check commit history for completed tasks.
4. Check tasks.md for ✅ markers.
5. Identify the **next pending task** (the first one not yet completed).

### Step 2: Execute the Task
For each pending task, use the **Agent tool** to spawn a `task-executor` sub-agent with:
- The task ID and title (e.g., "Task 0.2 — Docker Compose 인프라 구성")
- The full task description and requirements
- The current project state context (from project-analysis.md and file tree)
- Reference to relevant project docs: `docs/project-overview.md`, `CLAUDE.md`

**IMPORTANT**: Pass ALL of the following context to the sub-agent:
- Task requirements copied verbatim from tasks.md
- Current project file structure (run `find` excluding node_modules/.git/.claude)
- Content of files the task needs to modify (e.g., docker-compose.yml, pyproject.toml)
- The project's code conventions from CLAUDE.md

### Step 3: Verify the Work
After the sub-agent completes, run verification:

**Backend changes:**
```bash
cd backend && ruff check . && ruff format --check .
pytest  # if tests exist
```

**Frontend changes:**
```bash
cd frontend && npm run lint
npm run build  # type check + build verification
```

**Docker changes:**
```bash
docker compose config  # validate compose file
```

If verification **fails**, fix the issues directly (do NOT spawn another agent). Re-run verification until it passes.

### Step 4: Update tasks.md
Mark the completed task by changing its heading to include a status:
```
### Task X.Y — Task Title ✅
```

### Step 5: Update project-analysis.md
**이 단계는 필수입니다. 절대 건너뛰지 마세요.**

Read the current `docs/analysis/project-analysis.md` and update ALL of the following sections:

1. **현재 진행 상황** — Phase별 완료/전체 카운트 및 진행률 업데이트
2. **아키텍처 현황** — 구현된 컴포넌트 체크리스트 업데이트, 미구현 항목에서 제거
3. **기술 스택 상세** — 패키지 상태 변경 (미사용 → 사용중 등)
4. **파일 구조** — 새로 생성/수정된 파일 반영
5. **이슈 및 개선 사항** — 구현 중 발견된 이슈, 기술 부채, 리스크 기록
6. **태스크 완료 로그** — 새 행 추가: 태스크명, 완료일, 커밋 해시, 변경 요약
7. **추후 태스크 제안** — 구현 과정에서 떠오른 추가 태스크 아이디어 기록

분석 내용은 다음을 반드시 포함해야 합니다:
- 이번 태스크에서 만든/수정한 파일 목록과 각각의 역할
- 구현 시 내린 설계 결정과 그 이유
- 발견된 문제점이나 향후 개선이 필요한 부분
- 다음 태스크와의 연관성이나 의존성

### Step 6: Commit & Push
1. Stage all changed files: `git add -A` (but check for sensitive files first)
2. Commit with conventional commit format:
   ```
   feat: implement Task X.Y — <brief English description>
   ```
3. Push to remote: `git push`

### Step 7: Proceed to Next Task
After commit/push, repeat from Step 1 for the next task. Continue until:
- All tasks in the current Phase are complete, OR
- You encounter a task that requires external dependencies not available (e.g., API keys, running services)
- The user interrupts

## Rules
- Execute ONE task at a time. Do not parallelize tasks — they may have dependencies.
- Each task = one commit. Keep commits atomic.
- If a task seems too large, break it into sub-steps but keep it as one commit.
- If a task requires Docker services to be running for tests, note it but don't block on it.
- Skip Phase 6 (YouTube Automation) unless explicitly asked — it's Phase 2 expansion.
- Always read existing files before modifying them.
- Follow the code conventions in CLAUDE.md strictly.
- **project-analysis.md 업데이트를 절대 빠뜨리지 않는다.**

## Sub-Agent Prompt Template

When spawning the task-executor agent, use this structure:

```
You are implementing Task {ID} for the F1 Insight AI project.

## Task Requirements
{paste task requirements from tasks.md}

## Current Project State
{paste file tree}
{paste project-analysis.md 요약 - 아키텍처 현황 및 기술 스택 상태}

## Relevant Files
{paste content of files that need modification}

## Code Conventions
- Backend: Python 3.12+, FastAPI, async everywhere, Ruff linting, Pydantic v2
- Frontend: Next.js 15 App Router, TypeScript strict, Tailwind CSS v4, @/* imports
- See CLAUDE.md for full conventions

## Instructions
1. Implement ALL requirements listed above
2. Write clean, production-ready code
3. Add type hints to all Python functions
4. Follow existing patterns in the codebase
5. Do NOT create test files unless the task specifically asks for tests
6. Do NOT modify files outside the scope of this task
```

## Now Begin
Start by reading `docs/plan/tasks.md`, `docs/analysis/project-analysis.md`, and `git log --oneline` to determine the next task.
