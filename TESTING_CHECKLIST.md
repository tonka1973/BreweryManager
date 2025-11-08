# 🍺 BREWERY MANAGER - COMPREHENSIVE TESTING CHECKLIST

**Version:** Phase 2 Complete (All 9 Modules)
**Date:** November 2025
**Test Environment:** Windows Desktop
**Login:** `admin` / `admin`

---

## 📋 PRE-TESTING SETUP

### ✅ Step 1: Update Code
```bash
cd C:\Users\darre\Desktop\BreweryManager
git pull origin claude/work-in-progress-011CUrnRK9wxKPu695Qap243
```

### ✅ Step 2: Sample Data (Already loaded)
Sample data includes:
- 3 recipes (Pale Ale, IPA, Porter)
- 4 batches in various stages
- 3 customers (Red Lion, The Swan, The Bell Inn)
- 4 inventory items (some low stock)
- 3 sales records
- Invoice data

### ✅ Step 3: Launch Application
```bash
python main.py
```

**Login:** `admin` / `admin`

---

## 🎯 MODULE TESTING CHECKLIST

---

## ✅ MODULE 1: DASHBOARD

### Test 1.1: Quick Stats Cards
- [ ] **Total Batches** shows 4
- [ ] **In Production** shows 3
- [ ] **Customers** shows 3
- [ ] **Sales (Month)** shows count

**Expected:** Numbers match sample data

### Test 1.2: Recent Batches List
- [ ] Shows up to 10 recent batches
- [ ] Color coded by status:
  - 🟦 Blue = Brewing
  - 🟧 Orange = Fermenting
  - 🟪 Purple = Conditioning
  - 🟩 Green = Ready
  - ⬜ Grey = Packaged
- [ ] Displays: Gyle number, Beer name, Brew date, Status

**Expected:** 4 batches visible with correct colors

### Test 1.3: Alerts Section
- [ ] Shows **low stock alerts** (Crystal Malt, Cascade Hops, Ale Yeast)
- [ ] Shows **batches ready for packaging** (if any)
- [ ] Shows **overdue invoices** (if any)
- [ ] Displays "No alerts" if none present

**Expected:** At least 3 low stock alerts visible

### Test 1.4: Upcoming Deliveries
- [ ] Shows deliveries in next 7 days
- [ ] Displays: Date, Customer, Beer, Quantity
- [ ] Shows "No deliveries" if none scheduled

**Expected:** 2 upcoming deliveries visible

---

## ✅ MODULE 2: RECIPES

### Test 2.1: View Recipe List
- [ ] Click **"Recipes"** in sidebar
- [ ] See 3 existing recipes (Pale Ale, IPA, Porter)
- [ ] Recipes show: Name, Style, ABV, Batch Size, Version, Status
- [ ] Active recipes highlighted green

**Expected:** 3 recipes visible

### Test 2.2: Add New Recipe
- [ ] Click **"➕ New Recipe"**
- [ ] Fill in form:
  - Recipe Name: "Golden Ale"
  - Style: "Golden Ale"
  - ABV: 4.5
  - Batch Size: 800
  - Version: 1
  - Check "Active Recipe"
  - Notes: "Light and refreshing summer ale"
- [ ] Click **"Save Recipe"**
- [ ] See success message
- [ ] New recipe appears in list

**Expected:** 4 recipes now visible, Golden Ale at top (alphabetically)

### Test 2.3: Edit Recipe
- [ ] Select "Pale Ale"
- [ ] Click **"✏️ Edit Recipe"**
- [ ] Change ABV to: 4.3
- [ ] Add note: "Updated ABV for consistency"
- [ ] Click **"Save Recipe"**
- [ ] See success message

**Expected:** Pale Ale now shows 4.3% ABV

### Test 2.4: View Recipe Details
- [ ] Select "IPA"
- [ ] Click **"👁️ View Details"** (or double-click)
- [ ] See full recipe information:
  - Name, Style, ABV, Batch size
  - Version, Status
  - Created date, Last modified
  - Brewing notes
- [ ] Click **"Close"**

**Expected:** Detailed view opens and closes properly

### Test 2.5: Search Recipes
- [ ] Type "IPA" in search box
- [ ] Only IPA recipe shows
- [ ] Clear search
- [ ] All recipes reappear

**Expected:** Search filters correctly

### Test 2.6: Delete Recipe
- [ ] Select "Porter"
- [ ] Click **"🗑️ Delete"**
- [ ] Confirm deletion
- [ ] Recipe removed from list

**Expected:** Only 3 recipes remain (Porter gone)

---

## ✅ MODULE 3: INVENTORY

### Test 3.1: View Inventory List
- [ ] Click **"Inventory"** in sidebar
- [ ] See 4 materials listed
- [ ] Color coding:
  - 🟢 Green = Stock OK
  - 🔴 Red = Low stock (below reorder level)
- [ ] Shows: Material, Type, Stock, Unit, Reorder Level, Supplier, Cost

**Expected:** 2 items red (low stock), 2 items green

### Test 3.2: Add New Material
- [ ] Click **"➕ Add Material"**
- [ ] Fill in form:
  - Material Name: "Chocolate Malt"
  - Type: grain
  - Stock: 50
  - Unit: kg
  - Reorder Level: 20
  - Cost per Unit: 1.80
  - Supplier: "Malt Suppliers Ltd"
- [ ] Click **"Save"**
- [ ] See success message

**Expected:** 5 materials now visible, Chocolate Malt shown (green)

### Test 3.3: Edit Material
- [ ] Select "Pale Malt"
- [ ] Click **"✏️ Edit"**
- [ ] Change stock to: 200
- [ ] Change cost to: 1.25
- [ ] Click **"Save"**

**Expected:** Pale Malt updated with new values

### Test 3.4: Adjust Stock (Add)
- [ ] Select "Crystal Malt" (currently low stock - red)
- [ ] Click **"📦 Adjust Stock"**
- [ ] Select **"Add Stock"**
- [ ] Quantity: 50
- [ ] Notes: "New delivery from supplier"
- [ ] Click **"Apply"**
- [ ] See success message

**Expected:** Stock increases by 50, color changes from red to green

### Test 3.5: Adjust Stock (Remove)
- [ ] Select "Pale Malt"
- [ ] Click **"📦 Adjust Stock"**
- [ ] Select **"Remove Stock"**
- [ ] Quantity: 25
- [ ] Notes: "Used in batch brewing"
- [ ] Click **"Apply"**

**Expected:** Stock decreases by 25

### Test 3.6: Stock Alert Validation
- [ ] Try to remove more stock than available
- [ ] See error: "Stock cannot be negative"

**Expected:** Error prevents negative stock

### Test 3.7: Delete Material
- [ ] Select a material
- [ ] Click **"🗑️ Delete"**
- [ ] Confirm deletion
- [ ] Material removed

**Expected:** Material deleted successfully

---

## ✅ MODULE 4: BATCHES

### Test 4.1: View Batches List
- [ ] Click **"Batches"** in sidebar
- [ ] See 4 batches in various stages
- [ ] Color coding matches status
- [ ] Shows: Gyle, Recipe, Brew Date, ABV, Volume, Status, Brewer

**Expected:** 4 batches visible with colors

### Test 4.2: Filter by Status
- [ ] Change status filter to **"fermenting"**
- [ ] Only fermenting batches show
- [ ] Change filter back to **"all"**

**Expected:** Filter works correctly

### Test 4.3: Add New Batch
- [ ] Click **"➕ New Batch"**
- [ ] Select Recipe: "Pale Ale"
- [ ] Gyle Number: Auto-generated (GYLE-2025-005)
- [ ] Brew Date: Today's date (auto-filled)
- [ ] Brewer: Your name (auto-filled)
- [ ] Batch Size: 800
- [ ] ABV: 4.3
- [ ] Status: brewing
- [ ] Notes: "Test batch for new recipe version"
- [ ] Click **"Save Batch"**

**Expected:** New batch GYLE-2025-005 appears, pure alcohol auto-calculated

### Test 4.4: View Batch Details
- [ ] Select GYLE-2025-001
- [ ] Click **"👁️ View Details"** (or double-click)
- [ ] See full batch information:
  - Recipe name, Dates, Brewer, Size, ABV
  - Pure alcohol calculation
  - Production timeline dates
  - Brewing notes
- [ ] Click **"Close"**

**Expected:** Full traceability information displayed

### Test 4.5: Update Batch Status
- [ ] Select GYLE-2025-005 (brewing)
- [ ] Click **"📊 Update Status"**
- [ ] Change to: **"fermenting"**
- [ ] Click **"Update"**
- [ ] See success message
- [ ] Color changes to orange

**Expected:** Status updated, fermenting_start date auto-set

### Test 4.6: Status Progression
- [ ] Select same batch
- [ ] Update status to: **"conditioning"**
- [ ] Update status to: **"ready"**
- [ ] Update status to: **"packaged"**
- [ ] Watch colors change each time

**Expected:** Each status change sets corresponding date field

### Test 4.7: Edit Batch
- [ ] Select a batch
- [ ] Click **"✏️ Edit"**
- [ ] Change ABV or add notes
- [ ] Click **"Save Batch"**

**Expected:** Batch updated successfully

---

## ✅ MODULE 5: DUTY CALCULATOR ⭐ (CRITICAL)

### Test 5.1: Basic Calculation
- [ ] Click **"Duty Calculator"** in sidebar
- [ ] Left side shows calculator
- [ ] Right side shows rates reference
- [ ] Enter:
  - Volume: 800
  - ABV: 4.2
  - ✅ Draught (checked)
  - SPR Rate: 4.87
- [ ] Click **"Calculate Duty"**

**Expected Result:**
```
Pure Alcohol: 33.60 litres (0.3360 hl)
Base Duty Rate: £18.76/hl
SPR Discount: £4.87/hl
Effective Rate: £13.89/hl
DUTY PAYABLE: £46.67
```

### Test 5.2: Non-Draught Calculation
- [ ] Uncheck **"Draught (cask ≥20L)"**
- [ ] Click **"Calculate Duty"**

**Expected:** Higher duty (£21.78/hl base instead of £18.76/hl)

### Test 5.3: Different ABV Bands
Test each ABV band:
- [ ] ABV 3.0% → £8.28/hl (draught) or £9.61/hl (non-draught)
- [ ] ABV 5.0% → £18.76/hl (draught) or £21.78/hl (non-draught)
- [ ] ABV 9.0% → £29.54/hl (both - no draught relief)

**Expected:** Correct rate for each band

### Test 5.4: SPR Impact
- [ ] Set SPR Rate to: 10.00
- [ ] Recalculate
- [ ] See higher duty (less SPR discount)
- [ ] Set SPR to: 0.00
- [ ] See full rate applied (no SPR)

**Expected:** SPR correctly deducted from base rate

### Test 5.5: Large Batch Calculation
- [ ] Volume: 1600
- [ ] ABV: 5.8
- [ ] Draught: Yes
- [ ] SPR: 4.87
- [ ] Calculate

**Expected:** Larger duty amount (more volume)

### Test 5.6: Rates Reference Panel
- [ ] Verify right side shows:
  - Non-draught rates
  - Draught rates with 13.9% relief
  - SPR explanation
  - Example calculation
- [ ] Compare calculated results to reference

**Expected:** Rates match February 2025 HMRC specifications

---

## ✅ MODULE 6: CUSTOMERS

### Test 6.1: View Customer List
- [ ] Click **"Customers"** in sidebar
- [ ] See 3 existing customers
- [ ] Active customers highlighted green
- [ ] Shows: Name, Contact, Phone, Email, Type, Terms, Status

**Expected:** 3 customers visible (all active/green)

### Test 6.2: Add New Customer
- [ ] Click **"➕ New Customer"**
- [ ] Fill in form:
  - Customer Name: "The Kings Arms"
  - Contact Person: "Tom Wilson"
  - Phone: "01234 111222"
  - Email: "tom@kingsarms.co.uk"
  - Delivery Address: "56 High Street, Townville, TC1 2AB"
  - Billing Address: (same)
  - Type: pub
  - Payment Terms: net_14
  - Credit Limit: 1500
  - Delivery Day: Thursday
  - Time: 11:00
  - Likes: "IPAs, Strong ales"
  - Dislikes: "Very pale beers"
  - Notes: "Good regular customer"
- [ ] Click **"Save Customer"**

**Expected:** 4 customers now visible

### Test 6.3: Edit Customer
- [ ] Select "The Red Lion"
- [ ] Click **"✏️ Edit"**
- [ ] Change credit limit to: 1200
- [ ] Add note: "Increased credit limit"
- [ ] Click **"Save Customer"**

**Expected:** Customer updated

### Test 6.4: View Customer Details
- [ ] Select "The Swan"
- [ ] Click **"👁️ View Details"** (or double-click)
- [ ] See all customer information:
  - Contact details
  - Addresses
  - Type, Terms, Credit limit
  - Delivery preferences
  - Likes/Dislikes
  - Notes
- [ ] Click **"Close"**

**Expected:** Full customer profile displayed

### Test 6.5: Search Customers
- [ ] Type "Lion" in search box
- [ ] Only "Red Lion" and "Kings Arms" show
- [ ] Clear search

**Expected:** Search filters by name

### Test 6.6: Deactivate Customer
- [ ] Select "The Bell Inn"
- [ ] Click **"🗑️ Deactivate"**
- [ ] Confirm
- [ ] Customer turns red (inactive)

**Expected:** Customer deactivated but not deleted

---

## ✅ MODULE 7: SALES

### Test 7.1: View Sales List
- [ ] Click **"Sales"** in sidebar
- [ ] See existing sales
- [ ] Color coding:
  - 🟧 Orange = Reserved
  - 🟩 Green = Delivered
- [ ] Shows: Date, Customer, Beer, Container, Qty, Total, Delivery, Status

**Expected:** Sample sales visible

### Test 7.2: Add New Sale
- [ ] Click **"➕ New Sale"**
- [ ] Select Customer: "The Red Lion"
- [ ] Select Batch: GYLE-2025-002 (or any ready/packaged)
- [ ] Beer Name: Auto-fills from batch
- [ ] Container Type: firkin
- [ ] Quantity: 2
- [ ] Unit Price: 65.00
- [ ] Sale Date: Today
- [ ] Delivery Date: 3 days from now
- [ ] Status: reserved
- [ ] Notes: "Regular order"
- [ ] Click **"Save Sale"**

**Expected:** New sale appears (orange/reserved), total calculated (2 × £65 = £130)

### Test 7.3: Edit Sale
- [ ] Select a reserved sale
- [ ] Click **"✏️ Edit"**
- [ ] Change quantity to: 3
- [ ] Change delivery date
- [ ] Click **"Save Sale"**

**Expected:** Sale updated, new total calculated

### Test 7.4: Mark as Delivered
- [ ] Select a **reserved** sale
- [ ] Click **"✅ Mark Delivered"**
- [ ] Confirm
- [ ] Status changes to "delivered"
- [ ] Color changes to green
- [ ] Delivery date set to today

**Expected:** Status updated to delivered

### Test 7.5: Filter by Status
- [ ] Change filter to **"reserved"**
- [ ] Only reserved sales show
- [ ] Change to **"delivered"**
- [ ] Only delivered sales show
- [ ] Change to **"all"**

**Expected:** Filter works correctly

### Test 7.6: Container Size Auto-Calculation
- [ ] Add new sale with:
  - Firkin (40.9L) × 2 = 81.8L total
  - Pin (20.5L) × 1 = 20.5L total
  - Kilderkin (81.8L) × 1 = 81.8L total

**Expected:** Total litres calculated correctly

---

## ✅ MODULE 8: INVOICING

### Test 8.1: View Invoice List
- [ ] Click **"Invoicing"** in sidebar
- [ ] See existing invoices (if any)
- [ ] Color coding:
  - 🔴 Red = Unpaid
  - 🟧 Orange = Partially paid
  - 🟩 Green = Paid
- [ ] Shows: Invoice #, Date, Customer, Subtotal, VAT, Total, Paid, Outstanding, Status

**Expected:** Invoice list displayed

### Test 8.2: Create Invoice from Sales
- [ ] Click **"➕ Create Invoice"**
- [ ] Select Customer: "The Red Lion"
- [ ] See delivered sales (not yet invoiced)
- [ ] Check ☑ boxes to select sales (click on "☐")
- [ ] VAT Rate: 20% (default)
- [ ] Click **"Create Invoice"**
- [ ] See success message with invoice number (INV-2025-0001)

**Expected:** Invoice created, shows subtotal + 20% VAT = total

### Test 8.3: View Invoice
- [ ] Select an invoice
- [ ] Click **"👁️ View Invoice"**
- [ ] See:
  - Invoice number, customer, dates
  - Line items with gyle numbers
  - Subtotal, VAT, Total
  - Amount paid, Outstanding
- [ ] Click **"Close"**

**Expected:** Full invoice details displayed

### Test 8.4: Record Payment (Full)
- [ ] Select an **unpaid** invoice
- [ ] Click **"💰 Record Payment"**
- [ ] Outstanding amount shown
- [ ] Payment Amount: (full amount - default)
- [ ] Payment Method: bank_transfer
- [ ] Date: Today
- [ ] Reference: "BACS Transfer 123456"
- [ ] Click **"Record Payment"**
- [ ] See success message

**Expected:** Invoice status → "Paid" (green), outstanding = £0.00

### Test 8.5: Record Payment (Partial)
- [ ] Select an unpaid invoice
- [ ] Click **"💰 Record Payment"**
- [ ] Payment Amount: Enter half of outstanding
- [ ] Click **"Record Payment"**

**Expected:** Invoice status → "Partially Paid" (orange), outstanding reduced

### Test 8.6: Record Second Payment
- [ ] Select the partially paid invoice
- [ ] Record remaining balance
- [ ] Click **"Record Payment"**

**Expected:** Invoice status → "Paid" (green), outstanding = £0.00

### Test 8.7: Invoice Number Generation
- [ ] Create 3 invoices
- [ ] Check invoice numbers increment:
  - INV-2025-0001
  - INV-2025-0002
  - INV-2025-0003

**Expected:** Sequential numbering

### Test 8.8: Filter Invoices
- [ ] Filter by **"unpaid"**
- [ ] Filter by **"paid"**
- [ ] Filter by **"partially_paid"**
- [ ] Filter by **"all"**

**Expected:** Each filter shows correct invoices

### Test 8.9: Payment Validation
- [ ] Try to record payment > outstanding amount
- [ ] See error message

**Expected:** Overpayment prevented

---

## ✅ MODULE 9: LABEL PRINTING

### Test 9.1: Label Generation Setup
- [ ] Click **"Label Printing"** in sidebar
- [ ] See label configuration form
- [ ] Form shows:
  - Batch selection
  - Container type
  - Number of labels
  - Brewery name/address

**Expected:** Clean, centered form layout

### Test 9.2: Select Batch
- [ ] Select Batch: GYLE-2025-001 (or any ready/packaged)
- [ ] Beer name auto-fills
- [ ] ABV auto-fills

**Expected:** Beer details populate automatically

### Test 9.3: Configure Label
- [ ] Container Type: firkin
- [ ] Number of Labels: 3
- [ ] Brewery Name: "Your Brewery Name"
- [ ] Brewery Address:
  ```
  123 Brewery Lane
  Anytown, AB1 2CD
  United Kingdom
  ```

**Expected:** All fields editable

### Test 9.4: Generate PDF
- [ ] Click **"📄 Generate PDF Labels"**
- [ ] Choose save location (e.g., Desktop)
- [ ] Filename: GYLE-2025-001_labels.pdf
- [ ] Click **"Save"**
- [ ] See success message
- [ ] Click **"Yes"** to open PDF

**Expected:** PDF created with 3 labels (2 per page)

### Test 9.5: Verify PDF Content
Each label should show:
- [ ] Brewery name (large, top)
- [ ] Beer name (very large, center)
- [ ] ABV (large, prominent)
- [ ] Container type and gyle number
- [ ] Brewery address (small, bottom)

**Expected:** Professional, readable labels

### Test 9.6: Multiple Labels Test
- [ ] Generate 10 labels
- [ ] Check PDF has 5 pages (2 labels per page)

**Expected:** Correct pagination

### Test 9.7: Different Beer Types
- [ ] Generate labels for:
  - Pale Ale at 4.2%
  - IPA at 5.8%
  - Porter at 4.8%
- [ ] Verify each shows correct name and ABV

**Expected:** All labels accurate

---

## 🔄 CROSS-MODULE WORKFLOW TESTING

### Workflow 1: Complete Brewing Cycle
- [ ] **Recipes:** Create new recipe "Test Ale" (4.5% ABV, 800L)
- [ ] **Inventory:** Check stock of Pale Malt, Cascade Hops
- [ ] **Batches:** Create new batch using Test Ale recipe
- [ ] **Batches:** Update status: brewing → fermenting → conditioning → ready → packaged
- [ ] **Duty:** Calculate duty for completed batch
- [ ] **Labels:** Generate cask labels for batch

**Expected:** Full production workflow from recipe to labels

### Workflow 2: Complete Sales Cycle
- [ ] **Customers:** Add new customer
- [ ] **Batches:** Ensure batch is packaged
- [ ] **Sales:** Create sale to new customer
- [ ] **Sales:** Mark sale as delivered
- [ ] **Invoicing:** Create invoice from delivered sale
- [ ] **Invoicing:** Record payment
- [ ] **Dashboard:** Check all updates reflected in dashboard stats

**Expected:** Full sales cycle from order to payment

### Workflow 3: Low Stock Alert to Restocking
- [ ] **Dashboard:** See low stock alert for Crystal Malt
- [ ] **Inventory:** Navigate to Inventory
- [ ] **Inventory:** Find Crystal Malt (red/low stock)
- [ ] **Inventory:** Adjust stock (add 100kg)
- [ ] **Dashboard:** Return to Dashboard
- [ ] **Dashboard:** Low stock alert gone for Crystal Malt

**Expected:** Alert disappears after restocking

### Workflow 4: Recipe Scaling for Production
- [ ] **Recipes:** View IPA recipe (target 800L)
- [ ] **Batches:** Create batch with actual size 750L
- [ ] **Batches:** Note difference from target
- [ ] **Inventory:** Check if ingredients sufficient
- [ ] **Batches:** Complete and package batch
- [ ] **Duty:** Calculate duty on actual volume (750L)

**Expected:** System handles variation from target

---

## 🐛 ERROR HANDLING & VALIDATION TESTING

### Data Validation Tests

#### Recipes Module
- [ ] Try to save recipe without name → Error
- [ ] Try ABV < 0.5% → Error
- [ ] Try ABV > 20% → Error
- [ ] Try batch size < 1L → Error
- [ ] Try batch size > 5000L → Error

**Expected:** All validations work

#### Inventory Module
- [ ] Try to remove more stock than available → Error "cannot be negative"
- [ ] Try negative stock values → Error
- [ ] Try invalid cost format → Error

**Expected:** Prevents data corruption

#### Batches Module
- [ ] Try to create batch without recipe → Error
- [ ] Try to save without gyle number → Error
- [ ] Verify gyle auto-generation works

**Expected:** Required fields enforced

#### Duty Calculator
- [ ] Try volume = 0 → Error "must be positive"
- [ ] Try ABV = 0 → Error "must be positive"
- [ ] Try very large numbers → Calculates correctly

**Expected:** Handles edge cases

#### Sales Module
- [ ] Try to create sale without customer → Error
- [ ] Try to create sale without batch → Error
- [ ] Try invalid quantity → Error
- [ ] Try to mark delivered sale as delivered again → Info message

**Expected:** Business logic enforced

#### Invoicing Module
- [ ] Try to create invoice with no sales selected → Error
- [ ] Try to record payment > outstanding → Error "exceeds balance"
- [ ] Try negative payment → Error

**Expected:** Financial integrity maintained

---

## 🔧 USER INTERFACE TESTING

### General UI Tests
- [ ] **Responsive Resizing:** Resize window - all modules adapt
- [ ] **Scrolling:** Long lists scroll properly
- [ ] **Tab Navigation:** Tab key moves between fields
- [ ] **Enter Key:** Pressing Enter submits forms
- [ ] **Double-Click:** Double-click opens details
- [ ] **Color Coding:** Consistent across modules
- [ ] **Buttons:** All buttons have clear labels and hover effects
- [ ] **Search Boxes:** Real-time filtering works
- [ ] **Dropdown Menus:** All combos populate correctly
- [ ] **Date Fields:** Accept valid date formats

**Expected:** Consistent, professional UI

### Navigation Tests
- [ ] Click each sidebar module button
- [ ] Verify module loads correctly
- [ ] Active button highlighted green
- [ ] Previous module content clears
- [ ] Status bar remains visible
- [ ] User info shows in sidebar
- [ ] Logout button accessible

**Expected:** Smooth navigation

### Performance Tests
- [ ] Load module with 100+ records
- [ ] Search with filters
- [ ] Sort by columns (if available)
- [ ] Rapid clicking doesn't crash
- [ ] Multiple dialogs don't stack

**Expected:** Responsive performance

---

## 💾 DATA PERSISTENCE TESTING

### Database Tests
- [ ] Add data in one module
- [ ] Close and restart application
- [ ] Data still present
- [ ] Navigate to different module
- [ ] Return to first module
- [ ] Data unchanged

**Expected:** All data persists

### Sync Status Tests
- [ ] Create new record
- [ ] Check sync_status = 'pending'
- [ ] Verify appears in database
- [ ] Multiple changes tracked

**Expected:** Ready for Google Sheets sync (Phase 3)

---

## 📊 REPORTING & SUMMARY TESTING

### Dashboard Accuracy
After all tests:
- [ ] **Total Batches** = Count of all batches
- [ ] **In Production** = batches NOT ready/packaged
- [ ] **Customers** = Active customers only
- [ ] **Sales (Month)** = Sales in current month
- [ ] **Low Stock Alerts** = Materials below reorder
- [ ] **Ready Batches** = Status = 'ready'
- [ ] **Upcoming Deliveries** = Next 7 days only

**Expected:** All stats accurate

---

## ✅ CRITICAL ACCEPTANCE TESTS

### Must-Pass Tests (Blockers)
- [ ] ✅ Login works (admin/admin)
- [ ] ✅ All 9 modules load without errors
- [ ] ✅ Duty calculator matches HMRC rates (Feb 2025)
- [ ] ✅ Can create batch, sale, invoice workflow
- [ ] ✅ Data persists after restart
- [ ] ✅ PDF labels generate correctly
- [ ] ✅ No critical bugs or crashes
- [ ] ✅ Logout returns to login screen

**Expected:** All critical tests pass

---

## 📝 TESTING NOTES

### Issues Found
```
Issue #1: [Describe any bugs found]
Severity: Low/Medium/High
Steps to reproduce:
Expected:
Actual:

Issue #2: ...
```

### Performance Notes
```
- Load time: [seconds]
- Memory usage: [MB]
- Responsiveness: [Good/Fair/Poor]
```

### Suggestions
```
- Feature improvement ideas
- UI/UX feedback
- Additional functionality requests
```

---

## ✅ SIGN-OFF

Testing completed by: ___________________
Date: ___________________
Overall Status: ⬜ Pass ⬜ Pass with issues ⬜ Fail

**Comments:**
```
[Overall testing summary and notes]
```

---

## 🎯 NEXT STEPS AFTER TESTING

Based on test results:

### If All Tests Pass:
1. **Phase 3:** Integration & Testing
   - Connect Google Sheets sync
   - End-to-end workflow testing
   - Multi-user testing
   - Performance optimization

2. **Phase 4:** Packaging & Deployment
   - Create .exe installer with PyInstaller
   - Write user documentation
   - Final testing on clean Windows install

### If Issues Found:
1. Report bugs to developer
2. Prioritize by severity
3. Retest after fixes
4. Document workarounds

---

**Last Updated:** November 2025
**Version:** Phase 2 Complete (9/9 Modules)
**Status:** Ready for Testing 🍺
