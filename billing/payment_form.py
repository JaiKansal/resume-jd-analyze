"""
Payment Form UI for Resume + JD Analyzer
Handles Razorpay payment processing with Indian pricing
"""

import streamlit as st
import logging
import os
from typing import Dict, Any, Optional
from datetime import datetime

from auth.models import User, PlanType
from auth.services import subscription_service
from billing.razorpay_service import razorpay_service
from billing.payment_gateway import payment_gateway, PaymentGateway

logger = logging.getLogger(__name__)

class PaymentForm:
    """Payment form UI components"""
    
    def __init__(self):
        self.pricing = {
            PlanType.PROFESSIONAL: {
                'name': 'Professional',
                'price_monthly': 1499,  # INR
                'price_annual': 14990,  # INR
                'features': [
                    'Unlimited analyses',
                    'Advanced AI insights',
                    'All export formats',
                    'Email support',
                    'Resume templates'
                ]
            },
            PlanType.BUSINESS: {
                'name': 'Business',
                'price_monthly': 7999,  # INR
                'price_annual': 79990,  # INR
                'features': [
                    'Everything in Professional',
                    'Team collaboration (5 seats)',
                    'Bulk processing',
                    'Analytics dashboard',
                    'API access',
                    'Phone support'
                ]
            }
        }
    
    def render_payment_form(self, user: User, plan_type: PlanType):
        """Render the main payment form"""
        if not st.session_state.get('show_payment_form', False):
            return
        
        st.markdown("## 💳 Complete Your Payment")
        
        # Get plan details
        plan_data = self.pricing.get(plan_type)
        if not plan_data:
            st.error("Invalid plan selected")
            return
        
        # Billing cycle selection
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            billing_cycle = st.radio(
                "Choose billing cycle:",
                ["Monthly", "Annual (Save 17%)"],
                horizontal=True,
                key="billing_cycle_payment"
            )
        
        is_annual = "Annual" in billing_cycle
        amount = plan_data['price_annual'] if is_annual else plan_data['price_monthly']
        period = 'year' if is_annual else 'month'
        
        # Order summary
        self._render_order_summary(plan_data, amount, period, is_annual)
        
        # Payment methods info
        self._render_payment_methods()
        
        # Payment button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("💳 Pay with Razorpay", type="primary", use_container_width=True):
                self._process_payment(user, plan_type, amount, period)
        
        # Back button
        if st.button("← Back to Plans"):
            st.session_state.show_payment_form = False
            st.session_state.show_upgrade_modal = True
            st.rerun()
    
    def _render_order_summary(self, plan_data: Dict, amount: int, period: str, is_annual: bool):
        """Render order summary"""
        st.markdown("### 📋 Order Summary")
        
        with st.container():
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**{plan_data['name']} Plan** ({period}ly)")
                if is_annual:
                    monthly_price = plan_data['price_monthly']
                    savings = (monthly_price * 12) - amount
                    st.markdown(f"<small style='color: #28a745;'>You save ₹{savings:,} with annual billing!</small>", unsafe_allow_html=True)
                
                # Show key features
                st.markdown("**Includes:**")
                for feature in plan_data['features'][:3]:
                    st.markdown(f"✅ {feature}")
            
            with col2:
                st.markdown(f"### ₹{amount:,}")
                st.markdown(f"<small>per {period}</small>", unsafe_allow_html=True)
        
        st.markdown("---")
    
    def _render_payment_methods(self):
        """Render available payment methods"""
        st.markdown("### 💳 Payment Methods Available")
        
        payment_methods = [
            {"icon": "💳", "name": "Credit/Debit Cards", "desc": "Visa, Mastercard, RuPay"},
            {"icon": "📱", "name": "UPI", "desc": "Google Pay, PhonePe, Paytm"},
            {"icon": "🏦", "name": "Net Banking", "desc": "All major banks"},
            {"icon": "💰", "name": "Wallets", "desc": "Paytm, Mobikwik, etc."}
        ]
        
        cols = st.columns(len(payment_methods))
        for i, method in enumerate(payment_methods):
            with cols[i]:
                st.markdown(f"{method['icon']} **{method['name']}**")
                st.markdown(f"<small>{method['desc']}</small>", unsafe_allow_html=True)
        
        st.markdown("---")
    
    def _process_payment(self, user: User, plan_type: PlanType, amount: int, period: str):
        """Process the payment with Razorpay"""
        try:
            # Check if Razorpay is configured
            if not razorpay_service.client:
                st.error("❌ Payment system not configured. Please contact support.")
                st.info("**Debug Info**: Razorpay client not initialized. Check API keys in secrets.")
                return
            
            # Show processing message
            with st.spinner("Setting up payment..."):
                # Try to create payment link directly (without customer creation first)
                description = f"{plan_type.value.title()} Plan - {period}ly subscription"
                
                # Create payment link with simplified approach
                payment_link = self._create_simple_payment_link(
                    amount=amount * 100,  # Convert to paisa
                    description=description,
                    customer_email=user.email,
                    plan_type=plan_type
                )
                
                if payment_link:
                    st.success("✅ Payment link created successfully!")
                    
                    # Show payment link
                    st.markdown(f"""
                    ### 🚀 Complete Your Payment
                    
                    Click the link below to complete your payment securely:
                    
                    **[Pay ₹{amount:,} with Razorpay →]({payment_link['short_url']})**
                    """)
                    
                    # Show QR code if available
                    if 'qr_code' in payment_link:
                        st.image(payment_link['qr_code'], caption="Scan to pay with UPI", width=200)
                    
                    # Payment instructions
                    with st.expander("📋 Payment Instructions"):
                        st.markdown("""
                        1. **Click the payment link** above
                        2. **Choose your payment method** (UPI, Card, Net Banking, etc.)
                        3. **Complete the payment** securely through Razorpay
                        4. **Your account will be upgraded** automatically
                        5. **You'll receive a confirmation email**
                        
                        **Need help?** Contact support at support@resumeanalyzer.com
                        """)
                    
                    # Track payment initiation
                    st.session_state.payment_initiated = True
                    st.session_state.payment_link = payment_link['short_url']
                    
                else:
                    st.error("❌ Failed to create payment link.")
                    
                    # Show debug information
                    with st.expander("🔧 Debug Information"):
                        st.write("**Razorpay Configuration:**")
                        st.write(f"- Key ID: {razorpay_service.key_id[:12]}..." if razorpay_service.key_id else "- Key ID: Not set")
                        st.write(f"- Key Secret: {'Set' if razorpay_service.key_secret else 'Not set'}")
                        st.write(f"- Client: {'Initialized' if razorpay_service.client else 'Not initialized'}")
                        
                        st.write("**User Information:**")
                        st.write(f"- Email: {user.email}")
                        st.write(f"- Plan: {plan_type.value}")
                        st.write(f"- Amount: ₹{amount:,}")
                    
                    st.info("Please check your Razorpay configuration in Streamlit Cloud secrets.")
                
        except Exception as e:
            logger.error(f"Payment processing error: {e}")
            st.error(f"❌ Payment error: {str(e)}")
            
            # Show debug information
            with st.expander("🔧 Debug Information"):
                st.write(f"**Error Details:** {str(e)}")
                st.write(f"**Razorpay Available:** {razorpay_service.client is not None}")
    
    def _create_simple_payment_link(self, amount: int, description: str, 
                                   customer_email: str, plan_type: PlanType) -> Optional[Dict[str, Any]]:
        """Create a simple payment link without customer creation"""
        if not razorpay_service.client:
            return None
        
        try:
            payment_link_data = {
                'amount': amount,  # Amount in paisa
                'currency': 'INR',
                'accept_partial': False,
                'description': description,
                'customer': {
                    'email': customer_email
                },
                'notify': {
                    'sms': False,  # Disable SMS to avoid issues
                    'email': True
                },
                'reminder_enable': True,
                'notes': {
                    'plan_type': plan_type.value,
                    'product': 'resume_analyzer'
                },
                'callback_url': f"{os.getenv('APP_URL', 'http://localhost:8501')}/payment/success",
                'callback_method': 'get'
            }
            
            payment_link = razorpay_service.client.payment_link.create(payment_link_data)
            logger.info(f"Created payment link: {payment_link['id']}")
            return payment_link
            
        except Exception as e:
            logger.error(f"Failed to create simple payment link: {e}")
            return None
    
    def render_payment_success(self):
        """Render payment success page"""
        if not st.session_state.get('payment_success', False):
            return
        
        st.success("🎉 Payment Successful!")
        st.markdown("### Thank you for upgrading!")
        
        st.markdown("""
        Your account has been upgraded and you now have access to:
        
        ✅ **Unlimited resume analyses**  
        ✅ **Advanced AI insights**  
        ✅ **All export formats**  
        ✅ **Priority support**  
        ✅ **Premium features**
        
        **What's next?**
        - Start analyzing resumes with unlimited access
        - Explore advanced features in your dashboard
        - Contact support if you need any help
        """)
        
        if st.button("Continue to Dashboard", type="primary"):
            st.session_state.payment_success = False
            st.session_state.show_payment_form = False
            st.rerun()
    
    def render_payment_failed(self):
        """Render payment failed page"""
        if not st.session_state.get('payment_failed', False):
            return
        
        st.error("❌ Payment Failed")
        st.markdown("### Don't worry, let's try again")
        
        st.markdown("""
        Your payment could not be processed. This might be due to:
        
        • **Insufficient funds** in your account
        • **Bank security restrictions** on online payments
        • **Network connectivity issues**
        • **Card/UPI limits** exceeded
        
        ### What you can do:
        
        1. **Try a different payment method** (UPI, Net Banking, different card)
        2. **Contact your bank** if using a card
        3. **Check your internet connection**
        4. **Try again after some time**
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Try Payment Again", type="primary", use_container_width=True):
                st.session_state.payment_failed = False
                st.rerun()
        
        with col2:
            if st.button("Contact Support", use_container_width=True):
                st.markdown("""
                **📧 Email**: support@resumeanalyzer.com  
                **💬 Chat**: Use the feedback widget in the sidebar  
                **📞 Phone**: Available for Business & Enterprise plans
                """)

# Global instance
payment_form = PaymentForm()