# 🍺 START HERE - Local Testing Setup

## Quick Start (2 Minutes)

### Step 1: Open Command Prompt
```
Press Windows Key + R
Type: cmd
Press Enter
```

### Step 2: Navigate to Project
```bash
cd C:\Users\darre\Desktop\BreweryManager
```

### Step 3: Run Setup Script
```bash
setup.bat
```

This will:
- Check Python installation
- Install all dependencies
- Run tests
- Set everything up automatically

### Step 4: Launch Application
```bash
python main.py
```

### Step 5: Login
```
Username: admin
Password: admin
```

**IMPORTANT:** Change the password after first login!

---

## That's It! 🎉

You now have a working Brewery Management System running locally!

---

## What You'll See

When you run the application, you'll get:

✅ **Login Screen** - Professional authentication
✅ **Main Window** - Application with sidebar navigation
✅ **9 Module Buttons** - Dashboard, Recipes, Inventory, etc.
✅ **Status Bar** - Shows user, connection status
✅ **Menu System** - File, Edit, View, Tools menus

**Note:** The 9 modules are placeholders (Phase 2 not yet built). But the core infrastructure works perfectly!

---

## Alternative: Manual Setup

If the automatic setup doesn't work:

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Test Installation
```bash
python test_installation.py
```

### 3. Run Application
```bash
python main.py
```

---

## Troubleshooting

### "Python is not recognized"
- Install Python from: https://www.python.org/downloads/
- Make sure to check "Add Python to PATH"

### "tkinter not found"
- Reinstall Python
- Make sure "tcl/tk and IDLE" is checked during installation

### Other Issues
See detailed troubleshooting in: **LOCAL_SETUP_GUIDE.md**

---

## Files You Need

| File | Purpose |
|------|---------|
| `START_HERE.md` | This file - quick start |
| `LOCAL_SETUP_GUIDE.md` | Detailed setup instructions |
| `setup.bat` | Automatic setup script (Windows) |
| `test_installation.py` | Test script to verify setup |
| `main.py` | Run this to start the application |
| `requirements.txt` | Python dependencies |

---

## Testing Checklist

- [ ] Application launches
- [ ] Login screen appears
- [ ] Can login with admin/admin123
- [ ] Main window loads
- [ ] Can click module buttons
- [ ] Status bar shows "Offline" (normal)
- [ ] Can logout
- [ ] Can close application

---

## What Works Now (Phase 1 Complete)

✅ Core infrastructure
✅ User authentication
✅ Database system
✅ Google Sheets sync framework
✅ Main window GUI
✅ Navigation system
✅ Module placeholders

---

## What's Next (Phase 2)

⬜ Build 9 feature modules:
1. Dashboard
2. Recipes
3. Inventory
4. Batches
5. Customers
6. Sales & Dispatch
7. Invoicing
8. Duty Calculator
9. Label Printing

See `CONTINUATION_GUIDE.md` for development roadmap.

---

## Need More Help?

📄 **LOCAL_SETUP_GUIDE.md** - Comprehensive setup guide
📄 **QUICK_START.md** - Project quick reference
📄 **README.md** - Project overview
📄 **TECHNICAL_SPECIFICATION.md** - Full specification

---

## System Requirements

**Minimum:**
- Windows 10 (64-bit)
- Python 3.11+
- 4 GB RAM
- 500 MB disk space

**Your System:**
- Windows 10/11
- Python installed from python.org
- Internet connection (for setup only)

---

## Support

If you encounter issues:

1. Check `LOCAL_SETUP_GUIDE.md` troubleshooting section
2. Run `python test_installation.py` to diagnose
3. Check Python version: `python --version` (need 3.11+)
4. Verify you're in correct directory
5. Check logs at: `C:\Users\darre\.brewerymanager\app.log`

---

**Ready to test? Run `setup.bat` now!** 🚀
