"""
Streamlit UI components for upgrade flow and conversion optimization
Handles upgrade modals, pricing displays, and conversion tracking
"""

import streamlit as st
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from auth.models import User, PlanType
from auth.services import subscription_service
from billing.upgrade_flow import upgrade_flow, trial_manager, UpgradePrompt
from billing.subscription_tiers import tier_manager

logger = logging.getLogger(__name__)

class UpgradeUI:
    """UI components for upgrade flow"""
    
    def __init__(self):
        self.pricing_data = self._get_pricing_data()
    
    def _get_pricing_data(self) -> Dict[str, Any]:
        """Get pricing data for all tiers"""
        tiers = tier_manager.get_all_tiers()
        return {tier['plan_type']: tier for tier in tiers}
    
    def render_upgrade_prompt(self, user: User, prompt: UpgradePrompt) -> bool:
        """Render upgrade prompt and return True if user clicked upgrade"""
        # Track prompt shown event
        upgrade_flow.track_conversion_event(
            user_id=user.id,
            event_type="prompt_shown",
            prompt_id=prompt.id,
            variant=prompt.variant
        )
        
        # Style based on urgency level
        if prompt.urgency_level == "high":
            container_style = "border: 2px solid #ff4444; background: #fff5f5; padding: 1rem; border-radius: 10px; margin: 1rem 0;"
            icon = "🚨"
        elif prompt.urgency_level == "medium":
            container_style = "border: 2px solid #ff8800; background: #fff8f0; padding: 1rem; border-radius: 10px; margin: 1rem 0;"
            icon = "⚠️"
        else:
            container_style = "border: 2px solid #0066cc; background: #f0f8ff; padding: 1rem; border-radius: 10px; margin: 1rem 0;"
            icon = "💡"
        
        # Render prompt container
        st.markdown(f'<div style="{container_style}">', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"### {icon} {prompt.title}")
            st.markdown(prompt.message)
            
            # Show discount if applicable
            if prompt.show_discount and prompt.discount_percentage > 0:
                st.markdown(f"**🎉 Limited Time: {prompt.discount_percentage}% OFF!**")
        
        with col2:
            # Upgrade button
            if st.button(prompt.cta_text, type="primary", key=f"upgrade_{prompt.id}"):
                # Track click event
                upgrade_flow.track_conversion_event(
                    user_id=user.id,
                    event_type="prompt_clicked",
                    prompt_id=prompt.id,
                    variant=prompt.variant,
                    target_plan=prompt.target_plan.value
                )
                
                # Set session state to show upgrade modal
                st.session_state.show_upgrade_modal = True
                st.session_state.target_plan = prompt.target_plan
                st.session_state.upgrade_source = prompt.id
                
                st.markdown('</div>', unsafe_allow_html=True)
                return True
            
            # Dismiss option for low urgency prompts
            if prompt.urgency_level == "low":
                if st.button("Maybe Later", key=f"dismiss_{prompt.id}"):
                    upgrade_flow.track_conversion_event(
                        user_id=user.id,
                        event_type="prompt_dismissed",
                        prompt_id=prompt.id,
                        variant=prompt.variant
                    )
        
        st.markdown('</div>', unsafe_allow_html=True)
        return False
    
    def render_usage_warning(self, user: User) -> bool:
        """Render usage warning when approaching limits"""
        subscription = subscription_service.get_user_subscription(user.id)
        if not subscription or subscription.plan.monthly_analysis_limit == -1:
            return False
        
        used = subscription.monthly_analysis_used
        limit = subscription.plan.monthly_analysis_limit
        remaining = limit - used
        usage_percentage = (used / limit) * 100
        
        # Show warning when 80% or more is used
        if usage_percentage >= 80:
            prompt = upgrade_flow.should_show_upgrade_prompt(user, "analysis_limit_warning")
            if prompt:
                return self.render_upgrade_prompt(user, prompt)
        
        return False
    
    def render_usage_exceeded_modal(self, user: User):
        """Render modal when usage limit is exceeded"""
        prompt = upgrade_flow.should_show_upgrade_prompt(user, "analysis_limit_exceeded")
        if prompt:
            # Create modal-like container
            st.markdown("""
            <div style="
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.5);
                z-index: 1000;
                display: flex;
                justify-content: center;
                align-items: center;
            ">
                <div style="
                    background: white;
                    padding: 2rem;
                    border-radius: 15px;
                    max-width: 500px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                ">
            """, unsafe_allow_html=True)
            
            st.markdown(f"## {prompt.title}")
            st.markdown(prompt.message)
            
            # Show pricing comparison
            self._render_pricing_comparison(user, prompt.target_plan)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button(prompt.cta_text, type="primary", use_container_width=True):
                    upgrade_flow.track_conversion_event(
                        user_id=user.id,
                        event_type="prompt_clicked",
                        prompt_id=prompt.id,
                        variant=prompt.variant,
                        target_plan=prompt.target_plan.value
                    )
                    st.session_state.show_upgrade_modal = True
                    st.session_state.target_plan = prompt.target_plan
                    st.rerun()
            
            with col2:
                if st.button("Start Free Trial", use_container_width=True):
                    if trial_manager.start_trial(user.id, prompt.target_plan):
                        st.success("✅ Trial started! You now have unlimited access.")
                        st.session_state.show_usage_exceeded = False
                        st.rerun()
                    else:
                        st.error("Failed to start trial. Please try again.")
            
            st.markdown("</div></div>", unsafe_allow_html=True)
    
    def render_feature_gate_prompt(self, user: User, feature: str) -> bool:
        """Render feature gate prompt for premium features"""
        context_map = {
            "bulk_upload": "bulk_upload_attempt",
            "premium_ai": "premium_ai_attempt",
            "api_access": "api_access_attempt"
        }
        
        context = context_map.get(feature)
        if not context:
            return False
        
        prompt = upgrade_flow.should_show_upgrade_prompt(user, context)
        if prompt:
            return self.render_upgrade_prompt(user, prompt)
        
        return False
    
    def render_upgrade_modal(self, user: User, target_plan: PlanType = None):
        """Render full upgrade modal with pricing and features"""
        if not st.session_state.get('show_upgrade_modal', False):
            return
        
        # Modal container
        with st.container():
            st.markdown("## 🚀 Choose Your Plan")
            
            # Get current subscription
            subscription = subscription_service.get_user_subscription(user.id)
            current_plan = subscription.plan.plan_type if subscription else PlanType.FREE
            
            # Render pricing cards
            self._render_pricing_cards(user, current_plan, target_plan)
            
            # Close modal button
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("Close", use_container_width=True):
                    st.session_state.show_upgrade_modal = False
                    st.rerun()
    
    def _render_pricing_cards(self, user: User, current_plan: PlanType, highlight_plan: PlanType = None):
        """Render pricing cards for all plans"""
        plans_to_show = [PlanType.FREE, PlanType.PROFESSIONAL, PlanType.BUSINESS]
        
        cols = st.columns(len(plans_to_show))
        
        for i, plan_type in enumerate(plans_to_show):
            with cols[i]:
                self._render_single_pricing_card(user, plan_type, current_plan, highlight_plan)
    
    def _render_single_pricing_card(self, user: User, plan_type: PlanType, 
                                   current_plan: PlanType, highlight_plan: PlanType = None):
        """Render a single pricing card"""
        plan_data = self.pricing_data[plan_type]
        
        # Card styling
        is_current = plan_type == current_plan
        is_highlighted = plan_type == highlight_plan
        
        if is_highlighted:
            card_style = "border: 3px solid #ff6b35; background: #fff8f5;"
        elif is_current:
            card_style = "border: 2px solid #28a745; background: #f8fff8;"
        else:
            card_style = "border: 1px solid #ddd; background: white;"
        
        st.markdown(f"""
        <div style="{card_style} padding: 1.5rem; border-radius: 10px; margin: 0.5rem 0; height: 400px;">
        """, unsafe_allow_html=True)
        
        # Plan header
        if is_highlighted:
            st.markdown("### 🌟 **RECOMMENDED**")
        
        st.markdown(f"### {plan_data['name']}")
        
        # Pricing
        if plan_data['price_monthly'] == 0:
            st.markdown("## **FREE**")
        else:
            st.markdown(f"## **${plan_data['price_monthly']:.0f}**/month")
            if plan_data['price_annual'] < plan_data['price_monthly'] * 12:
                annual_savings = (plan_data['price_monthly'] * 12) - plan_data['price_annual']
                st.markdown(f"*Save ${annual_savings:.0f} with annual billing*")
        
        # Key features
        st.markdown("**Key Features:**")
        
        key_features = self._get_key_features(plan_type)
        for feature in key_features[:4]:  # Show top 4 features
            st.markdown(f"✅ {feature}")
        
        # Action button
        if is_current:
            st.success("✅ Current Plan")
        elif plan_type == PlanType.FREE:
            st.info("Always Free")
        else:
            # Check if user can upgrade to this plan
            can_upgrade = tier_manager.can_upgrade_to(current_plan, plan_type)
            
            if can_upgrade:
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button(f"Upgrade", key=f"upgrade_to_{plan_type.value}", 
                               type="primary", use_container_width=True):
                        self._handle_upgrade_click(user, plan_type)
                
                with col2:
                    if st.button(f"Try Free", key=f"trial_{plan_type.value}", 
                               use_container_width=True):
                        self._handle_trial_click(user, plan_type)
            else:
                st.info("Contact Sales")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    def _get_key_features(self, plan_type: PlanType) -> list:
        """Get key features for a plan type"""
        feature_map = {
            PlanType.FREE: [
                "3 analyses per month",
                "Basic AI analysis",
                "PDF download",
                "Community support"
            ],
            PlanType.PROFESSIONAL: [
                "Unlimited analyses",
                "Premium AI models",
                "All export formats",
                "Priority processing",
                "Email support"
            ],
            PlanType.BUSINESS: [
                "Everything in Professional",
                "Team collaboration",
                "Bulk upload",
                "Analytics dashboard",
                "API access",
                "Phone support"
            ]
        }
        
        return feature_map.get(plan_type, [])
    
    def _render_pricing_comparison(self, user: User, target_plan: PlanType):
        """Render pricing comparison for current vs target plan"""
        subscription = subscription_service.get_user_subscription(user.id)
        current_plan = subscription.plan.plan_type if subscription else PlanType.FREE
        
        current_data = self.pricing_data[current_plan]
        target_data = self.pricing_data[target_plan]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Current Plan**")
            st.markdown(f"{current_data['name']}")
            if current_data['price_monthly'] == 0:
                st.markdown("FREE")
            else:
                st.markdown(f"${current_data['price_monthly']:.0f}/month")
        
        with col2:
            st.markdown("**Upgrade To**")
            st.markdown(f"**{target_data['name']}**")
            st.markdown(f"**${target_data['price_monthly']:.0f}/month**")
    
    def _handle_upgrade_click(self, user: User, target_plan: PlanType):
        """Handle upgrade button click"""
        upgrade_flow.track_conversion_event(
            user_id=user.id,
            event_type="upgrade_initiated",
            target_plan=target_plan.value,
            source_plan=subscription_service.get_user_subscription(user.id).plan.plan_type.value
        )
        
        # In a real implementation, this would redirect to Stripe checkout
        st.success(f"Redirecting to checkout for {target_plan.value} plan...")
        
        # For demo purposes, simulate successful upgrade
        st.session_state.simulated_upgrade = target_plan
        st.session_state.show_upgrade_success = True
    
    def _handle_trial_click(self, user: User, target_plan: PlanType):
        """Handle trial button click"""
        if trial_manager.start_trial(user.id, target_plan):
            upgrade_flow.track_conversion_event(
                user_id=user.id,
                event_type="trial_started",
                target_plan=target_plan.value
            )
            
            st.success(f"✅ {target_plan.value.title()} trial started! You now have 14 days of unlimited access.")
            st.session_state.show_upgrade_modal = False
            st.rerun()
        else:
            st.error("Failed to start trial. Please try again.")
    
    def render_trial_status(self, user: User):
        """Render trial status information"""
        trial_status = trial_manager.get_trial_status(user.id)
        
        if trial_status:
            days_remaining = trial_status['days_remaining']
            
            if days_remaining <= 3:
                # Show urgent trial expiry prompt
                st.warning(f"⏰ Your {trial_status['plan_name']} trial expires in {days_remaining} days!")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Continue with Paid Plan", type="primary"):
                        st.session_state.show_upgrade_modal = True
                        st.session_state.target_plan = PlanType.PROFESSIONAL
                        st.rerun()
                
                with col2:
                    st.markdown(f"**Usage:** {trial_status['usage_this_period']} analyses")
            else:
                # Show trial info
                st.info(f"🎉 You're on a {trial_status['plan_name']} trial! {days_remaining} days remaining.")
    
    def render_watermarked_pdf_notice(self):
        """Render notice about watermarked PDFs for free users"""
        st.info("""
        📄 **Free Plan Notice**: PDF reports include a watermark. 
        Upgrade to Professional to remove watermarks and access all export formats.
        """)
        
        if st.button("Remove Watermarks - Upgrade Now", type="primary"):
            st.session_state.show_upgrade_modal = True
            st.session_state.target_plan = PlanType.PROFESSIONAL
            st.rerun()

# Service instance
upgrade_ui = UpgradeUI()