# ⚠️ OUTDATED - DO NOT USE

**This file contains outdated git commands!**

## 📌 USE THESE INSTEAD:
- **For Users:** `SESSION_START.md`
- **For Claude:** `CLAUDE_SESSION_WORKFLOW.md`

---

# 🔄 TWO COMPUTER WORKFLOW GUIDE (OUTDATED)

Working on BreweryManager from both your **Brewery Computer** and **Home Computer**

---

## 🎯 THE WORKFLOW

### When You Start Working (Either Computer)

**ALWAYS pull the latest changes first:**
```cmd
cd C:\Users\[YOUR_USERNAME]\Desktop\BreweryManager
git pull
```

### When You Finish Working (Either Computer)

**ALWAYS commit and push your changes:**
```cmd
git add .
git commit -m "Describe what you changed"
git push
```

---

## 📋 COMPLETE WORKFLOW EXAMPLE

### At the Brewery (Morning):
```cmd
cd C:\Users\darre\Desktop\BreweryManager
git pull
```
*Work on code, make changes...*
```cmd
git add .
git commit -m "Added recipe scaling feature"
git push
```

### At Home (Evening):
```cmd
cd C:\Users\Tonk\Desktop\BreweryManager
git pull
```
*Continue working where you left off...*
```cmd
git add .
git commit -m "Fixed recipe validation bug"
git push
```

### Back at Brewery (Next Day):
```cmd
cd C:\Users\darre\Desktop\BreweryManager
git pull
```
*All your home changes are here! Keep working...*

---

## ✅ SIMPLE 3-STEP PROCESS

### 1️⃣ BEFORE YOU START (Pull)
```cmd
git pull
```
*Gets the latest changes from the other computer*

### 2️⃣ DO YOUR WORK
- Edit code
- Test changes
- Make it work

### 3️⃣ WHEN YOU'RE DONE (Commit & Push)
```cmd
git add .
git commit -m "What you changed"
git push
```
*Sends your changes to GitHub so the other computer can get them*

---

## 🚨 GOLDEN RULES

### Rule #1: ALWAYS PULL FIRST
**Before you start coding each session:**
```cmd
git pull
```

### Rule #2: ALWAYS PUSH WHEN DONE
**Before you leave the computer:**
```cmd
git add .
git commit -m "Your message"
git push
```

### Rule #3: Commit Often
Don't wait until the end of the day. Commit every time you:
- Finish a feature
- Fix a bug
- Make something work
- Take a break

---

## 🎯 QUICK REFERENCE COMMANDS

### Starting Work
```cmd
cd C:\Users\Tonk\Desktop\BreweryManager          # (or \darre at brewery)
git pull
python main.py
```

### During Work
```cmd
# See what files you changed
git status

# See what code you changed
git diff
```

### Finishing Work
```cmd
git add .
git commit -m "Describe your changes"
git push
```

---

## 🔍 CHECK SYNC STATUS ANYTIME

```cmd
git status
```

**What you'll see:**
- `Your branch is up to date` - ✅ You're synced
- `Your branch is behind` - Run `git pull`
- `Your branch is ahead` - Run `git push`
- `Changes not staged` - You have uncommitted work

---

## 💡 BEST PRACTICES

### Good Commit Messages
**Bad:**
```cmd
git commit -m "changes"
git commit -m "stuff"
git commit -m "fix"
```

**Good:**
```cmd
git commit -m "Add recipe scaling to batch module"
git commit -m "Fix login validation bug"
git commit -m "Update dashboard with sales chart"
```

### Commit When You:
- ✅ Finish a feature
- ✅ Fix a bug
- ✅ Complete a module
- ✅ End your work session
- ✅ Switch tasks

### Don't Commit:
- ❌ Code that doesn't run
- ❌ Code with errors
- ❌ Half-finished features (unless you note it)

---

## 🆘 COMMON SCENARIOS

### Scenario 1: "I forgot to push before leaving work!"
**At home:**
```cmd
git pull
```
*You won't have the brewery changes, but that's OK.*
*Just work on something else, or wait until tomorrow.*

### Scenario 2: "I have changes on both computers!"
**If you accidentally worked on both without pulling:**
```cmd
git pull
```
*Git will try to merge automatically.*
*If there are conflicts, you'll need to resolve them.*

### Scenario 3: "I want to see what changed between computers"
```cmd
git log --oneline -10
```
*Shows last 10 commits with messages*

### Scenario 4: "Did I already push?"
```cmd
git status
```
*Tells you if you have unpushed commits*

---

## 🏠 COMPUTER-SPECIFIC PATHS

### Home Computer (Current)
```cmd
cd C:\Users\Tonk\Desktop\BreweryManager
```

### Brewery Computer
```cmd
cd C:\Users\darre\Desktop\BreweryManager
```

---

## 📊 WORKFLOW DIAGRAM

```
BREWERY COMPUTER                    GITHUB                    HOME COMPUTER
================                    ======                    =============

Morning:
  git pull ----------------> Pulls from GitHub
  Work on code
  git add .
  git commit -m "msg"
  git push ----------------> Pushes to GitHub

                                                              Evening:
                              GitHub has your changes ----->   git pull
                                                               Work on code
                                                               git add .
                                                               git commit
                              GitHub gets changes <---------   git push

Next Day:
  git pull ----------------> Gets home changes
  Continue working
```

---

## ✅ DAILY CHECKLIST

### When You Arrive (Either Computer)
- [ ] Open Command Prompt
- [ ] Navigate to BreweryManager folder
- [ ] Run `git pull`
- [ ] Check it says "Already up to date" or downloads changes
- [ ] Start working!

### When You Leave (Either Computer)
- [ ] Save all files
- [ ] Run `git status` to see what changed
- [ ] Run `git add .`
- [ ] Run `git commit -m "What you did"`
- [ ] Run `git push`
- [ ] Wait for "Done" message
- [ ] You're synced! ✅

---

## 🚀 WORKING WITH CLAUDE (AI)

When I (Claude) make changes:
1. I commit and push automatically
2. You just need to `git pull` to get them
3. You can continue working from there
4. When you make changes, commit and push
5. Tell me to pull, and I'll see your changes

**Example conversation:**
```
You: "I added a new feature to recipes"
You: (git commit and push your changes)
You: "Claude, pull the latest changes"
Me: "Got it! I can see your recipe feature. Let me help you..."
```

---

## 🎓 LEARNING GIT GRADUALLY

**Week 1:** Just use these commands
```cmd
git pull
git add .
git commit -m "Your message"
git push
```

**Week 2+:** Learn more as you go
- `git status` - Check what's changed
- `git log` - See history
- `git diff` - See code changes

---

## 📞 NEED HELP?

### Command Not Working?
1. Make sure you're in the right folder
2. Check if Git is installed: `git --version`
3. Try the command again

### Can't Pull?
```cmd
# See what's blocking
git status

# If you have uncommitted changes, commit first
git add .
git commit -m "Work in progress"
git pull
```

### Can't Push?
```cmd
# Usually need to pull first
git pull
git push
```

---

## 🎯 SUMMARY

**3 Commands to Remember:**

1. **Before working:** `git pull`
2. **After working:** `git add . && git commit -m "message" && git push`
3. **Check status anytime:** `git status`

**That's it!** This keeps both computers in sync automatically.

---

## 🎉 YOU'RE READY!

Now you can:
- ✅ Work at the brewery
- ✅ Work at home
- ✅ Never lose your work
- ✅ Always have the latest code
- ✅ Collaborate with Claude across both computers

**Start every session with `git pull`**
**End every session with commit and push**

Happy coding! 🍺

---

*Last Updated: November 6, 2025*
*Branch: claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx*
