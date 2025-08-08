"""
Registration and onboarding flow for Resume + JD Analyzer
Handles multi-step registration, email verification, and user onboarding
"""

import streamlit as st
import re
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
import logging

from auth.postgresql_service import postgresql_auth_service
from auth.services import user_service, subscription_service, session_service
from auth.models import UserRole, PlanType

logger = logging.getLogger(__name__)

def get_auth_service():
    """Get the appropriate auth service based on configuration"""
    try:
        # Check if DATABASE_URL is available and reinitialize if needed
        import os
        database_url = os.getenv('DATABASE_URL')
        if database_url and 'postgresql' in database_url.lower():
            # Reinitialize PostgreSQL service if DATABASE_URL was set after import
            if not postgresql_auth_service.is_postgresql:
                postgresql_auth_service.database_url = database_url
                postgresql_auth_service.is_postgresql = True
                logger.info("✅ PostgreSQL service reinitialized with DATABASE_URL")
            
            return postgresql_auth_service
    except Exception as e:
        logger.warning(f"PostgreSQL service not available: {e}")
    
    logger.info("Using fallback SQLite user service")
    return user_service

# Use the fallback service
auth_service = get_auth_service()

class RegistrationFlow:
    """Handles the multi-step registration and onboarding process"""
    
    def __init__(self):
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """Initialize session state for registration flow"""
        if 'registration_step' not in st.session_state:
            st.session_state.registration_step = 1
        if 'registration_data' not in st.session_state:
            st.session_state.registration_data = {}
        if 'user_authenticated' not in st.session_state:
            st.session_state.user_authenticated = False
        if 'current_user' not in st.session_state:
            st.session_state.current_user = None
        if 'user_session' not in st.session_state:
            st.session_state.user_session = None
    
    def validate_email(self, email: str) -> Tuple[bool, str]:
        """Validate email format and availability"""
        if not email:
            return False, "Email is required"
        
        # Basic email format validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False, "Please enter a valid email address"
        
        # Check if email already exists
        existing_user = auth_service.get_user_by_email(email)
        if existing_user:
            return False, "An account with this email already exists"
        
        return True, ""
    
    def validate_password(self, password: str, confirm_password: str) -> Tuple[bool, str]:
        """Validate password strength and confirmation"""
        if not password:
            return False, "Password is required"
        
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
        
        if password != confirm_password:
            return False, "Passwords do not match"
        
        return True, ""
    
    def render_step_1_user_type(self):
        """Step 1: User type selection"""
        st.markdown("### 👤 What describes you best?")
        st.markdown("This helps us customize your experience and provide relevant features.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🎯 Job Seeker", use_container_width=True, help="Looking for a job or career change"):
                st.session_state.registration_data['user_type'] = 'individual'
                st.session_state.registration_data['role'] = UserRole.INDIVIDUAL
                st.session_state.registration_step = 2
                st.rerun()
        
        with col2:
            if st.button("🏢 HR Professional", use_container_width=True, help="Hiring manager or HR professional"):
                st.session_state.registration_data['user_type'] = 'hr_professional'
                st.session_state.registration_data['role'] = UserRole.HR_MANAGER
                st.session_state.registration_step = 2
                st.rerun()
        
        st.markdown("---")
        
        col3, col4 = st.columns(2)
        
        with col3:
            if st.button("🚀 Startup Founder", use_container_width=True, help="Building a team for your startup"):
                st.session_state.registration_data['user_type'] = 'startup'
                st.session_state.registration_data['role'] = UserRole.ADMIN
                st.session_state.registration_step = 2
                st.rerun()
        
        with col4:
            if st.button("🏭 Enterprise", use_container_width=True, help="Large organization with complex hiring needs"):
                st.session_state.registration_data['user_type'] = 'enterprise'
                st.session_state.registration_data['role'] = UserRole.ENTERPRISE_ADMIN
                st.session_state.registration_step = 2
                st.rerun()
    
    def render_step_2_basic_info(self):
        """Step 2: Basic information collection"""
        user_type = st.session_state.registration_data.get('user_type', 'individual')
        
        st.markdown("### 📝 Tell us about yourself")
        
        # Show selected user type
        type_labels = {
            'individual': '🎯 Job Seeker',
            'hr_professional': '🏢 HR Professional',
            'startup': '🚀 Startup Founder',
            'enterprise': '🏭 Enterprise'
        }
        st.info(f"Selected: {type_labels.get(user_type, 'Unknown')}")
        
        with st.form("basic_info_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                first_name = st.text_input("First Name *", placeholder="John")
                email = st.text_input("Email Address *", placeholder="john@example.com")
                password = st.text_input("Password *", type="password", help="Min 8 chars, uppercase, lowercase, number, special char")
            
            with col2:
                last_name = st.text_input("Last Name *", placeholder="Doe")
                phone = st.text_input("Phone Number", placeholder="+1 (555) 123-4567")
                confirm_password = st.text_input("Confirm Password *", type="password")
            
            # Company information (conditional)
            if user_type != 'individual':
                st.markdown("#### 🏢 Company Information")
                col3, col4 = st.columns(2)
                
                with col3:
                    company_name = st.text_input("Company Name *", placeholder="Acme Corp")
                
                with col4:
                    country = st.selectbox("Country *", [
                        "United States", "Canada", "United Kingdom", "Australia",
                        "Germany", "France", "Netherlands", "Sweden", "India",
                        "Singapore", "Japan", "Other"
                    ])
            else:
                company_name = st.text_input("Current/Target Company", placeholder="Optional")
                country = st.selectbox("Country", [
                    "United States", "Canada", "United Kingdom", "Australia",
                    "Germany", "France", "Netherlands", "Sweden", "India",
                    "Singapore", "Japan", "Other"
                ])
            
            # Terms and privacy
            st.markdown("#### 📋 Terms & Privacy")
            terms_accepted = st.checkbox("I agree to the Terms of Service and Privacy Policy *")
            marketing_consent = st.checkbox("I'd like to receive product updates and career tips via email")
            
            # Submit button
            submitted = st.form_submit_button("Continue to Plan Selection", type="primary", use_container_width=True)
            
            if submitted:
                # Validation
                errors = []
                
                if not first_name.strip():
                    errors.append("First name is required")
                if not last_name.strip():
                    errors.append("Last name is required")
                if not email.strip():
                    errors.append("Email is required")
                if not password:
                    errors.append("Password is required")
                if not terms_accepted:
                    errors.append("You must accept the Terms of Service")
                
                # Email validation
                email_valid, email_error = self.validate_email(email)
                if not email_valid:
                    errors.append(email_error)
                
                # Password validation
                password_valid, password_error = self.validate_password(password, confirm_password)
                if not password_valid:
                    errors.append(password_error)
                
                # Company name validation for non-individuals
                if user_type != 'individual' and not company_name.strip():
                    errors.append("Company name is required")
                
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    # Store form data
                    st.session_state.registration_data.update({
                        'first_name': first_name.strip(),
                        'last_name': last_name.strip(),
                        'email': email.strip().lower(),
                        'password': password,
                        'phone': phone.strip() if phone else None,
                        'company_name': company_name.strip() if company_name else None,
                        'country': country,
                        'marketing_consent': marketing_consent
                    })
                    
                    st.session_state.registration_step = 3
                    st.rerun()
        
        # Back button
        if st.button("← Back to User Type", type="secondary"):
            st.session_state.registration_step = 1
            st.rerun()
    
    def render_step_3_plan_selection(self):
        """Step 3: Subscription plan selection"""
        user_type = st.session_state.registration_data.get('user_type', 'individual')
        
        st.markdown("### 💳 Choose Your Plan")
        st.markdown("Start with our free tier and upgrade anytime as your needs grow.")
        
        # Get available plans
        plans = subscription_service.get_all_plans()
        
        if not plans:
            st.error("Unable to load subscription plans. Please try again later.")
            return
        
        # Filter plans based on user type
        if user_type == 'individual':
            recommended_plans = ['free', 'professional']
        elif user_type == 'hr_professional':
            recommended_plans = ['professional', 'business']
        elif user_type == 'startup':
            recommended_plans = ['business', 'professional']
        else:  # enterprise
            recommended_plans = ['enterprise', 'business']
        
        # Display plans
        cols = st.columns(len(plans))
        
        for i, plan in enumerate(plans):
            with cols[i]:
                # Highlight recommended plans
                is_recommended = plan.plan_type.value in recommended_plans
                
                if is_recommended:
                    st.markdown(f"<div style='border: 2px solid #28a745; border-radius: 10px; padding: 1rem; background-color: #f8fff9;'>", unsafe_allow_html=True)
                    if plan.plan_type.value == recommended_plans[0]:
                        st.markdown("**🌟 RECOMMENDED**")
                else:
                    st.markdown(f"<div style='border: 1px solid #dee2e6; border-radius: 10px; padding: 1rem;'>", unsafe_allow_html=True)
                
                st.markdown(f"### {plan.name}")
                
                if plan.price_monthly == 0:
                    st.markdown("**FREE**")
                else:
                    st.markdown(f"**${plan.price_monthly:.0f}/month**")
                    if plan.price_annual < plan.price_monthly * 12:
                        savings = (plan.price_monthly * 12 - plan.price_annual) / (plan.price_monthly * 12) * 100
                        st.markdown(f"*${plan.price_annual:.0f}/year (Save {savings:.0f}%)*")
                
                # Plan features
                features = plan.features
                key_features = []
                
                if plan.plan_type == PlanType.FREE:
                    key_features = [
                        f"✅ {plan.monthly_analysis_limit} analyses/month",
                        "✅ Basic reports",
                        "✅ PDF download",
                        "✅ Community support"
                    ]
                elif plan.plan_type == PlanType.PROFESSIONAL:
                    key_features = [
                        "✅ Unlimited analyses",
                        "✅ Premium AI models",
                        "✅ All report formats",
                        "✅ Priority processing",
                        "✅ Email support"
                    ]
                elif plan.plan_type == PlanType.BUSINESS:
                    key_features = [
                        "✅ Team collaboration",
                        "✅ Bulk processing",
                        "✅ Analytics dashboard",
                        "✅ API access",
                        "✅ Phone support",
                        f"✅ {features.get('seats', 5)} team seats"
                    ]
                elif plan.plan_type == PlanType.ENTERPRISE:
                    key_features = [
                        "✅ Unlimited seats",
                        "✅ SSO integration",
                        "✅ Custom integrations",
                        "✅ Dedicated support",
                        "✅ SLA guarantee",
                        "✅ White-label options"
                    ]
                
                for feature in key_features:
                    st.markdown(feature)
                
                # Select button
                if st.button(f"Select {plan.name}", key=f"select_{plan.id}", use_container_width=True):
                    st.session_state.registration_data['selected_plan'] = plan.id
                    st.session_state.registration_step = 4
                    st.rerun()
                
                st.markdown("</div>", unsafe_allow_html=True)
        
        # Back button
        if st.button("← Back to Basic Info", type="secondary"):
            st.session_state.registration_step = 2
            st.rerun()
    
    def render_step_4_confirmation(self):
        """Step 4: Registration confirmation and account creation"""
        st.markdown("### ✅ Confirm Your Registration")
        
        data = st.session_state.registration_data
        selected_plan_id = data.get('selected_plan')
        
        # Find selected plan
        plans = subscription_service.get_all_plans()
        selected_plan = next((p for p in plans if p.id == selected_plan_id), None)
        
        if not selected_plan:
            st.error("Selected plan not found. Please go back and select a plan.")
            return
        
        # Display summary
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### 👤 Account Information")
            st.write(f"**Name:** {data['first_name']} {data['last_name']}")
            st.write(f"**Email:** {data['email']}")
            if data.get('company_name'):
                st.write(f"**Company:** {data['company_name']}")
            st.write(f"**Country:** {data['country']}")
            st.write(f"**User Type:** {data['user_type'].replace('_', ' ').title()}")
        
        with col2:
            st.markdown("#### 💳 Selected Plan")
            st.write(f"**Plan:** {selected_plan.name}")
            if selected_plan.price_monthly == 0:
                st.write("**Price:** FREE")
            else:
                st.write(f"**Price:** ${selected_plan.price_monthly:.0f}/month")
            
            if selected_plan.monthly_analysis_limit == -1:
                st.write("**Analyses:** Unlimited")
            else:
                st.write(f"**Analyses:** {selected_plan.monthly_analysis_limit}/month")
        
        # Create account button
        if st.button("🚀 Create My Account", type="primary", use_container_width=True):
            with st.spinner("Creating your account..."):
                try:
                    # Create user account
                    user = auth_service.create_user(
                        email=data['email'],
                        password=data['password'],
                        first_name=data['first_name'],
                        last_name=data['last_name'],
                        company_name=data.get('company_name'),
                        role=data['role'],
                        phone=data.get('phone'),
                        country=data['country']
                    )
                    
                    if user:
                        # Store user ID for payment step
                        st.session_state.registration_data['user_id'] = user.id
                        
                        # Check if selected plan requires payment
                        if selected_plan.plan_type != PlanType.FREE:
                            # Redirect to payment step for paid plans
                            st.session_state.registration_step = 5
                            st.rerun()
                        else:
                            # For free plan, create subscription directly
                            subscription = subscription_service.create_subscription(
                                user.id, 
                                selected_plan.id
                            )
                            
                            # Create session and complete registration
                            session = session_service.create_session(user.id)
                            
                            # Update session state
                            st.session_state.user_authenticated = True
                            st.session_state.current_user = user
                            st.session_state.user_session = session
                            st.session_state.registration_step = 6  # Skip payment step for free plan
                        
                        # Track conversion event
                        self.track_conversion_event(user.id, 'registration_completed', {
                            'user_type': data['user_type'],
                            'selected_plan': selected_plan.plan_type.value,
                            'marketing_consent': data.get('marketing_consent', False)
                        })
                        
                        st.success("🎉 Account created successfully!")
                        st.rerun()
                    
                    else:
                        st.error("Failed to create account. Please try again.")
                
                except Exception as e:
                    logger.error(f"Registration failed: {e}")
                    st.error("An error occurred during registration. Please try again.")
        
        # Back button
        if st.button("← Back to Plan Selection", type="secondary"):
            st.session_state.registration_step = 3
            st.rerun()
    
    def render_step_5_payment(self):
        """Step 5: Payment for paid plans"""
        data = st.session_state.registration_data
        selected_plan_id = data.get('selected_plan')
        user_id = data.get('user_id')
        
        # Find selected plan
        plans = subscription_service.get_all_plans()
        selected_plan = next((p for p in plans if p.id == selected_plan_id), None)
        
        if not selected_plan:
            st.error("Selected plan not found. Please contact support.")
            return
        
        st.markdown("### 💳 Complete Your Payment")
        st.markdown(f"You've selected the **{selected_plan.name}** plan. Please complete your payment to activate your account.")
        
        # Payment summary
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### 📋 Payment Summary")
            st.write(f"**Plan:** {selected_plan.name}")
            st.write(f"**Price:** ₹{selected_plan.price_monthly:,.0f}/month")
            if selected_plan.monthly_analysis_limit == -1:
                st.write("**Analyses:** Unlimited")
            else:
                st.write(f"**Analyses:** {selected_plan.monthly_analysis_limit}/month")
            
            # Key features
            st.markdown("**Includes:**")
            if selected_plan.plan_type == PlanType.PROFESSIONAL:
                features = ["✅ Unlimited analyses", "✅ Advanced AI insights", "✅ All export formats", "✅ Email support"]
            elif selected_plan.plan_type == PlanType.BUSINESS:
                features = ["✅ Team collaboration", "✅ Bulk processing", "✅ Analytics dashboard", "✅ API access"]
            elif selected_plan.plan_type == PlanType.ENTERPRISE:
                features = ["✅ Unlimited seats", "✅ SSO integration", "✅ Custom integrations", "✅ Dedicated support"]
            else:
                features = ["✅ Premium features"]
            
            for feature in features:
                st.markdown(feature)
        
        with col2:
            st.markdown("#### 💰 Total")
            st.markdown(f"### ₹{selected_plan.price_monthly:,.0f}")
            st.markdown("*per month*")
            
            # Payment methods
            st.markdown("**Payment Methods:**")
            st.markdown("💳 Credit/Debit Cards")
            st.markdown("📱 UPI")
            st.markdown("🏦 Net Banking")
            st.markdown("💰 Wallets")
        
        st.markdown("---")
        
        # Payment button
        if st.button("💳 Pay with Razorpay", type="primary", use_container_width=True):
            try:
                # Get user object
                user = user_service.get_user_by_id(user_id)
                if not user:
                    st.error("User not found. Please contact support.")
                    return
                
                # Create Razorpay payment link
                from billing.razorpay_service import razorpay_service
                
                description = f"{selected_plan.name} Plan - Monthly subscription"
                payment_link = razorpay_service.create_payment_link(
                    amount=int(selected_plan.price_monthly * 100),  # Convert to paisa
                    description=description,
                    customer_email=user.email,
                    plan_type=selected_plan.plan_type
                )
                
                if payment_link:
                    st.success("✅ Payment link created successfully!")
                    
                    # Store payment info for completion
                    st.session_state.registration_data['payment_link'] = payment_link['short_url']
                    st.session_state.registration_data['payment_id'] = payment_link['id']
                    
                    # Show payment link
                    st.markdown(f"""
                    ### 🚀 Complete Your Payment
                    
                    Click the link below to complete your payment securely:
                    
                    **[Pay ₹{selected_plan.price_monthly:,.0f} with Razorpay →]({payment_link['short_url']})**
                    """)
                    
                    # Payment instructions
                    with st.expander("📋 Payment Instructions"):
                        st.markdown("""
                        1. **Click the payment link** above
                        2. **Choose your payment method** (UPI, Card, Net Banking, etc.)
                        3. **Complete the payment** securely through Razorpay
                        4. **Return to this page** after successful payment
                        5. **Click "I've Completed Payment"** below
                        
                        **Need help?** Contact support at support@resumeanalyzer.com
                        """)
                    
                    # Payment completion button
                    if st.button("✅ I've Completed Payment", type="secondary", use_container_width=True):
                        # In a real implementation, you would verify the payment status
                        # For now, we'll create the subscription and proceed
                        
                        # Create subscription
                        subscription = subscription_service.create_subscription(
                            user_id, 
                            selected_plan.id
                        )
                        
                        if subscription:
                            # Create session
                            session = session_service.create_session(user_id)
                            
                            # Update session state
                            st.session_state.user_authenticated = True
                            st.session_state.current_user = user
                            st.session_state.user_session = session
                            
                            # Move to welcome step
                            st.session_state.registration_step = 6
                            st.success("🎉 Payment successful! Welcome to your premium account!")
                            st.rerun()
                        else:
                            st.error("Failed to create subscription. Please contact support.")
                else:
                    st.error("❌ Failed to create payment link. Please try again.")
                    
            except Exception as e:
                st.error(f"❌ Payment error: {str(e)}")
        
        # Back to free plan option
        st.markdown("---")
        if st.button("← Start with Free Plan Instead", type="secondary"):
            # Find free plan
            free_plan = next((p for p in plans if p.plan_type == PlanType.FREE), None)
            if free_plan:
                # Update selected plan to free
                st.session_state.registration_data['selected_plan'] = free_plan.id
                
                # Create subscription for free plan
                subscription = subscription_service.create_subscription(
                    user_id, 
                    free_plan.id
                )
                
                if subscription:
                    # Get user object
                    user = user_service.get_user_by_id(user_id)
                    
                    # Create session
                    session = session_service.create_session(user_id)
                    
                    # Update session state
                    st.session_state.user_authenticated = True
                    st.session_state.current_user = user
                    st.session_state.user_session = session
                    
                    # Move to welcome step
                    st.session_state.registration_step = 6
                    st.rerun()
    
    def render_step_6_welcome_onboarding(self):
        """Step 6: Welcome and onboarding"""
        user = st.session_state.current_user
        
        st.balloons()
        
        st.markdown("### 🎉 Welcome to Resume + JD Analyzer!")
        st.markdown(f"Hi **{user.first_name if user and user.first_name else 'User'}**! Your account has been created successfully.")
        
        # Email verification notice
        if user and not getattr(user, 'email_verified', False):
            st.info("📧 **Email Verification Required**")
            st.markdown(f"We've sent a verification email to **{user.email if user and user.email else 'your email'}**. Please check your inbox and click the verification link to activate all features.")
        
        # Onboarding based on user type
        user_type = st.session_state.registration_data.get('user_type', 'individual')
        
        if user_type == 'individual':
            self.render_job_seeker_onboarding()
        elif user_type == 'hr_professional':
            self.render_hr_professional_onboarding()
        elif user_type == 'startup':
            self.render_startup_onboarding()
        else:  # enterprise
            self.render_enterprise_onboarding()
        
        # Complete onboarding button
        if st.button("🚀 Start Using Resume + JD Analyzer", type="primary", use_container_width=True):
            # Track onboarding completion
            if user and hasattr(user, 'id'):
                self.track_conversion_event(user.id, 'onboarding_completed', {
                    'user_type': user_type
                })
            
            # Clear registration data
            st.session_state.registration_data = {}
            st.session_state.registration_step = 1
            
            # Redirect to main app
            st.success("Welcome aboard! Redirecting to the main application...")
            st.rerun()
    
    def render_job_seeker_onboarding(self):
        """Onboarding for job seekers"""
        st.markdown("#### 🎯 Getting Started as a Job Seeker")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **📄 What you can do:**
            - Upload your resume for analysis
            - Compare against job descriptions
            - Get personalized improvement suggestions
            - Download optimization reports
            - Track your application success
            """)
        
        with col2:
            st.markdown("""
            **💡 Pro Tips:**
            - Keep multiple resume versions for different roles
            - Use keywords from job descriptions
            - Quantify your achievements with numbers
            - Update your resume regularly
            - Practice with different job postings
            """)
        
        st.markdown("#### 🚀 Quick Start Guide")
        st.markdown("""
        1. **Upload Your Resume** - Start with your current resume (PDF format)
        2. **Add Job Description** - Copy and paste a job posting you're interested in
        3. **Analyze Match** - Get your compatibility score and detailed feedback
        4. **Implement Suggestions** - Update your resume based on recommendations
        5. **Re-analyze** - Check your improved score and apply with confidence!
        """)
    
    def render_hr_professional_onboarding(self):
        """Onboarding for HR professionals"""
        st.markdown("#### 🏢 Getting Started as an HR Professional")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **📊 What you can do:**
            - Screen multiple resumes quickly
            - Compare candidates objectively
            - Generate hiring decision reports
            - Identify skill gaps in candidates
            - Streamline your recruitment process
            """)
        
        with col2:
            st.markdown("""
            **💡 Pro Tips:**
            - Create standardized job descriptions
            - Use bulk analysis for high-volume roles
            - Focus on both hard and soft skills
            - Document your screening decisions
            - Share reports with hiring managers
            """)
        
        st.markdown("#### 🚀 Quick Start Guide")
        st.markdown("""
        1. **Prepare Job Description** - Create detailed, specific job requirements
        2. **Upload Resumes** - Use bulk upload for multiple candidates
        3. **Review Analysis** - Get objective compatibility scores
        4. **Generate Reports** - Create hiring decision documentation
        5. **Make Informed Decisions** - Use data-driven insights for better hires
        """)
    
    def render_startup_onboarding(self):
        """Onboarding for startup founders"""
        st.markdown("#### 🚀 Getting Started as a Startup Founder")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **🎯 What you can do:**
            - Find the right talent for key roles
            - Assess cultural fit and skills
            - Build diverse, high-performing teams
            - Make data-driven hiring decisions
            - Scale your recruitment process
            """)
        
        with col2:
            st.markdown("""
            **💡 Pro Tips:**
            - Define your company culture clearly
            - Look for adaptability and growth mindset
            - Consider potential over perfect matches
            - Build a strong employer brand
            - Leverage your network for referrals
            """)
        
        st.markdown("#### 🚀 Quick Start Guide")
        st.markdown("""
        1. **Define Key Roles** - Identify critical positions for growth
        2. **Create Role Profiles** - Detail skills, experience, and culture fit
        3. **Screen Candidates** - Use AI analysis for initial screening
        4. **Assess Potential** - Look beyond current skills to growth potential
        5. **Build Your Team** - Make strategic hires that scale with your startup
        """)
    
    def render_enterprise_onboarding(self):
        """Onboarding for enterprise users"""
        st.markdown("#### 🏭 Getting Started as an Enterprise User")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **🎯 What you can do:**
            - Scale recruitment across departments
            - Standardize hiring processes
            - Integrate with existing HR systems
            - Generate compliance reports
            - Manage team access and permissions
            """)
        
        with col2:
            st.markdown("""
            **💡 Pro Tips:**
            - Establish consistent evaluation criteria
            - Train your HR team on the platform
            - Set up automated workflows
            - Monitor hiring metrics and trends
            - Ensure compliance with regulations
            """)
        
        st.markdown("#### 🚀 Quick Start Guide")
        st.markdown("""
        1. **Setup Team Access** - Invite HR team members and set permissions
        2. **Configure Integrations** - Connect with your ATS and HRIS systems
        3. **Standardize Processes** - Create consistent job description templates
        4. **Train Your Team** - Ensure everyone knows how to use the platform
        5. **Monitor & Optimize** - Track metrics and continuously improve
        """)
        
        st.info("💼 **Enterprise Support**: Contact our team for custom integrations, training, and dedicated support.")
    
    def track_conversion_event(self, user_id: str, event_name: str, properties: Dict[str, Any]):
        """Track conversion events for analytics"""
        try:
            from database.connection import get_db
            
            db = get_db()
            query = """
                INSERT INTO conversion_events (id, user_id, event_name, event_properties, created_at)
                VALUES (?, ?, ?, ?, ?)
            """
            
            import uuid
            import json
            
            params = (
                str(uuid.uuid4()),
                user_id,
                event_name,
                json.dumps(properties),
                datetime.utcnow()
            )
            
            db.execute_command(query, params)
            
        except Exception as e:
            logger.error(f"Failed to track conversion event: {e}")
    
    def render_registration_flow(self):
        """Main method to render the registration flow"""
        # Progress indicator
        steps = ["User Type", "Basic Info", "Plan Selection", "Confirmation", "Payment", "Welcome"]
        current_step = st.session_state.registration_step
        
        # Progress bar
        progress = (current_step - 1) / (len(steps) - 1)
        st.progress(progress)
        
        # Step indicator
        cols = st.columns(len(steps))
        for i, step in enumerate(steps, 1):
            with cols[i-1]:
                if i < current_step:
                    st.markdown(f"✅ **{step}**")
                elif i == current_step:
                    st.markdown(f"🔄 **{step}**")
                else:
                    st.markdown(f"⏳ {step}")
        
        st.markdown("---")
        
        # Render current step
        if current_step == 1:
            self.render_step_1_user_type()
        elif current_step == 2:
            self.render_step_2_basic_info()
        elif current_step == 3:
            self.render_step_3_plan_selection()
        elif current_step == 4:
            self.render_step_4_confirmation()
        elif current_step == 5:
            self.render_step_5_payment()
        elif current_step == 6:
            self.render_step_6_welcome_onboarding()

def render_login_form():
    """Render login form for existing users"""
    st.markdown("### 🔐 Sign In to Your Account")
    
    with st.form("login_form"):
        email = st.text_input("Email Address", placeholder="your@email.com")
        password = st.text_input("Password", type="password")
        remember_me = st.checkbox("Remember me")
        
        col1, col2 = st.columns(2)
        
        with col1:
            login_submitted = st.form_submit_button("Sign In", type="primary", use_container_width=True)
        
        with col2:
            forgot_password = st.form_submit_button("Forgot Password?", use_container_width=True)
        
        if login_submitted:
            if email and password:
                with st.spinner("Signing you in..."):
                    user = auth_service.authenticate_user(email, password)
                    
                    # Verify authentication was successful
                    if user:
                        # Double-check user exists and is active
                        verified_user = user_service.get_user_by_id(user.id)
                        if not verified_user or not verified_user.is_active:
                            st.error("Account is inactive or not found")
                            return
                        user = verified_user
                    
                    if user:
                        # Create session
                        session = session_service.create_session(user.id)
                        
                        # Update session state
                        st.session_state.user_authenticated = True
                        st.session_state.current_user = user
                        st.session_state.user_session = session
                        
                        st.success(f"Welcome back, {user.first_name}!")
                        st.rerun()
                    else:
                        st.error("Invalid email or password. Please try again.")
            else:
                st.error("Please enter both email and password.")
        
        if forgot_password:
            if email:
                with st.spinner("Sending password reset email..."):
                    reset_token = user_service.request_password_reset(email)
                    if reset_token:
                        st.success("Password reset email sent! Check your inbox.")
                        # In production, this would send an actual email
                        st.info(f"Reset token (for testing): {reset_token}")
                    else:
                        st.error("Email not found or error occurred.")
            else:
                st.error("Please enter your email address first.")

def render_auth_page():
    """Main authentication page with login and registration options"""
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1>🎯 Welcome to Resume + JD Analyzer</h1>
        <p style="font-size: 1.2rem; color: #666;">AI-Powered Resume and Job Description Compatibility Analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if user is already authenticated
    if st.session_state.get('user_authenticated', False):
        user = st.session_state.get('current_user')
        if user:
            st.success(f"Welcome back, {user.first_name}!")
            if st.button("Continue to Application", type="primary"):
                return True
    
    # Auth mode selection
    auth_mode = st.radio(
        "Choose an option:",
        ["🔐 Sign In", "📝 Create Account"],
        horizontal=True
    )
    
    if auth_mode == "🔐 Sign In":
        render_login_form()
    else:
        registration_flow = RegistrationFlow()
        registration_flow.render_registration_flow()
    
    return st.session_state.get('user_authenticated', False)

# Global registration flow instance
registration_flow = RegistrationFlow()