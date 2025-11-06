# Google Sheets API Client
# Handles all interactions with Google Sheets as the cloud database

import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

from ..config.constants import (
    GOOGLE_SHEETS_SCOPES,
    SPREADSHEET_NAME,
    TOKEN_PATH,
    CREDENTIALS_PATH,
    TABLES,
)

logger = logging.getLogger(__name__)


class GoogleSheetsClient:
    """
    Manages connection to Google Sheets API and provides methods
    for reading/writing data to the brewery management spreadsheet.
    """
    
    def __init__(self):
        self.creds = None
        self.service = None
        self.spreadsheet_id = None
        self.is_authenticated = False
        
    def authenticate(self):
        """
        Authenticate with Google and get credentials.
        Uses OAuth2 flow for first-time setup, then uses saved token.
        """
        try:
            # Check if token already exists
            if os.path.exists(TOKEN_PATH):
                with open(TOKEN_PATH, 'rb') as token:
                    self.creds = pickle.load(token)
            
            # If credentials are invalid or don't exist, get new ones
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    # First time setup - need credentials.json
                    if not os.path.exists(CREDENTIALS_PATH):
                        raise FileNotFoundError(
                            f"Credentials file not found at {CREDENTIALS_PATH}. "
                            "Please download from Google Cloud Console."
                        )
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        CREDENTIALS_PATH, GOOGLE_SHEETS_SCOPES
                    )
                    self.creds = flow.run_local_server(port=0)
                
                # Save the credentials for next run
                with open(TOKEN_PATH, 'wb') as token:
                    pickle.dump(self.creds, token)
            
            # Build the service
            self.service = build('sheets', 'v4', credentials=self.creds)
            self.is_authenticated = True
            logger.info("Successfully authenticated with Google Sheets API")
            return True
            
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            self.is_authenticated = False
            return False
    
    def create_spreadsheet(self):
        """
        Create a new spreadsheet with all required sheets and headers.
        This is called once during initial setup.
        """
        try:
            if not self.is_authenticated:
                raise Exception("Not authenticated. Call authenticate() first.")
            
            # Create the spreadsheet
            spreadsheet = {
                'properties': {
                    'title': SPREADSHEET_NAME
                },
                'sheets': []
            }
            
            # Add all required sheets
            for table_name in TABLES.values():
                spreadsheet['sheets'].append({
                    'properties': {
                        'title': table_name
                    }
                })
            
            spreadsheet = self.service.spreadsheets().create(
                body=spreadsheet,
                fields='spreadsheetId'
            ).execute()
            
            self.spreadsheet_id = spreadsheet.get('spreadsheetId')
            logger.info(f"Created spreadsheet: {self.spreadsheet_id}")
            
            # Initialize each sheet with headers
            self._initialize_sheet_headers()
            
            return self.spreadsheet_id
            
        except HttpError as error:
            logger.error(f"Error creating spreadsheet: {error}")
            return None
    
    def find_spreadsheet(self):
        """
        Find existing brewery spreadsheet by name.
        Returns spreadsheet ID if found, None otherwise.
        """
        try:
            # This would use Google Drive API to search for the file
            # For now, we'll ask user to provide the ID or create new
            pass
        except Exception as e:
            logger.error(f"Error finding spreadsheet: {str(e)}")
            return None
    
    def read_sheet(self, sheet_name, range_notation=None):
        """
        Read data from a sheet.
        
        Args:
            sheet_name: Name of the sheet (e.g., "Batches")
            range_notation: Optional range (e.g., "A1:Z100"). If None, reads all data.
        
        Returns:
            List of rows, where each row is a list of values
        """
        try:
            if not self.is_authenticated:
                raise Exception("Not authenticated")
            
            if not self.spreadsheet_id:
                raise Exception("No spreadsheet ID set")
            
            # Build the range string
            if range_notation:
                range_str = f"{sheet_name}!{range_notation}"
            else:
                range_str = sheet_name
            
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_str
            ).execute()
            
            values = result.get('values', [])
            return values
            
        except HttpError as error:
            logger.error(f"Error reading sheet {sheet_name}: {error}")
            return []
    
    def append_row(self, sheet_name, row_data):
        """
        Append a row to the end of a sheet.
        
        Args:
            sheet_name: Name of the sheet
            row_data: List of values to append
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.is_authenticated:
                raise Exception("Not authenticated")
            
            body = {
                'values': [row_data]
            }
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=sheet_name,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            return True
            
        except HttpError as error:
            logger.error(f"Error appending row to {sheet_name}: {error}")
            return False
    
    def update_row(self, sheet_name, row_index, row_data):
        """
        Update a specific row in a sheet.
        
        Args:
            sheet_name: Name of the sheet
            row_index: Row number (1-indexed)
            row_data: List of values to write
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.is_authenticated:
                raise Exception("Not authenticated")
            
            range_str = f"{sheet_name}!A{row_index}"
            
            body = {
                'values': [row_data]
            }
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_str,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            return True
            
        except HttpError as error:
            logger.error(f"Error updating row in {sheet_name}: {error}")
            return False
    
    def batch_update(self, updates):
        """
        Perform multiple updates in a single API call.
        
        Args:
            updates: List of update dictionaries with 'range' and 'values' keys
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.is_authenticated:
                raise Exception("Not authenticated")
            
            body = {
                'valueInputOption': 'USER_ENTERED',
                'data': updates
            }
            
            result = self.service.spreadsheets().values().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body=body
            ).execute()
            
            return True
            
        except HttpError as error:
            logger.error(f"Error in batch update: {error}")
            return False
    
    def _initialize_sheet_headers(self):
        """
        Initialize all sheets with their column headers.
        This is called after creating a new spreadsheet.
        """
        # Define headers for each sheet
        # This is a large dictionary mapping sheet names to their headers
        # For now, we'll create placeholder headers
        
        headers_map = {
            "Batches": [
                "batch_id", "gyle_number", "recipe_id", "brew_date",
                "brewer_name", "actual_batch_size", "measured_abv",
                "pure_alcohol_litres", "status", "fermenting_start",
                "conditioning_start", "ready_date", "packaged_date",
                "spr_rate_applied", "duty_rate_applied", "is_draught",
                "brewing_notes", "created_by"
            ],
            "Recipes": [
                "recipe_id", "recipe_name", "style", "version", "target_abv",
                "target_batch_size_litres", "created_date", "created_by",
                "last_modified", "is_active", "brewing_notes"
            ],
            # Add more headers for other sheets...
        }
        
        # Update each sheet with headers
        updates = []
        for sheet_name, headers in headers_map.items():
            updates.append({
                'range': f"{sheet_name}!A1",
                'values': [headers]
            })
        
        if updates:
            self.batch_update(updates)
    
    def check_connection(self):
        """
        Check if we can connect to Google Sheets API.
        Returns True if connected, False otherwise.
        """
        try:
            if not self.is_authenticated:
                return False
            
            # Try to get spreadsheet metadata
            if self.spreadsheet_id:
                self.service.spreadsheets().get(
                    spreadsheetId=self.spreadsheet_id
                ).execute()
                return True
            return False
            
        except Exception as e:
            logger.error(f"Connection check failed: {str(e)}")
            return False
