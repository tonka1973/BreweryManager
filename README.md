# 🍺 BREWERY MANAGEMENT SYSTEM

**Windows Desktop Application for Commercial Brewery Management**

---

## 🚀 WANT TO TEST THE APP? START HERE!

**→ [START_HERE.md](START_HERE.md)** ← Quick setup for local testing (2 minutes!)

**→ [LOCAL_SETUP_GUIDE.md](LOCAL_SETUP_GUIDE.md)** ← Detailed setup instructions

**Default Login:** admin / admin (change after first login!)

---

## 📚 DOCUMENTATION INDEX

**New to this project? Start here:**

1. **START_HERE.md** ← Local testing setup (NEW!)
2. **LOCAL_SETUP_GUIDE.md** ← Detailed setup guide (NEW!)
3. **QUICK_START.md** ← Project quick reference
   - One-page summary
   - Current status at a glance
   - What to do next

2. **PROGRESS_TRACKER.md** ← Visual progress map
   - See exactly where we are
   - Visual milestone tracker
   - Timeline estimates

3. **CONTINUATION_GUIDE.md** ← Complete instructions
   - Full step-by-step guide
   - Code templates
   - All commands needed
   - Reference documentation

4. **PROGRESS.md** ← Detailed current status
   - What's been completed
   - What's in progress
   - What's remaining

5. **TECHNICAL_SPECIFICATION.md** ← Full project requirements
   - All features listed
   - Complete technical spec
   - System architecture

6. **UK_ALCOHOL_DUTY_REFERENCE.md** ← Critical reference
   - UK duty calculation rules
   - Current rates (Feb 2025)
   - Draught Relief calculations
   - Small Producer Relief tables
   - **Must use for Duty Calculator module!**

---

## 🚀 QUICK RESUME (For New AI Sessions)

```
Step 1: Read QUICK_START.md (1 minute)
Step 2: Read PROGRESS.md (2 minutes)
Step 3: Read CONTINUATION_GUIDE.md (5 minutes)
Step 4: Ask user for confirmation
Step 5: Continue from current task
```

---

## 📁 PROJECT STRUCTURE

```
BreweryManager/
├── README.md                        ← You are here
├── QUICK_START.md                   ← Start here!
├── CONTINUATION_GUIDE.md            ← Full instructions
├── PROGRESS.md                      ← Current status
├── PROGRESS_TRACKER.md              ← Visual tracker
├── TECHNICAL_SPECIFICATION.md       ← Complete spec
├── UK_ALCOHOL_DUTY_REFERENCE.md     ← Duty calculations
├── main.py                          ← Entry point
├── requirements.txt                 ← Dependencies
├── config/
│   └── settings.json               ← Configuration
└── src/
    ├── api/                         ← Google Sheets
    ├── database/                    ← SQLite
    ├── sync/                        ← Cloud sync
    ├── utilities/                   ← Auth system
    ├── gui/                         ← User interface
    └── modules/                     ← 9 feature modules
```

---

## 🎯 CURRENT STATUS

**Phase 1: Core Infrastructure** → ✅ 100% Complete
- ✅ All 8 components built and tested
- ✅ Database, API, Sync, Auth, Main Window GUI
- ✅ Backend systems fully operational

**Phase 2: Module Implementation** → ✅ 100% Complete
- ✅ All 9 feature modules built (178 KB of code)
- ✅ Dashboard, Recipes, Inventory, Batches, Customers
- ✅ Sales, Invoicing, Duty Calculator, Label Printing

**Phase 3: Integration & Testing** → 🔄 In Progress
- Testing module functionality
- Setting up two-computer workflow
- Fixing integration bugs

**Phase 4: Packaging & Deployment** → Not started

**Overall Project:** ~75% Complete

---

## 🛠️ WHAT THIS WILL BE

A complete Windows desktop application (.exe installer) for managing a commercial brewery:

- **Recipe Management** - Create, scale, store recipes
- **Inventory Tracking** - Ingredients & finished goods
- **Batch Management** - Full gyle tracking & traceability
- **Customer CRM** - Customer database with preferences
- **Sales & Dispatch** - Record sales, track deliveries
- **Invoicing** - Generate invoices, track payments
- **UK Duty Calculator** - Automatic duty calculations
- **Label Printing** - Professional cask labels
- **Google Sheets Sync** - Cloud backup & multi-computer access
- **Offline Mode** - Works without internet

---

## 💡 KEY FEATURES

- ✅ Offline-first design (works without internet)
- ✅ Google Sheets cloud sync across multiple computers
- ✅ User authentication with roles (admin/manager/staff)
- ✅ Automatic duty calculations (UK regulations)
- ✅ Complete ingredient → batch → customer traceability
- ✅ Professional invoicing with VAT
- ✅ Cask label printing with brewery logo
- ✅ No ongoing subscription required

---

## 🎨 USER INTERFACE

9 main modules accessible from sidebar navigation:
1. Dashboard - Overview and alerts
2. Recipes - Beer recipes with scaling
3. Inventory - Materials and finished goods
4. Batches - Gyle tracking and brewing logs
5. Customers - CRM with sales history
6. Sales - Dispatch and order management
7. Invoicing - Generate invoices, track payments
8. Duty Calculator - UK duty calculations
9. Label Printing - Professional cask labels

---

## 🔧 TECHNOLOGY STACK

- **Language:** Python 3.x
- **GUI:** tkinter
- **Database:** SQLite (local caching)
- **Cloud:** Google Sheets API
- **PDF Generation:** ReportLab
- **Packaging:** PyInstaller → .exe

---

## 📦 DEPENDENCIES

```
gspread==5.12.0          # Google Sheets API
oauth2client==4.1.3      # Google authentication
pillow==10.1.0           # Image handling
reportlab==4.0.7         # PDF generation
python-barcode==0.15.1   # Barcode generation
```

---

## 🏗️ DEVELOPMENT PHASES

### Phase 1: Core Infrastructure ✅ (100% Complete)
Backend systems, API clients, database, sync manager, authentication
- All infrastructure components built and tested
- Main Window GUI framework completed

### Phase 2: Module Implementation ✅ (100% Complete)
Build all 9 feature modules
- ✅ Dashboard (16 KB) - Overview and system alerts
- ✅ Recipes (23 KB) - Recipe management with scaling
- ✅ Inventory (16 KB) - Ingredient and finished goods tracking
- ✅ Batches (21 KB) - Gyle management and brewing logs
- ✅ Customers (19 KB) - Customer CRM with sales history
- ✅ Sales (17 KB) - Dispatch and order management
- ✅ Invoicing (23 KB) - Invoice generation and payment tracking
- ✅ Duty Calculator (11 KB) - UK duty calculations
- ✅ Label Printing (12 KB) - Professional cask labels

### Phase 3: Integration & Testing 🔄 (In Progress)
Connect modules, test workflows, fix bugs
- Testing module functionality
- Two-computer Git workflow established
- Documentation created

### Phase 4: Packaging & Deployment (Not Started)
Create .exe installer, documentation, final testing

---

## 👤 USER PREFERENCES

- **Path:** `C:\Users\darre\Desktop\BreweryManager\`
- **Workflow:** Always ask before implementing changes
- **Build Trigger:** Only start coding when user says "build"

---

## 📞 FOR NEW AI ASSISTANTS

If you're picking up this project:

1. Read **QUICK_START.md** first (1-page overview)
2. Read **PROGRESS.md** (current detailed status)
3. Read **CONTINUATION_GUIDE.md** (complete instructions)
4. Ask the user if they want to continue
5. Follow the step-by-step guide from where it left off

**Do NOT start building without asking the user first!**

---

## 🎉 PROJECT GOAL

Create a professional, production-ready brewery management system that:
- Installs with a single .exe file
- Works reliably offline
- Syncs seamlessly to the cloud
- Handles all brewery operations
- Calculates UK duty accurately
- Requires no technical knowledge to use

---

**Last Updated:** November 7, 2025
**Project Status:** Phase 3 - Integration & Testing
**Next Task:** Complete testing and begin Phase 4 (Packaging)

---

*Built with attention to detail for real-world brewery operations* 🍺
