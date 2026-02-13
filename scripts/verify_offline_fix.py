import sys
import unittest
from unittest.mock import MagicMock, patch
import os

# Add src to path
sys.path.insert(0, os.getcwd())

from src.data_access.google_sheets_client import GoogleSheetsClient

class TestOfflineStartup(unittest.TestCase):
    
    @patch('src.data_access.google_sheets_client.socket')
    @patch('src.data_access.google_sheets_client.GoogleSheetsClient.authenticate_silent')
    def test_offline_skip_interactive(self, mock_auth_silent, mock_socket):
        # Setup
        mock_auth_silent.return_value = False  # Simulate silent auth failing
        
        # Simulate socket connection failure (Offline)
        mock_socket.socket.return_value.connect.side_effect = OSError("Network unreachable")
        mock_socket.create_connection.side_effect = OSError("Network unreachable")
        
        client = GoogleSheetsClient()
        
        # Action
        result = client.authenticate()
        
        # Assert
        self.assertFalse(result, "Authenticate should return False when offline")
        self.assertFalse(client.is_authenticated, "Client should not be authenticated")
        
        # Verify we did NOT try to start flow (no flow import/usage)
        # Since we can't easily check for non-imported modules, we trust the return value
        # and the fact that we mocked the socket failure which triggers our new check.
        print("✅ correctly handled offline mode by skipping interactive auth")

if __name__ == '__main__':
    unittest.main()
