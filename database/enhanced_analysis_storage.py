"""
Enhanced Analysis Storage - Fallback for Streamlit Cloud
"""

import logging

logger = logging.getLogger(__name__)

class EnhancedAnalysisStorage:
    """Fallback analysis storage"""
    
    def __init__(self):
        logger.info("Using fallback analysis storage")
    
    def save_analysis(self, *args, **kwargs):
        """Save analysis - fallback implementation"""
        logger.info("Analysis save skipped (fallback mode)")
        return True
    
    def get_analysis_history(self, *args, **kwargs):
        """Get analysis history - fallback implementation"""
        return []
    
    def get_analysis_by_id(self, *args, **kwargs):
        """Get analysis by ID - fallback implementation"""
        return None

# Global instance
enhanced_analysis_storage = EnhancedAnalysisStorage()