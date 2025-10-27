"""
Battlefield Meta Aggregator - Streamlit Cloud Entry Point

This file serves as the entry point for Streamlit Cloud deployment.
It loads the main dashboard from dashboard/app.py

For local development, you can run either:
    streamlit run streamlit_app.py  (root)
    streamlit run dashboard/app.py  (dashboard folder)
"""

# Execute the dashboard app
exec(open("dashboard/app.py").read())

