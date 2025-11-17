# Database Migrations Needed on Brewery Computer

**Date Created:** 2025-11-17
**From Session:** Home Computer
**For Next Session:** Brewery Computer

⚠️ **CRITICAL:** Run these migrations on the brewery computer before using the application!

---

## Overview

This session completed the UK HMRC duty calculation system (Phase 1 & Phase 2) and added comprehensive reporting modules. The brewery computer database needs these migrations to match the new code.

---

## Step-by-Step Migration Instructions

### 1. Pull Latest Code First

```bash
cd C:\Users\darre\Desktop\BreweryManager
git fetch origin
git checkout claude/read-start-0194aExHtBNpeEuauYj96Kvm
git pull origin claude/read-start-0194aExHtBNpeEuauYj96Kvm
```

### 2. Fix Table Schema Issues (Run These First)

Some tables may exist with old schemas. Fix them before running the main migration:

```bash
# Fix spoilt_beer table schema
python src/data_access/fix_spoilt_beer_table.py
# Answer: yes

# Fix duty_returns table schema
python src/data_access/fix_duty_returns_table.py
# Answer: yes
```

**Expected Output:** Both should show "✅ TABLE FIXED SUCCESSFULLY!"

### 3. Run Main Duty System Migration

```bash
python src/data_access/migrate_duty_system.py
# Answer: yes
```

**What This Adds:**

**New Tables:**
- `settings` - SPR duty rates (3 rates) + Full duty rate configuration
- `settings_containers` - Container specs with sediment allowances (Firkins, Pins, Kegs, Bottles)
- `batch_packaging_lines` - Packaging records with automatic duty calculations
- `spoilt_beer` - Post-packaging spoilage tracking for duty refunds
- `duty_returns` - Monthly HMRC duty return submissions

**Updated Tables:**
- `batches` table gets new columns:
  - `fermented_volume` - Total volume after fermentation
  - `packaged_volume` - Total volume packaged
  - `waste_volume` - Brewery losses (no duty paid)
  - `waste_percentage` - Waste as % of fermented volume

**Expected Output:** "✅ MIGRATION COMPLETED SUCCESSFULLY!"

### 4. Generate Test Data (Optional but Recommended)

```bash
python src/testing/generate_test_data.py
# Answer: yes
```

**What This Creates:**
- 4 test batches covering all duty categories:
  - TEST001: Easy Session IPA (3.2% ABV, Draught Low)
  - TEST002: Classic Bitter (4.5% ABV, Draught Standard)
  - TEST003: West Coast IPA (5.8% ABV, Non-Draught Standard)
  - TEST004: Imperial Russian Stout (9.5% ABV, No SPR - Full Rate)

**Expected Output:** "✅ TEST DATA GENERATION COMPLETED!"

---

## Verification Steps

### Launch the Application
```bash
python main.py
```

### Check These Modules:

1. **Settings Module**
   - ✅ Should have 2 tabs: "Duty Rates" and "Containers"
   - ✅ Duty Rates tab shows SPR rates and Full rate
   - ✅ Containers tab shows 9 container types with duty-paid volumes

2. **Duty Module**
   - ✅ Loads without errors
   - ✅ Shows month selector
   - ✅ If test data was run, shows duty calculations for test batches
   - ✅ Shows spoilt beer deductions

3. **Production Module → Batches**
   - ✅ Package dialog shows containers with duty-paid volumes
   - ✅ Packaging automatically calculates duty

4. **Products Module**
   - ✅ Has 2 tabs: "Products" and "Spoilt Beer"
   - ✅ Spoilt Beer tab loads without errors

5. **Reports Module**
   - ✅ Has 5 tabs: Sales, Inventory, Production, Financial, Duty Reports
   - ✅ All tabs load without errors
   - ✅ If test data was run, Production and Duty reports show data

---

## Troubleshooting

### Error: "no such table: settings"
- Run the main migration: `python src/data_access/migrate_duty_system.py`

### Error: "no such column: duty_month"
- Run fix scripts first: `python src/data_access/fix_spoilt_beer_table.py` and `fix_duty_returns_table.py`

### Error: "'ReportsModule' object has no attribute 'load_sales_report'"
- Clear Python cache: `rd /s /q src\gui\__pycache__`
- This was fixed in commit d3de25b

### Application crashes on startup
1. Check you pulled the latest code
2. Clear all Python cache: `for /d /r . %d in (__pycache__) do @if exist "%d" rd /s /q "%d"`
3. Re-run migrations

---

## What's New in This Update

### Phase 1: Duty System Foundation
- ✅ Settings module with duty rates configuration
- ✅ Container configuration with sediment allowances
- ✅ Duty module for monthly HMRC returns
- ✅ Spoilt beer tracking (Products module)
- ✅ Database migration system

### Phase 2: Automatic Duty Integration
- ✅ Batch packaging automatically calculates duty
- ✅ SPR category auto-determination (based on ABV and draught status)
- ✅ Waste tracking and monitoring
- ✅ Immutable audit trail (duty rates snapshot at packaging time)

### Phase 3: Comprehensive Reporting
- ✅ Sales Reports (revenue by product/customer)
- ✅ Inventory Reports (stock levels, aging, value)
- ✅ Production Reports (volume, efficiency, packaging mix)
- ✅ Financial Reports (P&L with duty impact)
- ✅ Enhanced Duty Reports (historical view)

### Bug Fixes
- ✅ Fixed datetime import conflicts
- ✅ Fixed cache API usage across all modules
- ✅ Fixed test data generator schema issues
- ✅ Improved tab visibility across all modules
- ✅ Fixed Reports module method placement

---

## Important Notes

⚠️ **Database Path:**
- Home computer: `C:\Users\Tonk\.brewerymanager\cache.db`
- Brewery computer: `C:\Users\darre\.brewerymanager\cache.db`

These are SEPARATE databases! The migrations only affect the brewery computer database.

⚠️ **Production Data:**
If you have real production data on the brewery computer:
- The migration is NON-DESTRUCTIVE
- Existing batches, recipes, customers, etc. are preserved
- Only NEW tables/columns are added
- Test data is optional and uses distinct gyle numbers (TEST001-TEST004)

⚠️ **Backup Recommended:**
Before running migrations on production database:
```bash
copy C:\Users\darre\.brewerymanager\cache.db C:\Users\darre\.brewerymanager\cache_backup_2025-11-17.db
```

---

## Summary Checklist

Before using the app on brewery computer:

- [ ] Pull latest code from GitHub
- [ ] Run fix_spoilt_beer_table.py
- [ ] Run fix_duty_returns_table.py
- [ ] Run migrate_duty_system.py
- [ ] (Optional) Run generate_test_data.py
- [ ] Clear Python cache
- [ ] Launch app and verify all modules
- [ ] Test packaging a batch to see automatic duty calculation

Once verified, you're ready to go! ✅
