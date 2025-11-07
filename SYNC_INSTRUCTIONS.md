# 🔄 EXACT SYNC INSTRUCTIONS - STEP BY STEP

## WHERE YOU ARE NOW

**Home Computer:** `C:\Users\Tonk\Desktop\BreweryManager`
**Brewery Computer:** `C:\Users\darre\Desktop\BreweryManager`
**Branch:** `claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx`

---

## 📅 SCENARIO 1: TONIGHT AT HOME

You want to work on the project at home tonight.

### Step 1: Open Command Prompt
```
Windows Key + R
Type: cmd
Press Enter
```

### Step 2: Navigate to Project
```cmd
cd C:\Users\Tonk\Desktop\BreweryManager
```

### Step 3: Get Latest Code
```cmd
git pull origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
```

**What this does:** Downloads any changes made at the brewery

### Step 4: Work on Your Code
```cmd
python main.py
```
- Make your changes
- Edit files
- Test features

### Step 5: When You're Done - Save Your Changes

**See what you changed:**
```cmd
git status
```

**Add ALL your changes:**
```cmd
git add .
```

**Commit with a message describing what you did:**
```cmd
git commit -m "Added inventory tracking module"
```
*(Replace the message with what YOU actually did)*

**Send changes to GitHub:**
```cmd
git push origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
```

### Step 6: Confirm It Worked
You should see:
```
To https://github.com/tonka1973/BreweryManager.git
   [some numbers] -> claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
```

**✅ DONE! Your changes are saved to GitHub**

---

## 📅 SCENARIO 2: TOMORROW AT THE BREWERY

You arrive at the brewery and want to continue where you left off at home.

### Step 1: Open Command Prompt
```
Windows Key + R
Type: cmd
Press Enter
```

### Step 2: Navigate to Project
```cmd
cd C:\Users\darre\Desktop\BreweryManager
```

### Step 3: Get Your Home Changes
```cmd
git pull origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
```

**What happens:**
- If you made changes at home last night, you'll see them downloading
- Files will update automatically
- You'll see messages like "Updating files..." or "Already up to date"

### Step 4: Work at Brewery
```cmd
python main.py
```
- All your home changes are here!
- Continue working
- Make more changes

### Step 5: When Done at Brewery
```cmd
git status
git add .
git commit -m "Fixed bug in inventory module"
git push origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
```

**✅ DONE! Brewery changes saved**

---

## 📅 SCENARIO 3: BACK HOME THAT NIGHT

### Commands to Run:
```cmd
cd C:\Users\Tonk\Desktop\BreweryManager
git pull origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
python main.py
```

**Your brewery changes are now at home!**

---

## 📅 SCENARIO 4: WORKING WITH CLAUDE (ME)

When I make changes and push them, here's what YOU do:

### At Home:
```cmd
cd C:\Users\Tonk\Desktop\BreweryManager
git pull origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
```

### At Brewery:
```cmd
cd C:\Users\darre\Desktop\BreweryManager
git pull origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
```

**You'll get all my changes!**

---

## 📋 COPY-PASTE CHEAT SHEET

### HOME COMPUTER - START WORKING
```cmd
cd C:\Users\Tonk\Desktop\BreweryManager
git pull origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
python main.py
```

### HOME COMPUTER - FINISH WORKING
```cmd
git add .
git commit -m "What I changed tonight"
git push origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
```

### BREWERY COMPUTER - START WORKING
```cmd
cd C:\Users\darre\Desktop\BreweryManager
git pull origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
python main.py
```

### BREWERY COMPUTER - FINISH WORKING
```cmd
git add .
git commit -m "What I changed at brewery"
git push origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
```

---

## ⚠️ WHAT IF I FORGET TO PUSH?

### Example: You worked at brewery, forgot to push, now you're home

**At home, when you pull:**
```cmd
git pull origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
```

**You'll see:**
```
Already up to date
```

**This means:** You don't have the brewery changes because you forgot to push.

**Solution:**
- Work on something else at home tonight
- OR go back to brewery computer tomorrow and push
- OR remote desktop to brewery and push

---

## ⚠️ WHAT IF I CHANGE SAME FILE ON BOTH COMPUTERS?

**Example:** You edited `recipes.py` at home, forgot to push, then edited it at brewery

**When you pull, Git will say:**
```
CONFLICT (content): Merge conflict in recipes.py
```

**Solution:**
1. Open the file with the conflict
2. Look for lines like this:
```python
<<<<<<< HEAD
Your home version
=======
Your brewery version
>>>>>>> [some numbers]
```
3. Delete the markers and keep the version you want
4. Save the file
5. Run:
```cmd
git add .
git commit -m "Fixed merge conflict"
git push origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
```

**Better solution: DON'T let this happen!**
- Always push when done
- Always pull before starting

---

## 🎯 EXACT DAILY ROUTINE

### MORNING AT BREWERY (8 AM)
```cmd
cd C:\Users\darre\Desktop\BreweryManager
git pull origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
python main.py
```
*Work on project for 2 hours...*
```cmd
git add .
git commit -m "Finished customer module"
git push origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
```

### EVENING AT HOME (7 PM)
```cmd
cd C:\Users\Tonk\Desktop\BreweryManager
git pull origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
python main.py
```
*Work on project for 1 hour...*
```cmd
git add .
git commit -m "Added customer search feature"
git push origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
```

### NEXT MORNING AT BREWERY (8 AM)
```cmd
cd C:\Users\darre\Desktop\BreweryManager
git pull origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
```
**You now have last night's home changes!**

---

## 🔍 HOW TO CHECK IF YOU'RE SYNCED

### Run this command:
```cmd
git status
```

### What you might see:

**1. Everything is synced:**
```
On branch claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
Your branch is up to date with 'origin/claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx'.
nothing to commit, working tree clean
```
**Meaning:** ✅ You're good! Everything is synced.

**2. You have local changes:**
```
Changes not staged for commit:
  modified:   src/modules/recipes.py
```
**Meaning:** You edited files but haven't committed. Run:
```cmd
git add .
git commit -m "Your message"
git push origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
```

**3. You need to pull:**
```
Your branch is behind 'origin/claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx' by 3 commits
```
**Meaning:** There are changes on GitHub you don't have. Run:
```cmd
git pull origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
```

**4. You need to push:**
```
Your branch is ahead of 'origin/claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx' by 2 commits
```
**Meaning:** You committed but didn't push. Run:
```cmd
git push origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
```

---

## 🎓 PRACTICE RIGHT NOW

Let's practice! On your home computer right now:

### Step 1: Check status
```cmd
git status
```

### Step 2: Make a tiny change
Open any file, add a comment like:
```python
# Testing sync - added at home
```

### Step 3: Commit and push
```cmd
git add .
git commit -m "Test sync from home computer"
git push origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
```

### Step 4: Tomorrow at brewery, pull it
```cmd
git pull origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
```

**You should see your comment in the file!**

---

## 📞 TROUBLESHOOTING COMMANDS

### "I don't know if I pushed"
```cmd
git status
```
Look for "Your branch is ahead" = Need to push

### "Did I pull the latest?"
```cmd
git status
```
Look for "Your branch is behind" = Need to pull

### "What did I change?"
```cmd
git diff
```
Shows your changes line by line

### "What files did I change?"
```cmd
git status
```
Lists modified files in red

### "What did I commit recently?"
```cmd
git log --oneline -5
```
Shows last 5 commits

### "Start over, I'm confused"
```cmd
git status
```
Read what it says and follow the suggestions

---

## ✅ SIMPLE RULE

**Every single time you sit down to code:**
```cmd
git pull origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
```

**Every single time you stop coding:**
```cmd
git add .
git commit -m "What you did"
git push origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx
```

**That's literally it!**

---

## 🎯 YOUR EXACT WORKFLOW

### Right now (Home - Tonight):
1. Already have the code at `C:\Users\Tonk\Desktop\BreweryManager`
2. Already ran `git pull` and it works
3. Make some changes if you want
4. When done: `git add . && git commit -m "message" && git push origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx`

### Tomorrow (Brewery):
1. Open cmd: `cd C:\Users\darre\Desktop\BreweryManager`
2. Pull: `git pull origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx`
3. See your home changes!
4. Work on code
5. When done: `git add . && git commit -m "message" && git push origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx`

### Tomorrow Night (Home):
1. Open cmd: `cd C:\Users\Tonk\Desktop\BreweryManager`
2. Pull: `git pull origin claude/setup-local-testing-011CUsJqZ9Ui8ZrMTPn6jQnx`
3. See brewery changes!
4. Continue...

**Repeat forever!**

---

*Is this specific enough? Let me know what's still unclear!*
