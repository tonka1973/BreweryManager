"""
Fix cache API usage in GUI modules
Replaces incorrect get_connection() calls with correct connect() API
"""

import re
from pathlib import Path

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def fix_file(file_path):
    """Fix cache API usage in a single file"""
    print(f"\nFixing {file_path}...")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    changes = []

    # Pattern 1: conn = self.cache.get_connection()
    # Replace with: self.cache.connect()
    pattern1 = r'(\s+)conn = self\.cache\.get_connection\(\)\s+cursor = conn\.cursor\(\)'
    replacement1 = r'\1self.cache.connect()\n\1cursor = self.cache.cursor'
    if re.search(pattern1, content):
        content = re.sub(pattern1, replacement1, content)
        changes.append("Fixed conn = self.cache.get_connection() pattern")

    # Pattern 2: Standalone cursor = conn.cursor() after get_connection
    # This should already be caught by pattern 1, but check for any stragglers
    pattern2 = r'cursor = conn\.cursor\(\)'
    if re.search(pattern2, content):
        content = re.sub(pattern2, r'cursor = self.cache.cursor', content)
        changes.append("Fixed standalone cursor = conn.cursor()")

    # Pattern 3: conn.commit() -> self.cache.connection.commit()
    pattern3 = r'(\s+)conn\.commit\(\)'
    if re.search(pattern3, content):
        content = re.sub(pattern3, r'\1self.cache.connection.commit()', content)
        changes.append("Fixed conn.commit()")

    # Pattern 4: conn.close() at end of functions -> self.cache.close()
    # Be careful not to change this in finally blocks
    pattern4 = r'(\s+)conn\.close\(\)'
    if re.search(pattern4, content):
        content = re.sub(pattern4, r'\1self.cache.close()', content)
        changes.append("Fixed conn.close()")

    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  ✓ Applied {len(changes)} fix(es):")
        for change in changes:
            print(f"    - {change}")
        return True
    else:
        print("  - No changes needed")
        return False

def main():
    """Fix all affected files"""
    print("=" * 70)
    print("FIX CACHE API USAGE")
    print("=" * 70)

    base_path = Path(__file__).parent.parent / "gui"

    files_to_fix = [
        base_path / "duty.py",
        base_path / "reports.py",
        base_path / "products.py"
    ]

    fixed_count = 0
    for file_path in files_to_fix:
        if file_path.exists():
            if fix_file(file_path):
                fixed_count += 1
        else:
            print(f"\n⚠️  File not found: {file_path}")

    print("\n" + "=" * 70)
    print(f"✅ FIXED {fixed_count} FILE(S)")
    print("=" * 70)
    print("\nYou can now run the application: python main.py")
    print("=" * 70)

if __name__ == "__main__":
    main()
