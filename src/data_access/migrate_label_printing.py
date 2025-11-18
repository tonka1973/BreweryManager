"""
Database Migration: Label Printing Features

Adds support for:
1. Allergen tracking in recipes
2. Fill number tracking in batch packaging lines
"""

import sqlite3
import os
from datetime import datetime


def migrate_label_printing():
    """
    Add label printing features to database
    """
    # Get database path
    db_path = os.path.expanduser('~/.brewerymanager/cache.db')

    print("=" * 60)
    print("LABEL PRINTING FEATURES MIGRATION")
    print("=" * 60)
    print(f"\nDatabase: {db_path}")

    if not os.path.exists(db_path):
        print("\n❌ ERROR: Database not found!")
        print(f"   Expected location: {db_path}")
        return False

    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("\n" + "=" * 60)
        print("STEP 1: Add allergens column to recipes table")
        print("=" * 60)

        # Check if allergens column already exists
        cursor.execute("PRAGMA table_info(recipes)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'allergens' in columns:
            print("   ⚠️  allergens column already exists - skipping")
        else:
            cursor.execute('''
                ALTER TABLE recipes
                ADD COLUMN allergens TEXT
            ''')
            print("   ✅ Added allergens column to recipes table")

        print("\n" + "=" * 60)
        print("STEP 2: Add fill_number column to batch_packaging_lines table")
        print("=" * 60)

        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='batch_packaging_lines'")
        if not cursor.fetchone():
            print("   ⚠️  batch_packaging_lines table doesn't exist - skipping")
            print("   (This table is created by the duty system migration)")
        else:
            # Check if fill_number column already exists
            cursor.execute("PRAGMA table_info(batch_packaging_lines)")
            columns = [col[1] for col in cursor.fetchall()]

            if 'fill_number' in columns:
                print("   ⚠️  fill_number column already exists - skipping")
            else:
                cursor.execute('''
                    ALTER TABLE batch_packaging_lines
                    ADD COLUMN fill_number INTEGER
                ''')
                print("   ✅ Added fill_number column to batch_packaging_lines table")

        # Commit changes
        conn.commit()

        print("\n" + "=" * 60)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nChanges made:")
        print("  • recipes.allergens - Store allergen information")
        print("  • batch_packaging_lines.fill_number - Track container sequence")
        print("\nYou can now:")
        print("  • Add allergen info to recipes")
        print("  • Print labels with sequential numbering (1 of 10, 2 of 10, etc.)")
        print("\n" + "=" * 60)

        conn.close()
        return True

    except Exception as e:
        print(f"\n❌ ERROR during migration: {e}")
        conn.rollback()
        conn.close()
        return False


if __name__ == '__main__':
    print("\n🍺 Brewery Manager - Label Printing Migration")
    print("\nThis migration adds:")
    print("  1. Allergen tracking to recipes")
    print("  2. Fill number tracking to packaging lines")
    print("\n⚠️  BACKUP RECOMMENDED (but migration is non-destructive)")

    response = input("\nProceed with migration? (yes/no): ").strip().lower()

    if response == 'yes':
        success = migrate_label_printing()
        if success:
            print("\n✅ Migration complete! You can now use label printing features.")
        else:
            print("\n❌ Migration failed. Please check the errors above.")
    else:
        print("\n❌ Migration cancelled.")
