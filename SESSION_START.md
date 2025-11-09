# 🚀 SESSION START - Run These Commands First!

**Run these commands at the start of EVERY new Claude session to merge previous work.**

---

## 🎯 HOW TO START A NEW SESSION

**Just say to Claude:**
> "start session"

or

> "read files"

Claude will then:
1. ✅ Read the necessary project files
2. ✅ Give you these exact commands to run
3. ✅ Create a session log
4. ✅ Check your git status
5. ✅ Ask what you want to work on

---

## Step 1: Fetch All Branches from GitHub

```bash
git fetch origin
```

This downloads all the latest branches from GitHub (including previous session branches).

---

## Step 2: Check What Branches Exist

```bash
git branch -r | grep "claude/"
```

This shows all the Claude session branches. Look for the most recent one (it will have a different session ID than your current session).

---

## Step 3: Merge the Previous Session's Work

**If you see a previous `claude/` branch**, merge it into master:

```bash
git checkout master
git merge origin/claude/<PREVIOUS-SESSION-ID> --no-edit
```

Replace `<PREVIOUS-SESSION-ID>` with the actual branch name you saw in Step 2.

**Example:**
```bash
git merge origin/claude/fix-module-loading-011CUtigEPRBeHUoDnpcJYkR --no-edit
```

---

## Step 4: Tell Claude You're Ready

In the chat, simply say:
> "Ready to continue"

Claude will check the current state and continue working from where the last session left off.

---

## What This Does

- ✅ **Merges** previous session's work into your local master branch
- ✅ **Combines** all changes from previous sessions
- ✅ **Keeps** just one set of files (no duplicates)
- ✅ **Allows** Claude to continue working seamlessly

---

## At the End of Each Session

**Claude will automatically:**
- Push work to a new `claude/<session-id>` branch
- The stop hook will verify it's pushed
- Everything is saved on GitHub

**You don't need to do anything!**

---

## Quick Reference Card

**Copy/paste this at the start of each session:**

```bash
# 1. Fetch latest
git fetch origin

# 2. List previous session branches
git branch -r | grep "claude/"

# 3. Checkout master
git checkout master

# 4. Merge previous session (replace <BRANCH> with actual branch name)
git merge origin/<BRANCH> --no-edit

# 5. Tell Claude "Ready to continue"
```

---

## Troubleshooting

**"Already up to date" message?**
- Good! Nothing to merge, continue working.

**Merge conflicts?**
- Very unlikely with this workflow
- If it happens, let Claude know and they'll help resolve it

**Can't find previous branch?**
- If this is your FIRST session, there's nothing to merge
- Just say "Ready to continue"

---

## Why This Workflow?

Claude Code can only push to branches like `claude/<session-id>`. Each session gets a unique ID, so each session creates a new branch. By merging at the start of each session, you keep all work combined and up-to-date.

---

**Save this file! Refer to it at the start of every session.**
