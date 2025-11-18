# Database Migrations Needed

**Date Updated:** 2025-11-18
**From Session:** Home Computer (Session ID: 01NXxfYeUfGj4t7fo3VfjLat)
**Status:** Label printing + VAT rate migrations pending on BREWERY computer

---

## Current Status

✅ **Duty system migrations completed** (Nov 17 migrations were run at start of this session)
- fix_spoilt_beer_table.py ✅ Run
- fix_duty_returns_table.py ✅ Run
- migrate_duty_system.py ✅ Run
- generate_test_data.py ✅ Run

⚠️ **NEW: Two migrations need to be run on brewery computer**
1. Label printing migration
2. VAT rate migration

---

## Migrations Required on Brewery Computer

### 1. Run Label Printing Migration

This migration adds label printing capabilities to the application.

```bash
python src/data_access/migrate_label_printing.py
# Answer: yes
```

**What This Adds:**

**Updated Tables:**
- `recipes` table gets new column:
  - `allergens` TEXT - Store allergen information for label printing

- `batch_packaging_lines` table gets new column:
  - `fill_number` INTEGER - Track sequential container numbering (1 of 10, 2 of 10, etc.)

**Expected Output:** "✅ MIGRATION COMPLETED SUCCESSFULLY!"

---

### 2. Run VAT Rate Migration

This migration adds configurable VAT rate to Settings.

```bash
python src/data_access/migrate_add_vat.py
```

**What This Adds:**

**Updated Tables:**
- `settings` table gets new column:
  - `vat_rate` REAL DEFAULT 0.20 - Configurable VAT rate (0.20 = 20%)

**Note:** If you haven't run migrate_duty_system.py yet, the newer version already includes vat_rate, so this migration may not be needed. The script will check and skip if already exists.

**Expected Output:**
```
============================================================
Migration: Add VAT Rate to Settings
============================================================

Adding vat_rate column to settings table...
✓ vat_rate column added successfully (default: 0.20 = 20%)

============================================================
Migration completed successfully!
============================================================
```

---

## Verification Steps

### 1. Launch the Application
```bash
python main.py
```

### 2. Test Label Printing Feature

**Recipe Editor:**
- ✅ Recipe dialog should have "Allergens (for labels)" field
- ✅ Can enter allergen info (e.g., "Gluten (Barley), Sulphites")

**Production Module - Package Batch:**
- ✅ Package dialog now has 3 buttons: "Print Labels", "Save", "Package"
- ✅ "Print Labels" generates PDF with auto-populated labels
- ✅ Labels include: beer name, packaged date, ABV, gyle/fill number, duty paid volume, allergens
- ✅ Sequential numbering across all containers (1 of 10, 2 of 10, etc.)

**Label PDF:**
- ✅ Generated in: `~/.brewerymanager/labels/`
- ✅ Filename format: `[GYLE]_labels_[TIMESTAMP].pdf`
- ✅ PDF opens automatically (if possible)
- ✅ One label per page (100mm x 150mm default)

### 3. Test VAT Rate Feature

**Settings Module - Duty Rates Tab:**
- ✅ VAT Rate section should appear below Full Duty Rate
- ✅ Shows current VAT rate (default: 20%)
- ✅ Can edit and save VAT rate (0-100%)
- ✅ Success message confirms new rate

**Invoicing Module:**
- ✅ Create Invoice dialog loads VAT from settings (not hardcoded 20%)
- ✅ Can override VAT per invoice if needed
- ✅ New invoices use updated VAT rate
- ✅ Existing invoices keep original VAT rate

### 4. Workflow Test

1. Create/edit a recipe and add allergen info
2. Start packaging a batch
3. Click "Print Labels" - should generate PDF (F.G. not required)
4. Click "Save" - saves container selections (dialog stays open)
5. Enter F.G. value
6. Click "Package" - finalizes batch with duty calculations

---

## What's New in This Session

### VAT Rate Configuration (Session 01NXxfYeUfGj4t7fo3VfjLat - Home Computer)
- ✅ Added configurable VAT rate to Settings module
- ✅ Database migration for vat_rate column
- ✅ Settings GUI with VAT Rate section
- ✅ Invoicing loads VAT from settings (not hardcoded)
- ✅ Bug fix: sqlite3.Row attribute handling

### Label Printing Feature (Session 015MECmeLgcS95t2bHSnVb24 - Brewery Computer)
- ✅ Database migration for allergens and fill numbering
- ✅ Label printer utility (`src/utilities/label_printer.py`)
- ✅ ReportLab PDF generation
- ✅ Recipe editor allergen field
- ✅ PackageDialog redesigned with 3-button workflow
- ✅ Removed standalone Label Printing module

### UX Improvements
- ✅ Mousewheel scrolling in all 11 GUI modules
- ✅ Keyboard arrow navigation for all Treeviews
- ✅ Canvas scrolling (Page Up/Down, Home/End)
- ✅ Resize grips added to 12 dialogs
- ✅ Responsive dialog sizing

### Google Sheets Preparation
- ✅ Implementation plan created (`GOOGLE_SHEETS_IMPLEMENTATION_PLAN.md`)
- ✅ Ready for Phase A implementation after testing

### Bug Fixes
- ✅ Fixed PackageDialog AttributeError (self.cache.conn → self.cache.connection)

---

## Commits in This Session

1. `5923255` - Add session log for November 18 brewery session
2. `cd55d97` - Add diagnostic script for container configuration
3. `6cb1a88` - Fix: Use correct connection attribute in PackageDialog
4. `c7c1432` - Add mousewheel and keyboard scrolling support
5. `f5747df` - Add scrolling and resize grips to all GUI modules
6. `ee5f447` - Add label printing foundation (Part 1/2)
7. `06c3415` - Redesign PackageDialog with 3-button workflow (Part 2/2)
8. `48208ea` - Remove standalone Label Printing module
9. `bf68db9` - Update session log with label printing implementation
10. `5b15b6e` - Add Google Sheets implementation plan and update session log

---

## Important Notes

⚠️ **This is the BREWERY computer database**
- Database path: `~/.brewerymanager/cache.db`
- Label printing migration needs to be run on THIS computer
- Once run, all label printing features will be available

⚠️ **Migration is Non-Destructive**
- Only adds new columns to existing tables
- No data is deleted or modified
- Existing recipes and batches are preserved

⚠️ **Backup Recommended**
Before running migration:
```bash
cp ~/.brewerymanager/cache.db ~/.brewerymanager/cache_backup_2025-11-18.db
```

---

## Next Steps

**Immediate:**
1. Run label printing migration: `python src/data_access/migrate_label_printing.py`
2. Test label printing workflow with a real batch
3. Verify PDF generation and formatting

**Future:**
- Complete testing checklist (see `TESTING_CHECKLIST.md`)
- Implement Google Sheets sync (see `GOOGLE_SHEETS_IMPLEMENTATION_PLAN.md`)

---

## Summary Checklist

**Migrations:**
- [ ] Run migrate_label_printing.py
- [ ] Run migrate_add_vat.py (or verify vat_rate exists in settings table)

**Label Printing Tests:**
- [ ] Test recipe editor allergen field
- [ ] Test batch packaging with label printing
- [ ] Verify PDF generation in `~/.brewerymanager/labels/`
- [ ] Test 3-button workflow (Print/Save/Package)

**VAT Rate Tests:**
- [ ] Test Settings → Duty Rates → VAT Rate section
- [ ] Test changing and saving VAT rate
- [ ] Test invoice creation uses VAT from settings

**Final:**
- [ ] Complete full testing checklist before Google Sheets implementation

Once verified, all features ready for production use! ✅
