# 🤖 CLAUDE SESSION WORKFLOW

**THE DEFINITIVE GUIDE - Read this at the start of every session**

---

## 🚨 CRITICAL UNDERSTANDING

### The Session Branch Limitation

**Claude Code can ONLY push to branches matching:** `claude/*<current-session-id>`

**This means:**
- Each Claude session gets a unique session ID
- Session A can push to `claude/anything-ABC123` ✅
- Session B can push to `claude/anything-XYZ789` ✅
- But Session B **CANNOT** push to `claude/anything-ABC123` ❌ (wrong session ID)

**Therefore:** Every session creates a NEW branch, and previous session branches become read-only.

---

## 📋 WORKFLOW FOR USERS

### At the Start of EVERY New Claude Session:

**1. Open Command Prompt and navigate to project:**
```cmd
cd C:\Users\[YOUR_USERNAME]\Desktop\BreweryManager
```

**2. Fetch all branches from GitHub:**
```cmd
git fetch origin
```

**3. List previous Claude session branches:**
```cmd
git branch -r | grep "claude/"
```

**4. Checkout master and merge previous session work:**
```cmd
git checkout master
git merge origin/claude/<PREVIOUS-SESSION-BRANCH> --no-edit
```
*(Replace `<PREVIOUS-SESSION-BRANCH>` with the most recent branch from step 3)*

**5. Tell Claude:**
> "Ready to continue"

---

## 🤖 WORKFLOW FOR CLAUDE

### At the Start of Each Session:

**1. Check current branch:**
```bash
git branch --show-current
```

**2. If on master, create new session branch:**
```bash
git checkout -b claude/<descriptive-name>-<SESSION_ID>
```

**3. Work on this branch for the entire session**

### During the Session:

**Push frequently after:**
- ✅ Completing a feature
- ✅ Fixing a bug
- ✅ Creating new files
- ✅ Before user tests
- ✅ Every 15-20 minutes of coding
- ✅ Before switching tasks

**Standard push commands:**
```bash
git add .
git commit -m "Description of changes"
git push -u origin claude/<current-branch>
```

### At the End of Session:

**1. Final push:**
```bash
git status
git add .
git commit -m "End of session - [summary]"
git push origin claude/<current-branch>
```

**2. Verify clean state:**
```bash
git status
```
Should show: "nothing to commit, working tree clean"

**3. Tell user:**
"✅ All changes pushed to `claude/<branch-name>`. Follow SESSION_START.md next time."

---

## 🔄 TWO-COMPUTER WORKFLOW

### Computer A (Brewery):
1. Start session, merge previous work into master
2. Claude creates `claude/session-A-123`
3. Work and push to `claude/session-A-123`
4. End session

### Computer B (Home):
1. Fetch from GitHub
2. Merge `claude/session-A-123` into local master
3. Claude creates `claude/session-B-456`
4. Work and push to `claude/session-B-456`
5. End session

### Back to Computer A:
1. Fetch from GitHub
2. Merge `claude/session-B-456` into local master
3. Continue...

**Result:** Master branch on each computer stays current with all work from all sessions.

---

## ✅ BENEFITS OF THIS WORKFLOW

1. **No session conflicts** - Each session has its own branch
2. **Full history** - Every session's work is preserved
3. **Cross-computer sync** - Merge branches to share work
4. **Stop hook compatible** - Allows unpushed commits on master
5. **Future-proof** - Works with Claude Code's restrictions

---

## 🚨 IMPORTANT NOTES

### For Users:
- **Master branch is local only** - Used for merging session work
- **Never manually edit** on claude/* branches - Let Claude manage them
- **Always start new sessions** by merging previous work first

### For Claude:
- **Never try to push to master** - You'll get a 403 error
- **Always work on claude/* branches** - It's the only way
- **Push frequently** - Don't wait until the end
- **Session branches are write-once** - Once session ends, branch becomes read-only

---

## 📁 FILE LOCATIONS

- **This file:** `CLAUDE_SESSION_WORKFLOW.md` - For Claude sessions
- **User guide:** `SESSION_START.md` - Quick commands for users
- **Stop hook:** `~/.claude/stop-hook-git-check.sh` - Modified to allow master

---

## 🔧 TROUBLESHOOTING

### "403 error when pushing to master"
**Solution:** Don't push to master. Work on `claude/*` branch instead.

### "Can't push to previous session's branch"
**Solution:** Normal! Each session needs its own branch. Create a new one.

### "Merge conflicts"
**Solution:** Unlikely with this workflow. If it happens, resolve manually or start fresh.

### "Lost work between sessions"
**Solution:** Previous session didn't push. Check GitHub for available branches, merge what exists.

---

## 📊 QUICK REFERENCE

### User Commands (Start of Session):
```bash
git fetch origin
git branch -r | grep "claude/"
git checkout master
git merge origin/claude/<previous-branch> --no-edit
```

### Claude Commands (During Session):
```bash
# Create session branch
git checkout -b claude/<name>-<session-id>

# Regular push
git add .
git commit -m "What changed"
git push -u origin claude/<current-branch>

# Check status
git status
```

---

## 🎯 SUCCESS CHECKLIST

### For Users Starting a Session:
- [ ] Fetched latest from GitHub
- [ ] Listed available claude/* branches
- [ ] Merged previous session into master
- [ ] Told Claude "Ready to continue"

### For Claude During a Session:
- [ ] Created unique session branch
- [ ] Pushed after each significant change
- [ ] Verified pushes succeeded
- [ ] Ended with clean git status

### For Claude Ending a Session:
- [ ] All changes committed
- [ ] Final push completed
- [ ] Git status shows clean
- [ ] Told user about SESSION_START.md

---

**This workflow ensures no work is ever lost and all sessions can collaborate smoothly!**

---

*Created: November 7, 2025*
*Reason: Claude Code session branch restrictions require this workflow*
*Replaces: All previous git workflow documents*
