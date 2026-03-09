# Execute Next Task

Quick command to execute just the next pending task from `docs/plan/tasks.md`.

## Process
1. Read `docs/plan/tasks.md` and check `git log --oneline` for completed tasks
2. Find the first task not marked with ✅
3. Execute it using the Agent tool with the task-executor agent
4. Verify (lint/test/build)
5. Update tasks.md with ✅
6. Commit and push

Follow the same rules as `/auto-tasks` but stop after completing ONE task.
