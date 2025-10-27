"""
Streamlit Cloud Entry Point

This file serves as the entry point for Streamlit Cloud deployment.
It executes the main dashboard app located in the dashboard/ directory.
"""

import os
import sys
from pathlib import Path

# Add dashboard directory to Python path so imports work correctly
dashboard_dir = Path(__file__).parent / "dashboard"
sys.path.insert(0, str(dashboard_dir))

# Change to dashboard directory so relative imports work
os.chdir(dashboard_dir)

# Execute the main dashboard app
exec(open("app.py").read())

