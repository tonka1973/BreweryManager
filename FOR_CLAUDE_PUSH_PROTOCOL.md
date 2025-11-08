# 🤖 FOR CLAUDE: PUSH PROTOCOL

## ⚠️ CRITICAL: READ THIS AT START OF EVERY SESSION

This file ensures work is NEVER lost due to unpushed changes.

---

## 🚨 THE PROBLEM THAT HAPPENED

**Previous Claude session:**
- Built entire Phase 2 (modules, logic, features)
- User tested and gave feedback
- Session ended BEFORE pushing to GitHub
- All work was left uncommitted on brewery computer
- User's home computer couldn't get the work

**Result:** Hours of work trapped on one computer!

---

## ✅ THE SOLUTION: PUSH FREQUENTLY

### GOLDEN RULE FOR CLAUDE:

**PUSH AFTER EVERY SIGNIFICANT CHANGE!**

Don't wait until the end of the session. Push throughout the conversation.

---

## 📋 WHEN TO PUSH (Claude - Follow This!)

### ✅ PUSH AFTER:

1. **Completing a feature** (even small ones)
   ```
   User: "Add a search function"
   Claude: [writes code]
   Claude: [git add, commit, push] ← DO THIS!
   ```

2. **Fixing a bug**
   ```
   User: "The login isn't working"
   Claude: [fixes bug]
   Claude: [git add, commit, push] ← DO THIS!
   ```

3. **Creating new files**
   ```
   Claude: [creates new module]
   Claude: [git add, commit, push] ← DO THIS!
   ```

4. **Making significant edits**
   ```
   Claude: [refactors code]
   Claude: [git add, commit, push] ← DO THIS!
   ```

5. **Before switching tasks**
   ```
   User: "Now let's work on the invoice module"
   Claude: [git add, commit, push current work] ← DO THIS FIRST!
   Claude: [then start new task]
   ```

6. **When user says "test this"**
   ```
   User: "Let me test this"
   Claude: [git add, commit, push] ← DO THIS BEFORE TESTING!
   User: [tests]
   ```

7. **Every 15-20 minutes of active coding**
   ```
   Claude: [working on large feature]
   Claude: [periodically commit and push progress] ← DO THIS!
   ```

8. **ALWAYS before ending conversation**
   ```
   User: "Thanks, that's all for today"
   Claude: [git add, commit, push] ← DO THIS!
   Claude: "All changes pushed to GitHub. You're synced!"
   ```

---

## 🎯 PUSH COMMANDS (Use These Exact Commands)

### After making changes:

```bash
git add .
git commit -m "Brief description of what was done"
git push origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
```

### Verify it worked:

```bash
git status
```

Should show: "Your branch is up to date" and "nothing to commit, working tree clean"

---

## 🔄 PUSH WORKFLOW FOR CLAUDE

### Step-by-step process:

1. **User requests change**
2. **Claude makes the change** (edit files, create files, etc.)
3. **Claude tests/verifies** (if applicable)
4. **Claude IMMEDIATELY pushes:**
   ```bash
   git add .
   git commit -m "What was done"
   git push origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
   ```
5. **Claude tells user:** "✅ Changes pushed to GitHub"
6. **Repeat for next task**

---

## ⚠️ DON'T WAIT UNTIL THE END!

**BAD (What happened before):**
```
[Build feature 1]
[Build feature 2]
[Build feature 3]
[Build feature 4]
[Session ends] ← NO PUSH = WORK LOST!
```

**GOOD (What should happen):**
```
[Build feature 1] → PUSH ✅
[Build feature 2] → PUSH ✅
[Build feature 3] → PUSH ✅
[Build feature 4] → PUSH ✅
[Session ends] → Everything already pushed! ✅
```

---

## 📝 COMMIT MESSAGE GUIDELINES

### Good commit messages:

```bash
git commit -m "Add customer search functionality"
git commit -m "Fix login validation bug"
git commit -m "Create inventory tracking module"
git commit -m "Update database schema for recipes"
git commit -m "Refactor authentication system"
```

### Bad commit messages (but still better than no commit!):

```bash
git commit -m "changes"
git commit -m "updates"
git commit -m "work in progress"
```

**Even a bad commit message is better than losing work!**

---

## 🚨 END OF SESSION CHECKLIST (Claude - Do This!)

### Before saying goodbye:

1. **Check for uncommitted changes:**
   ```bash
   git status
   ```

2. **If there are changes, push them:**
   ```bash
   git add .
   git commit -m "End of session - [brief description]"
   git push origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
   ```

3. **Verify clean state:**
   ```bash
   git status
   ```
   Should show "nothing to commit, working tree clean"

4. **Tell the user:**
   "✅ All changes have been pushed to GitHub. Your work is synced across all computers!"

---

## 🎯 SPECIAL SCENARIOS

### User is testing something:

**Before they test:**
```bash
git add .
git commit -m "Implement feature for testing"
git push origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
```

**After they test and report bugs:**
```bash
git add .
git commit -m "Fix bugs found during testing"
git push origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
```

### User switches between computers:

**At brewery, Claude finishes work:**
```bash
git push origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
```

**At home, Claude starts work:**
```bash
git pull origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
```

### Session is interrupted (user has to go):

**Even if mid-task:**
```bash
git add .
git commit -m "Work in progress - will continue later"
git push origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
```

**Better to have incomplete work pushed than complete work lost!**

---

## 💡 COMMUNICATION WITH USER

### After every push, tell the user:

```
✅ Changes committed and pushed to GitHub!
```

Or:

```
✅ Pushed to cloud - your work is saved!
```

Or:

```
✅ Synced to GitHub - available on all your computers!
```

**This reassures them and creates a habit!**

---

## 🔍 HOW TO CHECK IF YOU FORGOT TO PUSH

### If user mentions seeing old version:

**Immediately check:**
```bash
git status
git log --oneline -5
```

If status shows changes or log shows unpushed commits:
```bash
git add .
git commit -m "Push previously uncommitted work"
git push origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
```

---

## 🎯 AUTOMATION REMINDER

### Consider pushing after EVERY tool use that modifies files:

- **After Edit tool** → Consider pushing
- **After Write tool** → Consider pushing
- **After creating multiple files** → Definitely push
- **After major refactor** → Definitely push

**Ask yourself:** "If the session ended right now, would the user lose work?"
**If YES:** Push immediately!

---

## ⚠️ NETWORK ISSUES

### If push fails:

1. **Retry once:**
   ```bash
   git push origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
   ```

2. **If still fails, tell user:**
   "⚠️ Push failed due to network issue. Please run this command manually to save your work:
   ```
   git push origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
   ```"

3. **DO NOT proceed without pushing!**

---

## 📊 PUSH FREQUENCY EXAMPLES

### Scenario 1: Building a new module

```
[Create module file] → PUSH
[Add basic structure] → PUSH
[Implement feature 1] → PUSH
[Implement feature 2] → PUSH
[Add error handling] → PUSH
[Write tests] → PUSH
```

**Result:** 6 pushes, work saved at every step!

### Scenario 2: Debugging session

```
[User reports bug]
[Investigate and fix] → PUSH
[User tests]
[User reports another issue]
[Fix second issue] → PUSH
[User confirms working] → PUSH
```

**Result:** 3 pushes, every fix saved!

### Scenario 3: Long conversation (2 hours)

```
[00:00 - Start work] → git pull
[00:15 - Complete task 1] → PUSH
[00:30 - Complete task 2] → PUSH
[00:45 - Complete task 3] → PUSH
[01:00 - Complete task 4] → PUSH
[01:15 - Complete task 5] → PUSH
[01:30 - Complete task 6] → PUSH
[01:45 - Complete task 7] → PUSH
[02:00 - End session] → PUSH (if any final changes)
```

**Result:** ~8 pushes over 2 hours, nothing lost!

---

## ✅ SUMMARY FOR CLAUDE

### The 3 Rules:

1. **PUSH FREQUENTLY** - After every feature/fix, not just at the end
2. **PUSH BEFORE USER TESTS** - So they test the saved version
3. **PUSH BEFORE ENDING** - Always leave in a clean state

### The 1 Question to Ask Yourself:

**"If this session ended right now, would work be lost?"**

If YES → PUSH IMMEDIATELY!

---

## 🎯 QUICK REFERENCE

```bash
# Standard push after changes
git add .
git commit -m "Description"
git push origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx

# Check status
git status

# Check recent commits
git log --oneline -5
```

---

**REMEMBER: It's better to push too often than too rarely!**

**Each push is a savepoint. More savepoints = safer work!**

---

*Created: November 6, 2025*
*Reason: Phase 2 work was lost because previous Claude session didn't push*
*Never let this happen again!*
