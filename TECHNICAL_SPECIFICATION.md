# BREWERY MANAGEMENT SYSTEM
## COMPLETE TECHNICAL SPECIFICATION DOCUMENT

**Project Name:** Brewery Management System  
**Version:** 1.0  
**Date:** November 5, 2025  
**Status:** Pre-Development - Ready to Build  
**Target Completion:** 1-2 months from start

---

## EXECUTIVE SUMMARY

### Purpose
Replace current Excel-based brewery operations with a comprehensive Windows desktop application that manages all aspects of commercial brewery operations including recipe formulation, inventory tracking, batch production with gyle tracking, customer relationship management, sales workflow, invoicing with payment tracking, HMRC-compliant UK alcohol duty calculations, and professional cask label printing.

### Business Context
- **Current System:** Excel spreadsheets tracking malt records, brewing/racking records, barrel records, and duty calculations
- **Pain Points:** Manual stock updates, time-consuming monthly duty calculations, forgotten entries, poor visibility into stock levels and container locations
- **Annual Production:** 8.79 hectolitres currently (expected significant growth with 800L batches)
- **Current SPR Rate:** £4.87 per hectolitre
- **Batch Size Range:** 160-900 litres (variable)
- **Users:** 3-4 initially (brewery, office, mobile delivery)

### Critical Success Factors
This system handles critical business operations where errors have serious consequences:
- **HMRC Compliance:** Incorrect duty calculations = legal/financial penalties
- **Inventory Accuracy:** Stock errors = production delays or over-selling
- **Customer Invoicing:** Billing errors = customer trust issues and cash flow problems
- **Traceability:** Complete audit trail required for regulatory compliance

**System must work flawlessly from day one.**

---

## TABLE OF CONTENTS

1. [System Architecture](#system-architecture)
2. [Core Modules Overview](#core-modules-overview)
3. [Database Structure](#database-structure)
4. [Module 1: Recipe Formulation](#module-1-recipe-formulation)
5. [Module 2: Inventory Management](#module-2-inventory-management)
6. [Module 3: Batch Management & Gyle Tracking](#module-3-batch-management--gyle-tracking)
7. [Module 4: Customer Relationship Management](#module-4-customer-relationship-management)
8. [Module 5: Sales Tools](#module-5-sales-tools)
9. [Module 6: Sales & Dispatch](#module-6-sales--dispatch)
10. [Module 7: Invoicing & Payment Tracking](#module-7-invoicing--payment-tracking)
11. [Module 8: UK Duty Calculator](#module-8-uk-duty-calculator)
12. [Module 9: Cask Label Printing](#module-9-cask-label-printing)
13. [User Roles & Permissions](#user-roles--permissions)
14. [Business Rules & Validation](#business-rules--validation)
15. [Workflows](#workflows)
16. [Reporting Requirements](#reporting-requirements)
17. [Integration Requirements](#integration-requirements)
18. [Technical Implementation Details](#technical-implementation-details)
19. [Development Phases](#development-phases)
20. [Testing Strategy](#testing-strategy)
21. [Deployment & Training](#deployment--training)

---

## SYSTEM ARCHITECTURE

### Technology Stack
- **Application Type:** Windows Desktop Application (.exe installer)
- **Primary Language:** Python 3.10+
- **GUI Framework:** tkinter (native Python GUI)
- **Cloud Backend:** Google Sheets API
- **Local Storage:** SQLite (offline cache)
- **PDF Generation:** ReportLab
- **Label Printing:** Python Imaging Library (PIL/Pillow)
- **Packaging:** PyInstaller (single .exe)

### Data Architecture
```
┌─────────────────────────────────────────────────┐
│           Desktop Application                    │
│  ┌──────────────────────────────────────────┐  │
│  │       tkinter GUI Layer                   │  │
│  └──────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────┐  │
│  │     Business Logic Layer                  │  │
│  │  - Validation Rules                       │  │
│  │  - Calculations (Duty, Pricing)           │  │
│  │  - Workflow Management                    │  │
│  └──────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────┐  │
│  │     Data Access Layer                     │  │
│  │  - Google Sheets API Client               │  │
│  │  - Local SQLite Cache                     │  │
│  │  - Sync Manager                           │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
                      │
                      ↓
        ┌─────────────────────────────┐
        │   Google Sheets (Cloud)      │
        │  - Master Data Source         │
        │  - Multi-user Access          │
        │  - Automatic Backup           │
        └─────────────────────────────────┘
```

### Offline Capability
- **Local Cache:** SQLite database mirrors Google Sheets
- **Sync Strategy:** 
  - Attempt sync every 5 minutes when online
  - Queue changes when offline
  - Auto-sync when connection restored
  - Manual sync button always available
- **Conflict Resolution:** Last write wins (with timestamp comparison)
- **Status Indicator:** Always visible sync status in GUI

---

## CORE MODULES OVERVIEW

### 1. Recipe Formulation
Create, edit, and scale beer recipes with complete ingredient lists and brewing instructions.

### 2. Inventory Management
Track all brewing materials and finished goods with automatic depletion and low stock alerts.

### 3. Batch Management & Gyle Tracking
Complete production workflow from brewing through conditioning to packaging with full traceability.

### 4. Customer Relationship Management (CRM)
Maintain customer database with preferences, history, and communication tracking.

### 5. Sales Tools
Calendar, call logging, task management, and sales pipeline tracking.

### 6. Sales & Dispatch
Record cask sales with two-stage workflow (reserved → delivered) and dispatch tracking.

### 7. Invoicing & Payment Tracking
Generate professional invoices, track payments, manage outstanding balances.

### 8. UK Duty Calculator
HMRC-compliant duty calculations with Small Producer Relief and Draught Relief.

### 9. Cask Label Printing
Professional cask labels with brewery logo, beer details, and duty declarations.

---

## DATABASE STRUCTURE

### Google Sheets Workbook Structure
**File Name:** `BreweryManager_Data.xlsx`

#### Sheet 1: Recipes
| Column | Type | Description |
|--------|------|-------------|
| recipe_id | TEXT (UUID) | Unique identifier |
| recipe_name | TEXT | Name of beer/recipe |
| style | TEXT | Beer style (IPA, Stout, etc.) |
| version | INTEGER | Version number (1, 2, 3...) |
| target_abv | DECIMAL | Target alcohol percentage |
| target_batch_size_litres | DECIMAL | Standard batch size |
| created_date | DATE | When recipe created |
| created_by | TEXT | Username |
| last_modified | TIMESTAMP | Last edit timestamp |
| is_active | BOOLEAN | Active/archived status |
| brewing_notes | TEXT | General brewing instructions |

#### Sheet 2: Recipe_Ingredients
| Column | Type | Description |
|--------|------|-------------|
| ingredient_id | TEXT (UUID) | Unique identifier |
| recipe_id | TEXT | Link to Recipes |
| ingredient_type | TEXT | grain/hops/yeast/other |
| ingredient_name | TEXT | Specific ingredient name |
| quantity | DECIMAL | Amount needed |
| unit | TEXT | kg/g/litres |
| timing | TEXT | When added (boil_start, dry_hop_day_3, etc.) |
| notes | TEXT | Special instructions |

#### Sheet 3: Inventory_Materials
| Column | Type | Description |
|--------|------|-------------|
| material_id | TEXT (UUID) | Unique identifier |
| material_type | TEXT | grain/hops/yeast/sundries |
| material_name | TEXT | Specific name/variety |
| current_stock | DECIMAL | Current quantity |
| unit | TEXT | kg/g/litres/units |
| reorder_level | DECIMAL | Low stock alert threshold |
| last_updated | TIMESTAMP | Last stock change |
| supplier | TEXT | Primary supplier name |
| cost_per_unit | DECIMAL | Purchase cost |

#### Sheet 4: Inventory_Transactions
| Column | Type | Description |
|--------|------|-------------|
| transaction_id | TEXT (UUID) | Unique identifier |
| transaction_date | DATE | When occurred |
| transaction_type | TEXT | purchase/usage/adjustment |
| material_id | TEXT | Link to Inventory_Materials |
| quantity_change | DECIMAL | +/- amount |
| new_balance | DECIMAL | Stock after transaction |
| reference | TEXT | Batch number or supplier invoice |
| username | TEXT | Who recorded it |
| notes | TEXT | Additional details |

#### Sheet 5: Casks_Empty
| Column | Type | Description |
|--------|------|-------------|
| cask_id | TEXT (UUID) | Unique identifier |
| cask_type | TEXT | pin/firkin/kilderkin/30L/50L/party_tin |
| cask_size_litres | DECIMAL | 20.5/40.9/81.8/30/50/variable |
| date_in | DATE | When returned to brewery |
| condition | TEXT | good/needs_cleaning/damaged |
| location | TEXT | Where stored |
| notes | TEXT | Any issues |

#### Sheet 6: Batches
| Column | Type | Description |
|--------|------|-------------|
| batch_id | TEXT (UUID) | Unique identifier |
| gyle_number | TEXT | Unique sequential gyle (auto-generated) |
| recipe_id | TEXT | Link to Recipes |
| brew_date | DATE | When brewing started |
| brewer_name | TEXT | Who brewed it |
| actual_batch_size | DECIMAL | Litres produced |
| measured_abv | DECIMAL | Final measured ABV |
| pure_alcohol_litres | DECIMAL | Auto-calculated (size × ABV/100) |
| status | TEXT | brewing/fermenting/conditioning/ready/packaged |
| fermenting_start | DATE | When fermentation started |
| conditioning_start | DATE | When moved to conditioning |
| ready_date | DATE | When ready for packaging |
| packaged_date | DATE | When packaged |
| spr_rate_applied | DECIMAL | SPR rate at production (£/hl) |
| duty_rate_applied | DECIMAL | Final duty rate used (£/L pure alcohol) |
| is_draught | BOOLEAN | Draught or non-draught |
| brewing_notes | TEXT | Batch-specific notes |
| created_by | TEXT | Username |

#### Sheet 7: Fermentation_Logs
| Column | Type | Description |
|--------|------|-------------|
| log_id | TEXT (UUID) | Unique identifier |
| batch_id | TEXT | Link to Batches |
| log_date | DATE | Date of reading |
| gravity_reading | DECIMAL | Specific gravity |
| temperature_c | DECIMAL | Temperature in Celsius |
| ph | DECIMAL | pH reading (optional) |
| notes | TEXT | Observations |
| recorded_by | TEXT | Username |

#### Sheet 8: Casks_Full
| Column | Type | Description |
|--------|------|-------------|
| full_cask_id | TEXT (UUID) | Unique identifier |
| batch_id | TEXT | Link to Batches |
| gyle_number | TEXT | For quick reference |
| beer_name | TEXT | For quick reference |
| cask_type | TEXT | pin/firkin/kilderkin/30L/50L/party_tin |
| cask_size_litres | DECIMAL | Container size |
| fill_date | DATE | When filled |
| quantity | INTEGER | Number of casks |
| location | TEXT | Where stored |
| status | TEXT | in_stock/reserved/sold |
| reserved_for_customer | TEXT | Customer name (if reserved) |
| reserved_date | DATE | When reserved |
| notes | TEXT | Any special notes |

#### Sheet 9: Bottles_Stock
| Column | Type | Description |
|--------|------|-------------|
| bottle_stock_id | TEXT (UUID) | Unique identifier |
| batch_id | TEXT | Link to Batches |
| gyle_number | TEXT | For quick reference |
| beer_name | TEXT | For quick reference |
| bottle_size_ml | INTEGER | 330/500/750 |
| quantity_bottled | INTEGER | Number of bottles |
| quantity_in_stock | INTEGER | Current stock |
| bottling_date | DATE | When bottled |
| best_before | DATE | Shelf life date |

#### Sheet 10: Customers
| Column | Type | Description |
|--------|------|-------------|
| customer_id | TEXT (UUID) | Unique identifier |
| customer_name | TEXT | Business/person name |
| contact_person | TEXT | Primary contact |
| phone | TEXT | Phone number |
| email | TEXT | Email address |
| delivery_address | TEXT | Full delivery address |
| billing_address | TEXT | Billing address (if different) |
| customer_type | TEXT | pub/restaurant/retail/private |
| payment_terms | TEXT | net_7/net_14/net_30/cash |
| credit_limit | DECIMAL | Maximum outstanding balance |
| preferred_delivery_day | TEXT | Monday/Tuesday/etc |
| preferred_delivery_time | TEXT | Morning/afternoon |
| likes | TEXT | Preferred beers/styles |
| dislikes | TEXT | What to avoid |
| notes | TEXT | General customer notes |
| is_active | BOOLEAN | Active/inactive status |
| created_date | DATE | When added |

#### Sheet 11: Sales_Calendar
| Column | Type | Description |
|--------|------|-------------|
| event_id | TEXT (UUID) | Unique identifier |
| event_date | DATE | Date of event |
| event_time | TEXT | Time (optional) |
| event_type | TEXT | call/delivery/meeting/follow_up |
| customer_id | TEXT | Link to Customers |
| description | TEXT | What's planned |
| status | TEXT | scheduled/completed/cancelled |
| created_by | TEXT | Username |
| completed_by | TEXT | Who completed it |
| completed_date | TIMESTAMP | When marked complete |

#### Sheet 12: Call_Log
| Column | Type | Description |
|--------|------|-------------|
| call_id | TEXT (UUID) | Unique identifier |
| call_date | DATE | Date of call |
| call_time | TEXT | Time of call |
| customer_id | TEXT | Link to Customers |
| call_type | TEXT | inbound/outbound |
| duration_minutes | INTEGER | Length of call |
| outcome | TEXT | placed_order/quote_sent/no_answer/etc |
| notes | TEXT | Call summary |
| follow_up_required | BOOLEAN | Need to follow up? |
| follow_up_date | DATE | When to follow up |
| recorded_by | TEXT | Username |

#### Sheet 13: Tasks
| Column | Type | Description |
|--------|------|-------------|
| task_id | TEXT (UUID) | Unique identifier |
| task_title | TEXT | Brief description |
| task_description | TEXT | Detailed description |
| task_type | TEXT | follow_up/quote/payment_chase/other |
| related_customer_id | TEXT | Link to customer (if applicable) |
| priority | TEXT | high/medium/low |
| due_date | DATE | When due |
| status | TEXT | pending/in_progress/completed/cancelled |
| assigned_to | TEXT | Username |
| created_by | TEXT | Username |
| created_date | DATE | When created |
| completed_date | DATE | When marked complete |

#### Sheet 14: Sales_Pipeline
| Column | Type | Description |
|--------|------|-------------|
| opportunity_id | TEXT (UUID) | Unique identifier |
| customer_id | TEXT | Link to Customers |
| opportunity_name | TEXT | Brief description |
| estimated_value | DECIMAL | Potential revenue |
| stage | TEXT | prospecting/quoted/negotiation/won/lost |
| probability_percent | INTEGER | Likelihood (0-100) |
| expected_close_date | DATE | When expecting decision |
| notes | TEXT | Details |
| created_by | TEXT | Username |
| created_date | DATE | When created |
| last_updated | TIMESTAMP | Last modification |

#### Sheet 15: Sales
| Column | Type | Description |
|--------|------|-------------|
| sale_id | TEXT (UUID) | Unique identifier |
| sale_date | DATE | When sale recorded |
| customer_id | TEXT | Link to Customers |
| batch_id | TEXT | Link to Batches |
| gyle_number | TEXT | For reference |
| beer_name | TEXT | For reference |
| container_type | TEXT | cask_type or "bottles" |
| container_size | DECIMAL | Litres or ml |
| quantity | INTEGER | Number of containers |
| total_litres | DECIMAL | Auto-calculated |
| unit_price | DECIMAL | Price per container |
| line_total | DECIMAL | Auto-calculated |
| status | TEXT | reserved/delivered |
| reserved_date | DATE | When reserved |
| delivery_date | DATE | When delivered |
| invoice_id | TEXT | Link to invoice (when created) |
| recorded_by | TEXT | Username |
| notes | TEXT | Any special notes |

#### Sheet 16: Invoices
| Column | Type | Description |
|--------|------|-------------|
| invoice_id | TEXT (UUID) | Unique identifier |
| invoice_number | TEXT | Sequential (INV-2025-0001) |
| invoice_date | DATE | Date issued |
| customer_id | TEXT | Link to Customers |
| subtotal | DECIMAL | Before VAT |
| vat_rate | DECIMAL | Usually 0.20 (20%) |
| vat_amount | DECIMAL | Auto-calculated |
| total | DECIMAL | Final amount due |
| payment_status | TEXT | unpaid/partially_paid/paid |
| amount_paid | DECIMAL | Payments received |
| amount_outstanding | DECIMAL | Auto-calculated |
| due_date | DATE | Payment due by |
| created_by | TEXT | Username |
| created_date | DATE | When created |
| notes | TEXT | Any special terms |

#### Sheet 17: Invoice_Lines
| Column | Type | Description |
|--------|------|-------------|
| line_id | TEXT (UUID) | Unique identifier |
| invoice_id | TEXT | Link to Invoices |
| sale_id | TEXT | Link to Sales (optional) |
| description | TEXT | What's being billed |
| quantity | DECIMAL | How many |
| unit_price | DECIMAL | Price each |
| line_total | DECIMAL | Auto-calculated |
| gyle_number | TEXT | For reference |

#### Sheet 18: Payments
| Column | Type | Description |
|--------|------|-------------|
| payment_id | TEXT (UUID) | Unique identifier |
| invoice_id | TEXT | Link to Invoices |
| payment_date | DATE | When received |
| payment_amount | DECIMAL | Amount received |
| payment_method | TEXT | cash/cheque/bacs/card |
| payment_reference | TEXT | Cheque number, BACS ref, etc |
| recorded_by | TEXT | Username |
| recorded_date | TIMESTAMP | When recorded |
| notes | TEXT | Any additional details |

#### Sheet 19: Duty_Returns
| Column | Type | Description |
|--------|------|-------------|
| return_id | TEXT (UUID) | Unique identifier |
| return_period_start | DATE | Period covered (start) |
| return_period_end | DATE | Period covered (end) |
| total_pure_alcohol_litres | DECIMAL | Sum for period |
| total_duty_payable | DECIMAL | Total duty owed |
| payment_due_date | DATE | HMRC deadline |
| payment_status | TEXT | unpaid/paid |
| payment_date | DATE | When paid |
| payment_reference | TEXT | HMRC reference |
| prepared_by | TEXT | Username |
| prepared_date | DATE | When prepared |

#### Sheet 20: Duty_Return_Lines
| Column | Type | Description |
|--------|------|-------------|
| line_id | TEXT (UUID) | Unique identifier |
| return_id | TEXT | Link to Duty_Returns |
| batch_id | TEXT | Link to Batches |
| gyle_number | TEXT | For reference |
| beer_name | TEXT | For reference |
| packaged_date | DATE | When passed duty point |
| pure_alcohol_litres | DECIMAL | From batch |
| duty_rate_applied | DECIMAL | Rate used |
| duty_amount | DECIMAL | Calculated duty |

#### Sheet 21: Pricing
| Column | Type | Description |
|--------|------|-------------|
| pricing_id | TEXT (UUID) | Unique identifier |
| container_type | TEXT | pin/firkin/30L/50L/party_tin/bottle |
| container_size | DECIMAL | Litres or ml |
| default_price | DECIMAL | Standard price |
| last_updated | TIMESTAMP | When price changed |

#### Sheet 22: Customer_Pricing_Overrides
| Column | Type | Description |
|--------|------|-------------|
| override_id | TEXT (UUID) | Unique identifier |
| customer_id | TEXT | Link to Customers |
| container_type | TEXT | What container |
| container_size | DECIMAL | Size |
| override_price | DECIMAL | Special price for this customer |
| effective_from | DATE | When it starts |
| effective_until | DATE | When it expires (null = indefinite) |

#### Sheet 23: Users
| Column | Type | Description |
|--------|------|-------------|
| user_id | TEXT (UUID) | Unique identifier |
| username | TEXT | Login username |
| full_name | TEXT | Display name |
| role | TEXT | admin/brewer/office/sales |
| is_active | BOOLEAN | Can log in? |
| created_date | DATE | When added |

#### Sheet 24: System_Settings
| Column | Type | Description |
|--------|------|-------------|
| setting_key | TEXT | Unique setting name |
| setting_value | TEXT | Value |
| setting_type | TEXT | text/number/boolean/date |
| description | TEXT | What it controls |
| last_updated | TIMESTAMP | When changed |

**Key System Settings:**
- `annual_production_hectolitres` - For SPR calculation
- `spr_discount_per_litre` - Current SPR rate
- `is_small_producer` - Eligible for SPR? (boolean)
- `production_year_start` - Feb 1
- `brewery_name` - For invoices/labels
- `brewery_address` - For invoices/labels
- `brewery_logo_path` - For labels
- `vat_number` - For invoices
- `next_gyle_number` - Auto-increment counter
- `next_invoice_number` - Auto-increment counter

#### Sheet 25: Audit_Log
| Column | Type | Description |
|--------|------|-------------|
| audit_id | TEXT (UUID) | Unique identifier |
| timestamp | TIMESTAMP | When action occurred |
| username | TEXT | Who did it |
| action_type | TEXT | create/update/delete |
| table_name | TEXT | Which sheet |
| record_id | TEXT | Which record |
| changes | TEXT | JSON of before/after values |
| ip_address | TEXT | Where from (if applicable) |

---

## MODULE 1: RECIPE FORMULATION

### Overview
Create, manage, and version beer recipes with complete ingredient specifications and brewing instructions.

### Features
1. **Recipe Management**
   - Create new recipes with unique names
   - Edit existing recipes (creates new version)
   - Archive old/unused recipes
   - Search and filter recipes by style, ABV, etc.

2. **Recipe Details**
   - Recipe name (e.g., "Tonk IPA")
   - Beer style (dropdown: IPA, Pale Ale, Stout, Porter, Bitter, etc.)
   - Target ABV (decimal, validated 0.5% - 15%)
   - Standard batch size in litres (default but scalable)
   - Version number (auto-increment)

3. **Grain Bill**
   - Add multiple grain types
   - Quantity in kg per grain type
   - Auto-calculate total grain weight
   - Percentages of total grist shown

4. **Hops Schedule**
   - Add multiple hop additions
   - Hop variety (dropdown: Cascade, Chinook, etc.)
   - Quantity in grams
   - Timing (boil start, 15 min, 5 min, flameout, dry hop day X)
   - Auto-calculate total hops

5. **Yeast**
   - Yeast strain (dropdown or free text)
   - Quantity needed (g or ml)   - Pitching temperature
   - Target fermentation temperature

6. **Other Ingredients**
   - Sundries (finings, priming sugar, etc.)
   - Quantity and timing

7. **Brewing Instructions**
   - Free-text field for detailed brewing notes
   - Mash schedule
   - Boil duration
   - Fermentation notes
   - Conditioning requirements

8. **Recipe Scaling**
   - Scale recipe to any batch size
   - All quantities automatically calculated
   - Maintains ingredient ratios

### UI Layout
```
┌────────────────────────────────────────────────┐
│ Recipe: Tonk IPA v3              [Edit] [Save] │
├────────────────────────────────────────────────┤
│ Style: [IPA ▼]    ABV: [5.8%]   Batch: [800L]  │
│                                                 │
│ GRAIN BILL                             [+ Add]  │
│ ┌──────────────────────────────────────────┐   │
│ │ Maris Otter Pale    80 kg    (85%)      │   │
│ │ Crystal 150          8 kg     (8%)      │   │
│ │ Wheat Malt           7 kg     (7%)      │   │
│ │ ─────────────────────────────────────── │   │
│ │ TOTAL:              95 kg   (100%)      │   │
│ └──────────────────────────────────────────┘   │
│                                                 │
│ HOPS SCHEDULE                          [+ Add]  │
│ ┌──────────────────────────────────────────┐   │
│ │ Cascade        200g    Boil start       │   │
│ │ Chinook        150g    15 minutes       │   │
│ │ Citra          250g    Dry hop day 3    │   │
│ │ ─────────────────────────────────────── │   │
│ │ TOTAL:         600g                     │   │
│ └──────────────────────────────────────────┘   │
│                                                 │
│ YEAST                                           │
│ Strain: [US-05]  Quantity: [50g]               │
│ Pitch temp: [20°C]  Ferm temp: [18-20°C]       │
│                                                 │
│ BREWING NOTES                                   │
│ ┌──────────────────────────────────────────┐   │
│ │ Mash at 65°C for 60 minutes              │   │
│ │ Boil 60 minutes                          │   │
│ │ Add dry hops on day 3 of fermentation    │   │
│ │ Condition for 7 days before packaging    │   │
│ └──────────────────────────────────────────┘   │
└────────────────────────────────────────────────┘
```

### Validation Rules
- Recipe name must be unique (except when versioning)
- ABV must be 0.5% - 15%
- Batch size must be 50 - 2000 litres
- At least one grain required
- At least one hop required
- Yeast required
- All quantities must be positive numbers

### Version Control
- Any edit to existing recipe creates new version
- Previous versions preserved (read-only)
- Version history viewable
- Can "revert to version X" (creates new version as copy)

---

## MODULE 2: INVENTORY MANAGEMENT

### Overview
Track all brewing materials and finished goods with automatic depletion, low stock alerts, and transaction history.

### Two Main Categories

#### A. BREWING MATERIALS
Track raw ingredients: grain, hops, yeast, sundries, empty casks.

**Features:**
1. **Material Database**
   - Material type (grain/hops/yeast/sundries/casks)
   - Specific name (e.g., "Maris Otter Pale Malt")
   - Current stock level
   - Unit (kg, g, litres, units)
   - Reorder level (alert threshold)
   - Supplier name
   - Cost per unit

2. **Incoming Stock**
   - Record purchases/deliveries
   - Date received
   - Supplier
   - Quantity
   - Cost (optional)
   - Updates stock level automatically

3. **Stock Adjustments**
   - Manual corrections
   - Reason required (spillage, spoilage, stocktake adjustment)
   - Audit trail

4. **Automatic Depletion**
   - When batch created: ingredients auto-deducted based on recipe
   - Transaction logged with batch reference
   - Can't create batch if insufficient ingredients (warning shown)

5. **Low Stock Alerts**
   - Visual indicator when stock below reorder level
   - Alert list on dashboard
   - Configurable per material

6. **Empty Casks**
   - Track empty cask returns
   - Cask type (pin/firkin/kilderkin/30L/50L/party_tin)
   - Date returned
   - Condition (good/needs cleaning/damaged)
   - Location in brewery
   - Automatically depleted when filling

#### B. FINISHED GOODS
Track packaged beer ready for sale.

**Categories:**
1. **Casks Full** (primary focus)
2. **Bottles Stock**

**Casks Full - Features:**
1. **Record Filled Casks**
   - Link to batch (gyle number)
   - Beer name (from batch)
   - Cask type and size
   - Number of casks filled
   - Fill date
   - Location in brewery

2. **Stock Status**
   - In Stock (available)
   - Reserved (for specific customer)
   - Sold (delivered out)

3. **Reservations**
   - Reserve casks for customer before delivery
   - Shows customer name and date reserved
   - Prevents accidental double-booking

4. **Automatic Depletion on Sale**
   - When sale marked "delivered" → casks removed from stock
   - Can't over-sell (validation checks stock)

**Bottles Stock - Features:**
- Similar to casks but tracked by bottle count
- Batch link, beer name, bottle size, quantity
- Best before date
- Current stock count

### UI Layout - Inventory Screen
```
┌────────────────────────────────────────────────┐
│ INVENTORY MANAGEMENT                    [Sync] │
├────────────────────────────────────────────────┤
│ [Brewing Materials] [Finished Goods]           │
├────────────────────────────────────────────────┤
│                                                 │
│ BREWING MATERIALS              [+ Add Stock]    │
│                                                 │
│ Filter: [All ▼] Search: [____________]          │
│                                                 │
│ 🔴 LOW STOCK ALERTS (3)                        │
│ ┌──────────────────────────────────────────┐   │
│ │ Cascade Hops       1.2 kg  (⚠️ < 2 kg)   │   │
│ │ Crystal 150 Malt   15 kg   (⚠️ < 20 kg)  │   │
│ │ US-05 Yeast        3 packs (⚠️ < 5)      │   │
│ └──────────────────────────────────────────┘   │
│                                                 │
│ GRAIN                                           │
│ ┌────────────────────────────────────────────┐ │
│ │ Item             Stock    Unit   Reorder   │ │
│ ├────────────────────────────────────────────┤ │
│ │ Maris Otter     185 kg    kg     50        │ │
│ │ Crystal 150      15 kg    kg     20 🔴    │ │
│ │ Wheat Malt       45 kg    kg     20        │ │
│ └────────────────────────────────────────────┘ │
│                                                 │
│ HOPS                                            │
│ ┌────────────────────────────────────────────┐ │
│ │ Cascade          1.2 kg   kg      2  🔴   │ │
│ │ Chinook          3.5 kg   kg      2        │ │
│ │ Citra            2.8 kg   kg      2        │ │
│ └────────────────────────────────────────────┘ │
│                                                 │
│ EMPTY CASKS                                     │
│ ┌────────────────────────────────────────────┐ │
│ │ Firkins (40.9L)      25 units              │ │
│ │ 30L Kegs             12 units              │ │
│ │ 50L Kegs              8 units              │ │
│ └────────────────────────────────────────────┘ │
└────────────────────────────────────────────────┘
```

### Validation Rules
- Stock levels cannot go negative
- Quantities must be positive
- Reorder levels must be ≤ current stock (warning only)
- Transaction dates cannot be future dates
- Each material must have unique name within type

### Reports Available
1. **Current Stock Report** - Snapshot of all stock levels
2. **Low Stock Report** - Items below reorder level
3. **Stock Movement Report** - All transactions in date range
4. **Stock Valuation Report** - Total inventory value (if costs tracked)

---

## MODULE 3: BATCH MANAGEMENT & GYLE TRACKING

### Overview
Complete production workflow from brewing through fermentation, conditioning, and packaging with full traceability via unique gyle numbers.

### Key Concept: GYLE NUMBER
- **Assigned at START of batch** (when brewing begins)
- **Format:** Auto-generated sequential (GYLE-2025-001, GYLE-2025-002, etc.)
- **Purpose:** Unique identifier for complete traceability from ingredients → batch → finished product → customer
- **Never changes:** Same gyle number throughout batch lifecycle

### Batch Lifecycle Stages

#### 1. CREATE BATCH (Brewing Starts)
**Actions:**
- Select recipe
- Enter brew date
- Enter brewer name
- Set actual batch size (may differ from recipe standard)
- System auto-generates next gyle number
- System checks ingredient availability
- If ingredients sufficient: Auto-deduct from inventory
- If insufficient: Show warning, can't proceed

**Recorded:**
- Batch ID (UUID)
- Gyle number (sequential)
- Recipe used (version locked)
- Brew date
- Brewer name
- Actual batch size (litres)
- Status: "Brewing"

#### 2. FERMENTING
**Actions:**
- Mark batch as "Fermenting"
- Enter fermentation start date
- Log gravity readings, temperature, notes

**Fermentation Log:**
- Multiple entries per batch
- Date, gravity, temperature, pH, notes
- Recorded by whom

**Status:** "Fermenting"

#### 3. CONDITIONING
**Actions:**
- Mark batch as "Conditioning"
- Enter conditioning start date
- Continue logging notes if needed

**Status:** "Conditioning"

#### 4. READY FOR PACKAGING
**Actions:**
- Mark batch as "Ready"
- Enter measured final ABV (required)
- System auto-calculates pure alcohol litres
- System looks up current SPR rate
- System calculates duty rate to apply

**Critical Duty Calculations:**
```python
pure_alcohol_litres = batch_size_litres * (measured_abv / 100)

# Get current SPR rate from system settings
spr_discount_per_litre = get_setting('spr_discount_per_litre')

# Determine base rate
if is_draught and abv < 8.5:
    base_rate = 18.76  # Draught beer 3.5-8.4% (Feb 2025)
elif abv >= 3.5 and abv <= 8.4:
    base_rate = 21.78  # Non-draught beer 3.5-8.4%
# ... other rates

# Apply SPR
duty_rate_applied = base_rate - spr_discount_per_litre

# Store for future duty return
batch.spr_rate_applied = spr_discount_per_litre
batch.duty_rate_applied = duty_rate_applied
```

**Status:** "Ready"

#### 5. PACKAGE BATCH
**Actions:**
- Select batch (must be "Ready" status)
- Choose packaging:
  - **Casks:** Select cask type(s), enter quantity for each
  - **Bottles:** Enter bottle size, quantity
  - Can do both (mixed packaging)
- Enter packaging date
- System creates finished goods records:
  - Adds to "Casks Full" with gyle number
  - Adds to "Bottles Stock" with gyle number
- System deducts empty casks from inventory
- System calculates estimated duty for batch

**Recorded:**
- Packaging date (= duty point date)
- What was packaged (casks/bottles, sizes, quantities)
- Links created to finished goods

**Status:** "Packaged"

### Batch Details View
Shows complete history and current status of any batch.

```
┌────────────────────────────────────────────────┐
│ BATCH DETAILS - GYLE-2025-042                  │
├────────────────────────────────────────────────┤
│ Recipe: Tonk IPA v3                            │
│ Status: [Conditioning]                         │
│                                                 │
│ TIMELINE                                        │
│ ├─ Brewing:      Oct 15, 2025  (Darren)       │
│ ├─ Fermenting:   Oct 16, 2025                 │
│ └─ Conditioning: Oct 23, 2025                 │
│                                                 │
│ MEASUREMENTS                                    │
│ Batch Size:     800 litres                     │
│ Final ABV:      [Enter when ready]             │
│ Pure Alcohol:   [Auto-calculated]              │
│                                                 │
│ FERMENTATION LOG                       [+ Add]  │
│ ┌──────────────────────────────────────────┐   │
│ │ Date       Gravity  Temp   Notes         │   │
│ ├──────────────────────────────────────────┤   │
│ │ Oct 16    1.058     20°C   Pitched yeast │   │
│ │ Oct 18    1.042     19°C   Active ferm   │   │
│ │ Oct 20    1.018     18°C   Slowing down  │   │
│ │ Oct 23    1.012     18°C   Ready to move │   │
│ └──────────────────────────────────────────┘   │
│                                                 │
│ NOTES                                           │
│ ┌──────────────────────────────────────────┐   │
│ │ Good fermentation, clean beer            │   │
│ │ Moved to conditioning tank on Day 7      │   │
│ └──────────────────────────────────────────┘   │
│                                                 │
│ [Mark as Ready] [Add Log Entry] [View Recipe]  │
└────────────────────────────────────────────────┘
```

### Validation Rules
- Gyle numbers must be unique and sequential
- Cannot skip gyle numbers
- Measured ABV required before packaging
- Cannot package if status not "Ready"
- Batch size must be > 0
- Brew date cannot be future date
- Fermentation start must be ≥ brew date
- Conditioning start must be ≥ fermentation start
- Packaging date must be ≥ ready date

### Traceability Chain
```
Ingredients Used (Recipe v3, 95kg Maris Otter, etc.)
    ↓
Batch Created (GYLE-2025-042, Tonk IPA)
    ↓
Fermentation Logs (gravity readings, notes)
    ↓
Packaged (20 firkins, 10 × 30L kegs)
    ↓
Finished Goods (Casks Full with GYLE-2025-042)
    ↓
Sales (Customer X bought 5 firkins of GYLE-2025-042)
    ↓
Invoice (INV-2025-0123 includes GYLE-2025-042)
    ↓
Duty Return (GYLE-2025-042 duty calculated and paid)
```

**Complete audit trail from grain to glass.**

---

## MODULE 4: CUSTOMER RELATIONSHIP MANAGEMENT (CRM)

### Overview
Centralized customer database with contact details, preferences, sales history, and relationship management.

### Customer Database Features

#### 1. Customer Details
**Basic Information:**
- Customer name (business or person)
- Contact person (primary contact)
- Phone number
- Email address
- Customer type (pub/restaurant/retail/private)

**Addresses:**
- Delivery address (full address including postcode)
- Billing address (if different from delivery)

**Business Terms:**
- Payment terms (net 7/net 14/net 30/cash on delivery)
- Credit limit (maximum outstanding balance)
- Active/Inactive status

#### 2. Preferences & Notes
**Likes:**
- Preferred beers/styles
- Successful previous orders
- What they ask for regularly

**Dislikes:**
- Beers/styles to avoid
- Any issues or problems
- What didn't work

**Delivery Preferences:**
- Preferred day (Monday, Tuesday, etc.)
- Preferred time (morning/afternoon/specific time)

**General Notes:**
- Free-text field for any other information
- Access requirements
- Special instructions
- Relationship notes

#### 3. Sales History
**View for Each Customer:**
- All past orders (chronological)
- Total revenue to date
- Average order value
- Last order date
- Order frequency

**Drill-down to:**
- Specific order details
- What they bought (which beers, gyle numbers)
- Invoices generated
- Payment history

#### 4. Outstanding Invoices
**Quick View:**
- Unpaid invoices
- Partially paid invoices
- Total outstanding balance
- Aged debt (0-30, 31-60, 61-90, 90+ days)

**Warning Indicators:**
- Credit limit exceeded (red flag)
- Overdue payments (yellow/red based on age)

### UI Layout - Customer Profile
```
┌────────────────────────────────────────────────┐
│ CUSTOMER: The Dog & Duck Inn          [Edit]   │
├────────────────────────────────────────────────┤
│ [Details] [Sales History] [Invoices] [Activity]│
├────────────────────────────────────────────────┤
│                                                 │
│ CONTACT INFORMATION                             │
│ Contact: John Smith                             │
│ Phone: 01234 567890                            │
│ Email: john@dogandduck.co.uk                   │
│                                                 │
│ DELIVERY ADDRESS                                │
│ The Dog & Duck Inn                             │
│ 123 High Street                                │
│ Stoke-on-Trent                                 │
│ ST1 1AA                                        │
│                                                 │
│ BUSINESS TERMS                                  │
│ Type: Pub                                      │
│ Payment Terms: Net 14 days                     │
│ Credit Limit: £2,000                           │
│ Outstanding: £450 ⚠️                           │
│                                                 │
│ PREFERENCES                                     │
│ ┌──────────────────────────────────────────┐   │
│ │ LIKES:                                    │   │
│ │ • Tonk IPA (always orders 3-4 firkins)   │   │
│ │ • Session Ale (popular with regulars)    │   │
│ │                                           │   │
│ │ DISLIKES:                                 │   │
│ │ • Strong stouts (don't sell)             │   │
│ │                                           │   │
│ │ DELIVERY:                                 │   │
│ │ • Preferred day: Thursday                │   │
│ │ • Preferred time: Morning (9-11am)       │   │
│ │ • Access: Rear entrance only             │   │
│ └──────────────────────────────────────────┘   │
│                                                 │
│ NOTES                                           │
│ Long-standing customer (5+ years)              │
│ Always pays on time                            │
│                                                 │
│ RECENT ACTIVITY                                 │
│ Oct 28: Called - placed order for 4 firkins    │
│ Oct 15: Delivered - INV-2025-0156             │
│ Oct 10: Payment received - £380                │
└────────────────────────────────────────────────┘
```

### Customer List View
```
┌────────────────────────────────────────────────┐
│ CUSTOMERS                         [+ Add New]   │
├────────────────────────────────────────────────┤
│ Filter: [All ▼] Type: [All ▼]                  │
│ Search: [____________]                          │
│ Sort by: [Name ▼]                              │
│                                                 │
│ ⚠️ REQUIRES ATTENTION (2)                      │
│ ┌──────────────────────────────────────────┐   │
│ │ The Red Lion      £1,850 outstanding 🔴  │   │
│ │ Crown Hotel       Overdue 45 days 🟡     │   │
│ └──────────────────────────────────────────┘   │
│                                                 │
│ ALL CUSTOMERS (alphabetical)                    │
│ ┌──────────────────────────────────────────┐   │
│ │ Customer Name         Type    Outstanding│   │
│ ├──────────────────────────────────────────┤   │
│ │ Builders Arms         Pub     £0         │   │
│ │ Crown Hotel           Pub     £675 🟡    │   │
│ │ Dog & Duck Inn        Pub     £450       │   │
│ │ Railway Tavern        Pub     £220       │   │
│ │ Red Lion              Pub     £1,850 🔴  │   │
│ │ Smiths Off-License    Retail  £0         │   │
│ └──────────────────────────────────────────┘   │
└────────────────────────────────────────────────┘
```

### Validation Rules
- Customer name must be unique
- Phone or email required (at least one)
- Payment terms must be valid option
- Credit limit must be ≥ 0
- Active status can be toggled (doesn't delete customer)

### Reports Available
1. **Customer List** - All customers with summary info
2. **Aged Debt Report** - Outstanding balances by age
3. **Customer Sales Analysis** - Sales by customer, revenue, frequency
4. **Inactive Customers** - Haven't ordered in X months

---

## MODULE 5: SALES TOOLS

### Overview
Tools to manage sales activities including calendar/diary, call logging, task management, and sales pipeline tracking.

### Sub-Modules

#### A. CALENDAR / DIARY

**Purpose:** Schedule and track sales activities.

**Features:**
1. **Event Types:**
   - Customer calls (scheduled)
   - Deliveries
   - Meetings
   - Follow-ups
   - General reminders

2. **Event Details:**
   - Date and time
   - Event type
   - Related customer (optional)
   - Description
   - Status (scheduled/completed/cancelled)

3. **Calendar Views:**
   - Day view
   - Week view
   - Month view
   - Agenda list view

4. **Reminders:**
   - Pop-up notifications
   - Dashboard alerts for today's events

**UI:** Standard calendar interface with color-coded event types.

#### B. CALL LOG

**Purpose:** Record all customer communications.

**Features:**
1. **Call Entry:**
   - Date and time of call
   - Customer (dropdown)
   - Call type (inbound/outbound)
   - Duration (minutes)
   - Outcome (placed order, quote sent, no answer, voicemail, etc.)
   - Notes (summary of conversation)
   - Follow-up required? (yes/no)
   - Follow-up date (if yes)

2. **Call History:**
   - View all calls chronologically
   - Filter by customer
   - Filter by date range
   - Filter by outcome

3. **Quick Actions:**
   - Click customer name → opens customer profile
   - Create task from call → auto-populates with customer and notes
   - Create order from call → jumps to sales entry

**UI:**
```
┌────────────────────────────────────────────────┐
│ CALL LOG                         [+ Log Call]   │
├────────────────────────────────────────────────┤
│ Filter: Customer [All ▼] Date [Last 30 days ▼] │
│                                                 │
│ TODAY - November 5, 2025                        │
│ ┌──────────────────────────────────────────┐   │
│ │ 10:30am - Dog & Duck Inn (Outbound)      │   │
│ │ Duration: 8 mins                         │   │
│ │ Outcome: Placed order                    │   │
│ │ Notes: Ordered 4 firkins Tonk IPA for    │   │
│ │        Thursday delivery                 │   │
│ │ [View Customer] [Create Order]           │   │
│ ├──────────────────────────────────────────┤   │
│ │ 2:15pm - Red Lion (Inbound)              │   │
│ │ Duration: 3 mins                         │   │
│ │ Outcome: No answer                       │   │
│ │ Notes: Left voicemail                    │   │
│ │ Follow-up: Tomorrow                      │   │
│ │ [Create Task]                            │   │
│ └──────────────────────────────────────────┘   │
└────────────────────────────────────────────────┘
```

#### C. TASKS / REMINDERS

**Purpose:** Manage to-do items and follow-ups.

**Features:**
1. **Task Entry:**
   - Task title (brief description)
   - Task description (detailed)
   - Task type (follow-up/quote/payment chase/other)
   - Related customer (optional)
   - Priority (high/medium/low)
   - Due date
   - Assigned to (username)
   - Status (pending/in progress/completed/cancelled)

2. **Task List Views:**
   - My tasks (assigned to me)
   - All tasks
   - Overdue tasks
   - Due today
   - Due this week
   - Completed tasks

3. **Sorting & Filtering:**
   - By priority
   - By due date
   - By customer
   - By task type
   - By assigned person

4. **Quick Actions:**
   - Mark as complete
   - Snooze (reschedule due date)
   - Link to customer
   - Add notes

**UI:**
```
┌────────────────────────────────────────────────┐
│ TASKS                            [+ New Task]   │
├────────────────────────────────────────────────┤
│ View: [My Tasks ▼] Status: [Pending ▼]         │
│                                                 │
│ 🔴 OVERDUE (1)                                 │
│ ┌──────────────────────────────────────────┐   │
│ │ ☐ Chase payment - Crown Hotel            │   │
│ │   Due: Nov 3 (2 days ago)                │   │
│ │   [Complete] [Snooze] [View Customer]    │   │
│ └──────────────────────────────────────────┘   │
│                                                 │
│ 📅 DUE TODAY (2)                               │
│ ┌──────────────────────────────────────────┐   │
│ │ ☐ Send quote - New prospect              │   │
│ │   Priority: High                         │   │
│ │                                           │   │
│ │ ☐ Follow up call - Builders Arms         │   │
│ │   Priority: Medium                       │   │
│ └──────────────────────────────────────────┘   │
│                                                 │
│ 📆 THIS WEEK (3)                               │
│ ┌──────────────────────────────────────────┐   │
│ │ ☐ Visit Railway Tavern - Thu Nov 7       │   │
│ │ ☐ Check stock for Xmas orders - Fri      │   │
│ │ ☐ Update pricing list - Fri              │   │
│ └──────────────────────────────────────────┘   │
└────────────────────────────────────────────────┘
```

#### D. SALES PIPELINE

**Purpose:** Track sales opportunities from prospect to close.

**Features:**
1. **Opportunity Entry:**
   - Customer (existing or new prospect)
   - Opportunity name/description
   - Estimated value (£)
   - Stage (prospecting/quoted/negotiation/won/lost)
   - Probability (0-100%)
   - Expected close date
   - Notes

2. **Pipeline Stages:**
   - **Prospecting:** Initial contact, gathering info
   - **Quoted:** Formal quote sent
   - **Negotiation:** Discussing terms, pricing
   - **Won:** Deal closed, customer confirmed
   - **Lost:** Opportunity lost (note why)

3. **Pipeline View:**
   - Kanban board style (drag between stages)
   - List view with all opportunities
   - Filter by stage, customer, date range
   - Sort by value, probability, close date

4. **Metrics:**
   - Total pipeline value
   - Weighted pipeline value (value × probability)
   - Conversion rates by stage
   - Average deal size
   - Time in each stage

**UI:**
```
┌────────────────────────────────────────────────┐
│ SALES PIPELINE                  [+ New Opp]     │
├────────────────────────────────────────────────┤
│ Total Pipeline: £8,500  Weighted: £4,250       │
├────────────────────────────────────────────────┤
│ Prospecting  │  Quoted     │ Negotiation │ Won │
│ (3 opps)     │  (2 opps)   │ (1 opp)     │     │
├──────────────┼─────────────┼─────────────┼─────┤
│ New Wine Bar │ Crown Xmas  │ Red Lion    │     │
│ £2,000       │ £1,500      │ £3,000      │     │
│ 20%          │ 60%         │ 80%         │     │
│              │             │             │     │
│ Hotel Group  │ Sports Club │             │     │
│ £1,200       │ £800        │             │     │
│ 30%          │ 40%         │             │     │
│              │             │             │     │
│ Restaurant   │             │             │     │
│ £600         │             │             │     │
│ 10%          │             │             │     │
└──────────────┴─────────────┴─────────────┴─────┘
```

### Integration Between Tools
- **Call → Task:** Log call outcome "needs follow-up" → auto-creates task
- **Task → Calendar:** Schedule task → creates calendar event
- **Pipeline → Customer:** Win opportunity → customer created/updated
- **Calendar → Call Log:** Scheduled call → quick log from calendar

---

## MODULE 6: SALES & DISPATCH

### Overview
Record cask/bottle sales with two-stage workflow: (1) Reserved, (2) Delivered. Links to finished goods inventory and customer records.

### Two-Stage Sales Workflow

#### STAGE 1: RESERVE SALE (Order Taken)
**When:** Customer places order but beer not yet delivered

**Actions:**
1. Create new sale record
2. Select customer
3. Select product:
   - **From Casks Full:** Choose gyle number, beer name, cask type/size
   - **From Bottles:** Choose gyle number, beer name, bottle size
4. Enter quantity
5. Confirm unit price (auto-fills from pricing table, can override)
6. Calculate line total (quantity × unit price)
7. Set status: "Reserved"
8. Record reserved date
9. Update finished goods status → "Reserved for [Customer]"

**Result:**
- Sale exists with status "Reserved"
- Stock shows as reserved (not available for other customers)
- Not yet invoiced
- Not yet depleted from stock count

#### STAGE 2: MARK AS DELIVERED (Dispatch/Delivery)
**When:** Beer physically delivered to customer

**Actions:**
1. Find reserved sale
2. Mark as "Delivered"
3. Enter delivery date
4. System automatically:
   - Depletes stock (removes from finished goods)
   - Makes sale eligible for invoicing
   - Updates customer's "last order date"

**Result:**
- Sale status = "Delivered"
- Stock reduced
- Ready to generate invoice

### Sales Entry UI
```
┌────────────────────────────────────────────────┐
│ RECORD SALE                     [Save] [Cancel] │
├────────────────────────────────────────────────┤
│ Customer: [Dog & Duck Inn ▼]                   │
│ Date: [Nov 5, 2025]                            │
│                                                 │
│ ITEMS                                 [+ Add]   │
│ ┌──────────────────────────────────────────┐   │
│ │ Gyle: GYLE-2025-042                      │   │
│ │ Beer: Tonk IPA                           │   │
│ │ Container: Firkin (40.9L)                │   │
│ │ Quantity: [4]                            │   │
│ │ Unit Price: [£65.00]                     │   │
│ │ Line Total: £260.00                      │   │
│ │ [Remove Line]                            │   │
│ └──────────────────────────────────────────┘   │
│                                                 │
│ TOTAL: £260.00                                 │
│                                                 │
│ Status: ⚫ Reserved  (not yet delivered)       │
│                                                 │
│ Notes: [Thursday morning delivery as requested] │
│                                                 │
│ [Save as Reserved] [Mark as Delivered & Save]  │
└────────────────────────────────────────────────┘
```

### Sales List / Dispatch View
```
┌────────────────────────────────────────────────┐
│ SALES & DISPATCH                [+ New Sale]    │
├────────────────────────────────────────────────┤
│ [Reserved Orders] [Delivered] [All Sales]       │
├────────────────────────────────────────────────┤
│                                                 │
│ RESERVED ORDERS (Pending Delivery)              │
│ ┌──────────────────────────────────────────┐   │
│ │ Customer         Beer         Qty  Value │   │
│ ├──────────────────────────────────────────┤   │
│ │ Dog & Duck       Tonk IPA     4F   £260  │   │
│ │ Reserved: Nov 5  Deliver: Thu Nov 7      │   │
│ │ [Mark Delivered] [Edit] [Cancel]         │   │
│ ├──────────────────────────────────────────┤   │
│ │ Crown Hotel      Session Ale   6F  £330  │   │
│ │ Reserved: Nov 4  Deliver: Fri Nov 8      │   │
│ │ [Mark Delivered] [Edit] [Cancel]         │   │
│ └──────────────────────────────────────────┘   │
│                                                 │
│ RECENT DELIVERIES                               │
│ ┌──────────────────────────────────────────┐   │
│ │ Nov 5 - Builders Arms  2F Tonk IPA  £130│   │
│ │ Nov 4 - Railway Tavern 3K Session   £195│   │
│ │ Nov 4 - Red Lion      10F Tonk IPA  £650│   │
│ └──────────────────────────────────────────┘   │
└────────────────────────────────────────────────┘
```

### Validation Rules
- Customer must be selected
- At least one item required
- Quantity must be positive
- Cannot reserve more stock than available
- Delivery date must be ≥ reserved date
- Unit price must be positive
- Cannot mark as delivered without delivery date

### Stock Checks
Before reserving:
```python
def check_stock_available(gyle_number, container_type, container_size, quantity_needed):
    # Query Casks_Full for this gyle/type/size
    available = get_available_stock(gyle_number, container_type, container_size)
    
    if available >= quantity_needed:
        return True
    else:
        show_error(f"Only {available} available, you requested {quantity_needed}")
        return False
```

### Reports Available
1. **Reserved Orders Report** - All pending deliveries
2. **Delivery Schedule** - What needs delivering when
3. **Sales by Customer** - Total sales per customer in date range
4. **Sales by Beer** - Which beers selling best
5. **Sales by Gyle** - Track specific batch performance

---

## MODULE 7: INVOICING & PAYMENT TRACKING

### Overview
Generate professional invoices from delivered sales, track payments, manage outstanding balances, and produce aged debt reports.

### Invoice Generation

#### Creating Invoices

**Method 1: From Delivered Sales**
1. View delivered sales not yet invoiced
2. Select customer
3. Select which sales to include on invoice
4. System auto-generates invoice with:
   - Auto-increment invoice number (INV-2025-0001)
   - Invoice date (today)
   - Customer details (from customer record)
   - Line items (from selected sales)
   - Subtotal calculation
   - VAT calculation (20% standard)
   - Total calculation
   - Due date (based on customer payment terms)

**Method 2: Manual Invoice**
1. Select customer
2. Manually add line items
3. Enter descriptions, quantities, unit prices
4. System calculates subtotal, VAT, total

#### Invoice Details
```
┌────────────────────────────────────────────────┐
│ INVOICE INV-2025-0156                   [Edit] │
├────────────────────────────────────────────────┤
│ Date: November 5, 2025                         │
│ Due Date: November 19, 2025 (Net 14)           │
│                                                 │
│ BILL TO:                                        │
│ Dog & Duck Inn                                 │
│ 123 High Street                                │
│ Stoke-on-Trent, ST1 1AA                        │
│ Contact: John Smith                            │
│                                                 │
│ LINE ITEMS                                      │
│ ┌──────────────────────────────────────────┐   │
│ │ Description          Qty  Price   Total  │   │
│ ├──────────────────────────────────────────┤   │
│ │ Tonk IPA Firkin       4   £65.00  £260.00│  │
│ │ (Gyle: GYLE-2025-042)                    │   │
│ │                                           │   │
│ │ Session Ale Firkin    2   £55.00  £110.00│  │
│ │ (Gyle: GYLE-2025-038)                    │   │
│ └──────────────────────────────────────────┘   │
│                                                 │
│ Subtotal:                           £370.00    │
│ VAT (20%):                          £74.00     │
│ ───────────────────────────────────────────    │
│ TOTAL:                              £444.00    │
│                                                 │
│ Payment Status: UNPAID                         │
│ Amount Paid: £0.00                             │
│ Outstanding: £444.00                           │
│                                                 │
│ [Record Payment] [Send Email] [Print] [PDF]    │
└────────────────────────────────────────────────┘
```

### Invoice Formatting
**Professional Layout:**
- Brewery logo (top)
- Brewery name, address, VAT number
- Invoice number (prominent)
- Invoice date and due date
- Customer details
- Clear line item table
- Subtotal, VAT breakdown, total
- Payment terms reminder
- Bank details for payment

**Exportable Formats:**
- PDF (primary)
- Print directly
- Email directly (with PDF attachment)

### Payment Tracking

#### Recording Payments
1. Find invoice (by number or customer)
2. Click "Record Payment"
3. Enter:
   - Payment date
   - Amount received
   - Payment method (cash/cheque/BACS/card)
   - Payment reference (cheque number, BACS ref, etc.)
4. System automatically:
   - Updates "amount paid"
   - Recalculates "amount outstanding"
   - Updates payment status:
     - "Paid" if outstanding = £0
     - "Partially Paid" if 0 < outstanding < total
     - "Unpaid" if nothing paid yet
   - Updates customer's total outstanding balance

#### Partial Payments
- Allowed and fully supported
- Can record multiple payments against one invoice
- Payment history visible on invoice
- Each payment logged with date, amount, method

#### Payment History
View all payments for:
- Specific invoice
- Specific customer (all invoices)
- Date range (all payments received)

### Outstanding Balances

#### Customer Balance
Auto-calculated for each customer:
```
Total Outstanding = Sum of all unpaid/partially paid invoices
```

**Dashboard Indicators:**
- Green: £0 outstanding
- Yellow: Outstanding but within credit limit
- Red: Outstanding exceeds credit limit

#### Aged Debt Report
Categorize outstanding invoices by age:
- **0-30 days:** Current
- **31-60 days:** Slightly overdue
- **61-90 days:** Overdue
- **90+ days:** Seriously overdue

**UI:**
```
┌────────────────────────────────────────────────┐
│ AGED DEBT REPORT - November 5, 2025            │
├────────────────────────────────────────────────┤
│ Customer        0-30   31-60  61-90  90+  Total│
│ ────────────────────────────────────────────── │
│ Crown Hotel     £450   £225    £0    £0   £675 │
│ Red Lion        £800   £650   £400   £0  £1,850│
│ Railway Tavern  £220    £0     £0    £0   £220 │
│ Dog & Duck      £450    £0     £0    £0   £450 │
│ ────────────────────────────────────────────── │
│ TOTALS        £1,920  £875   £400   £0  £3,195 │
└────────────────────────────────────────────────┘
```

### Invoice List View
```
┌────────────────────────────────────────────────┐
│ INVOICES                       [+ New Invoice]  │
├────────────────────────────────────────────────┤
│ [Unpaid] [Partially Paid] [Paid] [All]         │
│                                                 │
│ Filter: Customer [All ▼] Date [Last 3 months ▼]│
│                                                 │
│ UNPAID (3)                                      │
│ ┌──────────────────────────────────────────┐   │
│ │ INV-2025-0156  Dog & Duck    £444.00     │   │
│ │ Due: Nov 19    (14 days)                 │   │
│ │                                           │   │
│ │ INV-2025-0152  Crown Hotel   £675.00 🔴  │   │
│ │ Due: Nov 1     (4 days OVERDUE)          │   │
│ │                                           │   │
│ │ INV-2025-0148  Red Lion    £1,850.00 🔴  │   │
│ │ Due: Oct 15    (21 days OVERDUE)         │   │
│ └──────────────────────────────────────────┘   │
│                                                 │
│ Total Unpaid: £2,969.00                        │
└────────────────────────────────────────────────┘
```

### Validation Rules
- Invoice numbers must be sequential and unique
- Invoice date cannot be future date
- At least one line item required
- Line quantities and prices must be positive
- VAT rate must be valid (usually 0.20)
- Payment date cannot be before invoice date
- Payment amount cannot exceed outstanding balance
- Customer must exist

### Email Integration
**Send Invoice by Email:**
- Uses customer's email from profile
- Subject: "Invoice [INV-NUMBER] from [BREWERY NAME]"
- Body: Professional message with payment terms
- Attachment: PDF of invoice
- Logs email sent in activity history

### QuickBooks Export
**Export Format:**
- CSV file with required columns
- Invoice number, date, customer, line items, amounts
- Importable to QuickBooks
- Batch export capability (all invoices in date range)

### Reports Available
1. **Unpaid Invoices Report** - All outstanding invoices
2. **Aged Debt Report** - Balances by age category
3. **Sales Revenue Report** - Total invoiced in date range
4. **Customer Account Statement** - All invoices and payments for customer
5. **Payment Receipts Report** - All payments received in period

---

## MODULE 8: UK DUTY CALCULATOR

### Overview
HMRC-compliant automatic duty calculations incorporating current UK alcohol duty rates, Draught Relief, and Small Producer Relief (SPR).

### Current UK Duty Framework (Feb 2025)

#### Base Duty Rates (Non-Draught)
| ABV Range | Rate per Litre Pure Alcohol |
|-----------|----------------------------|
| 0-1.2% | £0.00 |
| 1.3-3.4% | £9.61 |
| **3.5-8.4%** | **£21.78** (most craft beer) |
| 8.5-22% | £29.54 |
| Over 22% | £32.79 |

#### Draught Relief (Products < 8.5% ABV)
- **Eligibility:** Packaged in containers ≥20L designed for dispensing system
- **Discount:** 13.9% off full rate
- **Draught Rate (3.5-8.4%):** £18.76 per litre pure alcohol

#### Small Producer Relief (SPR)
- **Eligibility:**
  - Annual production < 4,500 hectolitres pure alcohol
  - Product < 8.5% ABV
  - Not produced under license
- **Benefit:** Sliding scale discount based on annual production
- **Current SPR Rate:** £4.87 per hectolitre (user's brewery)

### Automatic Duty Calculation

#### At Batch Level (When marking "Ready")
**System calculates and stores:**
1. **Pure Alcohol Litres:**
   ```python
   pure_alcohol = batch_size_litres × (measured_abv / 100)
   ```

2. **Determine Base Rate:**
   ```python
   if is_draught and abv < 8.5:
       base_rate = 18.76  # Draught beer 3.5-8.4%
   elif 3.5 <= abv <= 8.4:
       base_rate = 21.78  # Non-draught beer 3.5-8.4%
   # ... other ABV ranges
   ```

3. **Apply SPR Discount:**
   ```python
   # Get current SPR rate from system settings
   spr_discount_per_litre = get_setting('spr_discount_per_litre')  # £0.0487
   
   if is_small_producer and abv < 8.5:
       duty_rate_applied = base_rate - spr_discount_per_litre
   else:
       duty_rate_applied = base_rate
   ```

4. **Calculate Duty Amount:**
   ```python
   duty_amount = pure_alcohol × duty_rate_applied
   duty_amount = math.floor(duty_amount * 100) / 100  # Round DOWN to penny
   ```

5. **Store for Future Reference:**
   - `spr_rate_applied` - The SPR discount used (£/hl)
   - `duty_rate_applied` - Final duty rate used (£/L pure alcohol)
   - These are locked at production date (don't change if rates change later)

### Monthly Duty Return

#### Duty Period
- Based on **packaging date** (when duty point passed)
- Typically monthly returns
- Period: 1st to end of month

#### Generating Return
1. Select period (start date, end date)
2. System finds all batches packaged in period
3. For each batch:
   - Get pure alcohol litres
   - Get duty rate applied (stored at production)
   - Calculate duty amount
4. Sum all duty amounts = **Total Duty Payable**
5. Create return record with:
   - Period covered
   - List of batches (gyle numbers)
   - Individual duty calculations
   - Total duty payable
   - Payment due date (usually 14 days after period end)

#### Return UI
```
┌────────────────────────────────────────────────┐
│ DUTY RETURN - October 2025                     │
├────────────────────────────────────────────────┤
│ Period: Oct 1-31, 2025                         │
│ Due Date: November 14, 2025                    │
│                                                 │
│ BATCHES PACKAGED IN PERIOD                      │
│ ┌──────────────────────────────────────────┐   │
│ │ Gyle      Beer         Pure    Rate  Duty│   │
│ │                       Alcohol             │   │
│ ├──────────────────────────────────────────┤   │
│ │ GYLE-042  Tonk IPA    46.4L  £16.91 £784.62│ │
│ │ GYLE-043  Session     30.4L  £16.91 £514.08│ │
│ │ GYLE-044  Tonk IPA    42.0L  £16.91 £710.22│ │
│ │ GYLE-045  Porter      38.5L  £16.91 £650.98│ │
│ └──────────────────────────────────────────┘   │
│                                                 │
│ TOTAL PURE ALCOHOL: 157.3 litres               │
│ TOTAL DUTY PAYABLE: £2,659.90                  │
│                                                 │
│ Payment Status: UNPAID                         │
│                                                 │
│ [Mark as Paid] [Export to Excel] [Print]       │
└────────────────────────────────────────────────┘
```

### Duty Calculation Examples

**Example 1: Draught Beer with SPR**
```
Batch: 800L of 4.2% ABV Pale Ale in 30L kegs (draught)
Pure alcohol: 800 × 0.042 = 33.6 litres

Base rate (draught 3.5-8.4%): £18.76/L
SPR discount: £0.0487/L (£4.87/hL)
Final rate: £18.76 - £0.0487 = £18.7113/L

Duty: 33.6 × £18.7113 = £628.70 (rounded down)
```

**Example 2: Bottles (Non-Draught) with SPR**
```
Batch: 400L of 5.8% ABV IPA in 500ml bottles (non-draught)
Pure alcohol: 400 × 0.058 = 23.2 litres

Base rate (non-draught 3.5-8.4%): £21.78/L
SPR discount: £0.0487/L
Final rate: £21.78 - £0.0487 = £21.7313/L

Duty: 23.2 × £21.7313 = £504.17 (rounded down)
```

### System Settings for Duty

**Brewery Configuration (in System Settings):**
- `annual_production_hectolitres` - Total production for SPR calculation
- `is_small_producer` - Boolean (currently TRUE)
- `spr_discount_per_litre` - Current SPR rate (£0.0487)
- `production_year_start` - Feb 1
- `production_year_end` - Jan 31

**Updating SPR Rate:**
- Done annually based on previous year's production
- Formula provided in UK Duty Reference guide
- Recalculated using SPR lookup tables
- System admin can update setting

### Validation Rules
- Measured ABV required before calculating duty
- Batch size must be > 0
- ABV must be 0-100% (realistic 2-15%)
- Is_draught flag must be set correctly
- Packaging date required (duty point)
- Cannot modify batch duty rates after packaging

### Reports Available
1. **Monthly Duty Summary** - Total duty for period
2. **Annual Duty Report** - Year-to-date duty paid
3. **Batch Duty Breakdown** - Duty per gyle number
4. **SPR Calculation Report** - Shows how SPR discount was calculated

### HMRC Compliance Notes
- **Rounding:** Always round DOWN to nearest penny (per HMRC rules)
- **Duty Point:** Packaging date = when duty becomes due
- **Records:** Must retain for 6 years
- **SPR Rate:** Apply rate from production date, not duty payment date
- **Audit Trail:** Complete traceability required (ingredients → batch → packaging → duty)

---

## MODULE 9: CASK LABEL PRINTING

### Overview
Generate and print professional cask labels with brewery logo, beer details, gyle number, and HMRC-required duty declarations.

### Label Content

#### Required Information (HMRC)
1. **Beer Name**
2. **ABV** (alcohol by volume %)
3. **Volume Declaration:** "Duty paid on X litres"
4. **Packaging Date**
5. **Gyle Number** (for traceability)

#### Branding
1. **Brewery Logo** (user uploads during setup)
2. **Brewery Name**
3. **(Optional) Beer Style**
4. **(Optional) Tasting Notes / Description**

### Label Sizes
Support common cask label sizes:
- **Standard Cask Label:** 4" × 3" (100mm × 75mm)
- **Large Cask Label:** 5" × 4" (127mm × 100mm)
- **Mini-Keg Label:** 3" × 2" (76mm × 50mm)

User can select size or use default (standard).

### Label Design

**Layout Example:**
```
┌─────────────────────────────────────────┐
│         [BREWERY LOGO]                  │
│      YOUR BREWERY NAME                  │
│                                         │
│         TONK IPA                        │
│     American-Style IPA                  │
│                                         │
│    ABV: 5.8%    Packaged: Nov 5, 2025  │
│                                         │
│    Gyle: GYLE-2025-042                  │
│                                         │
│    Duty paid on 40.9 litres            │
│                                         │
│  Hoppy, citrusy, with a clean finish   │
└─────────────────────────────────────────┘
```

### Label Generation Workflow

#### Method 1: From Batch (During Packaging)
1. Package batch (record casks filled)
2. Click "Print Labels"
3. System auto-fills:
   - Beer name
   - Gyle number
   - ABV
   - Packaging date
   - Volume (based on cask size)
4. Select quantity of labels needed
5. Preview labels
6. Print

#### Method 2: Reprint Labels Later
1. Find batch by gyle number
2. Click "Reprint Labels"
3. Same auto-filled info
4. Select quantity
5. Print

### Label Printing Options

**Print Methods:**
1. **Direct Print** - Print to label printer
2. **PDF Export** - Save as PDF for printing later
3. **Sheet Print** - Print multiple labels per A4 sheet (e.g., 10 labels per sheet)

**Printer Setup:**
- Support standard label printers (Zebra, Dymo, Brother)
- Support A4 label sheets (Avery templates)
- Configurable margins and spacing

### Customization Options

**User Can Customize:**
- Logo image (upload .png, .jpg)
- Brewery name (from system settings)
- Font sizes (small/medium/large presets)
- Include/exclude tasting notes
- Include/exclude beer style
- Color scheme (basic: black/white or color)

**Fixed Requirements (HMRC):**
- ABV always shown
- Volume declaration always shown ("Duty paid on X litres")
- Cannot be removed/hidden

### UI for Label Printing
```
┌────────────────────────────────────────────────┐
│ PRINT LABELS - GYLE-2025-042          [Print]  │
├────────────────────────────────────────────────┤
│ Beer: Tonk IPA                                 │
│ Gyle: GYLE-2025-042                            │
│ ABV: 5.8%                                      │
│ Packaged: Nov 5, 2025                          │
│                                                 │
│ CASK DETAILS                                    │
│ Cask Type: [Firkin ▼]                          │
│ Cask Size: 40.9 litres (auto-filled)           │
│ Number of Labels: [20]                         │
│                                                 │
│ LABEL OPTIONS                                   │
│ Label Size: [Standard (4×3) ▼]                 │
│ Include Style: [✓] American-Style IPA          │
│ Include Notes: [✓] Hoppy, citrusy finish       │
│                                                 │
│ PREVIEW                                         │
│ ┌───────────────────────────────────────────┐  │
│ │      [LOGO]                               │  │
│ │   TONK'S BREWERY                          │  │
│ │                                           │  │
│ │       TONK IPA                            │  │
│ │   American-Style IPA                      │  │
│ │                                           │  │
│ │ ABV: 5.8%    Nov 5, 2025                  │  │
│ │ Gyle: GYLE-2025-042                       │  │
│ │ Duty paid on 40.9 litres                  │  │
│ │                                           │  │
│ │ Hoppy, citrusy, with a clean finish       │  │
│ └───────────────────────────────────────────┘  │
│                                                 │
│ [Print Now] [Save as PDF] [Cancel]             │
└────────────────────────────────────────────────┘
```

### Label Templates
**Pre-designed templates:**
- Classic (traditional brewery style)
- Modern (clean, minimalist)
- Craft (hand-drawn aesthetic)
- Bold (strong typography)

User selects template, system applies styling automatically.

### Validation Rules
- Brewery logo must be uploaded before printing
- ABV required
- Volume required
- Packaging date required
- Gyle number required
- Quantity must be 1-500 per print job

### Technical Implementation
- **Library:** Python Imaging Library (PIL/Pillow)
- **Format:** Generate as PNG images first
- **Conversion:** Convert to PDF for printing
- **Resolution:** 300 DPI for quality printing
- **Color:** RGB color space (or grayscale for B&W printers)

---

## USER ROLES & PERMISSIONS

### Four User Roles

#### 1. ADMIN
**Full system access - can do everything.**

**Permissions:**
- All recipe management
- All inventory management
- All batch/gyle operations
- All CRM/customer management
- All sales & dispatch
- All invoicing & payments
- All duty calculations & returns
- All label printing
- **System settings** (only role with this access)
  - Update brewery details
  - Update pricing
  - Configure system settings
  - Manage users (add/edit/deactivate)
  - Update SPR rates
- View all reports
- Export data

**Typical User:** Brewery owner, general manager

#### 2. BREWER
**Focus on production and inventory.**

**Permissions:**
- View recipes (read-only or edit depending on setup)
- Record incoming brewing materials
- Create new batches
- Log fermentation data
- Mark batches through stages (fermenting → conditioning → ready)
- Package batches
- Print labels
- View inventory levels
- Record stock adjustments (with reason)

**Restrictions:**
- Cannot modify system settings
- Cannot manage customers
- Cannot create invoices
- Cannot record payments
- Read-only access to sales data
- Cannot update pricing

**Typical User:** Head brewer, assistant brewer

#### 3. OFFICE
**Focus on admin, sales, and finances.**

**Permissions:**
- View all recipes (read-only)
- View all batches and stock levels
- Full CRM access (add/edit customers)
- Full sales tools access (calendar, calls, tasks, pipeline)
- Record sales (reserve & deliver)
- Generate invoices
- Record payments
- View/print reports
- Export data (invoices, reports)
- View duty calculations

**Restrictions:**
- Cannot create/edit recipes
- Cannot create batches
- Cannot modify brewing inventory (read-only)
- Cannot change system settings
- Cannot manage users

**Typical User:** Office manager, bookkeeper, sales admin

#### 4. SALES
**Focus on customer relationships and taking orders.**

**Permissions:**
- View customers (read-only)
- View available stock (finished goods)
- Record sales (reserve orders)
- Use sales tools (calendar, call log, tasks, pipeline)
- View own tasks/calendar events
- View pricing

**Restrictions:**
- Cannot modify customer details (can add notes only)
- Cannot mark sales as delivered (office does this)
- Cannot create invoices
- Cannot view/record payments
- Cannot access brewing/production modules
- Cannot access inventory management
- Cannot view duty information
- Cannot change system settings

**Typical User:** Sales rep, delivery driver (when taking orders)

### User Management

**Admin Can:**
- Add new users
- Assign roles
- Activate/deactivate users
- Reset passwords
- View user activity log

**User Profile:**
- Username (unique login)
- Full name (display name)
- Role (admin/brewer/office/sales)
- Active status (can log in?)
- Date created

### Login & Authentication
- Simple username/password
- Remember me option (local machine only)
- Session timeout after 60 minutes inactivity
- Auto-save work before timeout

### Permission Enforcement
```python
@require_permission('admin')
def edit_system_settings():
    # Only admins can access
    pass

@require_permission(['admin', 'brewer'])
def create_batch():
    # Admins and brewers can access
    pass

@require_permission(['admin', 'office'])
def generate_invoice():
    # Admins and office staff can access
    pass
```

---

## BUSINESS RULES & VALIDATION

### Core Business Rules

#### Inventory
1. **Stock cannot go negative**
   - Validation prevents creating batch without sufficient ingredients
   - Warning shown: "Insufficient stock of [ingredient]. Need X kg, have Y kg."
   - User can choose to: Cancel batch, adjust recipe, or manually add stock first

2. **Low stock alerts triggered when:**
   - Current stock < reorder level
   - Visual indicator (red dot or exclamation)
   - Alert list on dashboard

3. **Automatic depletion**
   - Batch creation → ingredients deducted immediately
   - Batch packaging → empty casks deducted immediately
   - Sale delivery → finished goods deducted immediately

4. **Stock adjustments require reason**
   - Dropdown: Spillage / Spoilage / Damaged / Stocktake Correction / Other
   - Free text for additional notes
   - Logged in audit trail

#### Batches & Gyle Tracking
1. **Gyle numbers are sequential and never reused**
   - Auto-increment from system setting
   - Format: GYLE-[YEAR]-[###] (e.g., GYLE-2025-001)
   - System prevents manual editing
   - Cannot skip numbers

2. **Status transitions must follow workflow:**
   - Brewing → Fermenting → Conditioning → Ready → Packaged
   - Cannot skip stages (except conditioning, which is optional)
   - Cannot go backward (read-only once moved forward)

3. **ABV measurement required before packaging**
   - System enforces: Status cannot be "Ready" without measured ABV
   - ABV must be realistic (0.5% - 15% range with warning outside 2-12%)

4. **Packaging date = Duty point date**
   - Recorded automatically
   - Cannot be changed after packaging (locked)
   - Used for duty return period assignment

5. **SPR rate locked at production**
   - When batch marked "Ready": current SPR rate stored
   - If SPR rate changes later, old batches keep old rate
   - Ensures correct duty calculation even if rates change

#### Sales & Dispatch
1. **Two-stage workflow enforced:**
   - Stage 1: Reserved (order taken, stock reserved)
   - Stage 2: Delivered (physical delivery, stock depleted, can invoice)
   - Cannot skip straight to delivered without reserving first

2. **Stock reservation prevents double-booking:**
   - Reserved stock shows as "unavailable" for other customers
   - System checks available (in_stock) quantity before allowing reservation
   - Warning if trying to reserve more than available

3. **Cannot over-sell:**
   - Validation: Quantity requested ≤ Available stock
   - Error shown: "Only X casks available, you requested Y"

4. **Delivery date must be ≥ Reserved date**
   - System validates chronology
   - Cannot deliver before order was placed

5. **Sales link to specific gyle numbers:**
   - Traceability requirement
   - Each sale line must reference a gyle
   - System shows available gyles with sufficient stock

#### Invoicing & Payments
1. **Invoice numbers are sequential:**
   - Format: INV-[YEAR]-[####] (e.g., INV-2025-0001)
   - Auto-increment, cannot skip
   - Cannot manually edit invoice number

2. **Invoice must have ≥1 line item:**
   - Validation prevents saving empty invoice

3. **VAT calculation automatic:**
   - Standard rate: 20%
   - Formula: VAT = Subtotal × 0.20
   - Total = Subtotal + VAT
   - User cannot override (hard-coded for UK)

4. **Payment cannot exceed outstanding balance:**
   - Validation: Payment amount ≤ Amount outstanding
   - Error if trying to overpay

5. **Payment date cannot be before invoice date:**
   - Chronology validation

6. **Credit limit warnings:**
   - When customer's total outstanding exceeds credit limit:
     - Warning shown (yellow/orange alert)
     - Does not prevent sale (just warns user)
     - Highlighted in customer list

7. **Overdue invoice indicators:**
   - Automatic calculation: Days overdue = Today - Due date
   - Color coding:
     - Green: Paid
     - White: Not yet due
     - Yellow: 1-14 days overdue
     - Orange: 15-30 days overdue
     - Red: 30+ days overdue

#### Pricing
1. **Pricing hierarchy:**
   - **Default pricing:** Set per container type/size (system-wide)
   - **Customer override:** Specific price for specific customer (optional)
   - **Sale-time override:** Can manually override at point of sale

2. **Price lookup order:**
   ```
   1. Check for customer-specific override (active within date range)
   2. If none, use default pricing
   3. If manually overridden at sale time, use manual price
   ```

3. **Pricing effective dates:**
   - Customer overrides can have start/end dates
   - System automatically uses correct price based on sale date

#### Duty Calculations
1. **Rounding rule: Always round DOWN**
   - HMRC requirement
   - Formula: `math.floor(duty_amount * 100) / 100`
   - Example: £628.7059 → £628.70 (not £628.71)

2. **Calculation precision:**
   - Calculate to 4 decimal places during calculation
   - Only round at final step

3. **Duty rates locked at production:**
   - Current rates stored when batch marked "Ready"
   - If rates change mid-year, old batches use old rates
   - New batches use new rates

4. **Duty point is packaging date:**
   - Batch enters duty return for month/period when packaged
   - Not when brewed, not when sold - when packaged

#### Data Integrity
1. **Audit logging for critical changes:**
   - Log who, when, what changed
   - Tables logged: Batches, Inventory, Sales, Invoices, Payments, System_Settings
   - Audit log table stores: timestamp, username, action (create/update/delete), table name, record ID, before/after values

2. **Soft deletes preferred:**
   - Instead of deleting records, mark as inactive/archived
   - Preserves history and traceability
   - Examples: Customers, recipes can be archived (not deleted)

3. **Required fields enforced:**
   - System marks mandatory fields with (asterisk)
   - Cannot save record without required fields
   - Clear error messages when validation fails

4. **Date validations:**
   - No future dates (except scheduled events/tasks)
   - Chronological consistency (e.g., fermentation start ≥ brew date)
   - Date ranges must be start ≤ end

5. **Numeric validations:**
   - Quantities must be positive (> 0)
   - Percentages must be 0-100
   - Prices must be ≥ 0
   - ABV must be realistic (warning if outside 2-12% range)

### Error Handling
**User-Friendly Messages:**
- No technical jargon
- Clear explanation of problem
- Suggest solution when possible

**Examples:**
- ❌ Bad: "FK constraint violation on customer_id"
- ✅ Good: "Customer not found. Please select a valid customer from the list."

- ❌ Bad: "Value out of range"
- ✅ Good: "Quantity must be between 1 and 1000. You entered 0."

- ❌ Bad: "NULL constraint"
- ✅ Good: "Beer name is required. Please enter a name for this batch."

---

## WORKFLOWS

### Complete Workflows for Key Processes

#### WORKFLOW 1: Brewing a Batch (Start to Finish)

**Actors:** Brewer (primary), Office (packaging may be done by either)

**Steps:**
1. **Brewer:** Click "Create New Batch"
2. **System:** Shows batch creation form
3. **Brewer:** Select recipe from dropdown
4. **System:** Auto-fills expected batch size, ingredients from recipe
5. **Brewer:** Adjust batch size if needed (recipe scales automatically)
6. **Brewer:** Enter brew date, brewer name
7. **Brewer:** Click "Check Ingredients"
8. **System:** Checks inventory for all required ingredients
   - If sufficient: Green checkmarks shown
   - If insufficient: Red X, shows shortage amounts
9. **If sufficient:**
   - **Brewer:** Click "Create Batch"
   - **System:** 
     - Generates next gyle number (GYLE-2025-XXX)
     - Deducts ingredients from inventory
     - Creates batch record with status "Brewing"
     - Shows success message with gyle number
10. **Brewer:** Physical brewing occurs (outside system)
11. **Brewer:** Click batch in list, click "Mark as Fermenting"
12. **System:** Updates status, prompts for fermentation start date
13. **Brewer:** Enter date, save
14. **Brewer:** Log gravity readings daily/periodically
   - Click "Add Log Entry"
   - Enter date, gravity, temperature, notes
   - Save
15. **When fermentation complete:**
   - **Brewer:** Click "Mark as Conditioning"
   - **System:** Updates status, prompts for conditioning start date
   - **Brewer:** Enter date, save
16. **When conditioning complete:**
   - **Brewer:** Click "Mark as Ready"
   - **System:** Prompts for measured ABV
   - **Brewer:** Enter ABV (e.g., 5.8%)
   - **System:** 
     - Calculates pure alcohol litres
     - Looks up current SPR rate
     - Calculates duty rate to apply
     - Stores all calculations
     - Updates status to "Ready"
17. **When ready to package:**
   - **Brewer/Office:** Click "Package Batch"
   - **System:** Shows packaging form
   - **User:** Select cask types and quantities:
     - E.g., 20 firkins, 10 × 30L kegs
   - **User:** Enter packaging date
   - **System:** Validates empty casks available
   - **User:** Click "Confirm Packaging"
   - **System:**
     - Deducts empty casks from inventory
     - Creates finished goods records (Casks_Full)
     - Updates batch status to "Packaged"
     - Calculates estimated duty
   - **User:** Click "Print Labels"
   - **System:** Opens label printing dialog (pre-filled)
   - **User:** Review, adjust quantity if needed, print

**Result:** Batch complete, casks in stock ready to sell, labels printed, duty calculated.

---

#### WORKFLOW 2: Taking an Order & Delivering

**Actors:** Sales/Office (taking order), Office/Brewer (marking delivered)

**Steps:**
1. **Sales/Office:** Customer calls/visits to place order
2. **User:** Navigate to "Sales & Dispatch" → "New Sale"
3. **System:** Shows sale entry form
4. **User:** Select customer from dropdown
5. **System:** Shows customer details, payment terms
6. **User:** Click "Add Item"
7. **System:** Shows item selection dialog
8. **User:** 
   - Select product type (cask or bottles)
   - If cask: Select gyle number from available stock
   - System shows: Beer name, gyle, ABV, available quantity
   - Enter quantity needed
   - Select cask type/size
9. **System:** 
   - Checks stock availability
   - Shows unit price (from pricing table or customer override)
   - Calculates line total
10. **User:** Review, confirm item
11. **User:** Add more items if needed (repeat steps 6-10)
12. **User:** Review total order, add notes if needed
13. **User:** Click "Save as Reserved"
14. **System:**
   - Creates sale record with status "Reserved"
   - Updates finished goods: marks casks as "Reserved for [Customer]"
   - Records reserved date
   - Shows success message
   - Optionally: Add to calendar for delivery day

**Later - When Delivering:**

15. **Office/Brewer:** Navigate to "Reserved Orders"
16. **System:** Shows list of reserved sales
17. **User:** Find order, click "Mark as Delivered"
18. **System:** Prompts for delivery date
19. **User:** Enter date (usually today), confirm
20. **System:**
   - Updates sale status to "Delivered"
   - Depletes stock (removes casks from Casks_Full)
   - Updates customer's last order date
   - Shows "Ready to Invoice" indicator
   - Shows success message

**Result:** Order recorded, stock reserved, then delivered and depleted, ready for invoicing.

---

#### WORKFLOW 3: Invoicing & Payment Collection

**Actors:** Office (primary)

**PART A: Creating Invoice**

1. **Office:** Navigate to "Invoicing" → "Create Invoice"
2. **System:** Shows two options:
   - "From Delivered Sales" (recommended)
   - "Manual Invoice"
3. **Office:** Click "From Delivered Sales"
4. **System:** Shows list of delivered sales not yet invoiced, grouped by customer
5. **Office:** Select customer
6. **System:** Shows all uninvoiced delivered sales for that customer
7. **Office:** Check boxes for sales to include on this invoice
8. **Office:** Click "Generate Invoice"
9. **System:**
   - Creates new invoice record
   - Auto-generates invoice number (INV-2025-XXXX)
   - Pulls customer details
   - Creates line items from selected sales
   - Calculates subtotal
   - Calculates VAT (20%)
   - Calculates total
   - Sets due date (based on customer payment terms)
   - Shows invoice preview
10. **Office:** Review invoice
11. **Office:** Optional: Add manual adjustments, notes
12. **Office:** Click "Finalize Invoice"
13. **System:** 
   - Saves invoice
   - Links sales to invoice
   - Updates invoice status to "Unpaid"
   - Shows success message
14. **Office:** Choose action:
   - Print invoice
   - Email to customer
   - Export as PDF
   - Or all of the above

**PART B: Recording Payment**

15. **Office:** When payment received (days/weeks later)
16. **Office:** Navigate to "Invoices" → "Unpaid"
17. **Office:** Find invoice, click it
18. **System:** Shows invoice details
19. **Office:** Click "Record Payment"
20. **System:** Shows payment entry form
21. **Office:** Enter:
   - Payment date
   - Amount received
   - Payment method (BACS/cash/cheque/card)
   - Payment reference (e.g., BACS reference, cheque number)
   - Optional notes
22. **Office:** Click "Save Payment"
23. **System:**
   - Records payment
   - Updates invoice "amount paid"
   - Recalculates "amount outstanding"
   - Updates payment status:
     - If outstanding = 0: "Paid" (green)
     - If 0 < outstanding < total: "Partially Paid" (yellow)
   - Updates customer's total outstanding balance
   - Shows success message: "Payment recorded. Outstanding balance: £X"

**PART C: Partial Payments (if applicable)**

24. **If partial payment:**
   - Repeat steps 15-23 when next payment received
   - System tracks multiple payments per invoice
   - Payment history visible on invoice

**Result:** Invoice generated from sales, emailed to customer, payment(s) recorded, outstanding balance tracked.

---

#### WORKFLOW 4: Monthly Duty Return

**Actors:** Office or Admin

**Steps:**
1. **User:** Navigate to "Duty Calculator" → "Monthly Returns"
2. **System:** Shows list of previous returns + "Create New Return"
3. **User:** Click "Create New Return"
4. **System:** Prompts for period:
   - Start date (e.g., Oct 1, 2025)
   - End date (e.g., Oct 31, 2025)
5. **User:** Enter dates, click "Generate Return"
6. **System:**
   - Queries all batches packaged in this period
   - For each batch:
     - Gets gyle number, beer name, packaging date
     - Gets pure alcohol litres (stored in batch)
     - Gets duty rate applied (stored in batch)
     - Calculates duty amount (pure alcohol × rate)
   - Sums all duty amounts = Total Duty Payable
   - Calculates payment due date (typically 14 days after period end)
   - Creates return record
   - Shows return summary
7. **User:** Review return details:
   - List of all batches included
   - Individual duty calculations
   - Total pure alcohol
   - Total duty payable
8. **User:** Optional: Export to Excel for HMRC submission
9. **User:** Optional: Print for records
10. **User:** Confirm return is correct, click "Finalize"
11. **System:**
   - Saves return
   - Sets status to "Unpaid"
   - Adds to dashboard alert: "Duty payment due [date]"

**Later - When Paid:**

12. **User:** When duty paid to HMRC
13. **User:** Navigate to return, click "Mark as Paid"
14. **System:** Prompts for:
   - Payment date
   - HMRC payment reference
15. **User:** Enter details, save
16. **System:**
   - Updates return status to "Paid"
   - Records payment date and reference
   - Removes from dashboard alerts
   - Shows success message

**Result:** Monthly duty return calculated, exported for HMRC, payment recorded.

---

## REPORTING REQUIREMENTS

### Standard Reports

#### 1. INVENTORY REPORTS

**A. Current Stock Report**
- **Purpose:** Snapshot of all inventory at this moment
- **Contents:**
  - All brewing materials (grain, hops, yeast, sundries, casks)
  - Current quantity, unit, reorder level
  - Low stock indicators
  - Total value (if costs tracked)
- **Filters:** Material type, supplier
- **Exports:** PDF, Excel

**B. Stock Movement Report**
- **Purpose:** All inventory transactions in date range
- **Contents:**
  - Date, transaction type (purchase/usage/adjustment)
  - Material, quantity change, new balance, reference (batch/supplier)
  - Username who recorded it
- **Filters:** Date range, material type, transaction type
- **Exports:** PDF, Excel

**C. Low Stock Alert Report**
- **Purpose:** Items below reorder level
- **Contents:**
  - Material name, current stock, reorder level, shortage amount
  - Supplier name for re-ordering
- **Filters:** Material type
- **Exports:** PDF, Excel

#### 2. PRODUCTION REPORTS

**A. Batch Production Log**
- **Purpose:** Complete history of a specific batch
- **Contents:**
  - Gyle number, beer name, recipe version
  - Brew date, brewer name
  - All fermentation log entries
  - Conditioning notes
  - Final ABV, pure alcohol
  - Packaging details (casks filled, date)
  - Duty calculation
  - Where sold (if applicable)
- **Use Case:** Traceability, quality control, duty audit
- **Exports:** PDF

**B. Production Summary Report**
- **Purpose:** Overview of all batches in period
- **Contents:**
  - Date range
  - List of all batches: gyle, beer, size, ABV, status
  - Total litres produced
  - Total pure alcohol produced
  - Breakdown by beer style
- **Filters:** Date range, beer name, status
- **Exports:** PDF, Excel

**C. Recipe Usage Report**
- **Purpose:** How many times each recipe brewed
- **Contents:**
  - Recipe name, version
  - Number of times brewed
  - Total litres produced
  - Date of first/last brew
- **Filters:** Date range
- **Exports:** PDF, Excel

#### 3. SALES REPORTS

**A. Sales by Customer**
- **Purpose:** Revenue analysis per customer
- **Contents:**
  - Customer name
  - Number of orders
  - Total litres sold
  - Total revenue
  - Average order value
  - Last order date
  - Ranking (by revenue)
- **Filters:** Date range, customer type
- **Sorts:** By revenue, by order count, by customer name
- **Exports:** PDF, Excel

**B. Sales by Beer**
- **Purpose:** Which beers selling best
- **Contents:**
  - Beer name
  - Total litres sold
  - Total revenue
  - Number of sales
  - Percentage of total sales
- **Filters:** Date range
- **Exports:** PDF, Excel

**C. Sales by Gyle**
- **Purpose:** Track specific batch performance
- **Contents:**
  - Gyle number, beer name
  - Total produced (litres)
  - Total sold (litres)
  - Remaining stock
  - Revenue generated
  - Average price per litre
- **Filters:** Date range, status (all/sold out/in stock)
- **Exports:** PDF, Excel

**D. Delivery Schedule Report**
- **Purpose:** What needs delivering when
- **Contents:**
  - Delivery date
  - Customer name, address
  - Items reserved (beer, quantity, cask types)
  - Total volume to deliver
  - Notes/special instructions
- **Filters:** Date range (upcoming week typical)
- **Sorts:** By date, by customer, by route
- **Exports:** PDF (for delivery driver)

#### 4. FINANCIAL REPORTS

**A. Unpaid Invoices Report**
- **Purpose:** All outstanding invoices
- **Contents:**
  - Invoice number, date, customer
  - Total amount, amount paid, outstanding
  - Due date, days overdue (if applicable)
  - Color-coded by status
- **Filters:** Customer, date range
- **Sorts:** By due date, by amount, by days overdue
- **Exports:** PDF, Excel

**B. Aged Debt Report**
- **Purpose:** Outstanding balances by age
- **Contents:**
  - Customer name
  - Balances by age: 0-30, 31-60, 61-90, 90+ days
  - Total outstanding per customer
  - Grand total
- **Visual:** Bar chart or table
- **Exports:** PDF, Excel

**C. Payment Receipts Report**
- **Purpose:** All payments received in period
- **Contents:**
  - Date, customer, invoice number
  - Amount received, payment method, reference
  - Running total
- **Filters:** Date range, customer, payment method
- **Exports:** PDF, Excel

**D. Sales Revenue Report**
- **Purpose:** Total revenue in period
- **Contents:**
  - Total invoiced
  - Total paid
  - Total outstanding
  - Breakdown by month/week
  - Comparison to previous period
- **Visual:** Line chart, bar chart
- **Filters:** Date range, customer type
- **Exports:** PDF, Excel

**E. Customer Account Statement**
- **Purpose:** Complete financial history for one customer
- **Contents:**
  - Customer details
  - All invoices (date, number, amount)
  - All payments (date, amount, method)
  - Current balance
- **Use Case:** Send to customer, resolve disputes
- **Exports:** PDF

#### 5. DUTY REPORTS

**A. Monthly Duty Summary**
- **Purpose:** Duty calculation for HMRC submission
- **Contents:**
  - Period covered (start/end dates)
  - List of all batches packaged in period
  - Per batch: gyle, beer, pure alcohol, rate, duty amount
  - Total pure alcohol
  - Total duty payable
  - Payment due date, status
- **Exports:** PDF, Excel (for HMRC submission)

**B. Annual Duty Report**
- **Purpose:** Year-to-date duty overview
- **Contents:**
  - Production year (Feb-Jan)
  - Monthly duty amounts
  - Cumulative total
  - Total pure alcohol produced
  - SPR rate used
  - Annual production hectolitres (for SPR calculation)
- **Visual:** Bar chart by month
- **Exports:** PDF, Excel

**C. Batch Duty Breakdown**
- **Purpose:** Duty calculation details for specific batch
- **Contents:**
  - Gyle number, beer name
  - Batch size, ABV, pure alcohol
  - Base duty rate
  - SPR discount applied
  - Final duty rate
  - Total duty amount
  - Is draught? (yes/no)
  - Packaging date (duty point)
- **Use Case:** Audit trail, dispute resolution
- **Exports:** PDF

#### 6. CRM REPORTS

**A. Customer List Report**
- **Purpose:** All customers with summary info
- **Contents:**
  - Name, contact, phone, email
  - Customer type, payment terms
  - Outstanding balance
  - Last order date
  - Total lifetime revenue
- **Filters:** Active/inactive, customer type
- **Sorts:** Alphabetical, by revenue, by last order
- **Exports:** PDF, Excel

**B. Inactive Customers Report**
- **Purpose:** Customers who haven't ordered recently
- **Contents:**
  - Customer name, contact
  - Last order date
  - Days since last order
  - Lifetime revenue
- **Filters:** Threshold (e.g., no order in 90 days)
- **Use Case:** Re-engagement campaigns
- **Exports:** PDF, Excel

**C. Sales Pipeline Report**
- **Purpose:** Current opportunities
- **Contents:**
  - All active opportunities
  - Customer/prospect, value, stage, probability
  - Expected close date
  - Total pipeline value
  - Weighted pipeline value
- **Visual:** Pipeline chart, funnel
- **Filters:** Stage, date range
- **Exports:** PDF, Excel

### Report Access by Role
| Report Category | Admin | Brewer | Office | Sales |
|-----------------|-------|--------|--------|-------|
| Inventory | ✓ | ✓ | View only | ✗ |
| Production | ✓ | ✓ | View only | ✗ |
| Sales | ✓ | View only | ✓ | ✓ (own only) |
| Financial | ✓ | ✗ | ✓ | ✗ |
| Duty | ✓ | View only | ✓ | ✗ |
| CRM | ✓ | ✗ | ✓ | ✓ (limited) |

---

## INTEGRATION REQUIREMENTS

### 1. Google Sheets Integration

**Purpose:** Cloud-based data storage and sync

**How It Works:**
- Application connects to Google Sheets via API
- One master workbook per brewery
- 25 sheets within workbook (see Database Structure)
- All data stored in sheets
- Local SQLite cache mirrors for offline use

**Setup Process:**
1. User creates Google account (if don't have)
2. Application prompts for Google authorization
3. User grants access (OAuth2)
4. Application creates new workbook: "BreweryManager_Data"
5. Application creates all required sheets with headers
6. Initial sync establishes connection

**Sync Behavior:**
- **Online:** Changes immediately synced to Google Sheets
- **Offline:** Changes stored locally, queued for sync
- **Auto-sync:** Attempts every 5 minutes when online
- **Manual sync:** Button always available
- **Conflict resolution:** Last write wins (timestamp comparison)

**Sync Status Indicator:**
- ✓ Green: Synced
- ⟳ Yellow: Syncing...
- ✗ Red: Offline / Sync failed
- Always visible in GUI (top bar or status bar)

**Benefits:**
- **Multi-device:** Access from any computer (brewery, office, home)
- **Backup:** Google handles backups automatically
- **Collaboration:** Multiple users can work simultaneously
- **No server costs:** Using Google's infrastructure
- **Familiar:** Users can view/export data directly in Google Sheets if needed

**Limitations:**
- Requires internet for real-time sync
- Google API rate limits (unlikely to hit with typical brewery usage)
- Privacy consideration (data stored on Google servers - user aware and consents)

### 2. Email Integration

**Purpose:** Send invoices, quotes, reminders

**Requirements:**
- SMTP configuration
- User provides: SMTP server, port, username, password
- Or: Use Gmail API (if using Google account)

**Features:**
- **Send Invoice by Email:**
  - Attaches PDF of invoice
  - Professional email template
  - Customer email from customer record
  - Logs email sent in activity history
- **Email Quotes:**
  - Similar to invoices
- **Payment Reminders:**
  - Automated reminders for overdue invoices (optional feature)
  - User configurable (enable/disable, frequency)

**Security:**
- Passwords encrypted locally
- Secure connection (TLS/SSL)

### 3. QuickBooks Export

**Purpose:** Export financial data to QuickBooks for accounting

**Export Format:**
- CSV file
- QuickBooks-compatible column structure
- Includes: Invoice number, date, customer, line items, amounts, VAT

**Workflow:**
1. User selects date range
2. User clicks "Export to QuickBooks"
3. System generates CSV file
4. User saves file
5. User imports file into QuickBooks (manual step)

**Scope:**
- Invoices
- Payments
- Customer list

**Note:** One-way export only (no import from QuickBooks back into system)

### 4. Label Printer Integration

**Purpose:** Print cask labels directly

**Supported Printers:**
- Zebra label printers (common)
- Dymo label printers
- Brother label printers
- Generic thermal printers (via standard drivers)
- A4 laser/inkjet (using Avery label sheets)

**Print Workflow:**
1. User clicks "Print Labels"
2. System generates label image (PNG, 300 DPI)
3. System converts to appropriate format for printer
4. System sends to selected printer
5. Labels print

**Configuration:**
- User selects printer from dropdown (detects installed printers)
- User configures label size
- Test print function available

### 5. Future Integrations (Out of Scope for Initial Release)

**Potential Future Enhancements:**
- **Xero/Sage Integration:** Similar to QuickBooks
- **E-commerce Integration:** Sell bottles online, sync stock
- **Delivery Route Optimization:** Plan optimal delivery routes
- **SMS Reminders:** Text alerts for deliveries, payment reminders
- **Mobile App:** Native iOS/Android apps
- **Untappd Integration:** Share beer info with Untappd community

---

## TECHNICAL IMPLEMENTATION DETAILS

### Application Structure
```
BreweryManager/
├── main.py                     # Application entry point
├── gui/                        # GUI modules
│   ├── __init__.py
│   ├── main_window.py          # Main application window
│   ├── dashboard.py            # Dashboard/home screen
│   ├── recipes/                # Recipe module UI
│   ├── inventory/              # Inventory module UI
│   ├── batches/                # Batch management UI
│   ├── crm/                    # CRM module UI
│   ├── sales_tools/            # Sales tools UI
│   ├── sales_dispatch/         # Sales & dispatch UI
│   ├── invoicing/              # Invoicing UI
│   ├── duty/                   # Duty calculator UI
│   └── labels/                 # Label printing UI
├── business_logic/             # Business rules & calculations
│   ├── __init__.py
│   ├── duty_calculator.py      # Duty calculation engine
│   ├── pricing_engine.py       # Pricing logic
│   ├── validation.py           # Validation rules
│   └── workflows.py            # Workflow management
├── data_access/                # Data layer
│   ├── __init__.py
│   ├── google_sheets_client.py # Google Sheets API
│   ├── sqlite_cache.py         # Local SQLite cache
│   ├── sync_manager.py         # Sync logic
│   └── models.py               # Data models
├── utilities/                  # Helper functions
│   ├── __init__.py
│   ├── pdf_generator.py        # PDF creation (invoices, reports)
│   ├── label_generator.py      # Label image generation
│   ├── email_sender.py         # Email functionality
│   └── auth.py                 # User authentication
├── config/                     # Configuration files
│   ├── __init__.py
│   ├── settings.py             # App settings
│   └── constants.py            # Constants (duty rates, etc.)
├── assets/                     # Images, logos, icons
├── requirements.txt            # Python dependencies
└── build/                      # PyInstaller build output
```

### Key Python Libraries
```
tkinter                  # GUI framework (built-in)
google-api-python-client # Google Sheets API
google-auth              # Google authentication
sqlite3                  # Local database (built-in)
reportlab                # PDF generation
pillow                   # Image processing (labels)
requests                 # HTTP requests (if needed)
python-dateutil          # Date handling
pandas                   # Data manipulation (optional, for reports)
```

### Database: Google Sheets + SQLite

**Google Sheets:**
- Master data source
- 25 sheets (see Database Structure section)
- Accessed via Google Sheets API v4

**SQLite:**
- Local cache (mirrors Google Sheets)
- File: `~/.brewerymanager/cache.db`
- Schema matches Google Sheets structure
- Used for offline access and fast queries

**Sync Logic:**
```python
def sync_to_google_sheets(table_name, record):
    try:
        # Push change to Google Sheets
        sheets_api.append_row(table_name, record)
        # Update local cache
        sqlite_db.update(table_name, record)
        # Mark as synced
        sync_status[table_name] = True
    except ConnectionError:
        # Queue for later sync
        sync_queue.append((table_name, record))
        sync_status[table_name] = False
```

### Offline Capability

**How It Works:**
1. Application checks internet connection on startup
2. If online: Sync with Google Sheets
3. If offline: Use local SQLite cache
4. All user actions stored locally first
5. Periodic sync attempts (every 5 minutes)
6. When connection restored: Auto-sync queued changes

**Conflict Resolution:**
- Simple strategy: Last write wins
- Timestamp comparison
- Most recent change overwrites older
- Edge case: Rare conflicts manually resolved by user (warning shown)

### User Authentication

**Local Authentication:**
- Users created by admin
- Credentials stored in SQLite (hashed passwords)
- No connection to external auth service
- Simple login screen on app launch

**Google Authentication:**
- OAuth2 flow for Google Sheets access
- One-time setup per user/computer
- Credentials cached securely
- Token refresh handled automatically

### Data Models (Example)

```python
@dataclass
class Batch:
    batch_id: str
    gyle_number: str
    recipe_id: str
    brew_date: date
    brewer_name: str
    actual_batch_size: float
    measured_abv: float
    pure_alcohol_litres: float
    status: str  # brewing/fermenting/conditioning/ready/packaged
    spr_rate_applied: float
    duty_rate_applied: float
    is_draught: bool
    created_by: str
    
    def calculate_pure_alcohol(self):
        return self.actual_batch_size * (self.measured_abv / 100)
    
    def calculate_duty(self):
        return math.floor(self.pure_alcohol_litres * self.duty_rate_applied * 100) / 100
```

### Duty Calculation Engine

```python
class DutyCalculator:
    def __init__(self):
        self.rates = load_duty_rates()  # From config or Google Sheets
        self.spr_discount = get_system_setting('spr_discount_per_litre')
    
    def get_base_rate(self, abv, is_draught):
        if is_draught and abv < 8.5:
            if 3.5 <= abv <= 8.4:
                return 18.76  # Draught beer 3.5-8.4%
            # ... other rates
        else:
            if 3.5 <= abv <= 8.4:
                return 21.78  # Non-draught beer 3.5-8.4%
            # ... other rates
    
    def apply_spr(self, base_rate, is_small_producer, abv):
        if is_small_producer and abv < 8.5:
            return base_rate - self.spr_discount
        return base_rate
    
    def calculate_duty(self, batch):
        base_rate = self.get_base_rate(batch.measured_abv, batch.is_draught)
        duty_rate = self.apply_spr(base_rate, is_small_producer=True, abv=batch.measured_abv)
        duty_amount = batch.pure_alcohol_litres * duty_rate
        return math.floor(duty_amount * 100) / 100  # Round down
```

### PDF Generation (Invoices)

```python
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def generate_invoice_pdf(invoice, filename):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    
    # Header
    c.drawImage('assets/brewery_logo.png', 50, height-100, width=100, height=50)
    c.setFont('Helvetica-Bold', 16)
    c.drawString(200, height-60, "INVOICE")
    c.setFont('Helvetica', 10)
    c.drawString(200, height-80, f"Invoice #: {invoice.invoice_number}")
    c.drawString(200, height-95, f"Date: {invoice.invoice_date}")
    
    # Customer details
    c.drawString(50, height-150, "Bill To:")
    c.drawString(50, height-165, invoice.customer_name)
    c.drawString(50, height-180, invoice.customer_address)
    
    # Line items table
    y = height - 250
    c.line(50, y, width-50, y)
    c.drawString(60, y-15, "Description")
    c.drawString(300, y-15, "Qty")
    c.drawString(350, y-15, "Price")
    c.drawString(450, y-15, "Total")
    y -= 30
    c.line(50, y, width-50, y)
    
    for line in invoice.lines:
        y -= 20
        c.drawString(60, y, line.description)
        c.drawString(300, y, str(line.quantity))
        c.drawString(350, y, f"£{line.unit_price:.2f}")
        c.drawString(450, y, f"£{line.line_total:.2f}")
    
    # Totals
    y -= 40
    c.drawString(350, y, "Subtotal:")
    c.drawString(450, y, f"£{invoice.subtotal:.2f}")
    y -= 20
    c.drawString(350, y, f"VAT ({invoice.vat_rate*100}%):")
    c.drawString(450, y, f"£{invoice.vat_amount:.2f}")
    y -= 20
    c.setFont('Helvetica-Bold', 12)
    c.drawString(350, y, "TOTAL:")
    c.drawString(450, y, f"£{invoice.total:.2f}")
    
    c.save()
```

### Packaging with PyInstaller

**Build Command:**
```bash
pyinstaller --onefile --windowed --name="Brewery Manager" \
    --icon=assets/icon.ico \
    --add-data="assets:assets" \
    --hidden-import=PIL \
    --hidden-import=reportlab \
    main.py
```

**Output:**
- Single `.exe` file (Windows)
- Self-contained (includes Python interpreter, all dependencies)
- Size: ~50-80 MB (typical)
- Installer: Created with Inno Setup or NSIS

### Error Logging

```python
import logging

logging.basicConfig(
    filename='~/.brewerymanager/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

try:
    # Some operation
    pass
except Exception as e:
    logger.error(f"Error in operation: {str(e)}", exc_info=True)
    show_user_error_message("An error occurred. Please try again.")
```

---

## DEVELOPMENT PHASES

### PHASE 1: Core Foundation (Weeks 1-2)
**Goal:** Establish architecture, database, authentication

**Deliverables:**
- Project structure created
- Google Sheets API integration working
- SQLite local cache implemented
- Basic sync manager functional
- User authentication system
- Main window GUI skeleton
- Navigation between modules (empty placeholders)

**Testing:**
- Google Sheets connection
- Offline mode
- Sync functionality
- User login

### PHASE 2: Inventory & Recipes (Weeks 3-4)
**Goal:** Implement inventory and recipe management

**Deliverables:**
- Recipe creation/editing UI
- Recipe database (Google Sheets)
- Recipe scaling calculator
- Inventory management UI (brewing materials)
- Incoming stock entry
- Stock adjustment
- Low stock alerts
- Automatic ingredient depletion logic

**Testing:**
- Create/edit recipes
- Scale recipes
- Add/adjust inventory
- Verify low stock alerts
- Test depletion when batch created

### PHASE 3: Batch Management & Gyle Tracking (Weeks 5-6)
**Goal:** Complete production workflow

**Deliverables:**
- Batch creation UI
- Gyle number auto-generation
- Batch status tracking (brewing → packaged)
- Fermentation logging
- Packaging UI
- Finished goods tracking (Casks Full, Bottles)
- Empty cask inventory
- Traceability chain complete

**Testing:**
- Create batches
- Log fermentation data
- Move through statuses
- Package batches
- Verify stock updates
- Test gyle number generation
- Verify traceability

### PHASE 4: Duty Calculator (Week 7)
**Goal:** HMRC-compliant duty calculations at packaging

**Why This Phase Here:**
Duty is calculated at the **duty point** (packaging time). Phase 3 packages batches, so Phase 4 must immediately calculate duty. This ensures batch records include duty amounts from the start and allows proper end-to-end testing of the brewing workflow.

**Deliverables:**
- Duty calculation engine (£4.87/HL SPR method)
- SPR rate configuration
- Container duty volumes (Firkin = 39.8L, Pin = 20.0L, etc.)
- **Duty calculation integrated into packaging workflow**
- Batch-level duty calculation
- Monthly duty return generation
- Duty reports
- Duty payment tracking

**Testing:**
- Package a batch → verify duty auto-calculates
- Verify duty calculations (compare to Excel - must match exactly!)
- Test with various ABV ranges
- Test draught vs non-draught containers
- Test SPR application
- Generate monthly returns
- Verify rounding (always down to nearest penny)

### PHASE 5: CRM & Sales Tools (Week 8)
**Goal:** Customer management and sales support

**Deliverables:**
- Customer database UI
- Customer profile pages
- Calendar/diary
- Call logging
- Task management
- Sales pipeline
- Integration between tools

**Testing:**
- Add/edit customers
- Schedule events
- Log calls
- Create tasks
- Manage opportunities
- Test cross-module links

### PHASE 6: Sales, Dispatch, & Invoicing (Weeks 9-10)
**Goal:** Sales recording and financial management

**Deliverables:**
- Sales entry UI (two-stage workflow)
- Reserved orders list
- Mark as delivered functionality
- Stock depletion on delivery
- Invoice generation (from sales)
- Manual invoice creation
- Invoice list views
- Payment recording
- Customer balance tracking
- Aged debt report

**Testing:**
- Record sales (reserve)
- Mark as delivered
- Verify stock updates
- Generate invoices
- Record payments
- Test payment status updates
- Verify customer balances
- Generate aged debt report

### PHASE 7: Label Printing (Week 11)
**Goal:** Professional cask labels

**Deliverables:**
- Label design templates
- Label generator (PIL/Pillow)
- Label customization UI
- Print functionality
- PDF export
- Logo upload feature

**Testing:**
- Generate labels
- Test various templates
- Print to actual label printer
- Export to PDF
- Verify all required info included

### PHASE 8: Reports & Exports (Week 12)
**Goal:** Comprehensive reporting

**Deliverables:**
- All standard reports (see Reporting Requirements section)
- PDF generation for reports
- Excel export functionality
- QuickBooks export
- Report filters and sorts
- Report scheduling (optional)

**Testing:**
- Generate all report types
- Test filters and date ranges
- Verify calculations
- Test exports (PDF, Excel)
- QuickBooks import test

### PHASE 9: Polish & Refinement (Weeks 13-14)
**Goal:** User experience improvements

**Deliverables:**
- Dashboard with key metrics
- Search functionality
- Keyboard shortcuts
- Help system (tooltips, user guide)
- Error message improvements
- Performance optimization
- UI consistency pass
- Icon and color refinement

**Testing:**
- Usability testing
- Performance testing
- Visual consistency check
- Help system review

### PHASE 10: Testing & Documentation (Weeks 15-16)
**Goal:** Ensure quality and prepare for deployment

**Deliverables:**
- Comprehensive testing (all modules)
- Bug fixes
- User manual (PDF)
- Quick start guide
- Video tutorials (optional)
- Installer creation
- Deployment instructions

**Testing:**
- Full system testing
- Integration testing
- Edge case testing
- User acceptance testing (with brewery team)

### PHASE 11: Deployment & Training (Week 17)
**Goal:** Launch the system

**Deliverables:**
- Installer distributed
- Installation on all brewery computers
- Data migration (from Excel)
- User training sessions
- Go-live support
- Post-launch monitoring

**Activities:**
- Install on production machines
- Migrate existing data
- Train all users (by role)
- Monitor first week closely
- Gather feedback
- Quick fixes if needed

---

## TESTING STRATEGY

### Testing Levels

#### 1. UNIT TESTING
**What:** Test individual functions/methods in isolation

**Examples:**
- Duty calculation functions
- Pricing logic
- Validation rules
- Date calculations

**Tools:** unittest (Python built-in)

**Coverage Goal:** 80%+ for business logic

#### 2. INTEGRATION TESTING
**What:** Test interactions between modules

**Examples:**
- Batch creation → Inventory depletion
- Sale delivery → Stock update → Invoice eligibility
- Payment recording → Customer balance update
- Google Sheets sync ↔ Local cache

**Approach:** Automated scripts + manual verification

#### 3. SYSTEM TESTING
**What:** Test complete workflows end-to-end

**Examples:**
- Complete brewing workflow (create batch → package → print labels)
- Complete sales workflow (reserve → deliver → invoice → payment)
- Complete duty workflow (batches → monthly return → payment)

**Approach:** Manual testing with test cases

#### 4. USER ACCEPTANCE TESTING (UAT)
**What:** Real users test in real scenarios

**Who:** Brewery team members

**Approach:**
- Provide test scenarios
- Users perform tasks
- Collect feedback
- Prioritize issues

**Duration:** 1-2 weeks before go-live

### Test Data

**Create Realistic Test Data:**
- 10-15 test recipes
- 20-30 test batches (various stages)
- 15-20 test customers
- 50+ test sales
- 20+ test invoices

**Data Sources:**
- Mock data generator
- Anonymized real data (from Excel)

### Key Test Cases

**Critical Scenarios to Test:**

1. **Stock Depletion:**
   - Create batch → Verify ingredients deducted
   - Package batch → Verify empty casks deducted
   - Deliver sale → Verify finished goods deducted

2. **Duty Calculations:**
   - Various ABV values (3.5%, 5%, 8.4%, 8.5%)
   - Draught vs non-draught
   - With SPR vs without
   - Rounding verification (always down)

3. **Financial Accuracy:**
   - Invoice totals (subtotal + VAT)
   - Payment allocation
   - Outstanding balance calculation
   - Aged debt categorization

4. **Traceability:**
   - Ingredients → Batch → Casks → Sale → Invoice → Customer
   - Complete audit trail verification

5. **Sync Behavior:**
   - Create data online → Verify in Google Sheets
   - Create data offline → Go online → Verify sync
   - Modify same record on two devices → Verify conflict resolution

6. **User Permissions:**
   - Test each role can access appropriate modules
   - Test restrictions work (brewers can't invoice, sales can't view duty, etc.)

### Bug Tracking

**System:** GitHub Issues or Trello board

**Priority Levels:**
- **P0 - Critical:** Blocks core functionality, immediate fix
- **P1 - High:** Major feature broken, fix ASAP
- **P2 - Medium:** Minor feature issue, fix before release
- **P3 - Low:** Nice-to-have, fix if time permits

### Performance Testing

**Metrics:**
- Application startup time (< 5 seconds target)
- Screen load time (< 2 seconds)
- Sync time for 1000 records (< 30 seconds)
- Report generation time (< 10 seconds)

**Load Testing:**
- Test with large datasets (1000+ batches, 500+ customers)
- Ensure responsive at scale

---

## DEPLOYMENT & TRAINING

### Deployment Plan

#### PRE-DEPLOYMENT (Week 16)

**1. Installer Creation**
- Build .exe with PyInstaller
- Create installer with Inno Setup
- Include:
  - Application executable
  - Required DLL files (if any)
  - Assets (logo, icons)
  - Default configuration file
  - User manual PDF

**2. System Requirements Check**
- Verify brewery computers meet requirements:
  - Windows 10/11
  - 4 GB RAM minimum
  - 500 MB disk space
  - Internet connection (for Google Sheets sync)

**3. Google Account Setup**
- Create dedicated Google account for brewery (if not exists)
- Enable Google Sheets API
- Generate API credentials
- Share with development team for initial setup

**4. Data Migration Plan**
- Export all data from Excel
- Clean and format data
- Prepare import scripts
- Map Excel columns to new system fields

#### DEPLOYMENT DAY (Week 17, Day 1)

**1. Install Application (All Computers)**
- Run installer on each computer
- Grant necessary permissions
- Verify installation successful

**2. Initial Setup**
- Launch application
- Connect to Google account
- Authorize access to Google Sheets
- Application creates master workbook

**3. Configure System Settings**
- Enter brewery details (name, address, VAT number, logo)
- Set annual production for SPR
- Configure pricing (default prices for each cask type)
- Upload brewery logo

**4. Migrate Data**
- Import recipes from Excel
- Import customer list
- Import current inventory levels
- Import active batches (in-progress)
- Import outstanding invoices
- Verify all data migrated correctly

**5. Create Users**
- Admin creates user accounts for each team member
- Assign roles (admin/brewer/office/sales)
- Distribute login credentials

#### POST-DEPLOYMENT (Week 17, Days 2-7)

**1. Parallel Running (Recommended)**
- Run new system alongside Excel for 1 week
- Enter data in both systems
- Compare results daily
- Builds confidence before full switchover

**2. Go-Live Support**
- Developer available (remote or on-site)
- Quick response to issues
- Daily check-ins with users

**3. Feedback Collection**
- Daily feedback sessions
- Track issues in bug tracker
- Prioritize and fix critical issues immediately

### Training Plan

#### TRAINING MATERIALS

**1. User Manual (PDF, ~50 pages)**
- Overview of system
- Getting started guide
- Module-by-module instructions
- Screenshots and examples
- FAQ section
- Troubleshooting guide

**2. Quick Reference Guides (1-2 pages each)**
- Common tasks cheat sheet
- Keyboard shortcuts
- How to: Create batch
- How to: Record sale
- How to: Generate invoice
- How to: Print labels

**3. Video Tutorials (Optional, 5-10 min each)**
- System overview
- Brewing workflow
- Sales workflow
- Invoicing workflow

#### TRAINING SESSIONS

**Session 1: Overview for Everyone (1 hour)**
- **Audience:** All users
- **Content:**
  - System overview and benefits
  - Navigation and interface basics
  - Logging in/out
  - Sync status and offline mode
  - Getting help
- **Format:** Group presentation

**Session 2: Brewing & Production (2 hours)**
- **Audience:** Brewers, Admin
- **Content:**
  - Recipe management
  - Creating batches
  - Logging fermentation data
  - Packaging workflow
  - Printing labels
  - Hands-on practice
- **Format:** Workshop with guided exercises

**Session 3: Sales & Customers (2 hours)**
- **Audience:** Office, Sales, Admin
- **Content:**
  - Customer management
  - Sales tools (calendar, calls, tasks)
  - Recording sales (two-stage workflow)
  - Hands-on practice
- **Format:** Workshop with guided exercises

**Session 4: Invoicing & Payments (1.5 hours)**
- **Audience:** Office, Admin
- **Content:**
  - Generating invoices
  - Recording payments
  - Customer statements
  - Reports (aged debt, etc.)
  - Hands-on practice
- **Format:** Workshop with guided exercises

**Session 5: Duty Calculations (1 hour)**
- **Audience:** Office, Admin
- **Content:**
  - How duty is calculated
  - Monthly duty returns
  - Exporting for HMRC
  - Hands-on practice
- **Format:** Workshop with guided exercises

**Session 6: Q&A and Advanced Topics (1 hour)**
- **Audience:** All users (optional attendance)
- **Content:**
  - Answer outstanding questions
  - Advanced tips and tricks
  - Report customization
  - Future enhancements
- **Format:** Open discussion

#### ONGOING SUPPORT

**1. Internal Champion**
- Designate one "super user" (likely Admin)
- They become go-to person for questions
- Developer trains champion more deeply

**2. Documentation**
- Keep user manual updated
- Create FAQ based on common questions
- Maintain internal wiki or shared document

**3. Developer Support**
- Month 1: Daily availability
- Month 2: Weekly check-ins
- Month 3+: On-demand support (email/phone)

**4. Version Updates**
- Bug fixes released as needed
- Feature enhancements released quarterly (after initial release)
- Update notification in application
- Automatic update download (if possible)

---

## APPENDICES

### APPENDIX A: Glossary

**ABV (Alcohol By Volume):** Percentage of alcohol in beer

**Batch:** A single brewing run producing a specific quantity of beer

**Cask:** Large container (typically 20L+) for draught beer

**Draught Relief:** UK duty discount for beer in containers ≥20L

**Duty Point:** The moment when alcohol duty becomes payable (packaging date)

**Firkin:** Traditional cask size (9 gallons / 40.9 litres)

**Gyle Number:** Unique identifier for each batch (e.g., GYLE-2025-042)

**Hectolitre (hL):** 100 litres (common unit for production volumes)

**HMRC:** Her Majesty's Revenue and Customs (UK tax authority)

**Kilderkin:** Traditional cask size (18 gallons / 81.8 litres)

**Pin:** Smallest traditional cask size (4.5 gallons / 20.5 litres)

**Pure Alcohol:** Alcohol content measured in litres (volume × ABV)

**SPR (Small Producer Relief):** UK duty discount for small breweries

**VAT:** Value Added Tax (20% in UK)

### APPENDIX B: UK Duty Rates Reference

**See separate document:** `UK_ALCOHOL_DUTY_REFERENCE.md`

Includes:
- Current duty rates (Feb 2025)
- SPR lookup tables
- Calculation examples
- HMRC compliance notes

### APPENDIX C: Container Size Reference

| Container Type | Size (Litres) | Size (Gallons) | Draught Eligible? |
|----------------|---------------|----------------|-------------------|
| Pin | 20.5 | 4.5 | Yes (≥20L) |
| Firkin | 40.9 | 9 | Yes |
| Kilderkin | 81.8 | 18 | Yes |
| 30L Keg | 30 | 6.6 | Yes |
| 50L Keg | 50 | 11 | Yes |
| Party Tin (variable) | Typically 20-30 | 4.4-6.6 | Yes (if ≥20L) |
| Bottle (500ml) | 0.5 | 0.11 | No |
| Bottle (330ml) | 0.33 | 0.07 | No |

### APPENDIX D: System Settings Reference

Key settings stored in `System_Settings` sheet:

| Setting Key | Type | Description | Example Value |
|-------------|------|-------------|---------------|
| `brewery_name` | Text | Brewery name | "Tonk's Brewery" |
| `brewery_address` | Text | Full address | "123 Brewery Lane..." |
| `vat_number` | Text | VAT registration | "GB123456789" |
| `annual_production_hectolitres` | Number | For SPR calculation | 8.79 |
| `is_small_producer` | Boolean | SPR eligible? | true |
| `spr_discount_per_litre` | Number | Current SPR rate | 0.0487 |
| `production_year_start` | Date | Feb 1 | 2025-02-01 |
| `production_year_end` | Date | Jan 31 | 2026-01-31 |
| `next_gyle_number` | Number | Auto-increment | 43 |
| `next_invoice_number` | Number | Auto-increment | 157 |
| `default_payment_terms` | Text | For new customers | "net_14" |
| `low_stock_alert_days` | Number | Dashboard alert | 7 |

### APPENDIX E: Keyboard Shortcuts (Planned)

| Shortcut | Action |
|----------|--------|
| Ctrl+N | New (context-aware: new batch, new sale, etc.) |
| Ctrl+S | Save current form |
| Ctrl+F | Search |
| Ctrl+P | Print current view/report |
| Ctrl+R | Refresh/Sync |
| F1 | Help |
| Ctrl+Q | Quit application |
| Ctrl+1 to Ctrl+9 | Jump to module (1=Dashboard, 2=Recipes, etc.) |
| Esc | Close dialog/cancel |

---

## END OF SPECIFICATION

**Document Version:** 1.0  
**Date:** November 5, 2025  
**Status:** Final  
**Next Steps:** Begin Phase 1 development upon approval

**For Questions or Clarifications:**
Contact project stakeholders or development team.

---

**APPROVAL SIGNATURES:**

_______________________________  
Brewery Owner / Manager

Date: _______________

_______________________________  
Development Lead

Date: _______________
