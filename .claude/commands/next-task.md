# Execute Next Task

Quick command to execute just the next pending task from `docs/plan/tasks.md`.

## Process
1. Read `docs/plan/tasks.md` and `docs/analysis/project-analysis.md`
2. Check `git log --oneline` for completed tasks
3. Find the first task not marked with ✅
4. Execute it using the Agent tool with the task-executor agent
5. Verify (lint/test/build)
6. Update tasks.md with ✅
7. **Update `docs/analysis/project-analysis.md`** (필수 — 아래 가이드 참고)
8. Commit and push

Follow the same rules as `/auto-tasks` but stop after completing ONE task.

## project-analysis.md 업데이트 가이드

태스크 완료 후 반드시 `docs/analysis/project-analysis.md`를 업데이트한다:

1. **현재 진행 상황** — 진행률 테이블 업데이트
2. **아키텍처 현황** — 구현/미구현 체크리스트 반영
3. **기술 스택 상세** — 패키지 상태 변경
4. **파일 구조** — 새 파일/디렉토리 추가
5. **이슈 및 개선 사항** — 발견된 이슈, 기술 부채, 리스크
6. **태스크 완료 로그** — 완료 행 추가 (태스크, 날짜, 커밋, 요약)
7. **추후 태스크 제안** — 구현 중 발견된 추가 작업 아이디어

분석은 구체적으로 작성한다:
- 만든/수정한 파일과 역할
- 설계 결정 사항과 이유
- 다음 태스크와의 의존성
