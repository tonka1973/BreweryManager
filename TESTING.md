# BREWERY MANAGEMENT SYSTEM - TESTING GUIDE

**Last Updated:** November 6, 2025
**Phase:** Phase 1 Complete - Testing Phase

---

## 🚀 QUICK START TESTING COMMANDS

### 1. Install Dependencies

```bash
# Navigate to project directory
cd /home/user/BreweryManager

# Install all required Python packages
pip3 install -r requirements.txt
```

### 2. Run the Application

```bash
# From project root directory
python3 main.py
```

**Default Login Credentials:**
- Username: `admin`
- Password: `admin`
(Note: You should change this password after first login)

---

## 📋 STEP-BY-STEP TESTING CHECKLIST

### ✅ Phase 1: Environment Setup

```bash
# Check Python version (should be 3.10+)
python3 --version

# Verify project structure
ls -la
ls -la src/
ls -la src/gui/
ls -la src/data_access/

# Check if requirements file exists
cat requirements.txt
```

### ✅ Phase 2: Install Dependencies

```bash
# Install all dependencies
pip3 install -r requirements.txt

# Verify key packages installed
pip3 list | grep google-api
pip3 list | grep Pillow
pip3 list | grep reportlab
pip3 list | grep pandas
```

### ✅ Phase 3: Database Initialization

```bash
# The database will be auto-created on first run
# Check if data directory exists
ls -la src/data/ 2>/dev/null || echo "Data directory will be created on first run"

# After first run, verify database was created
ls -la src/data/local_cache.db
```

### ✅ Phase 4: Run Application

```bash
# Launch the application
python3 main.py

# The GUI should open with a login screen
```

### ✅ Phase 5: Test Login System

**Test Steps:**
1. Application opens with login screen
2. Enter username: `admin`
3. Enter password: `admin123`
4. Click "Login" button
5. Should see main interface with sidebar navigation

**Expected Results:**
- ✅ Login successful
- ✅ Main window displays (1200x800)
- ✅ Left sidebar shows 9 module buttons
- ✅ Status bar shows user info
- ✅ Menu bar shows File and Help menus

### ✅ Phase 6: Test Navigation

**Test Each Module Button:**
1. Click "Dashboard" - should switch to Dashboard view
2. Click "Recipes" - should switch to Recipes view
3. Click "Inventory" - should switch to Inventory view
4. Click "Batches" - should switch to Batches view
5. Click "Customers" - should switch to Customers view
6. Click "Sales Tools" - should switch to Sales Tools view
7. Click "Sales & Dispatch" - should switch to Sales & Dispatch view
8. Click "Invoicing" - should switch to Invoicing view
9. Click "Duty Calculator" - should switch to Duty view
10. Click "Label Printing" - should switch to Labels view

**Expected Results:**
- ✅ Active button highlights in blue
- ✅ Content area updates (shows placeholder for now)
- ✅ No errors in terminal

### ✅ Phase 7: Test Status Bar

**Check Status Bar Elements:**
- Connection Status: 🔴 Offline (no Google Sheets credentials yet)
- User Info: "User: admin (Admin)"
- Last Sync: "Never" (no sync yet)
- Sync button present

### ✅ Phase 8: Test Menu System

**File Menu:**
1. Click "File" → "Switch User" - should logout to login screen
2. Login again
3. Click "File" → "Settings" - should show settings dialog
4. Click "File" → "Exit" - should close application

**Help Menu:**
1. Click "Help" → "About" - should show about dialog
2. Click "Help" → "Documentation" - should show documentation info

### ✅ Phase 9: Test Logout

**Test Steps:**
1. Click logout button or File → Switch User
2. Should return to login screen
3. Login again with same credentials
4. Should work correctly

---

## 🔧 TROUBLESHOOTING COMMANDS

### Check for Python Import Errors

```bash
# Test importing main modules
python3 -c "from src.gui.main_window import BreweryMainWindow; print('✅ Main window imports OK')"
python3 -c "from src.utilities.auth import UserAuth; print('✅ Auth imports OK')"
python3 -c "from src.data_access.sqlite_cache import SQLiteCache; print('✅ Database imports OK')"
python3 -c "from src.data_access.sync_manager import SyncManager; print('✅ Sync manager imports OK')"
python3 -c "from src.data_access.google_sheets_client import GoogleSheetsClient; print('✅ Google Sheets imports OK')"
```

### Check Database Creation

```bash
# After running the app once, check database
sqlite3 src/data/local_cache.db ".tables"

# Should show tables:
# batches, customers, finished_goods, inventory, invoices,
# products, recipes, sales, sessions, users
```

### View Database Contents

```bash
# Check if admin user was created
sqlite3 src/data/local_cache.db "SELECT username, role FROM users;"

# Should show: admin|Admin
```

### Check Log Files (if implemented)

```bash
# Check for any error logs
ls -la logs/ 2>/dev/null || echo "No log directory yet"
```

### Test in Verbose Mode

```bash
# Run with Python verbose output to see detailed errors
python3 -v main.py
```

---

## 🐛 COMMON ISSUES AND FIXES

### Issue: "ModuleNotFoundError: No module named 'google'"

**Fix:**
```bash
pip3 install google-api-python-client google-auth google-auth-oauthlib
```

### Issue: "ModuleNotFoundError: No module named 'PIL'"

**Fix:**
```bash
pip3 install Pillow
```

### Issue: "ModuleNotFoundError: No module named 'reportlab'"

**Fix:**
```bash
pip3 install reportlab
```

### Issue: "No module named 'tkinter'"

**Fix (Ubuntu/Debian):**
```bash
sudo apt-get install python3-tk
```

**Fix (Fedora/RHEL):**
```bash
sudo yum install python3-tkinter
```

### Issue: Database file not found

**Fix:**
```bash
# Create data directory if it doesn't exist
mkdir -p src/data
# The database will be auto-created on first run
```

### Issue: Permission denied on database

**Fix:**
```bash
# Make data directory writable
chmod 755 src/data
```

---

## 📊 EXPECTED TEST RESULTS

### After Successful Installation:

```
✅ All dependencies installed
✅ No import errors
✅ Application launches without errors
✅ Login screen appears
✅ Database auto-created in src/data/local_cache.db
✅ Admin user exists in database
```

### After Successful Login:

```
✅ Main window displays (1200x800 pixels)
✅ Left sidebar with 10 buttons visible
✅ Top menu bar (File, Help) visible
✅ Bottom status bar visible
✅ Status bar shows: User: admin (Admin)
✅ Connection status: Offline (red)
✅ Can click through all navigation buttons
✅ Active button highlights
```

### Current Limitations (Expected):

```
⚠️ Module content areas are placeholders (Phase 2 not started)
⚠️ Google Sheets sync shows "Offline" (no credentials configured)
⚠️ No actual data entry forms yet (modules not implemented)
⚠️ Reports and exports not available (Phase 2 features)
```

---

## 🧪 AUTOMATED TEST COMMANDS

### Quick System Check Script

```bash
# Create a quick test script
cat > test_system.sh << 'EOF'
#!/bin/bash

echo "=== Brewery Management System - Quick Test ==="
echo ""

echo "1. Checking Python version..."
python3 --version
echo ""

echo "2. Checking project structure..."
if [ -f "main.py" ]; then
    echo "✅ main.py found"
else
    echo "❌ main.py not found"
fi

if [ -d "src/gui" ]; then
    echo "✅ src/gui directory found"
else
    echo "❌ src/gui directory not found"
fi

echo ""
echo "3. Checking dependencies..."
python3 -c "import tkinter; print('✅ tkinter available')" 2>/dev/null || echo "❌ tkinter not available"
python3 -c "import sqlite3; print('✅ sqlite3 available')" 2>/dev/null || echo "❌ sqlite3 not available"
python3 -c "from google.oauth2 import service_account; print('✅ google-auth available')" 2>/dev/null || echo "❌ google-auth not available"
python3 -c "from PIL import Image; print('✅ Pillow available')" 2>/dev/null || echo "❌ Pillow not available"
python3 -c "from reportlab.pdfgen import canvas; print('✅ reportlab available')" 2>/dev/null || echo "❌ reportlab not available"

echo ""
echo "4. Checking module imports..."
python3 -c "from src.gui.main_window import BreweryMainWindow; print('✅ Main window OK')" 2>/dev/null || echo "❌ Main window import failed"
python3 -c "from src.utilities.auth import UserAuth; print('✅ Auth OK')" 2>/dev/null || echo "❌ Auth import failed"
python3 -c "from src.data_access.sqlite_cache import SQLiteCache; print('✅ Database OK')" 2>/dev/null || echo "❌ Database import failed"

echo ""
echo "=== Test Complete ==="
EOF

chmod +x test_system.sh
./test_system.sh
```

---

## 📝 MANUAL TEST CHECKLIST

Print this checklist and mark off as you test:

### Pre-Launch Tests
- [ ] Python 3.10+ installed
- [ ] All dependencies installed (`pip3 list` shows all packages)
- [ ] No import errors when testing modules
- [ ] Project directory structure correct

### Launch Tests
- [ ] `python3 main.py` starts without errors
- [ ] Login window appears
- [ ] Window is properly centered on screen
- [ ] Window title is "Brewery Management System"

### Authentication Tests
- [ ] Can login with admin/admin123
- [ ] Wrong password shows error message
- [ ] Wrong username shows error message
- [ ] Successful login shows main interface
- [ ] Database creates admin user on first run

### UI Tests
- [ ] Main window is 1200x800 pixels
- [ ] Window is resizable
- [ ] Minimum size is enforced (1000x600)
- [ ] Left sidebar is visible (200px wide, light gray)
- [ ] All 10 navigation buttons are visible
- [ ] Top menu bar shows File and Help
- [ ] Bottom status bar shows all elements

### Navigation Tests
- [ ] Dashboard button works
- [ ] Recipes button works
- [ ] Inventory button works
- [ ] Batches button works
- [ ] Customers button works
- [ ] Sales Tools button works
- [ ] Sales & Dispatch button works
- [ ] Invoicing button works
- [ ] Duty Calculator button works
- [ ] Label Printing button works
- [ ] Active button highlights correctly
- [ ] Previous button unhighlights

### Status Bar Tests
- [ ] Shows connection status (Offline/Online)
- [ ] Shows current user (admin)
- [ ] Shows user role (Admin)
- [ ] Shows last sync time (Never initially)
- [ ] Sync button is visible

### Menu Tests
- [ ] File → Switch User logs out
- [ ] File → Settings opens (or shows placeholder)
- [ ] File → Exit closes application
- [ ] Help → About shows info
- [ ] Help → Documentation shows info

### Database Tests
- [ ] Database file created at src/data/local_cache.db
- [ ] Database has all required tables
- [ ] Admin user exists in users table
- [ ] User session is recorded in sessions table

### Logout Tests
- [ ] Logout returns to login screen
- [ ] Can login again after logout
- [ ] Session is properly cleared

---

## 🔍 PERFORMANCE TESTS

### Startup Time
```bash
# Measure application startup time
time python3 main.py
# Should start in < 2 seconds
```

### Memory Usage
```bash
# Check memory usage (Linux)
ps aux | grep python3 | grep main.py
# Should use < 100MB RAM for base application
```

---

## 📸 SCREENSHOTS TO CAPTURE

For documentation, capture these screenshots:

1. **Login Screen** - Initial state
2. **Login Error** - Wrong password
3. **Main Interface** - After successful login
4. **Each Module View** - All 10 navigation states
5. **Status Bar** - Showing offline state
6. **Menu Dropdown** - File menu open
7. **Menu Dropdown** - Help menu open
8. **About Dialog** - Help → About
9. **Logout** - Return to login screen

---

## ✅ PHASE 1 ACCEPTANCE CRITERIA

Mark these as complete only when ALL tests pass:

- [ ] ✅ Application installs without errors
- [ ] ✅ Application launches successfully
- [ ] ✅ Login system works correctly
- [ ] ✅ Main UI displays properly
- [ ] ✅ All navigation buttons work
- [ ] ✅ Status bar updates correctly
- [ ] ✅ Menus function properly
- [ ] ✅ Logout/re-login works
- [ ] ✅ Database creates automatically
- [ ] ✅ No console errors during normal operation

**If all checked: PHASE 1 COMPLETE! Ready for Phase 2!** 🎉

---

## 🚀 NEXT STEPS AFTER TESTING

Once all tests pass:

1. **Review Test Results** - Document any issues found
2. **Update PROGRESS.md** - Confirm Phase 1 is 100% complete
3. **Plan Phase 2** - Review module implementation order
4. **Start Dashboard Module** - First module to implement
5. **Continue Testing** - Test each module as it's built

---

## 📞 GETTING HELP

If tests fail:

1. Check error messages in terminal
2. Review TROUBLESHOOTING section above
3. Verify all dependencies installed
4. Check Python version compatibility
5. Review CONTINUATION_GUIDE.md for setup details

---

**TESTING GUIDE v1.0**
*Last Updated: November 6, 2025*
