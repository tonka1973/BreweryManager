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

## STEP 3: Ask Which PC User is On

Ask the user:
```
Which computer are you on?
1. Home PC
2. Brewery PC
3. Other (please specify)
```

---

## STEP 4: Check PC Information

Read the `PC_INFO.md` file to get the correct path for the user's computer.

**If the PC is listed in PC_INFO.md:**
- Use the path from that file

**If the PC is NOT listed (user said "Other" or new PC):**
1. Ask: "What is the full path to the BreweryManager folder on this computer?"
2. When they provide it, add a new entry to PC_INFO.md with:
   - PC name/description
   - Full path
   - User
   - OS (if known)

---

## STEP 5: Provide Merge Commands to User

Give the user these exact commands (fill in the actual branch name you found AND the correct path from PC_INFO.md):

```
Please run these commands to merge the previous session's work:

cd [PATH-FROM-PC-INFO]
git fetch origin
git checkout master
git merge origin/claude/<MOST-RECENT-BRANCH-NAME> --no-edit
```

Tell them: "Let me know when you've run these commands!"

---

## STEP 6: Wait for User Confirmation

Wait for the user to confirm they've run the commands.

---

## STEP 7: Check Current Git Status and Sync Claude Branch

After user confirms, run:
```bash
git branch --show-current
git status
git log --oneline -3
```

**CRITICAL: Sync Claude branch with master to prevent merge conflicts later**

If on a claude/* branch, merge master into it:
```bash
git merge master --no-edit
```

This ensures the Claude branch has all the latest changes from the previous session merge.

---

## STEP 8: Create Session Log

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

## STEP 9: Report Status and Ask What to Work On

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
