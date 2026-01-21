
import sys
import os
import logging

# Add src to pythonpath
sys.path.append(os.getcwd())

from src.data_access.sqlite_cache import SQLiteCacheManager

# Configure logging
logging.basicConfig(level=logging.INFO)

def run_migration():
    print("Initializing SQLiteCacheManager to trigger migrations...")
    cache = SQLiteCacheManager()
    if cache.connect():
        print("Connected to database.")
        try:
            cache.initialize_database()
            print("Database initialization/migration called successfully.")
        except Exception as e:
            print(f"Error during initialization: {e}")
        finally:
            cache.close()
    else:
        print("Failed to connect to database.")

if __name__ == "__main__":
    run_migration()
