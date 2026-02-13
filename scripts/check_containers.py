"""Quick diagnostic to check if containers exist in database"""
import sqlite3
import os

# Get database path
db_path = os.path.expanduser('~/.brewerymanager/cache.db')

print(f"Checking database: {db_path}")
print("=" * 60)

if not os.path.exists(db_path):
    print("❌ Database file doesn't exist!")
    print(f"   Expected location: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if settings_containers table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='settings_containers'")
if not cursor.fetchone():
    print("❌ settings_containers table doesn't exist!")
    print("   The migration may not have run successfully.")
    conn.close()
    exit(1)

print("✅ settings_containers table exists\n")

# Check table schema
cursor.execute("PRAGMA table_info(settings_containers)")
columns = cursor.fetchall()
print("Table columns:")
for col in columns:
    print(f"   - {col[1]} ({col[2]})")

# Check containers
cursor.execute("SELECT id, name, actual_capacity, duty_paid_volume, is_draught_eligible, active FROM settings_containers")
containers = cursor.fetchall()

print(f"\nTotal containers in database: {len(containers)}\n")

if not containers:
    print("❌ No containers found!")
    print("   The migration didn't populate default containers.")
else:
    print("Containers:")
    for c in containers:
        id, name, actual, duty, draught, active = c
        status = "✅ ACTIVE" if active == 1 else "❌ INACTIVE"
        draught_text = "Draught" if draught == 1 else "Non-Draught"
        print(f"   {status} - {name}: {actual}L → {duty}L duty-paid ({draught_text})")

# Check active containers (what the dialog sees)
cursor.execute("SELECT name FROM settings_containers WHERE active = 1")
active_containers = cursor.fetchall()
print(f"\nActive containers (visible in package dialog): {len(active_containers)}")

conn.close()

print("\n" + "=" * 60)
if len(active_containers) == 0:
    print("⚠️  NO ACTIVE CONTAINERS! This is why the package dialog is empty.")
    print("   Solution: Run the migration again or manually activate containers.")
else:
    print(f"✅ {len(active_containers)} containers should appear in the package dialog.")
