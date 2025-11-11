# END SESSION INSTRUCTIONS FOR CLAUDE

When the user says "read end.md", follow these steps:

---

## STEP 1: Check for Uncommitted Changes

Run: `git status`

If there are uncommitted changes, proceed to commit them.

---

## STEP 2: Commit All Changes

```bash
git add .
git commit -m "End of session - [brief summary of work done]"
```

---

## STEP 3: Update Session Log

Update the `SESSION_LOG_YYYY-MM-DD.md` file:
- Mark completed tasks as done
- Add any issues encountered
- List what to do next session

Commit the updated log:
```bash
git add SESSION_LOG_*.md
git commit -m "Update session log"
```

---

## STEP 4: Push to GitHub (with retry logic)

```bash
git push -u origin [current-branch-name]
```

If push fails with network error, retry up to 4 times with delays (2s, 4s, 8s, 16s).

---

## STEP 5: Verify Push Succeeded

Run: `git status`

Should show: "Your branch is up to date with 'origin/...'"

And: `git log origin/[current-branch] --oneline -3`

Should show your recent commits are on GitHub.

---

## STEP 6: Report to User

Tell the user:

```
✅ Session ended successfully!
All changes pushed to: claude/[branch-name]
Summary:
- Total commits: [number]
- Last commit: [message]
- GitHub status: ✅ Synchronized

Safe to close session. Next session: say 'read start.md'
```

---

## CRITICAL

Do not let the user end the session until all these steps are complete!
