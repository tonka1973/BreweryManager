
import py_compile
import sys

try:
    py_compile.compile('src/gui/customers.py', doraise=True)
    print("✅ Syntax OK")
except Exception as e:
    print(f"❌ Syntax Error: {e}")
    sys.exit(1)
