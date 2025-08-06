"""
Startup initialization for Resume + JD Analyzer
Ensures proper environment setup for Streamlit Cloud deployment
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Set environment variables for Streamlit Cloud
os.environ.setdefault('PYTHONPATH', str(project_root))
os.environ.setdefault('STREAMLIT_SERVER_HEADLESS', 'true')
os.environ.setdefault('STREAMLIT_SERVER_ENABLE_CORS', 'false')

# Initialize logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info("🚀 Startup initialization completed")
logger.info(f"📁 Project root: {project_root}")
logger.info(f"🐍 Python path: {sys.path[:3]}...")

# Ensure data directory exists
data_dir = project_root / 'data'
data_dir.mkdir(exist_ok=True)
logger.info(f"📊 Data directory: {data_dir}")
