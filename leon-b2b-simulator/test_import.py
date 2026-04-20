import sys
import os
print(f"PYTHONPATH: {sys.path}")
print(f"CWD: {os.getcwd()}")
try:
    from src.config.settings import INTERNAL_DOCS_BUCKET
    print(f"IMPORT SUCCESS: {INTERNAL_DOCS_BUCKET}")
except Exception as e:
    print(f"IMPORT ERROR: {e}")
