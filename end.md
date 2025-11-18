# END SESSION INSTRUCTIONS FOR CLAUDE

When the user says "read end.md", follow these steps:

---

## STEP 1: Check for Uncommitted Changes

Run: `git status`

If there are uncommitted changes, proceed to commit them.

---

## STEP 2: Commit All Changes

```bash
git add .
git commit -m "End of session - [brief summary of work done]"
```

---

## STEP 3: Update Session Log

Update the `SESSION_LOG_YYYY-MM-DD.md` file:
- Mark completed tasks as done
- Add any issues encountered
- List what to do next session

Commit the updated log:
```bash
git add SESSION_LOG_*.md
git commit -m "Update session log"
```

---

## STEP 4: Push to GitHub (with retry logic)

```bash
git push -u origin [current-branch-name]
```

If push fails with network error, retry up to 4 times with delays (2s, 4s, 8s, 16s).

---

## STEP 5: Verify Push Succeeded

Run: `git status`

Should show: "Your branch is up to date with 'origin/...'"

And: `git log origin/[current-branch] --oneline -3`

Should show your recent commits are on GitHub.

---

## STEP 6: Document Database Migrations for Next Computer

**IMPORTANT:** If database migrations were run during this session, document them for the next computer!

Create/update `DATABASE_MIGRATIONS_PENDING.md` with:
- List of all migration scripts that need to be run
- Order they should be run in
- Any test data scripts to run
- Expected results/verification steps

Example:
```markdown
# Database Migrations Needed on Brewery Computer

Run these in order after pulling the latest code:

1. **Duty System Migration**
   ```bash
   python src/data_access/migrate_duty_system.py
   ```
   - Adds: settings, settings_containers, batch_packaging_lines, spoilt_beer, duty_returns tables
   - Adds: waste tracking fields to batches table

2. **Fix Scripts (if needed)**
   ```bash
   python src/data_access/fix_spoilt_beer_table.py
   python src/data_access/fix_duty_returns_table.py
   ```

3. **Test Data (optional)**
   ```bash
   python src/testing/generate_test_data.py
   ```
   - Creates 4 test batches (TEST001-TEST004)
   - Covers all 4 SPR duty categories

**Verification:**
- Launch app: `python main.py`
- Check Settings module has Duty Rates and Containers tabs
- Check Duty module loads without errors
- Check Reports module has all 5 tabs
```

Commit this file:
```bash
git add DATABASE_MIGRATIONS_PENDING.md
git commit -m "Document pending database migrations for brewery computer"
git push -u origin [current-branch-name]
```

---

## STEP 7: Merge to Master and Push

Now that the claude branch is tested and verified, merge to master and push:

**Tell the user:**
```
✅ Testing complete! Now let's merge to master and push:

git checkout master
git merge claude/[current-branch-name]
git push origin master
```

**What this does:**
1. Switches to master branch
2. Merges your tested work from the claude branch into master
3. Pushes master to GitHub (makes it the official state)
4. Ensures origin/master stays synchronized across all computers
5. Next session can safely start from origin/master

**Important:** Claude cannot push master automatically due to security restrictions (only claude/* branches allowed). The user must do this step manually.

**Wait for user confirmation** before proceeding to Step 8.

---

## STEP 8: Report to User

Tell the user:

```
✅ Session ended successfully!

Pushed to GitHub:
- ✅ Claude branch: claude/[branch-name]
- ✅ Master branch: origin/master (verified work)

Summary:
- Total commits: [number]
- Last commit: [message]
- GitHub status: ✅ Fully synchronized

⚠️  IMPORTANT FOR NEXT SESSION:
- Database migrations documented in DATABASE_MIGRATIONS_PENDING.md
- Run migrations on brewery computer before using the app
- See start.md for complete setup instructions

Safe to close session. Next session: say 'read start.md'
```

---

## CRITICAL

Do not let the user end the session until all these steps are complete!
