# START SESSION INSTRUCTIONS FOR CLAUDE

**When the user says "read start.md", follow these steps:**

---

## STEP 1: Read Project Context Files

Read these files to understand the project:
1. CLAUDE_SESSION_WORKFLOW.md
2. README.md (first 100 lines)
3. PROGRESS.md (if it exists)

---

## STEP 2: Check Available Branches

Run this command to see previous session branches:
```bash
git branch -r | grep "claude/"
```

Identify the most recent `claude/*` branch.

---

## STEP 3: Provide Merge Commands to User

Give the user these exact commands (fill in the actual branch name you found):

```
Please run these commands to merge the previous session's work:

cd C:\Users\darre\Desktop\BreweryManager
git fetch origin
git checkout master
git merge origin/claude/<MOST-RECENT-BRANCH-NAME> --no-edit
```

Tell them: "Let me know when you've run these commands!"

---

## STEP 4: Wait for User Confirmation

Wait for the user to confirm they've run the commands.

---

## STEP 5: Check Current Git Status

After user confirms, run:
```bash
git branch --show-current
git status
git log --oneline -3
```

---

## STEP 6: Create Session Log

Create a file named `SESSION_LOG_YYYY-MM-DD.md` with this content:

```markdown
# Session Log - [Today's Date]

## Session Info
- **Session ID:** [current session ID from branch name]
- **Branch:** [current branch]
- **Previous Branch Merged:** [branch they just merged]

## Starting State
- Git status: [clean/modified]
- Last commit: [latest commit message]

## Tasks Completed This Session
- [ ] (Will be updated as we work)

## Issues Encountered
- None yet

## Next Session TODO
- (Will be updated at end of session)

---
*Session started: [timestamp]*
```

---

## STEP 7: Report Status and Ask What to Work On

Say something like:

```
✅ Session started successfully!

Current status:
- Branch: [current branch]
- Git status: [clean/uncommitted changes]
- Last commit: [commit message]

What would you like to work on today?
```

---

## IMPORTANT REMINDERS

- Push frequently after each feature/fix
- Update the session log as tasks are completed
- At end of session, do final push and update session log
- Always work on a claude/* branch, never on master directly

---

**That's it! Follow these steps every time the user says "read start.md"**
