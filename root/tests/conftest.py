# tests/conftest.py
import sys
import os
from pathlib import Path

# Add root directory to Python path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))