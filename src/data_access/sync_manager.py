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
        
    def check_connection(self) -> bool:
        """
        Check if we have internet connectivity.
        
        Returns:
            True if online, False if offline
        """
        try:
            # Try to connect to Google's DNS server
            socket.create_connection(
                ("8.8.8.8", 53),
                timeout=CONNECTION_TIMEOUT_SECONDS
            )
            self.is_online = True
            logger.info("Connection check: ONLINE")
            return True
        except OSError:
            self.is_online = False
            logger.info("Connection check: OFFLINE")
            return False
    
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
                    
                    # Check if record exists in Google Sheets
                    # For now, we'll use append (add to end)
                    # In production, you'd want to check and update existing records
                    
                    # Convert record dict to list for Google Sheets
                    values = list(record.values())
                    
                    # Append to Google Sheets
                    self.sheets_client.append_row(sheets_table, values)
                    
                    # Mark as synced in local cache
                    record_id = record.get(f"{table_name}_id") or record.get('id')
                    self.cache.update_record(
                        table_name, 
                        record_id, 
                        {'sync_status': 'synced'}
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
        
        try:
            # First, push any local changes to sheets
            push_result = self.sync_local_changes_to_sheets()
            
            # Then, pull any changes from sheets
            # (In a real implementation, you'd track timestamps and only pull changed records)
            # For now, we'll just sync pending local changes
            
            return {
                "pushed": push_result,
                "pulled": 0,  # Simplified for now
                "last_sync": datetime.now().strftime(DATETIME_FORMAT)
            }
            
        except Exception as e:
            logger.error(f"Incremental sync failed: {str(e)}")
            return {"error": str(e)}
    
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
    
    def resolve_conflicts(self, local_record: Dict, remote_record: Dict) -> Dict:
        """
        Resolve conflicts between local and remote records.
        Uses "last modified wins" strategy.
        
        Args:
            local_record: Local record from SQLite
            remote_record: Remote record from Google Sheets
        
        Returns:
            The record that should be kept
        """
        local_time = local_record.get('last_modified', '')
        remote_time = remote_record.get('last_modified', '')
        
        # If timestamps are available, use them
        if local_time and remote_time:
            if local_time > remote_time:
                logger.info("Conflict resolved: keeping local record (newer)")
                return local_record
            else:
                logger.info("Conflict resolved: keeping remote record (newer)")
                return remote_record
        
        # Default to remote (Google Sheets) if no timestamps
        logger.info("Conflict resolved: keeping remote record (no timestamps)")
        return remote_record
