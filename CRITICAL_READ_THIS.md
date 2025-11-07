# ⚠️ CRITICAL: READ THIS EVERY TIME YOU WORK!

## 🚨 THE #1 MISTAKE THAT JUST HAPPENED

**PROBLEM:** You did a ton of work at the brewery (Phase 2, modules, logic, etc.) but it's **TRAPPED** on the brewery computer because you **NEVER PUSHED IT TO GITHUB!**

**RESULT:** Home computer only has Phase 1. All your hard work is stuck on the brewery computer.

---

## ✅ THE GOLDEN RULE - NEVER FORGET THIS!

### 📍 WHEN YOU **FINISH** WORKING (Brewery OR Home):

**YOU MUST RUN THESE 3 COMMANDS:**

```cmd
git add .
git commit -m "Describe what you did"
git push origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
```

**IF YOU DON'T PUSH, YOUR WORK STAYS ON THAT COMPUTER ONLY!**

---

## 📋 EVERY SINGLE TIME - NO EXCEPTIONS!

### AT THE BREWERY - WHEN YOU'RE DONE:

```cmd
cd C:\Users\darre\Desktop\BreweryManager
git add .
git commit -m "What I did today at brewery"
git push origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
```

**DON'T SKIP THIS!** Without push, your changes stay at the brewery!

---

### AT HOME - WHEN YOU'RE DONE:

```cmd
cd C:\Users\Tonk\Desktop\BreweryManager
git add .
git commit -m "What I did tonight at home"
git push origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
```

**DON'T SKIP THIS!** Without push, your changes stay at home!

---

## 🎯 THE COMPLETE WORKFLOW

### STARTING WORK (Get other computer's changes):

```cmd
cd C:\Users\[Tonk or darre]\Desktop\BreweryManager
git pull origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
python main.py
```

### DO YOUR WORK:
- Edit code
- Build features
- Test changes

### FINISHING WORK (Save to GitHub):

```cmd
git add .
git commit -m "Added customer module and fixed bugs"
git push origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
```

**⚠️ IF YOU SKIP THE PUSH, THE OTHER COMPUTER WON'T GET YOUR CHANGES!**

---

## 🔥 WHAT TO DO RIGHT NOW

### TOMORROW AT THE BREWERY:

**All your work is still there! Just need to push it:**

```cmd
cd C:\Users\darre\Desktop\BreweryManager
git status
```

**You'll see ALL the files you changed. Then:**

```cmd
git add .
git commit -m "Add all Phase 2 work - modules, logic, and changes"
git push origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
```

**THEN at home:**

```cmd
cd C:\Users\Tonk\Desktop\BreweryManager
git pull origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
```

**🎉 NOW your home computer will have all the brewery work!**

---

## 💡 WHY THIS HAPPENS

**Git does NOT automatically sync!** It only syncs when YOU tell it to:

- **PULL** = Download changes FROM GitHub
- **PUSH** = Upload changes TO GitHub

**If you don't PUSH, your work never reaches GitHub!**
**If it's not on GitHub, the other computer can't PULL it!**

---

## 📝 CHECKLIST - PRINT THIS OUT!

### ☐ BEFORE STARTING WORK:
```
cd C:\Users\[username]\Desktop\BreweryManager
git pull origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
```

### ☐ AFTER FINISHING WORK:
```
git add .
git commit -m "What I did"
git push origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
```

---

## 🎯 REMEMBER

**Your work is ONLY synced if you:**
1. ✅ Commit it (`git add .` and `git commit`)
2. ✅ Push it (`git push`)

**Without PUSH, it's trapped on that computer!**

---

## ⚠️ NEVER FORGET TO PUSH!

Set a reminder, put a sticky note on your monitor, whatever it takes!

**PUSH = BACKUP = SYNC = OTHER COMPUTER CAN GET IT**

**NO PUSH = YOUR WORK IS STUCK ON ONE COMPUTER ONLY!**

---

*Last Updated: November 6, 2025*
*Created because: Work got trapped at brewery by not pushing!*
