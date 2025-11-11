# BREWERY MANAGEMENT SYSTEM - CONTINUATION GUIDE
**Project Path:** `C:\Users\darre\Desktop\BreweryManager\`
**Last Updated:** November 11, 2025
**Current Phase:** Phase 3 - Testing (All 9 modules implemented)

---

## 🎯 QUICK START FOR NEW SESSION

### 1. Check Current Status
```
Read file: C:\Users\darre\Desktop\BreweryManager\PROGRESS.md
```
This shows exactly what's been completed and what's next.

### 2. Review Project Requirements
```
Read file: C:\Users\darre\Desktop\BreweryManager\TECHNICAL_SPECIFICATION.md
```
Complete technical spec with all features and requirements.

### 3. Check Reference Documentation
```
Read file: C:\Users\darre\Desktop\BreweryManager\UK_ALCOHOL_DUTY_REFERENCE.md
```
UK duty calculation rules (critical for duty calculator module).

---

## 📁 PROJECT STRUCTURE

```
C:\Users\darre\Desktop\BreweryManager\
├── main.py                          # Entry point (exists)
├── requirements.txt                 # Python dependencies (exists)
├── PROGRESS.md                      # Current progress tracker
├── TECHNICAL_SPECIFICATION.md       # Full project spec
├── UK_ALCOHOL_DUTY_REFERENCE.md     # Duty calculation reference
├── CONTINUATION_GUIDE.md            # This file
├── config/
│   └── settings.json               # App configuration
├── src/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── google_sheets_client.py  # ✅ COMPLETE
│   ├── database/
│   │   ├── __init__.py
│   │   └── sqlite_manager.py        # ✅ COMPLETE
│   ├── sync/
│   │   ├── __init__.py
│   │   └── sync_manager.py          # ✅ COMPLETE
│   ├── utilities/
│   │   ├── __init__.py
│   │   └── auth.py                  # ✅ COMPLETE
│   ├── gui/
│   │   ├── __init__.py
│   │   └── main_window.py           # 🔄 NEXT TO CREATE
│   ├── modules/                     # Phase 2 - all modules
│   │   ├── __init__.py
│   │   ├── recipes.py               # ⬜ Future
│   │   ├── inventory.py             # ⬜ Future
│   │   ├── batches.py               # ⬜ Future
│   │   ├── customers.py             # ⬜ Future
│   │   ├── sales.py                 # ⬜ Future
│   │   ├── invoicing.py             # ⬜ Future
│   │   ├── duty.py                  # ⬜ Future
│   │   └── labels.py                # ⬜ Future
│   └── data/
│       ├── local_cache.db           # SQLite database (auto-created)
│       └── credentials.json         # Google API credentials
└── assets/
    └── logo.png                     # Brewery logo for labels
```

---

## ✅ COMPLETED COMPONENTS (Phase 1: 7/8)

### 1. Project Structure ✅
- All folders created
- `__init__.py` files in place
- Base structure ready

### 2. Configuration System ✅
**File:** `config/settings.json`
- Google Sheets config
- Offline mode settings
- Window preferences
- Last sync tracking

### 3. Requirements ✅
**File:** `requirements.txt`
```
gspread==5.12.0
oauth2client==4.1.3
pillow==10.1.0
reportlab==4.0.7
python-barcode==0.15.1
```

### 4. Google Sheets API Client ✅
**File:** `src/api/google_sheets_client.py` (348 lines)
- Authenticate with Google Sheets
- Read/write data from sheets
- Batch operations
- Error handling
- Offline mode support

### 5. SQLite Cache Manager ✅
**File:** `src/database/sqlite_manager.py` (401 lines)
- Local database for offline mode
- All tables created (recipes, inventory, batches, customers, etc.)
- CRUD operations for all tables
- Data integrity checks

### 6. Sync Manager ✅
**File:** `src/sync/sync_manager.py` (367 lines)
- Sync local SQLite ↔ Google Sheets
- Conflict resolution (timestamp-based)
- Batch sync operations
- Auto-sync scheduler
- Manual sync trigger

### 7. User Authentication ✅
**File:** `src/utilities/auth.py` (282 lines)
- User management (create, deactivate)
- Password hashing (SHA-256)
- Login/logout system
- Role-based permissions (admin, manager, staff)
- Session tracking
- Default admin user creation

---

## 🔄 CURRENT TASK: Main Window GUI

### What Needs to Be Created
**File:** `src/gui/main_window.py` (~400-500 lines)

### Requirements
1. **Main Window Setup**
   - tkinter root window (1200x800)
   - Title: "Brewery Management System"
   - Resizable with minimum size
   - Center on screen

2. **Login Screen** (shows first)
   - Username entry
   - Password entry (hidden)
   - Login button
   - Error message display
   - Uses `src/utilities/auth.py` for authentication

3. **Main Interface** (after login)
   - **Left Sidebar** (200px wide, light gray)
     - 9 navigation buttons (one per module):
       1. Dashboard
       2. Recipes
       3. Inventory
       4. Batches
       5. Customers
       6. Sales
       7. Invoicing
       8. Duty Calculator
       9. Label Printing
     - Highlight active button
   
   - **Content Area** (center, white background)
     - Shows active module content
     - Initially shows Dashboard placeholder
   
   - **Status Bar** (bottom)
     - Connection status: 🟢 Online / 🔴 Offline
     - Current user: "User: [username] ([role])"
     - Last sync: "Last sync: [timestamp]"
     - Manual sync button

4. **Menu Bar**
   - File menu:
     - Switch User
     - Settings
     - Exit
   - Help menu:
     - About
     - Documentation

5. **Key Functions**
   - `__init__()`: Initialize window, create widgets
   - `create_login_screen()`: Build login interface
   - `authenticate_user()`: Handle login button click
   - `create_main_interface()`: Build main UI after login
   - `switch_module()`: Change content area when sidebar button clicked
   - `update_status_bar()`: Refresh connection/user/sync info
   - `manual_sync()`: Trigger sync button
   - `logout()`: Return to login screen

### Code Template Structure
```python
import tkinter as tk
from tkinter import ttk, messagebox
from src.utilities.auth import UserAuth
from src.sync.sync_manager import SyncManager

class BreweryMainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Brewery Management System")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        self.auth = UserAuth()
        self.sync_manager = SyncManager()
        self.current_user = None
        self.current_module = None
        
        # Center window on screen
        self.center_window()
        
        # Start with login screen
        self.create_login_screen()
        
    def center_window(self):
        # Calculate position
        pass
    
    def create_login_screen(self):
        # Build login UI
        pass
    
    def authenticate_user(self):
        # Handle login
        pass
    
    def create_main_interface(self):
        # Build main UI
        pass
    
    def switch_module(self, module_name):
        # Change content area
        pass
    
    def update_status_bar(self):
        # Refresh status
        pass
    
    def run(self):
        self.root.mainloop()
```

---

## 📋 STEP-BY-STEP: CREATE main_window.py

### Step 1: Read Progress File
```
Read: C:\Users\darre\Desktop\BreweryManager\PROGRESS.md
```
Confirm main_window.py is next.

### Step 2: Create the File
```
Create: C:\Users\darre\Desktop\BreweryManager\src\gui\main_window.py
```

### Step 3: Write Code in Chunks
Write the file in ~30 line chunks for optimal performance:
- Chunk 1: Imports and class initialization
- Chunk 2: Window setup and centering
- Chunk 3: Login screen creation
- Chunk 4: Authentication handling
- Chunk 5: Main interface creation
- Chunk 6: Sidebar with navigation buttons
- Chunk 7: Content area setup
- Chunk 8: Status bar
- Chunk 9: Menu bar
- Chunk 10: Module switching
- Chunk 11: Sync functions
- Chunk 12: Utility methods
- Chunk 13: Main execution

### Step 4: Update main.py
Update `main.py` to launch the GUI:
```python
from src.gui.main_window import BreweryMainWindow

if __name__ == "__main__":
    app = BreweryMainWindow()
    app.run()
```

### Step 5: Update PROGRESS.md
Mark main_window.py as complete and Phase 1 as 100% done.

---

## 🎯 AFTER PHASE 1 COMPLETES

### Phase 2: Module Implementation (9 modules)
Create each module file in `src/modules/`:

1. **Dashboard** (`dashboard.py`)
   - Welcome screen
   - Quick stats
   - Recent activity
   - Alerts (low stock, overdue payments)

2. **Recipes** (`recipes.py`)
   - Recipe list view
   - Create/edit recipe form
   - Grain bill, hops schedule, yeast
   - Scalable batch size calculator

3. **Inventory** (`inventory.py`)
   - Tabs: Brewing Materials | Finished Goods
   - Add stock, use stock, view levels
   - Low stock alerts
   - Auto-deduction when brewing

4. **Batches** (`batches.py`)
   - Create batch from recipe
   - Gyle number assignment
   - Status tracking (Brewing → Fermenting → etc.)
   - Fermentation logs
   - Package batch → move to finished goods

5. **Customers** (`customers.py`)
   - Customer database
   - Add/edit customers
   - Contact info, preferences
   - Sales history
   - Notes (likes/dislikes)

6. **Sales** (`sales.py`)
   - Record sale
   - Link to customer & gyle
   - Dispatch tracking
   - Sales history reports

7. **Invoicing** (`invoicing.py`)
   - Generate invoice from sale
   - Auto-increment invoice numbers
   - Line items, VAT calculation
   - Payment tracking
   - Print/PDF export
   - Aged debt reports

8. **Duty Calculator** (`duty.py`)
   - Automatic duty calculations
   - Current UK rates (from reference doc)
   - Batch-level estimates
   - Monthly/annual summaries
   - Export reports
   - **CRITICAL:** Use `UK_ALCOHOL_DUTY_REFERENCE.md` for all calculations!

9. **Label Printing** (`labels.py`)
   - Select batch
   - Generate cask labels
   - Include: Beer name, date, ABV, gyle, duty info, logo
   - Print or export to PDF

---

## 🔑 KEY COMMANDS FOR CONTINUATION

### File Operations
```bash
# Read file
Read: C:\Users\darre\Desktop\BreweryManager\[filename]

# Create new file
Create: C:\Users\darre\Desktop\BreweryManager\[path]\[filename]

# Write content (chunk by chunk for large files)
Write to: [filename] (chunk 1 of N)

# List directory
List: C:\Users\darre\Desktop\BreweryManager\src\
```

### Testing
```bash
# Test the application
python C:\Users\darre\Desktop\BreweryManager\main.py
```

---

## 📚 IMPORTANT REFERENCES

### UK Duty Calculations
**File:** `C:\Users\darre\Desktop\BreweryManager\UK_ALCOHOL_DUTY_REFERENCE.md`

**Key Points:**
- Current rates (Feb 2025)
- Draught Relief (13.9% discount for beer)
- Small Producer Relief (SPR) - sliding scale
- Calculation formula: `litres × ABV × duty_rate`
- Always round DOWN to nearest penny
- SPR lookup tables included

### Google Sheets Structure
Each module will have its own sheet:
- Recipes
- Inventory_Materials
- Inventory_Finished
- Batches
- Customers
- Sales
- Invoices
- Duty_Records
- Users

### Database Schema
Defined in `src/database/sqlite_manager.py`
- 10 tables total
- All relationships defined
- Foreign keys for data integrity

---

## ⚠️ CRITICAL REMINDERS

1. **Always ask before implementing** - User preference is to discuss first
2. **Chunk large files** - Write in ~30 line pieces for best performance
3. **Update PROGRESS.md** - After each component completion
4. **Test incrementally** - Don't wait until everything is done
5. **Use reference docs** - UK duty calculations must be accurate
6. **Offline-first** - Everything must work without internet
7. **Google Sheets sync** - Background process, not blocking
8. **Windows .exe** - Final deliverable is a single installer file

---

## 🚀 QUICK RESUME CHECKLIST

When starting a new session:

- [ ] Read `PROGRESS.md` to see current status
- [ ] Read `CONTINUATION_GUIDE.md` (this file)
- [ ] Check what was last being worked on
- [ ] Review relevant reference docs
- [ ] Ask user for confirmation before proceeding
- [ ] Continue from where it left off
- [ ] Update `PROGRESS.md` when done

---

## 📞 USER PREFERENCES

- **Username:** darre
- **Desktop Path:** `C:\Users\darre\Desktop\`
- **Working Directory:** `C:\Users\darre\Desktop\BreweryManager\`
- **Communication:** Always ask before implementing changes
- **Build Command:** Only start coding when user says "build"

---

## 🎉 FINAL DELIVERABLE

**What the user wants:**
- Single Windows .exe installer
- No ongoing subscription
- Offline capability with Google Sheets cloud sync
- Professional, production-ready
- All 9 modules fully functional

**Packaging (Final Phase):**

**Prerequisites:**
1. Obtain Google Cloud credentials (see TECHNICAL_SPECIFICATION.md "Google Account Setup" section)
2. Place `credentials.json` in `data/` folder
3. Verify all assets are in place (logo, icons, etc.)

**Build Command:**
```bash
pyinstaller --onefile --windowed --name="Brewery Manager" \
    --icon=assets/icon.ico \
    --add-data="assets:assets" \
    --add-data="data/credentials.json:data" \
    --add-data="config/settings.json:config" \
    --hidden-import=PIL \
    --hidden-import=reportlab \
    --hidden-import=google.auth \
    --hidden-import=google_auth_oauthlib \
    main.py
```

**What Gets Bundled:**
- ✅ All Python code
- ✅ All dependencies (tkinter, Google API libraries, PIL, ReportLab)
- ✅ credentials.json (Google Cloud OAuth credentials)
- ✅ Assets (logo, icons)
- ✅ Default config files
- ❌ token.pickle (generated locally on each computer during first run)

**Create Installer:**
- Use Inno Setup or NSIS to create installer
- Include .exe and any additional runtime files
- Test on clean Windows machine

**For Android App:**
- Build with Flutter: `flutter build apk --release`
- Credentials are bundled into APK during build
- Upload to Google Play Store (£20 one-time fee)
- OR sideload APK directly to devices (free)

---

**END OF CONTINUATION GUIDE**

*This document should contain everything needed to pick up the project at any point.*
