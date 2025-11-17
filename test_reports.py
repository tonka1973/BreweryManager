"""
Test script to diagnose reports.py issue
"""
import sys
sys.path.insert(0, '.')

from src.gui.reports import ReportsModule

print("Checking ReportsModule methods...")
print("=" * 70)

methods = [m for m in dir(ReportsModule) if not m.startswith('_')]
print(f"\nTotal methods: {len(methods)}")

load_methods = [m for m in methods if m.startswith('load_')]
print(f"\nLoad methods found ({len(load_methods)}):")
for m in sorted(load_methods):
    print(f"  - {m}")

create_methods = [m for m in methods if m.startswith('create_')]
print(f"\nCreate methods found ({len(create_methods)}):")
for m in sorted(create_methods):
    print(f"  - {m}")

print("\n" + "=" * 70)

# Check if the specific methods exist
required_methods = [
    'load_sales_report',
    'load_inventory_report',
    'load_production_report',
    'load_financial_report'
]

print("\nChecking required methods:")
for method in required_methods:
    exists = hasattr(ReportsModule, method)
    status = "✓" if exists else "✗"
    print(f"  {status} {method}")

if all(hasattr(ReportsModule, m) for m in required_methods):
    print("\n✓ All required methods found!")
else:
    print("\n✗ Some methods are missing!")
    print("\nThis suggests an indentation or class definition issue.")
