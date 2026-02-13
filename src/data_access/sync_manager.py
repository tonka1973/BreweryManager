"""
Sync Manager for Brewery Management System
Handles synchronization between local SQLite cache and Google Sheets
"""

import logging
import time
import socket
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from ..config.constants import (
    TABLES,
    CONNECTION_TIMEOUT_SECONDS,
    SYNC_INTERVAL_SECONDS,
    DATETIME_FORMAT
)

PRIMARY_KEYS = {
    "recipes": "recipe_id",
    "recipe_ingredients": "ingredient_id",
    "recipe_grains": "grain_id",
    "recipe_hops": "hop_id",
    "recipe_yeast": "yeast_id",
    "recipe_adjuncts": "adjunct_id",
    "inventory_materials": "material_id",
    "inventory_transactions": "transaction_id",
    "casks_empty": "cask_id",
    "batches": "batch_id",
    "fermentation_logs": "log_id",
    "casks_full": "cask_record_id",
    "bottles_stock": "bottle_record_id",
    "customers": "customer_id",
    "sales_calendar": "event_id",
    "call_log": "call_id",
    "tasks": "task_id",
    "sales_pipeline": "opportunity_id",
    "sales": "sale_id",
    "invoices": "invoice_id",
    "invoice_lines": "line_id",
    "payments": "payment_id",
    "duty_returns": "return_id",
    "duty_return_lines": "line_id",
    "pricing": "price_id",
    "customer_pricing_overrides": "override_id",
    "users": "user_id",
    "system_settings": "setting_key",
    "container_types": "container_type_id",
    "products": "product_id",
    "product_sales": "product_sale_id",
    "batch_packaging_lines": "line_id",
    "spoilt_beer": "id",
    "cans_empty": "can_id",
    "bottles_empty": "bottle_id",
    "settings_containers": "container_id",
    "settings": "id"
}

logger = logging.getLogger(__name__)


class SyncManager:
    """
    Manages synchronization between local SQLite database and Google Sheets.
    Handles online/offline detection, sync strategies, and conflict resolution.
    """
    
    def __init__(self, sheets_client, cache_manager):
        """
        Initialize the sync manager.
        
        Args:
            sheets_client: GoogleSheetsClient instance
            cache_manager: SQLiteCacheManager instance
        """
        self.sheets_client = sheets_client
        self.cache = cache_manager
        self.is_online = False
        self.last_sync_time = None
        self.sync_in_progress = False
        self.auth_in_progress = False
        
    def initialize(self):
        """
        Initialize sync state, persistence, and bootstrap if needed.
        Should be called after initialization.
        """
        try:
            # 1. Try to load spreadsheet ID from local DB (works offline)
            if not self.sheets_client.spreadsheet_id:
                self.cache.connect()
                try:
                    setting = self.cache.get_record('system_settings', 'spreadsheet_id', 'setting_key')
                    
                    if setting:
                        # ID exists in DB -> use it
                        stored_id = setting.get('setting_value')
                        
                        # VALIDATE: Check if this sheet actually exists (Self-Healing)
                        # If user deleted it cloud-side, we need to know so we can recreate it.
                        if self.check_connection():
                            try:
                                # Start with a lightweight check (e.g., read metadata)
                                self.sheets_client.spreadsheet_id = stored_id
                                # Just try to read metadata or first sheet titles
                                self.sheets_client.service.spreadsheets().get(spreadsheetId=stored_id).execute()
                                logger.info(f"Loaded and validated spreadsheet ID: {stored_id}")
                            except Exception as e:
                                error_str = str(e)
                                if "404" in error_str or "not found" in error_str.lower():
                                    logger.warning(f"Spreadsheet {stored_id} not found on server (Deleted?). Clearing local ID to force recreation.")
                                    # Clear invalid ID so we enter the creation block below
                                    self.sheets_client.spreadsheet_id = None
                                    # Optional: Delete from DB so next boot is clean if we crash now
                                    self.cache.delete_record('system_settings', 'spreadsheet_id', 'setting_key')
                                else:
                                    # Other error (auth/internet), keep the ID but maybe log warning
                                    self.sheets_client.spreadsheet_id = stored_id
                                    logger.warning(f"Could not validate sheet (Error: {e}), but keeping ID: {stored_id}")
                        else:
                             # Offline: Trust the stored ID
                             self.sheets_client.spreadsheet_id = stored_id
                             logger.info(f"Offline: Trusted stored spreadsheet ID: {stored_id}")

                    # Load last sync time
                    sync_setting = self.cache.get_record('system_settings', 'last_full_sync', 'setting_key')
                    if sync_setting:
                        self.last_sync_time = sync_setting.get('setting_value')
                        logger.info(f"Loaded last sync time: {self.last_sync_time}")
                finally:
                    self.cache.close()

            # 2. If no ID found (or cleared because it was deleted), try to create new spreadsheet
            if not self.sheets_client.spreadsheet_id:
                if self.check_connection():
                    logger.info("No valid spreadsheet ID found and Online. Creating new spreadsheet...")
                    # Generate a name based on Winery/User or just generic
                    new_id = self.sheets_client.create_spreadsheet(title=f"Brewery_Manager_Data_{datetime.now().strftime('%Y%m%d')}")
                    
                    if new_id:
                        # Save to DB
                        self._update_system_setting('spreadsheet_id', new_id)
                        logger.info(f"Created and saved new spreadsheet ID: {new_id}")
                        
                        # TRIGGER BOOTSTRAP: Push all local data to the new sheet
                        # This restores the cloud copy from our local "Master"
                        self.bootstrap_sync()
                else:
                     logger.warning("No spreadsheet ID found and Offline. Cannot create sync sheet.")

        except Exception as e:
            logger.error(f"Error during sync initialization: {e}")
            # Ensure cache is closed if it was left open
            if self.cache.connection:
                self.cache.close()

    def check_connection(self) -> bool:
        """
        Check if we have internet connectivity.
        Tries DNS first, then HTTP fallback.
        
        Returns:
            True if online, False if offline
        """
        try:
            # 1. Try fast DNS socket check
            socket.create_connection(
                ("8.8.8.8", 53),
                timeout=CONNECTION_TIMEOUT_SECONDS
            )
            self.is_online = True
            
            # If we are online but not authenticated, try again
            # Use a lock-flag to prevent multiple threads from triggering auth at once (Signin Loop Fix)
            if not self.sheets_client.is_authenticated and not self.auth_in_progress:
                try:
                    self.auth_in_progress = True
                    logger.info("Connection available but not authenticated. Attempting re-auth...")
                    self.sheets_client.authenticate()
                finally:
                    self.auth_in_progress = False

            return True
        except OSError:
            # 2. Fallback to HTTP check (can be slower but more robust)
            try:
                import urllib.request
                urllib.request.urlopen('http://google.com', timeout=CONNECTION_TIMEOUT_SECONDS)
                self.is_online = True
                
                # If we are online but not authenticated, try again
                if not self.sheets_client.is_authenticated and not self.auth_in_progress:
                   try:
                       self.auth_in_progress = True
                       self.sheets_client.authenticate()
                   finally:
                       self.auth_in_progress = False

                return True
            except:
                self.is_online = False
                return False

    def bootstrap_sync(self):
        """
        Perform initial upload of ALL local data to a fresh spreadsheet.
        """
        logger.info("Starting BOOTSTRAP SYNC (Initial Upload)...")
        try:
            self.cache.connect()
            
            for table_key, table_name in TABLES.items():
                try:
                    # Get all records for this table
                    records = self.cache.get_all_records(table_key)
                    if not records:
                        continue
                        
                    logger.info(f"Bootstrapping {len(records)} records for {table_name}")
                    
                    # Get headers from first record or schema
                    if records:
                        # Use keys from first record as basis
                        # ideally we should use schema definition to be safe
                        headers = list(records[0].keys()) 
                        # Note: create_spreadsheet usually initializes headers.
                        # We just need to ensure values align with those headers.
                        # For simplicity in Phase 1, we assume dict iteration order matches
                        # (Python 3.7+ guarantees insertion order)
                    
                    # Prepare batch of rows
                    rows_to_append = []
                    for record in records:
                        rows_to_append.append(list(record.values()))
                        
                        # Update local sync status
                        pk = PRIMARY_KEYS.get(table_key, 'id')
                        record_id = record.get(pk)
                        
                        if record_id:
                             self.cache.update_record(
                                table_key, 
                                record_id, 
                                {'sync_status': 'synced'},
                                id_column=pk
                            )
                    
                    # We can use append_row in a loop, or implement batch_append in client
                    # For now, looping append_row is safer/easier implemented even if slower
                    sheets_table = TABLES.get(table_key)
                    
                    # Better: Implement batch append if list is huge, but let's stick to 
                    # row-by-row or small chunks if we didn't add batch_append yet.
                    # Actually, let's just loop for now.
                    for row in rows_to_append:
                        self.sheets_client.append_row(sheets_table, row)
                        
                    logger.info(f"Bootstrapped {table_name} successfully.")
                    
                except Exception as e:
                    logger.error(f"Error bootstrapping {table_name}: {e}")
            
            self.cache.close()
            logger.info("Bootstrap Sync Completed.")
            
        except Exception as e:
            logger.error(f"Bootstrap sync failed: {e}")
            if self.cache: self.cache.close()
    
    def full_sync_from_sheets(self) -> Dict[str, int]:
        """
        Perform a full sync from Google Sheets to local SQLite.
        This is typically done on initial setup or after being offline.
        
        Returns:
            Dictionary with sync results per table
        """
        if not self.check_connection():
            logger.error("Cannot sync: No internet connection")
            return {"error": "offline"}
        
        if self.sync_in_progress:
            logger.warning("Sync already in progress")
            return {"error": "sync_in_progress"}
        
        self.sync_in_progress = True
        sync_results = {}
        
        try:
            self.cache.connect()
            
            # Sync each table
            for table_key, table_name in TABLES.items():
                try:
                    logger.info(f"Syncing table: {table_name}")
                    
                    # Read all data from Google Sheets
                    data = self.sheets_client.read_sheet(table_name)
                    
                    if not data:
                        sync_results[table_name] = 0
                        continue
                    
                    # Clear existing data in table
                    self.cache.cursor.execute(f"DELETE FROM {table_key}")
                    
                    # Insert all records
                    headers = data[0]
                    records_synced = 0
                    
                    for row in data[1:]:
                        if row:  # Skip empty rows
                            record_dict = dict(zip(headers, row))
                            record_dict['sync_status'] = 'synced'
                            self.cache.insert_record(table_key, record_dict)
                            records_synced += 1
                    
                    sync_results[table_name] = records_synced
                    logger.info(f"Synced {records_synced} records from {table_name}")
                    
                except Exception as e:
                    logger.error(f"Failed to sync {table_name}: {str(e)}")
                    sync_results[table_name] = f"error: {str(e)}"
            
            # Update last sync time
            self.last_sync_time = datetime.now().strftime(DATETIME_FORMAT)
            self._update_system_setting('last_full_sync', self.last_sync_time)
            
            logger.info(f"Full sync completed: {sync_results}")
            return sync_results
            
        except Exception as e:
            logger.error(f"Full sync failed: {str(e)}")
            return {"error": str(e)}
        finally:
            self.sync_in_progress = False
            self.cache.close()
    
    def sync_local_changes_to_sheets(self) -> Dict[str, int]:
        """
        Sync all pending local changes to Google Sheets.
        This is called when coming back online or on manual sync.
        
        Returns:
            Dictionary with sync results
        """
        if not self.check_connection():
            logger.error("Cannot sync: No internet connection")
            return {"error": "offline"}
        
        try:
            self.cache.connect()
            
            # Get all pending syncs from cache
            pending_syncs = self.cache.get_pending_syncs()
            
            if not pending_syncs:
                logger.info("No pending syncs")
                return {"pending": 0}
            
            synced_count = 0
            failed_count = 0
            
            for table_name, record in pending_syncs:
                try:
                    # Get the Google Sheets table name
                    sheets_table = TABLES.get(table_name)
                    if not sheets_table:
                        continue
                    
                    # Convert record dict to list for Google Sheets
                    # Note: We need to ensure the order matches headers. 
                    # Ideally, we should read headers first or store schema order.
                    # For now, assuming dict values turn into list in correct order is RISKY if python < 3.7 or dict modified
                    # Robust way: Read header from sheet or config, then map.
                    # As a safe fallback for this phase, we'll just use values() but TODO: Order by schema
                    values = list(record.values())

                    # Check if record exists in Google Sheets to decide Update vs Append
                    pk = PRIMARY_KEYS.get(table_name, 'id')
                    record_id = record.get(pk) or record.get('id')
                    
                    # Try to find row index (using first column as ID usually)
                    row_index = None
                    try:
                        row_index = self.sheets_client.find_row_index(sheets_table, record_id)
                    except Exception as e:
                        logger.warning(f"Failed to find row index: {e}")
                        row_index = None
                    
                    if row_index:
                        # UPDATE existing row
                        self.sheets_client.update_row(sheets_table, row_index, values)
                        logger.info(f"Updated record {record_id} in {table_name} at row {row_index}")
                    else:
                        # APPEND new row
                        self.sheets_client.append_row(sheets_table, values)
                        logger.info(f"Appended new record {record_id} to {table_name}")
                    
                    # Mark as synced in local cache
                    # Mark as synced in local cache
                    pk = PRIMARY_KEYS.get(table_name, 'id')
                    self.cache.update_record(
                        table_name, 
                        record_id, 
                        {'sync_status': 'synced'},
                        id_column=pk
                    )
                    
                    synced_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to sync record from {table_name}: {str(e)}")
                    failed_count += 1
            
            logger.info(f"Synced {synced_count} records, {failed_count} failed")
            return {
                "synced": synced_count,
                "failed": failed_count
            }
            
        except Exception as e:
            logger.error(f"Failed to sync local changes: {str(e)}")
            return {"error": str(e)}
        finally:
            self.cache.close()
    
    def incremental_sync(self) -> Dict[str, any]:
        """
        Perform an incremental sync - only sync changed records.
        This is more efficient than full sync.
        
        Returns:
            Dictionary with sync results
        """
        if not self.check_connection():
            return {"error": "offline"}
        
        if self.sync_in_progress:
            logger.warning("Sync already in progress")
            return {"error": "sync_in_progress"}

        self.sync_in_progress = True
        
        try:
            # First, push any local changes to sheets
            push_result = self.sync_local_changes_to_sheets()
            
            # Then, pull any changes from sheets
            pulled_count = 0
            
            # If we don't have a last sync time, we can't do incremental (or treat as full sync?)
            # For now, rely on last_sync_time. If None, arguably should do full sync, 
            # but let's just default to a very old date or skip.
            last_sync = self.last_sync_time or "2000-01-01 00:00:00"

            self.cache.connect()
            
            for table_key, table_name in TABLES.items():
                try:
                    # RATE LIMIT: Sleep 0.2 seconds between table reads to avoid 429 errors
                    time.sleep(0.2)
                    
                    try:
                        sheets_data = self.sheets_client.read_sheet(table_name)
                    except Exception as e:
                        logger.error(f"Failed to read sheet {table_name}: {e}")
                        sheets_data = []

                    if not sheets_data: 
                        continue
                        
                    headers = sheets_data[0]
                    # Find 'last_modified' index if it exists in headers
                    try:
                        lm_index = headers.index('last_modified')
                    except ValueError:
                        # Table has no last_modified tracking, skip incremental pull for it
                        continue

                    # Check each row
                    for row in sheets_data[1:]:
                        if len(row) > lm_index:
                            row_time = row[lm_index]
                            
                            # If row modified after last sync
                            if row_time > last_sync:
                                record_dict = dict(zip(headers, row))
                                pk = PRIMARY_KEYS.get(table_key, 'id')
                                record_id = record_dict.get(pk) or list(record_dict.values())[0]
                                
                                # Check local version for conflict
                                local_record = self.cache.get_record(table_key, record_id, id_column=pk)
                                
                                if local_record:
                                    # Conflict Resolution
                                    resolution = self.resolve_conflicts(local_record, record_dict)
                                    if resolution == record_dict:
                                        # Remote wins
                                        pk = PRIMARY_KEYS.get(table_key, 'id')
                                        self.cache.update_record(table_key, record_id, record_dict, id_column=pk)
                                        pulled_count += 1
                                else:
                                    # New record from remote
                                    self.cache.insert_record(table_key, record_dict)
                                    pulled_count += 1
                                    
                except Exception as e:
                    logger.error(f"Error pulling from {table_name}: {e}")
                    # If rate limit hit (429), pause longer
                    if "429" in str(e):
                         time.sleep(10)

            self.last_sync_time = datetime.now().strftime(DATETIME_FORMAT)
            self._update_system_setting('last_full_sync', self.last_sync_time)
            
            return {
                "pushed": push_result,
                "pulled": pulled_count,
                "last_sync": self.last_sync_time
            }
            
        except Exception as e:
            logger.error(f"Incremental sync failed: {str(e)}")
            return {"error": str(e)}
        finally:
            self.sync_in_progress = False
    
    def auto_sync_if_online(self) -> bool:
        """
        Check if online and perform incremental sync if so.
        This can be called periodically in the background.
        
        Returns:
            True if sync was performed, False otherwise
        """
        if self.check_connection() and not self.sync_in_progress:
            result = self.incremental_sync()
            return "error" not in result
        return False
    
    def manual_sync(self) -> Dict[str, any]:
        """
        Manually trigger a sync.
        User can call this from UI.
        
        Returns:
            Dictionary with sync results
        """
        logger.info("Manual sync triggered")
        return self.incremental_sync()
    
    def get_sync_status(self) -> Dict[str, any]:
        """
        Get current sync status for display in UI.
        
        Returns:
            Dictionary with sync status information
        """
        try:
            self.cache.connect()
            pending_count = len(self.cache.get_pending_syncs())
            self.cache.close()
            
            return {
                "is_online": self.is_online,
                "last_sync": self.last_sync_time or "Never",
                "pending_syncs": pending_count,
                "sync_in_progress": self.sync_in_progress
            }
        except Exception as e:
            logger.error(f"Failed to get sync status: {str(e)}")
            return {
                "is_online": self.is_online,
                "last_sync": "Unknown",
                "pending_syncs": 0,
                "error": str(e)
            }

    def sync_all(self):
        """
        Wrapper for incremental_sync to match interface expected by UI.
        """
        return self.incremental_sync()

    def get_last_sync_time(self) -> Optional[str]:
        """
        Get the timestamp of the last successful sync.
        """
        return self.last_sync_time
        
    def _update_system_setting(self, key: str, value: str):
        """
        Update a system setting in the database.
        
        Args:
            key: Setting key
            value: Setting value
        """
        try:
            self.cache.connect()
            
            # Check if setting exists
            existing = self.cache.get_record('system_settings', key, 'setting_key')
            
            setting_data = {
                'setting_key': key,
                'setting_value': value,
                'last_updated': datetime.now().strftime(DATETIME_FORMAT),
                'sync_status': 'synced'
            }
            
            if existing:
                self.cache.update_record('system_settings', key, setting_data, 'setting_key')
            else:
                self.cache.insert_record('system_settings', setting_data)
            
            self.cache.close()
            
        except Exception as e:
            logger.error(f"Failed to update system setting: {str(e)}")
    
    def resolve_conflicts(self, local_record: Dict, remote_record: Dict, table_name: str) -> Dict:
        """
        Resolve conflicts based on table type (Hybrid Strategy).
        
        Strategies:
        1. SERVER_WINS (First-Past-The-Post): For Sales, Inventory, Finance.
           - Prevents overwriting valid transactions.
           - If server has changed, we assume our local view was stale.
           
        2. NEWER_WINS (Last-Post): For Readings, Logs, Notes.
           - The latest data is always the truth.
           - Corrects mistakes or adds newer readings.
           
        Args:
            local_record: Local record from SQLite
            remote_record: Remote record from Google Sheets
            table_name: Name of the table to determine strategy
        
        Returns:
            The record that should be kept
        """
        # Defines tables that need "Newer Wins" (Last Post)
        # All others default to "Server Wins" (First Past Post) for safety
        NEWER_WINS_TABLES = [
            'fermentation_logs', 
            'batches',            # Batches often get updated statuses/readings
            'recipes',            # Developing recipes usually wants latest version
            'tasks',              # Latest status update matters
            'call_log',           # Latest notes matter
            'settings',
            'system_settings'
        ]

        local_time = local_record.get('last_modified', '')
        remote_time = remote_record.get('last_modified', '')
        
        # 1. Handle missing timestamps (Fail safe)
        if not local_time and remote_time: return remote_record
        if local_time and not remote_time: return local_record # Trust local if remote is untracked
        
        # 2. Compare Timestamps
        if local_time and remote_time:
            
            # STRATEGY 1: NEWER WINS (Last Post)
            # Used for: Readings, Statuses, Notes
            if table_name in NEWER_WINS_TABLES:
                if local_time > remote_time:
                    logger.info(f"Conflict ({table_name}): KEEPING LOCAL (Strategy: Newer Wins)")
                    return local_record
                else:
                    logger.info(f"Conflict ({table_name}): KEEPING REMOTE (Strategy: Newer Wins)")
                    return remote_record
            
            # STRATEGY 2: SERVER WINS (First Past The Post)
            # Used for: Sales, Invoices, Stock Levels (Critical Transactions)
            else:
                if local_time > remote_time:
                     # Even if local is newer, we respect the server's version to prevent
                     # overwriting a transaction we might not have seen.
                    logger.info(f"Conflict ({table_name}): KEEPING REMOTE (Strategy: Server Wins/Safety)")
                    return remote_record
                else:
                    return remote_record

        # Default fallback
        return remote_record

    def incremental_sync(self) -> Dict[str, any]:
        """
        Perform an incremental sync - only sync changed records.
        This is more efficient than full sync.
        
        ORDER: PULL THEN PUSH (Optimistic Locking approximation).
        We get latest changes first. If conflicts arise, 'Server Wins' logic (in resolve_conflicts)
        will update our local DB. Then we push any remaining non-conflicting local changes.
        
        Returns:
            Dictionary with sync results
        """
        if not self.check_connection():
            return {"error": "offline"}
        
        if self.sync_in_progress:
            logger.warning("Sync already in progress")
            return {"error": "sync_in_progress"}

        self.sync_in_progress = True
        
        try:
            # 1. PULL: Get latest changes from Sheets
            pulled_count = 0
            
            last_sync = self.last_sync_time or "2000-01-01 00:00:00"

            self.cache.connect()
            
            for table_key, table_name in TABLES.items():
                try:
                    # RATE LIMIT: Sleep 0.2 seconds between table reads to avoid 429 errors
                    time.sleep(0.2)
                    
                    try:
                        sheets_data = self.sheets_client.read_sheet(table_name)
                    except Exception as e:
                        logger.error(f"Failed to read sheet {table_name}: {e}")
                        sheets_data = []

                    if not sheets_data: 
                        continue
                        
                    headers = sheets_data[0]
                    # Find 'last_modified' index if it exists in headers
                    try:
                        lm_index = headers.index('last_modified')
                    except ValueError:
                        # Table has no last_modified tracking, skip incremental pull for it
                        continue

                    # Check each row for updates
                    for row in sheets_data[1:]:
                        if len(row) > lm_index:
                            row_time = row[lm_index]
                            
                            # If row modified after last sync (Newer than when I last checked)
                            if row_time > last_sync:
                                record_dict = dict(zip(headers, row))
                                pk = PRIMARY_KEYS.get(table_key, 'id')
                                record_id = record_dict.get(pk) or list(record_dict.values())[0]
                                
                                # Check local version for conflict
                                local_record = self.cache.get_record(table_key, record_id, id_column=pk)
                                
                                if local_record:
                                    # Conflict Resolution (Pass table_key/name for strategy decision)
                                    resolution = self.resolve_conflicts(local_record, record_dict, table_key)
                                    
                                    if resolution == record_dict:
                                        # Remote wins (Update Local)
                                        pk = PRIMARY_KEYS.get(table_key, 'id')
                                        self.cache.update_record(table_key, record_id, record_dict, id_column=pk)
                                        pulled_count += 1
                                    else:
                                        # Local wins (Keep Local)
                                        # effectively we do nothing, and next Push will send our local version
                                        pass
                                else:
                                    # New record from remote
                                    self.cache.insert_record(table_key, record_dict)
                                    pulled_count += 1
                                    
                except Exception as e:
                    logger.error(f"Error pulling from {table_name}: {e}")
                    # If rate limit hit (429), pause longer
                    if "429" in str(e):
                         time.sleep(10)

            # 2. PUSH: Push local changes to sheets
            # Now that we are up to date (and conflicts resolved in favor of server), we push what's left.
            push_result = self.sync_local_changes_to_sheets()

            self.last_sync_time = datetime.now().strftime(DATETIME_FORMAT)
            self._update_system_setting('last_full_sync', self.last_sync_time)
            
            return {
                "pushed": push_result,
                "pulled": pulled_count,
                "last_sync": self.last_sync_time
            }
            
        except Exception as e:
            logger.error(f"Incremental sync failed: {str(e)}")
            return {"error": str(e)}
        finally:
            self.sync_in_progress = False
            if self.cache.connection:
                self.cache.close()
