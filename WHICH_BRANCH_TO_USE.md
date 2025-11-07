# ⚠️ CRITICAL: WHICH BRANCH TO USE

## 🎯 USE THIS BRANCH FOR ALL WORK:

```
master
```

**This is your MAIN development branch!** It has:
- ✅ All Phase 2 modules (dashboard, batches, customers, inventory, etc.)
- ✅ All working features
- ✅ All documentation
- ✅ Everything you need

---

## ❌ DO NOT USE THESE BRANCHES:

### `claude/work-in-progress-011CUrnRK9wxKPu695Qap243`
- **What it is:** Previous development branch
- **Status:** Merged into master, no longer needed

### `claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx`
- **What it is:** Documentation-only branch from home PC setup
- **What it has:** Git guides, setup scripts, documentation
- **Status:** Merged, no longer needed

### `claude/implement-cmd-commands-011CUsC4oq5JagebZSgigwEu`
- **What it is:** Old session from different time
- **Status:** Outdated, ignore this

### `claude/session-planning-011CUtLcUBiAQZp8BoZ55NS8`
- **What it is:** Old session from different time
- **Status:** Outdated, ignore this

---

## 📋 DAILY WORKFLOW

### AT BREWERY - START OF DAY:
```cmd
cd C:\Users\darre\Desktop\BreweryManager
git checkout master
git pull origin master
python main.py
```

### AT BREWERY - END OF DAY:
```cmd
git add .
git commit -m "What I worked on today"
git push origin master
```

### AT HOME - EVENING:
```cmd
cd C:\Users\Tonk\OneDrive\Desktop\BreweryManager
git checkout master
git pull origin master
python main.py
```

### AT HOME - WHEN DONE:
```cmd
git add .
git commit -m "What I worked on tonight"
git push origin master
```

---

## ✅ VERIFY YOU'RE ON THE RIGHT BRANCH

### Check current branch:
```cmd
git branch
```

**Should show:** `* master` (with the asterisk)

### If you're on the wrong branch:
```cmd
git checkout master
```

---

## 🎯 WHAT'S ON THIS BRANCH

### Code Files (Your Phase 2 Work):
- `src/gui/dashboard.py` - Dashboard with stats and charts
- `src/gui/batches.py` - Batch/brewing management
- `src/gui/customers.py` - Customer CRM
- `src/gui/inventory.py` - Inventory tracking
- `src/gui/invoicing.py` - Invoice generation
- `src/gui/recipes.py` - Recipe management
- `src/gui/sales.py` - Sales and dispatch
- `src/gui/duty.py` - UK duty calculator
- `src/gui/labels.py` - Label printing
- `src/gui/main_window.py` - Main application window

### Documentation Files:
- `README.md` - Project overview
- `CRITICAL_READ_THIS.md` - Git push reminders
- `FOR_CLAUDE_PUSH_PROTOCOL.md` - Claude's push guidelines
- `GIT_EXPLAINED_SIMPLY.md` - Git tutorial
- `SYNC_INSTRUCTIONS.md` - Step-by-step sync guide
- `TWO_COMPUTER_WORKFLOW.md` - Two-computer workflow
- `LOCAL_SETUP_GUIDE.md` - Local setup instructions
- `TEST_RESULTS.md` - Test results
- `START_HERE.md` - Quick start
- `WHICH_BRANCH_TO_USE.md` - This file!

### Test/Setup Files:
- `test_backend.py` - Backend testing
- `test_installation.py` - Installation testing
- `setup.bat` - Windows setup script

---

## 🚨 COMMON MISTAKE TO AVOID

**DON'T accidentally work on the wrong branch!**

### Signs you're on the wrong branch:
- ❌ You don't see your modules (dashboard, batches, etc.)
- ❌ The app looks like "Phase 1" only
- ❌ Git status shows a different branch name

### How to fix:
```cmd
git checkout master
git pull origin master
```

---

## 🎯 SIMPLE RULE

**ALWAYS use:** `master`

**NEVER use:** Any other branch (unless you have a specific reason)

---

## 📞 QUICK CHECK COMMANDS

### Am I on the right branch?
```cmd
git branch
```
Look for `*` next to `master`

### Do I have the latest code?
```cmd
git status
```
Should say "Your branch is up to date"

### What files do I have?
```cmd
dir src\gui
```
Should see: dashboard.py, batches.py, customers.py, etc.

---

## ✅ CHECKLIST - PRINT THIS OUT!

**Before starting work:**
- [ ] Open Command Prompt
- [ ] Navigate to BreweryManager folder
- [ ] Run: `git branch` (check you're on master)
- [ ] Run: `git pull origin master`
- [ ] Launch: `python main.py`

**Before ending work:**
- [ ] Run: `git status` (see what changed)
- [ ] Run: `git add .`
- [ ] Run: `git commit -m "What I did"`
- [ ] Run: `git push origin master`
- [ ] Wait for "Done" message

---

## 🎉 SUMMARY

**One branch to rule them all:**
```
master
```

**Use it everywhere:**
- ✅ Brewery computer
- ✅ Home computer
- ✅ Any computer you work on

**Ignore everything else!**

---

*Updated: November 7, 2025*
*All development branches merged into master*
*Solution: Always use master for ALL development*
