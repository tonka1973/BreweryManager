#!/usr/bin/env python3
"""
Simple test script for Brewery Management System
Tests core functionality without GUI
"""

import os
import sys


def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def main():
    """Run simple tests."""
    print("\n" * 2)
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 12 + "BREWERY MANAGEMENT SYSTEM" + " " * 21 + "║")
    print("║" + " " * 18 + "SIMPLE TEST SUITE" + " " * 23 + "║")
    print("╚" + "═" * 58 + "╝")

    all_passed = True

    # Test 1: Module Imports
    print_header("TEST 1: Core Module Imports")
    try:
        from src.utilities.auth import AuthManager
        print("✅ AuthManager imported")
    except Exception as e:
        print(f"❌ AuthManager import failed: {e}")
        all_passed = False

    try:
        from src.data_access.sqlite_cache import SQLiteCacheManager
        print("✅ SQLiteCacheManager imported")
    except Exception as e:
        print(f"❌ SQLiteCacheManager import failed: {e}")
        all_passed = False

    try:
        from src.data_access.sync_manager import SyncManager
        print("✅ SyncManager imported")
    except Exception as e:
        print(f"❌ SyncManager import failed: {e}")
        all_passed = False

    try:
        from src.config import constants
        print("✅ Constants module imported")
        print(f"   App Name: {constants.APP_NAME}")
        print(f"   Version: {constants.APP_VERSION}")
        print(f"   Database Path: {constants.CACHE_DB_PATH}")
    except Exception as e:
        print(f"❌ Constants import failed: {e}")
        all_passed = False

    # Test 2: Database Initialization
    print_header("TEST 2: Database Initialization")
    try:
        from src.data_access.sqlite_cache import SQLiteCacheManager

        cache = SQLiteCacheManager()
        print("✅ Database manager initialized")

        # Connect to database
        if cache.connect():
            print("✅ Connected to database")
        else:
            print("❌ Failed to connect to database")
            all_passed = False

        # Initialize database tables
        cache.initialize_database()
        print("✅ Database tables created")

        # Check if database file was created
        from src.config import constants
        if os.path.exists(constants.CACHE_DB_PATH):
            print(f"✅ Database file exists: {constants.CACHE_DB_PATH}")
            size = os.path.getsize(constants.CACHE_DB_PATH)
            print(f"   Size: {size:,} bytes")
        else:
            print("❌ Database file not found")
            all_passed = False

    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False

    # Test 3: Authentication System
    print_header("TEST 3: Authentication System")
    try:
        from src.utilities.auth import AuthManager
        from src.data_access.sqlite_cache import SQLiteCacheManager

        cache = SQLiteCacheManager()
        cache.connect()
        cache.initialize_database()
        auth = AuthManager(cache)
        print("✅ Auth manager initialized")

        # Create default admin user
        auth.create_default_admin()
        print("✅ Default admin user created")

        # Test login with default admin credentials
        print("\nAttempting login with admin credentials...")
        user = auth.login("admin", "admin")

        if user:
            print("✅ Admin login successful")
            print(f"   Username: {user.username}")
            print(f"   Full Name: {user.full_name}")
            print(f"   Role: {user.role}")
            print(f"   User ID: {user.user_id}")

            # Test logout
            auth.logout()
            print("✅ Logout successful")
        else:
            print("❌ Admin login failed: No user object returned")
            all_passed = False

        # Test invalid password
        print("\nTesting invalid password (should fail)...")
        user = auth.login("admin", "wrongpassword")
        if not user:
            print("✅ Invalid password correctly rejected")
        else:
            print("❌ Invalid password was accepted (security issue!)")
            all_passed = False

    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False

    # Test 4: Configuration
    print_header("TEST 4: Configuration Constants")
    try:
        from src.config import constants

        print(f"✅ App Configuration:")
        print(f"   App Name: {constants.APP_NAME}")
        print(f"   Version: {constants.APP_VERSION}")
        print(f"   Window Size: {constants.WINDOW_WIDTH}x{constants.WINDOW_HEIGHT}")
        print(f"   Sync Interval: {constants.SYNC_INTERVAL_SECONDS}s")
        print(f"   VAT Rate: {constants.VAT_RATE * 100}%")
        print(f"\n✅ User Roles: {', '.join(constants.USER_ROLES.values())}")
        print(f"\n✅ Container Sizes:")
        for name, size in list(constants.CONTAINER_SIZES.items())[:5]:
            print(f"   {name}: {size}L")

    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        all_passed = False

    # Test 5: Google Sheets Client (optional)
    print_header("TEST 5: Google Sheets Client (Optional)")
    try:
        from src.data_access.google_sheets_client import GoogleSheetsClient

        client = GoogleSheetsClient()
        print("✅ Google Sheets client created")
        print("⚠️  Note: Actual connection requires credentials.json")
        print("   This is expected in testing environment")

    except Exception as e:
        print(f"⚠️  Google Sheets client test: {str(e)[:80]}")
        print("   (This is expected without credentials file)")

    # Final Summary
    print("\n" + "=" * 60)
    print("  SUMMARY")
    print("=" * 60)

    if all_passed:
        print("\n✅ ALL CORE TESTS PASSED!\n")
        print("The application core is working correctly.")
        print("\nNext steps:")
        print("  1. Run the full application: python3 main.py")
        print("  2. Login with: admin / admin123")
        print("  3. Test navigation between modules")
        print("\nNote: GUI requires tkinter and a display.")
        print("      On Linux: sudo apt-get install python3-tk")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED\n")
        print("Please review the errors above.")
        print("Check TESTING.md for troubleshooting steps.")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
