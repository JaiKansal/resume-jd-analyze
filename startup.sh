#!/bin/bash
# Streamlit Cloud startup script

echo "🚀 Starting Resume + JD Analyzer..."

# Set environment variables for Streamlit Cloud
export PYTHONPATH="${PYTHONPATH}:."
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Clean any problematic cache
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

echo "✅ Environment prepared"

# Start the application
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
