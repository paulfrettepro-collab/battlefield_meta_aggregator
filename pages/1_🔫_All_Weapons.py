"""
All Weapons Statistics Page - Streamlit Cloud Version

Wrapper that executes the actual page from dashboard/pages/
"""

import os
import sys
from pathlib import Path

# Navigate to dashboard directory for proper imports
dashboard_dir = Path(__file__).parent.parent / "dashboard"
sys.path.insert(0, str(dashboard_dir))
os.chdir(dashboard_dir)

# Execute the actual page
with open("pages/1_🔫_All_Weapons.py", "r", encoding="utf-8") as f:
    exec(f.read())
