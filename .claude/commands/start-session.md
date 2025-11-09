---
description: Start a new session - reads project files and provides merge commands
---

Read the following files to understand the project:
- START_OF_SESSION_PROTOCOL.md
- SESSION_START.md
- CLAUDE_SESSION_WORKFLOW.md
- README.md
- PROGRESS.md (if exists)

After reading these files:

1. Greet the user: "👋 Hi! I've read the project files and I'm ready to help with BreweryManager."

2. Check what branch exists on GitHub:
   - Run: `git branch -r | grep "claude/"`
   - Identify the most recent claude/* branch

3. Provide the user with these commands:
   ```
   Please run these commands to merge the previous session's work:

   cd C:\Users\darre\Desktop\BreweryManager
   git fetch origin
   git checkout master
   git merge origin/claude/<MOST-RECENT-BRANCH> --no-edit
   ```
   (Replace <MOST-RECENT-BRANCH> with the actual branch name you found)

4. After user confirms they ran the commands, create a session log file named `SESSION_LOG_YYYY-MM-DD.md` with:
   - Session ID
   - Branch name
   - Previous branch merged
   - Starting git status
   - Tasks completed (empty to start)

5. Check current git status and report it to the user

6. Ask: "What would you like to work on today?"

Follow these steps in order every time this command is run!
