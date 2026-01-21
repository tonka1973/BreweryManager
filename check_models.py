
import os
import pickle
from google import genai
from src.config.constants import CREDENTIALS_PATH, APP_DATA_DIR

# Try to get API key from database or environment
# For this script we will try to read from the db manually or just ask the user? 
# Actually, the user has the app running which means they have an API key in the DB.
# Let's try to reuse the AIClient logic slightly or just connect to the DB.

import sqlite3

def get_api_key():
    try:
        db_path = os.path.join(os.path.expanduser('~'), '.brewerymanager', 'cache.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT setting_value FROM system_settings WHERE setting_key = 'ai_api_key'")
        row = cursor.fetchone()
        conn.close()
        if row:
            return row[0]
    except Exception as e:
        print(f"Error reading DB: {e}")
    return None

def list_models():
    api_key = get_api_key()
    if not api_key:
        print("Could not find API Key in database.")
        return

    print(f"Using API Key: {api_key[:5]}...")
    
    try:
        client = genai.Client(api_key=api_key)
        # The new SDK might specific calls. checking documentation via search or just trying common ones.
        # Based on error message: "Call ListModels"
        
        print("Attempting to list models...")
        models = client.models.list()
        for m in models:
            print(f"Model Object: {m}")
            # print(f"Attributes: {dir(m)}") 
            # based on typical Google APIs, it might be .name, .display_name
            # If m is a pydantic model or similar, it might dump to dict
            try:
                print(f"Name: {m.name}")
            except:
                pass
            print("-" * 20)
            
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    list_models()
