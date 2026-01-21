import pickle
import os
import json
from google.oauth2.credentials import Credentials

TOKEN_DIR = r"c:\Users\darre\.brewerymanager"
TOKEN_PATH_PICKLE = os.path.join(TOKEN_DIR, "token.json") 
# Note: google_sheets_client saves as 'token.json' but writes a pickle dump.

if os.path.exists(TOKEN_PATH_PICKLE):
    print(f"Found token at: {TOKEN_PATH_PICKLE}")
    try:
        with open(TOKEN_PATH_PICKLE, 'rb') as token:
            creds = pickle.load(token)
            print("Token loaded successfully.")
            print(f"Valid: {creds.valid}")
            print(f"Scopes: {creds.scopes}")
    except Exception as e:
        print(f"Error reading pickle: {e}")
        # Try reading as JSON just in case
        try:
            with open(TOKEN_PATH_PICKLE, 'r') as token:
                data = json.load(token)
                print("Read as JSON:")
                print(data)
        except:
            pass
else:
    print("No token file found.")
