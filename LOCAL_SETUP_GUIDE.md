# LOCAL TESTING SETUP GUIDE
## Brewery Management System

This guide will help you set up the Brewery Management System on your local Windows computer for testing and development.

---

## PREREQUISITES

### 1. Python Installation
- **Required:** Python 3.11 or higher
- **Download:** https://www.python.org/downloads/
- **Installation Notes:**
  - ✅ Check "Add Python to PATH" during installation
  - ✅ Check "Install for all users" (recommended)
  - ✅ tkinter is included with standard Windows Python installation

### 2. Git (Optional, for pulling updates)
- **Download:** https://git-scm.com/download/win
- **Alternative:** Download ZIP from GitHub

---

## QUICK START (5 MINUTES)

### Step 1: Clone or Download Repository

**Option A: Using Git**
```bash
cd C:\Users\darre\Desktop
git clone <your-repo-url> BreweryManager
cd BreweryManager
```

**Option B: Download ZIP**
1. Download repository ZIP
2. Extract to `C:\Users\darre\Desktop\BreweryManager\`
3. Open Command Prompt and navigate:
   ```bash
   cd C:\Users\darre\Desktop\BreweryManager
   ```

### Step 2: Install Dependencies
Open Command Prompt in the project directory and run:
```bash
pip install -r requirements.txt
```

This installs all required packages:
- Google Sheets API libraries
- PDF generation (ReportLab)
- Image processing (Pillow)
- Data analysis tools (pandas, openpyxl)
- Plus all dependencies

### Step 3: Run the Application
```bash
python main.py
```

The application should launch immediately with a login screen!

### Step 4: Login
**Default credentials:**
- Username: `admin`
- Password: `admin`

**IMPORTANT:** You should change this password immediately after first login for security!

---

## WHAT WORKS NOW

The application will start and you'll see:

✅ **Login Screen** - Authentication system
✅ **Main Window** - Application shell with navigation
✅ **Module Buttons** - 9 module buttons in sidebar
✅ **Status Bar** - Connection status indicator
✅ **Menu System** - File, Edit, View, Tools menus

### Current Functionality:
1. **User Authentication**
   - Login/logout
   - Default admin account
   - Session management

2. **Navigation**
   - Switch between modules (placeholder screens)
   - Menu navigation
   - Keyboard shortcuts

3. **Status Monitoring**
   - Online/offline indicator
   - Sync status
   - User display

### Module Screens (Phase 2 - Not Yet Built):
- Dashboard
- Recipes
- Inventory
- Batches
- Customers
- Sales & Dispatch
- Invoicing
- Duty Calculator
- Label Printing

---

## DIRECTORY STRUCTURE

```
C:\Users\darre\Desktop\BreweryManager\
├── main.py                          ← Run this file
├── requirements.txt                 ← Dependencies list
├── README.md                        ← Project overview
├── LOCAL_SETUP_GUIDE.md            ← This file
├── QUICK_START.md                  ← Quick reference
├── PROGRESS.md                     ← Development status
└── src/
    ├── config/
    │   └── constants.py           ← Configuration
    ├── data_access/
    │   ├── google_sheets_client.py    ← Google Sheets API
    │   ├── sqlite_cache.py            ← Local database
    │   └── sync_manager.py            ← Cloud sync
    ├── utilities/
    │   └── auth.py                    ← Authentication
    └── gui/
        ├── main_window.py             ← Main application window
        └── [modules]/                 ← Module GUIs (Phase 2)
```

---

## APPLICATION DATA LOCATION

The application stores its data in:
```
C:\Users\darre\.brewerymanager\
├── cache.db              ← Local SQLite database
├── config.json           ← User configuration
├── app.log              ← Application logs
├── credentials.json     ← Google API credentials (optional)
└── token.json          ← Google auth token (optional)
```

This directory is created automatically on first run.

---

## GOOGLE SHEETS INTEGRATION (OPTIONAL)

The application works **offline-first** and doesn't require Google Sheets to run.

However, to enable cloud sync:

### Step 1: Get Google Cloud Credentials
1. Go to https://console.cloud.google.com/
2. Create a new project
3. Enable Google Sheets API
4. Create OAuth 2.0 credentials
5. Download credentials as `credentials.json`

### Step 2: Add Credentials
Copy `credentials.json` to:
```
C:\Users\darre\.brewerymanager\credentials.json
```

### Step 3: First Login
On first sync, a browser window will open for Google authentication.
After authorization, a `token.json` file is created for future use.

---

## TESTING THE APPLICATION

### Test 1: Launch & Login
```bash
python main.py
```
- Application window should appear
- Enter credentials: admin / admin123
- Main window should load

### Test 2: Navigation
- Click each module button in the sidebar
- Each should display a placeholder screen
- Check status bar shows "Offline" (normal without Google Sheets)

### Test 3: Menu System
- **File Menu:**
  - Settings (placeholder)
  - Exit (closes app)
- **Edit Menu:**
  - Undo, Redo, Cut, Copy, Paste (placeholders)
- **View Menu:**
  - Refresh
- **Tools Menu:**
  - Sync, Database, Import/Export (placeholders)

### Test 4: Logout
- Click "Logout" in menu
- Should return to login screen

---

## TROUBLESHOOTING

### Issue: "No module named 'tkinter'"
**Solution:** tkinter is included with Windows Python. If missing:
1. Reinstall Python from python.org
2. Ensure "tcl/tk and IDLE" is checked during installation

### Issue: "pip: command not found"
**Solution:**
1. Reinstall Python with "Add to PATH" checked
2. Or use: `python -m pip install -r requirements.txt`

### Issue: "No module named 'src'"
**Solution:**
- Ensure you're in the correct directory:
  ```bash
  cd C:\Users\darre\Desktop\BreweryManager
  ```

### Issue: "Permission denied" errors
**Solution:**
- Run Command Prompt as Administrator
- Or check folder permissions

### Issue: Application won't start
**Debug steps:**
```bash
# Check Python version (need 3.11+)
python --version

# Test imports
python -c "import tkinter; print('GUI: OK')"
python -c "import sqlite3; print('Database: OK')"
python -c "from src.gui.main_window import BreweryMainWindow; print('App: OK')"
```

---

## DEVELOPMENT WORKFLOW

### Making Changes
1. Edit Python files in `src/`
2. Save changes
3. Restart application to see changes:
   ```bash
   python main.py
   ```

### Checking Logs
View application logs at:
```
C:\Users\darre\.brewerymanager\app.log
```

### Database
Inspect SQLite database with tools like:
- DB Browser for SQLite: https://sqlitebrowser.org/
- Or: `sqlite3 C:\Users\darre\.brewerymanager\cache.db`

---

## NEXT STEPS (PHASE 2)

The core infrastructure (Phase 1) is complete! Next up:

### Module Development
Build out the 9 feature modules:
1. Dashboard - Overview, alerts, quick stats
2. Recipes - Beer recipe management
3. Inventory - Materials and finished goods
4. Batches - Brewing workflow and tracking
5. Customers - CRM and customer database
6. Sales & Dispatch - Sales orders and deliveries
7. Invoicing - Invoice generation and payment tracking
8. Duty Calculator - UK alcohol duty calculations
9. Label Printing - Professional cask label printing

See `CONTINUATION_GUIDE.md` for detailed implementation steps.

---

## KEYBOARD SHORTCUTS

| Shortcut | Action |
|----------|--------|
| Ctrl+Q | Quit application |
| Ctrl+R | Refresh current view |
| F5 | Sync with Google Sheets |
| Ctrl+S | Save (context dependent) |
| Ctrl+P | Print (context dependent) |
| F1 | Help |

---

## GETTING HELP

### Documentation
- `README.md` - Project overview
- `QUICK_START.md` - Quick reference card
- `PROGRESS.md` - Current development status
- `TECHNICAL_SPECIFICATION.md` - Complete specification
- `CONTINUATION_GUIDE.md` - Implementation guide

### Support
- Check logs: `C:\Users\darre\.brewerymanager\app.log`
- Review error messages in Command Prompt
- Consult Python documentation: https://docs.python.org/3/

---

## TIPS FOR TESTING

### 1. Use the Command Prompt
Always run from Command Prompt to see:
- Startup messages
- Error messages
- Debug output
- Sync status

### 2. Check the Status Bar
Bottom of window shows:
- Current user
- Connection status (Online/Offline)
- Last sync time
- Active module

### 3. Monitor the Database
After using features:
```bash
# View tables
sqlite3 C:\Users\darre\.brewerymanager\cache.db ".tables"

# View users
sqlite3 C:\Users\darre\.brewerymanager\cache.db "SELECT * FROM users;"
```

### 4. Test Offline Mode
The application should work perfectly offline:
- All CRUD operations
- Local database storage
- Navigation and UI
- (Sync will show "Offline" - this is normal)

---

## SYSTEM REQUIREMENTS

### Minimum:
- **OS:** Windows 10 (64-bit)
- **CPU:** Dual-core 2.0 GHz
- **RAM:** 4 GB
- **Disk:** 500 MB free space
- **Python:** 3.11 or higher

### Recommended:
- **OS:** Windows 10/11 (64-bit)
- **CPU:** Quad-core 2.5 GHz
- **RAM:** 8 GB
- **Disk:** 1 GB free space
- **Screen:** 1920x1080 or higher

---

## PROJECT STATUS

**Phase 1: COMPLETE ✅**
- Core infrastructure built
- Application launches
- Authentication works
- Database operational

**Phase 2: IN PROGRESS 🔄**
- Building 9 feature modules
- Current progress: 0/9 modules complete

**Phase 3: PENDING ⏳**
- Integration testing
- Bug fixes
- Performance optimization

**Phase 4: PENDING ⏳**
- Create .exe installer
- Documentation
- User manual

---

## HAPPY TESTING! 🍺

The application is now ready for local testing. While the feature modules are still being built (Phase 2), you have a fully functional application shell with:
- Professional login system
- Navigation framework
- Database management
- Cloud sync infrastructure
- Module placeholders

**Ready to build the brewery features!**

---

*Last Updated: November 2025*
*Version: Phase 1 Complete - Module Development Ready*
