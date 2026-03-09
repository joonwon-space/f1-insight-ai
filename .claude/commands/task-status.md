# Task Status

Show the current progress of the project tasks.

## Process
1. Read `docs/plan/tasks.md`
2. Check `git log --oneline` for task-related commits
3. Display a summary table:

```
Phase | Task | Status | Commit
------|------|--------|-------
0     | 0.1  | ✅ Done | abc1234
0     | 0.2  | ⏳ Next |
0     | 0.3  | ⬜ Todo |
...
```

4. Show which task is next to be executed
5. Show any blockers or dependencies for the next task
