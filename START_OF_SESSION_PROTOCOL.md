# 🤖 FOR CLAUDE: START OF SESSION PROTOCOL

**Read this file FIRST when the user starts a new session!**

---

## 🎯 TRIGGER PHRASES

When the user says any of these:
- "start session"
- "new session"
- "read files"
- "begin"
- "continue from last time"

**→ Follow this protocol!**

---

## 📖 STEP 1: READ THESE FILES (IN ORDER)

**Read these files to understand the project state:**

1. **SESSION_START.md** - User commands for starting sessions
2. **CLAUDE_SESSION_WORKFLOW.md** - Your workflow guide
3. **README.md** - Project overview
4. **PROGRESS.md** - Current status (if exists)

**Optional (if user mentions specific issues):**
5. **TECHNICAL_SPECIFICATION.md** - Full requirements
6. **TESTING_CHECKLIST.md** - What needs testing

---

## 💬 STEP 2: GREET THE USER

Say something like:

```
👋 Hi! I've read the project files and I'm ready to help with BreweryManager.

Before we continue, let's sync your local repository with the previous session's work.
```

---

## 📋 STEP 3: PROVIDE SESSION START COMMANDS

**Give the user these commands:**

```
Please run these commands to merge the previous session's work:

1. Fetch latest branches:
   git fetch origin

2. List previous session branches:
   git branch -r | grep "claude/"

3. Checkout master:
   git checkout master

4. Merge the most recent claude/* branch:
   git merge origin/claude/<BRANCH-NAME> --no-edit

Replace <BRANCH-NAME> with the most recent branch from step 2.

Once done, let me know and I'll check the current state!
```

---

## 📝 STEP 4: CREATE SESSION LOG

**After user confirms they've run the commands, create a session log:**

File: `SESSION_LOG_<DATE>.md`

Template:
```markdown
# Session Log - [DATE] [TIME]

## Session Info
- **Session ID:** <current-session-id>
- **Branch:** claude/<name>-<session-id>
- **Previous Branch:** <previous-branch-merged>
- **User:** [Username from git]

## Starting State
- Git status: [clean/modified]
- Current branch: [branch-name]
- Last commit: [commit-hash] [commit-message]

## Tasks Completed This Session
- [ ] Task 1
- [ ] Task 2

## Issues Encountered
- None yet

## Next Session TODO
- Continue from here

---
*Log created: [timestamp]*
```

---

## 🔍 STEP 5: CHECK CURRENT STATE

Run these commands:
```bash
git branch --show-current
git status
git log --oneline -5
```

Report to user:
- What branch they're on
- If there are uncommitted changes
- Recent commits

---

## 🚀 STEP 6: ASK WHAT TO WORK ON

Say something like:

```
✅ All set! Your repository is up to date.

Current status:
- Branch: master
- Status: [clean/modified]
- Last commit: [commit message]

What would you like to work on today?
```

---

## ⚠️ IMPORTANT REMINDERS

### During the Session:
- **Push frequently** (after each feature/fix)
- **Update session log** as tasks are completed
- **Always work on claude/* branch**, not master

### At End of Session:
- **Final push** to ensure all work is saved
- **Update session log** with summary
- **Tell user** the branch name for next session

---

## 📂 FILE LOCATIONS

- **This file:** `START_OF_SESSION_PROTOCOL.md` (for Claude)
- **User guide:** `SESSION_START.md` (for users)
- **Workflow:** `CLAUDE_SESSION_WORKFLOW.md` (for Claude)
- **Session logs:** `SESSION_LOG_*.md` (created each session)

---

## 🎯 QUICK CHECKLIST

At start of EVERY session:
- [ ] User said trigger phrase
- [ ] Read key files (SESSION_START.md, CLAUDE_SESSION_WORKFLOW.md, README.md)
- [ ] Greeted user
- [ ] Provided SESSION_START commands
- [ ] User confirmed they ran commands
- [ ] Created session log
- [ ] Checked git status
- [ ] Asked what to work on
- [ ] Ready to begin!

---

**Follow this protocol for a smooth start to every session!**
