# BREWERY MANAGEMENT SYSTEM - COMMAND REFERENCE

**Quick reference for all command-line operations**

---

## 📦 INSTALLATION COMMANDS

### Install Dependencies
```bash
# Install all required Python packages
pip3 install -r requirements.txt

# Install specific packages if needed
pip3 install google-api-python-client google-auth
pip3 install Pillow reportlab
pip3 install pandas openpyxl
```

### Install tkinter (Linux only - if needed)
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora/RHEL
sudo yum install python3-tkinter
```

---

## 🚀 RUNNING THE APPLICATION

### Launch the GUI Application
```bash
# From project root directory
python3 main.py
```

**Default Login:**
- Username: `admin`
- Password: `admin123`

### Run Core Tests (without GUI)
```bash
# Test core functionality without requiring display
python3 test_core.py
```

---

## 🧪 TESTING COMMANDS

### Quick System Check
```bash
# Check Python version
python3 --version

# Verify project structure
ls -la
ls -la src/

# Check if all modules can be imported
python3 -c "from src.utilities.auth import AuthManager; print('✅ Auth OK')"
python3 -c "from src.data_access.sqlite_cache import SQLiteCacheManager; print('✅ Database OK')"
python3 -c "from src.data_access.sync_manager import SyncManager; print('✅ Sync OK')"
```

### Check Installed Packages
```bash
# List all installed packages
pip3 list

# Check specific packages
pip3 list | grep google
pip3 list | grep Pillow
pip3 list | grep reportlab
pip3 list | grep pandas
```

### Database Commands
```bash
# Check if database exists
ls -la ~/.brewerymanager/cache.db

# Or check legacy location
ls -la src/data/local_cache.db

# View database tables
sqlite3 ~/.brewerymanager/cache.db ".tables"

# Query users table
sqlite3 ~/.brewerymanager/cache.db "SELECT username, role FROM users;"

# View database schema
sqlite3 ~/.brewerymanager/cache.db ".schema"

# Exit sqlite3 interactive mode
.quit
```

---

## 📁 FILE SYSTEM COMMANDS

### Navigate Project
```bash
# Go to project root
cd /home/user/BreweryManager

# List all Python files
find . -name "*.py" -type f

# Count lines of code
find src -name "*.py" -exec wc -l {} + | sort -n

# Search for specific code
grep -r "class.*:" src/
grep -r "def.*:" src/utilities/
```

### Check Directory Structure
```bash
# Show full project tree
tree -L 3

# Or without tree command
find . -type d | sort

# Show only source directories
ls -la src/
ls -la src/gui/
ls -la src/data_access/
```

---

## 🔍 DEBUGGING COMMANDS

### View Error Logs
```bash
# Check application log (if it exists)
tail -f ~/.brewerymanager/app.log

# View last 50 lines
tail -50 ~/.brewerymanager/app.log

# Search for errors
grep -i "error" ~/.brewerymanager/app.log
grep -i "exception" ~/.brewerymanager/app.log
```

### Run with Verbose Output
```bash
# Run Python with verbose imports
python3 -v main.py

# Run with debugging
python3 -m pdb main.py

# Check for syntax errors
python3 -m py_compile main.py
python3 -m py_compile src/gui/main_window.py
```

### Test Specific Modules
```bash
# Test imports interactively
python3
>>> from src.utilities.auth import AuthManager
>>> from src.data_access.sqlite_cache import SQLiteCacheManager
>>> cache = SQLiteCacheManager()
>>> auth = AuthManager(cache)
>>> exit()
```

---

## 🔄 GIT COMMANDS

### Check Status
```bash
# View current branch and changes
git status

# View recent commits
git log --oneline -10

# Show changes
git diff
```

### Make Commits
```bash
# Stage all changes
git add .

# Stage specific files
git add src/gui/recipes.py

# Commit with message
git commit -m "Implement recipes module"

# View commit history
git log --graph --oneline --all
```

### Push Changes
```bash
# Push to current branch
git push -u origin claude/implement-cmd-commands-011CUsC4oq5JagebZSgigwEu

# Or push to a different branch
git push -u origin <branch-name>
```

---

## 📊 CODE ANALYSIS COMMANDS

### Count Lines of Code
```bash
# Total Python lines
find src -name "*.py" -exec wc -l {} + | tail -1

# Lines per module
wc -l src/gui/main_window.py
wc -l src/utilities/auth.py
wc -l src/data_access/sqlite_cache.py
```

### Find TODO Comments
```bash
# Search for TODO/FIXME
grep -r "TODO" src/
grep -r "FIXME" src/
grep -r "XXX" src/
```

### Search for Functions/Classes
```bash
# Find all classes
grep -r "^class " src/

# Find all functions
grep -r "^def " src/

# Find specific pattern
grep -r "def login" src/
```

---

## 🔐 GOOGLE SHEETS SETUP

### Check Credentials
```bash
# Check if credentials file exists
ls -la ~/.brewerymanager/credentials.json

# View credentials (be careful!)
cat ~/.brewerymanager/credentials.json

# Check token
ls -la ~/.brewerymanager/token.json
```

### Test Google Sheets Connection
```bash
# Run Python test
python3 -c "
from src.data_access.google_sheets_client import GoogleSheetsClient
client = GoogleSheetsClient()
print('✅ Google Sheets client initialized')
"
```

---

## 📦 PACKAGING COMMANDS

### Create Executable (PyInstaller)
```bash
# Create standalone executable
pyinstaller --onefile --windowed main.py

# Create with custom name
pyinstaller --onefile --windowed --name BreweryManager main.py

# Include data files
pyinstaller --onefile --windowed --add-data "assets:assets" main.py

# Executable will be in dist/ folder
ls -la dist/
```

### Test Executable
```bash
# Run the built executable
./dist/BreweryManager

# Or on Windows
dist\BreweryManager.exe
```

---

## 🧹 CLEANUP COMMANDS

### Remove Cache Files
```bash
# Remove Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# Remove .pyc files
find . -name "*.pyc" -delete

# Remove build artifacts
rm -rf build/ dist/ *.spec
```

### Reset Database
```bash
# WARNING: This deletes all data!
rm ~/.brewerymanager/cache.db

# Database will be recreated on next run
```

---

## 📝 USEFUL SHORTCUTS

### Quick Test Run
```bash
# One-liner to install deps and run
pip3 install -r requirements.txt && python3 main.py
```

### Full System Test
```bash
# Test everything
python3 test_core.py && python3 main.py
```

### Update Dependencies
```bash
# Upgrade all packages
pip3 install --upgrade -r requirements.txt

# Or upgrade specific package
pip3 install --upgrade google-api-python-client
```

---

## 🆘 EMERGENCY COMMANDS

### Kill Hung Process
```bash
# Find Python processes
ps aux | grep python3

# Kill specific process
kill <PID>

# Force kill if needed
kill -9 <PID>
```

### Check System Resources
```bash
# Check disk space
df -h

# Check memory
free -h

# Check CPU
top
# Press 'q' to quit
```

### Reinstall Everything
```bash
# Uninstall all packages
pip3 freeze | xargs pip3 uninstall -y

# Reinstall from requirements
pip3 install -r requirements.txt
```

---

## 📚 DOCUMENTATION COMMANDS

### Generate Documentation
```bash
# Generate docs from docstrings
pydoc src.gui.main_window > docs/main_window.txt
pydoc src.utilities.auth > docs/auth.txt

# View documentation
pydoc -b  # Opens browser with docs
```

### View Help
```bash
# Python help
python3 -h

# Package help
pip3 -h

# Git help
git --help
```

---

## 🎯 MOST COMMON COMMANDS

```bash
# Start fresh session
cd /home/user/BreweryManager
pip3 install -r requirements.txt
python3 test_core.py
python3 main.py

# Quick status check
git status
ls -la
python3 --version

# Test database
sqlite3 ~/.brewerymanager/cache.db ".tables"

# Check logs
tail -f ~/.brewerymanager/app.log
```

---

**Last Updated:** November 6, 2025
**For:** Brewery Management System v1.0
