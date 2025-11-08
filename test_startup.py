"""
Test the application startup sequence without GUI
Simulates what main.py does at startup
"""

import sys
sys.path.insert(0, '/home/user/BreweryManager')

print("=" * 60)
print("TESTING APPLICATION STARTUP SEQUENCE")
print("=" * 60)
print()

# Clean slate
import os
db_path = '/root/.brewerymanager/cache.db'
if os.path.exists(db_path):
    os.remove(db_path)
    print("✅ Removed existing database")

print()
print("Step 1: Initialize SQLite Cache Manager...")
from src.data_access.sqlite_cache import SQLiteCacheManager
cache_manager = SQLiteCacheManager()
print("✅ Cache manager created")

print()
print("Step 2: Initialize database (create tables)...")
cache_manager.connect()
cache_manager.initialize_database()
cache_manager.close()
print("✅ Database tables created")

print()
print("Step 3: Initialize Auth Manager...")
from src.utilities.auth import AuthManager
auth = AuthManager(cache_manager)
print("✅ Auth manager created")

print()
print("Step 4: Create default admin user...")
admin_created = auth.create_default_admin()
if admin_created:
    print("✅ Default admin user created")
else:
    print("✅ Admin user already exists")

print()
print("Step 5: Test login...")
user = auth.login('admin', 'admin')
if user:
    print(f"✅ Login successful!")
    print(f"   Username: {user.username}")
    print(f"   Role: {user.role}")
    print(f"   Active: {user.is_active}")
else:
    print("❌ Login failed!")
    sys.exit(1)

print()
print("=" * 60)
print("✅ STARTUP SEQUENCE SUCCESSFUL")
print("=" * 60)
print()
print("The application should now work on Windows!")
print("Run: python main.py")
