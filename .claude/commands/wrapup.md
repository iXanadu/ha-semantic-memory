Create a session progress document for today's work:

1. **Create a new file** in `claude/session_progress/` with format: `YYYY-MM-DD_brief_description.md`
   - Include session overview and objectives
   - List major accomplishments with technical details
   - List files modified/created with specific changes
   - Document bugs fixed and how they were resolved
   - Note any architectural decisions made
   - List pending tasks or issues for next session

2. **Update `claude/CODEBASE_STATE.md`**:
   - Update "Last Updated" date
   - Update "Recent Major Work" section with today's work
   - Update "Next Planned Work" based on what remains
   - Update test count if tests were added/changed

3. **Update `claude/CONTEXT_MEMORY.md`**:
   - Update current status with today's accomplishments
   - Mark completed items
   - Update next session priorities
   - Update known issues

4. **Store session summary in persistent memory**:
   - `memory_store` at `scope=project` with key `session/YYYY-MM-DD-brief-desc` — for next session continuity
   - If any fix, pattern, or lesson is generalizable, store ALSO at `scope=shared` with a `lesson/` or `fix/` key prefix

5. **Commit changes**:
   - `git add` the updated state files and session progress
   - `git commit` with a descriptive message
   - `git push`

6. **Summary**: Provide a brief recap of what should be remembered for the next session
