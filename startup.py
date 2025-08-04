"""
Startup Script for Resume + JD Analyzer
Ensures all systems are initialized before the app starts
"""

import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ensure_startup_requirements():
    """Ensure all startup requirements are met"""
    try:
        # 1. Ensure data directory exists
        data_dir = Path('data')
        data_dir.mkdir(exist_ok=True)
        logger.info("Data directory ensured")
        
        # 2. Initialize database with simple approach
        from database.simple_init import ensure_database_exists
        db_success = ensure_database_exists()
        
        if db_success:
            logger.info("Database initialization successful")
        else:
            logger.error("Database initialization failed")
        
        # 3. Check environment variables
        required_vars = ['PERPLEXITY_API_KEY', 'RAZORPAY_KEY_ID', 'RAZORPAY_KEY_SECRET']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.warning(f"Missing environment variables: {missing_vars}")
        else:
            logger.info("All required environment variables are set")
        
        # 4. Test database connection
        try:
            from database.connection import get_db
            db = get_db()
            # Simple test query
            result = db.execute_query("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1")
            logger.info("Database connection test successful")
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
        
        logger.info("Startup requirements check completed")
        return True
        
    except Exception as e:
        logger.error(f"Startup requirements check failed: {e}")
        return False

# Run startup check when imported
if __name__ != "__main__":
    ensure_startup_requirements()