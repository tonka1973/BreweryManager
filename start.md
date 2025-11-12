# START SESSION INSTRUCTIONS FOR CLAUDE

**When the user says "read start.md", follow these steps:**

---

## STEP 1: Ask Which Computer User Is On

**First, ask the user:**

```
Which computer are you on?
1. Brewery
2. Home
3. Other (new computer)
```

**Then read COMPUTER_PATHS.md to get the correct folder path.**

If they answer "Other":
- Ask them for their full path to BreweryManager
- Remind them to add it to COMPUTER_PATHS.md
- Ask if they've completed initial setup (Python, dependencies, etc.)

---

## STEP 2: Read Project Context Files

Read these files to understand the project:
1. COMPUTER_PATHS.md (to get folder paths)
2. CLAUDE_SESSION_WORKFLOW.md
3. README.md (first 100 lines)
4. PROGRESS.md (if it exists)

---

## STEP 3: Check Available Branches (Sorted by Date)

Run this command to see previous session branches sorted by most recent:
```bash
git for-each-ref --sort=-committerdate --format='%(committerdate:short) %(refname:short) - %(subject)' refs/remotes/origin/claude/ | head -10
```

Identify the most recent `claude/*` branch.

IMPORTANT: If there are multiple branches from the same date, choose the one with the LATEST timestamp.

---

## STEP 4: Check for Old Unpushed Local Work

Before merging, check if local master has unpushed commits:
```bash
git checkout master
git status
```

If it says "Your branch is ahead of origin/master by X commits":
- These are OLD commits from a previous session that weren't pushed
- They are OUT OF DATE
- Discard them with: `git reset --hard origin/master`

---

## STEP 5: Provide Merge Commands to User

Give the user these exact commands (fill in the actual branch name AND computer path):

```
Please run these commands to merge the previous session's work:

cd <PATH-FROM-COMPUTER_PATHS.MD>
git fetch origin
git checkout master
git reset --hard origin/master
git merge origin/claude/<MOST-RECENT-BRANCH-NAME> --no-edit
```

**Replace:**
- `<PATH-FROM-COMPUTER_PATHS.MD>` with the correct path from STEP 1
- `<MOST-RECENT-BRANCH-NAME>` with the branch from STEP 3

**What this does:**
- Resets local master to match origin/master (discards any old unpushed work)
- Merges the most recent claude branch into local master
- **Note:** Master will be pushed at END of session after testing/verification

Tell them: "Let me know when you've run these commands!"

**Note:** If merge has conflicts, STOP and ask user which version to keep.

---

## STEP 6: Wait for User Confirmation

Wait for the user to confirm they've run the commands.

---

## STEP 7: Check for New Dependencies

**After user confirms merge, check if requirements.txt was updated:**

Run this command to check if requirements.txt changed:
```bash
git diff HEAD~10..HEAD --name-only | grep requirements.txt
```

**If it shows "requirements.txt":**

Tell the user:
```
⚠️  IMPORTANT: Dependencies have been updated!

Please run this command to install new packages:

pip install -r requirements.txt

This will install any new libraries needed for the updated code.
Without this, the program may crash with import errors!

Let me know when you've run this command.
```

**If requirements.txt didn't change:**
- Skip this message and continue to next step

---

## STEP 8: Check for Database Migrations

**After dependencies are handled, check if any migration scripts exist:**

Run this command to look for migration scripts in recent commits:
```bash
git diff HEAD~10..HEAD --name-only | grep migrate
```

**If it shows any `migrate_*.py` files:**

Tell the user:
```
⚠️  IMPORTANT: Database schema has been updated!

A migration script was found: [filename]

Please run this command BEFORE launching the application:

python src/data_access/[migration_script_name].py

This will add new columns/tables to your database.
Without this, the program will crash when trying to use the new features!

Let me know when you've run the migration script.
```

**If no migration scripts are found:**
- Skip this message and continue to next step

**Common migration scripts:**
- `migrate_batches_schema.py` - Adds O.G./F.G./ABV tracking fields

---

## STEP 9: Check Current Git Status

After dependencies and migrations are handled, run:
```bash
git branch --show-current
git status
git log --oneline -3
```

---

## STEP 10: Create Session Log

Create a file named `SESSION_LOG_YYYY-MM-DD_<session-id>.md` with this content:

**Example filename:** `SESSION_LOG_2025-11-12_011CV4EhkjMSEy84V3cXvgQp.md`
(Use the session ID from the current branch name)

```markdown
# Session Log - [Today's Date]

## Session Info
- **Computer:** [Brewery/Home/Other]
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

**Note:** Including the session ID in the filename prevents overwriting if multiple sessions happen on the same day.

---

## STEP 11: Report Status and Ask What to Work On

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

## HANDLING NEW/UNKNOWN COMPUTERS

If the user is on a new computer not listed in COMPUTER_PATHS.md:

### Step A: Verify Setup
Ask them:
1. Have you cloned the repository to this computer?
2. Where is it located? (full path)
3. Have you installed Python 3.11+?
4. Have you run `pip install -r requirements.txt`?
5. Have you tested with `python main.py`?

### Step B: Get Computer Info
Ask them to provide:
- Computer name/identifier (e.g., "Work Laptop", "Office Desktop")
- Full path to BreweryManager folder
- Username on that computer

### Step C: Add to COMPUTER_PATHS.md
Tell them:
```
Please add this computer to COMPUTER_PATHS.md:

### [Number]. [Computer Name]
- **Name:** [Computer Name]
- **Path:** [Full Path]
- **User:** [Username]
- **Added:** [Today's Date]
```

### Step D: Continue Normally
Once added to COMPUTER_PATHS.md, proceed with the normal workflow using the new path.

---

## STEP 12: Provide Program Start Commands

After completing the session setup, provide the user with commands to start testing the application:

```
🚀 Ready to test the Brewery Manager!

To launch the application, run these commands:

cd <PATH-FROM-COMPUTER_PATHS.MD>
python main.py

Login credentials:
Username: admin
Password: admin

The application is currently in Phase 3 (Testing). All 9 modules are implemented and ready to test!
```

**Replace `<PATH-FROM-COMPUTER_PATHS.MD>` with the correct path from STEP 1.**

---

**That's it! Follow these steps every time the user says "read start.md"**
