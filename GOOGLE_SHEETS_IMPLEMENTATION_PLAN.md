# Google Sheets Sync Implementation Plan

**Status:** Prepared for implementation after Phase 3 testing

---

## Current State Analysis

### Files That Exist:
- ✅ `src/data_access/google_sheets_client.py` - Google Sheets API client
- ✅ `src/data_access/sync_manager.py` - Sync orchestration
- ✅ `src/data_access/sqlite_cache.py` - Local database cache
- ✅ `config/settings.json` - Configuration file

### What Needs to Be Done:

**Phase 1: Authentication & Connection**
1. Set up Google Cloud Project
2. Enable Google Sheets API
3. Create service account credentials
4. Store credentials securely
5. Test basic connection

**Phase 2: Schema Mapping**
1. Map database tables to Google Sheets
2. Define which tables sync (not all need to)
3. Handle data types (dates, numbers, text)
4. Field mapping documentation

**Phase 3: Sync Logic**
1. Pull from Sheets → Local DB (on startup)
2. Push from Local DB → Sheets (on changes)
3. Conflict resolution strategy
4. Offline mode handling
5. Sync status tracking

**Phase 4: Testing**
1. Test on single computer
2. Test across Brewery ↔ Home
3. Test offline scenarios
4. Test conflict scenarios

---

## Tables That Should Sync

### ✅ Core Production Data (SYNC):
- `recipes` - Beer recipes
- `batches` - Production batches
- `batch_packaging_lines` - Packaging details
- `products` - Finished goods inventory
- `customers` - Customer database
- `sales` - Sales transactions
- `invoices` - Invoice records
- `duty_returns` - HMRC duty submissions
- `spoilt_beer` - Spoilage tracking

### ❌ Local-Only Data (NO SYNC):
- `users` - User authentication (security)
- `settings` - Duty rates and containers (may differ by location)
- `settings_containers` - Container configurations
- `sync_log` - Sync history
- `inventory_materials` - Local brewery inventory (unless needed?)
- `inventory_containers` - Local container stock

### ⚠️ Maybe Sync (Discuss):
- `inventory_logbook` - Transaction history
- `recipe_ingredients` - Recipe details

---

## Sync Strategy Recommendations

### **Two-Way Sync with Timestamp-Based Conflict Resolution**

**On Startup (Pull):**
```
1. Connect to Google Sheets
2. Get last_sync_time from local config
3. Pull all records modified after last_sync_time
4. For conflicts (same record modified both places):
   - Take the newer timestamp
   - OR prompt user to choose
5. Update local database
6. Update last_sync_time
```

**On Data Change (Push):**
```
1. User creates/edits record locally
2. Mark record with sync_status = 'pending'
3. On next sync (manual or automatic):
   - Push pending records to Google Sheets
   - Update sync_status = 'synced'
   - Update timestamps
```

**Offline Mode:**
```
- All changes marked as 'pending'
- Queue builds up
- On reconnection, sync all pending changes
- Handle conflicts by timestamp
```

---

## Google Sheets Structure

### Approach 1: One Sheet per Table (Recommended)
```
Spreadsheet: "Brewery Manager Data"
  ├─ Sheet: "recipes"
  ├─ Sheet: "batches"
  ├─ Sheet: "customers"
  ├─ Sheet: "sales"
  ├─ Sheet: "products"
  └─ Sheet: "sync_metadata"
```

**Pros:** Clean, organized, easy to query
**Cons:** Many API calls to sync multiple sheets

### Approach 2: Multiple Spreadsheets
```
Spreadsheet: "Production Data"
  ├─ recipes
  └─ batches

Spreadsheet: "Sales Data"
  ├─ customers
  ├─ sales
  └─ invoices
```

**Pros:** Organized by domain
**Cons:** More complex to manage

**Recommendation: Use Approach 1 initially**

---

## Implementation Phases

### Phase A: Basic Connection (2-3 hours)
- [ ] Set up Google Cloud credentials
- [ ] Test authentication
- [ ] Read from test spreadsheet
- [ ] Write to test spreadsheet

### Phase B: Single Table Sync (3-4 hours)
- [ ] Choose simple table (e.g., customers)
- [ ] Implement pull from Sheets → Local
- [ ] Implement push from Local → Sheets
- [ ] Test on single computer

### Phase C: Full Sync (5-6 hours)
- [ ] Extend to all production tables
- [ ] Add sync_status tracking
- [ ] Implement conflict resolution
- [ ] Add sync UI (status, manual trigger)

### Phase D: Cross-Computer Testing (4-5 hours)
- [ ] Test Brewery → Home sync
- [ ] Test Home → Brewery sync
- [ ] Test offline scenarios
- [ ] Test simultaneous edits

**Total Estimated Time: 14-18 hours**

---

## Prerequisites Before Implementation

### 1. Google Cloud Setup
- [ ] Create Google Cloud Project
- [ ] Enable Google Sheets API
- [ ] Create service account
- [ ] Download credentials JSON
- [ ] Store in: `config/google_credentials.json` (add to .gitignore!)

### 2. Test Spreadsheet
- [ ] Create "Brewery Manager Data" spreadsheet
- [ ] Share with service account email
- [ ] Get spreadsheet ID
- [ ] Add to settings.json

### 3. Local Testing
- [ ] Test all current features work without sync
- [ ] Verify database is stable
- [ ] Backup database before testing sync

---

## Questions to Answer Before Implementation

1. **Sync Frequency:**
   - Manual only (user clicks "Sync Now")?
   - On app startup only?
   - Periodic (every 5 minutes)?
   - On every data change?

2. **Conflict Resolution:**
   - Always take newest timestamp?
   - Prompt user to choose?
   - Keep both versions?

3. **Initial Data:**
   - Which computer has the "master" data to start?
   - Do we need to migrate existing data to Sheets?

4. **Credentials:**
   - Service account (app has full access) - RECOMMENDED
   - OR OAuth (user logs in with Google account)

5. **Error Handling:**
   - What if sync fails?
   - Show error message?
   - Retry automatically?
   - Log errors for debugging?

---

## Testing Checklist (Before Sync Implementation)

Current features to verify work correctly:

### Recipes Module
- [ ] Create recipe with allergens
- [ ] Edit recipe
- [ ] Recipe list displays correctly

### Production Module
- [ ] Create batch
- [ ] Package batch with containers
- [ ] Print labels (PDF generates)
- [ ] F.G. entry and finalization

### Duty Module
- [ ] Duty calculations correct
- [ ] Packaging lines recorded
- [ ] Spoilt beer tracking

### Sales/Invoicing
- [ ] Record sale
- [ ] Generate invoice
- [ ] Track payments

### Reports
- [ ] All 5 report types load
- [ ] Data displays correctly

---

## Ready for Implementation?

When you finish testing and are ready to implement sync:

1. Run through testing checklist above
2. Answer the questions in "Questions to Answer" section
3. Set up Google Cloud credentials
4. Tell me you're ready, and I'll implement Phase A (Basic Connection)

---

**This document will be your guide when implementing Google Sheets sync!**
