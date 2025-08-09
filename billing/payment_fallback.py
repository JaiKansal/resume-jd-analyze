#!/usr/bin/env python3
"""
Payment system fallback for when Razorpay is not configured
"""

import logging
import streamlit as st
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class PaymentFallbackService:
    """Fallback payment service when Razorpay is not configured"""
    
    def __init__(self):
        self.status = "fallback_mode"
        logger.info("Payment fallback service initialized")
    
    def is_configured(self) -> bool:
        """Check if payment system is configured"""
        return False  # Always false for fallback
    
    def create_order(self, amount: float, currency: str = "INR", **kwargs) -> Dict[str, Any]:
        """Create a mock order for fallback"""
        logger.warning("Payment system not configured - using fallback")
        return {
            'id': 'fallback_order_id',
            'amount': amount,
            'currency': currency,
            'status': 'created',
            'fallback': True
        }
    
    def verify_payment(self, payment_data: Dict[str, Any]) -> bool:
        """Verify payment (always fails in fallback)"""
        logger.warning("Payment verification not available - payment system not configured")
        return False
    
    def create_subscription(self, plan_id: str, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create subscription (not available in fallback)"""
        logger.warning("Subscription creation not available - payment system not configured")
        return {
            'id': 'fallback_subscription_id',
            'status': 'not_configured',
            'fallback': True
        }
    
    def get_payment_status(self, payment_id: str) -> str:
        """Get payment status (always returns not configured)"""
        return "not_configured"
    
    def render_payment_not_configured_message(self):
        """Render message when payment system is not configured"""
        st.warning("💳 Payment system is currently being configured. You can still use the free tier!")
        
        with st.expander("ℹ️ About Payment Configuration"):
            st.info("""
            **Current Status:** Payment system configuration in progress
            
            **What you can do:**
            - ✅ Use all free tier features (3 analyses per month)
            - ✅ Upload and analyze resumes
            - ✅ Download analysis reports
            - ✅ Access analysis history
            
            **Coming Soon:**
            - 💳 Professional plan upgrades
            - 🚀 Unlimited analyses
            - 📊 Advanced analytics
            - 🎯 Priority support
            
            The free tier provides full functionality for getting started!
            """)
    
    def render_upgrade_not_available(self, current_plan: str = "Free"):
        """Render upgrade not available message"""
        st.info(f"🎯 You're currently on the **{current_plan}** plan")
        
        st.warning("""
        💳 **Plan upgrades are temporarily unavailable**
        
        Payment system configuration is in progress. You can continue using all free tier features:
        - ✅ 3 resume analyses per month
        - ✅ PDF report downloads
        - ✅ Analysis history access
        - ✅ All core features
        """)
        
        if st.button("🔄 Check Again Later"):
            st.rerun()

# Global fallback service instance
payment_fallback_service = PaymentFallbackService()

def get_payment_service():
    """Get the appropriate payment service (with fallback)"""
    try:
        from billing.enhanced_razorpay_service import enhanced_razorpay_service
        
        # Try to reinitialize if status is not connected
        if enhanced_razorpay_service.status != "connected":
            logger.info("🔄 Attempting to reinitialize Razorpay service...")
            enhanced_razorpay_service.reinitialize()
        
        # Check if Razorpay is properly configured
        if enhanced_razorpay_service.status == "connected" and enhanced_razorpay_service.client:
            logger.info("✅ Using Razorpay payment service")
            return enhanced_razorpay_service
        else:
            status_info = enhanced_razorpay_service.get_status_info()
            logger.warning(f"Razorpay not available (status: {enhanced_razorpay_service.status})")
            logger.warning(f"Status info: {status_info}")
            return payment_fallback_service
    except Exception as e:
        logger.error(f"Failed to load Razorpay service: {e}")
        return payment_fallback_service

def render_payment_status():
    """Render current payment system status"""
    payment_service = get_payment_service()
    
    if payment_service.status == "fallback_mode":
        st.sidebar.info("💳 Free Tier Active")
    elif payment_service.status == "connected":
        st.sidebar.success("💳 Payment System Ready")
    else:
        st.sidebar.warning("💳 Payment System Configuring")