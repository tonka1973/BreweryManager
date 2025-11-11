# INSTRUCTIONS FOR HOME COMPUTER SESSION

**Read this to Claude when starting a session on the Home computer**

---

## Problem Summary

The Brewery and Home computers have different code:
- **Brewery computer**: Recipe editor Save/Cancel buttons are NOT visible
- **Home computer**: Recipe editor Save/Cancel buttons ARE visible
- **Root cause**: The two computers are on different branches with different code
- **Goal**: Get both computers synced with the working code that has visible buttons

---

## Task for Claude

Claude, please complete these steps to fix the syncing issue:

### STEP 1: Identify Current Branch and Status

Run these commands and tell me the results:
```cmd
cd C:\Users\Tonk\OneDrive\Desktop\BreweryManager
git branch
git status
git log --oneline -5
```

**Tell me:**
- Which branch am I currently on?
- Is the working tree clean?
- Are there any unpushed commits?

---

### STEP 2: Verify This Code Has Working Buttons

Check the Recipe editor code:
```cmd
powershell "(Get-Content src\gui\recipes.py)[554..575] | ForEach-Object -Begin { $i=555 } -Process { Write-Output ('{0}: {1}' -f $i++, $_) }"
```

**Confirm:**
- Does line 555-575 show the scrollable canvas layout? (Should have `container`, `canvas`, `scrollbar`)
- OR does it show the buggy layout? (Just `main_frame.pack(fill=tk.BOTH, expand=True)`)

If this computer has the buggy layout too, we have a different problem. Stop and tell me.

---

### STEP 3: Push Working Code to Master

If the code on this computer is correct (has scrollable canvas), then push it to master:

```cmd
git checkout master
git status
```

If master is behind or diverged, merge the working branch into master:
```cmd
git merge [branch-name-from-step-1]
```

Then push to GitHub:
```cmd
git push origin master
```

**Important:** If there are merge conflicts, stop and tell me.

---

### STEP 4: Verify Master on GitHub is Updated

After pushing, verify:
```cmd
git log origin/master --oneline -3
```

Confirm that master now contains the working Recipe editor code.

---

### STEP 5: Test the Program

Run the program and verify buttons are still visible:
```cmd
python main.py
```

Open Recipe editor and confirm Save/Cancel buttons are visible.

---

### STEP 6: Document What Was Fixed

Create a note explaining:
1. Which branch had the working code on Home computer
2. What was different from origin/master
3. Confirmation that origin/master is now updated with working code

---

### STEP 7: Provide Instructions for Brewery Computer

Once master is updated on GitHub, tell me the exact commands to run on the Brewery computer to get the fixed code:

**Expected commands:**
```cmd
cd C:\Users\darre\Desktop\BreweryManager
git checkout master
git fetch origin
git reset --hard origin/master
python main.py
```

Verify these commands will work.

---

## Success Criteria

- ✅ Home computer master branch pushed to GitHub
- ✅ Recipe editor buttons are visible on Home computer
- ✅ Clear instructions provided for Brewery computer sync
- ✅ Both computers will follow start.md workflow going forward

---

## If Things Go Wrong

**If Home computer ALSO has the buggy layout:**
Then we need to manually fix the Recipe editor on the Home computer first, test it, then push to master.

**If there are merge conflicts:**
Stop and ask me which version to keep.

**If git push fails:**
Check authentication and try again with proper credentials.

---

**End of Instructions**
