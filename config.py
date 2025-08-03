"""
Configuration Management for Resume + JD Analyzer
Handles environment variables and application settings for Streamlit Cloud
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

# Import streamlit for secrets (if available)
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

def get_secret(key: str, default: str = '') -> str:
    """Get secret from Streamlit secrets or environment variables"""
    if STREAMLIT_AVAILABLE and hasattr(st, 'secrets'):
        try:
            return st.secrets.get(key, os.getenv(key, default))
        except:
            return os.getenv(key, default)
    return os.getenv(key, default)

class Config:
    """Application configuration"""
    
    # AI Service
    PERPLEXITY_API_KEY: str = get_secret('PERPLEXITY_API_KEY', '')
    
    # Payment Gateway - Razorpay (Primary for India)
    RAZORPAY_KEY_ID: str = get_secret('RAZORPAY_KEY_ID', '')
    RAZORPAY_KEY_SECRET: str = get_secret('RAZORPAY_KEY_SECRET', '')
    RAZORPAY_WEBHOOK_SECRET: str = get_secret('RAZORPAY_WEBHOOK_SECRET', '')
    
    # Payment Gateway - Stripe (Fallback for International)
    STRIPE_SECRET_KEY: str = get_secret('STRIPE_SECRET_KEY', '')
    STRIPE_PUBLISHABLE_KEY: str = get_secret('STRIPE_PUBLISHABLE_KEY', '')
    STRIPE_WEBHOOK_SECRET: str = get_secret('STRIPE_WEBHOOK_SECRET', '')
    
    # Application Settings
    APP_URL: str = get_secret('APP_URL', 'http://localhost:8501')
    ENVIRONMENT: str = get_secret('ENVIRONMENT', 'development')
    SECRET_KEY: str = get_secret('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database
    DATABASE_URL: str = get_secret('DATABASE_URL', 'sqlite:///data/app.db')
    
    # Email Settings
    SMTP_HOST: str = get_secret('SMTP_HOST', '')
    SMTP_PORT: int = int(get_secret('SMTP_PORT', '587'))
    SMTP_USER: str = get_secret('SMTP_USER', '')
    SMTP_PASSWORD: str = get_secret('SMTP_PASSWORD', '')
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production"""
        return cls.ENVIRONMENT.lower() == 'production'
    
    @classmethod
    def is_razorpay_configured(cls) -> bool:
        """Check if Razorpay is properly configured"""
        return bool(cls.RAZORPAY_KEY_ID and cls.RAZORPAY_KEY_SECRET)
    
    @classmethod
    def is_stripe_configured(cls) -> bool:
        """Check if Stripe is properly configured"""
        return bool(cls.STRIPE_SECRET_KEY)
    
    @classmethod
    def get_payment_gateway_status(cls) -> dict:
        """Get status of payment gateways"""
        return {
            'razorpay': {
                'configured': cls.is_razorpay_configured(),
                'key_id': cls.RAZORPAY_KEY_ID[:12] + '...' if cls.RAZORPAY_KEY_ID else 'Not set',
                'recommended_for': 'Indian customers'
            },
            'stripe': {
                'configured': cls.is_stripe_configured(),
                'key_id': cls.STRIPE_SECRET_KEY[:12] + '...' if cls.STRIPE_SECRET_KEY else 'Not set',
                'recommended_for': 'International customers'
            }
        }

# Global config instance
config = Config()