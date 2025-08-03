"""
Beta Program Dashboard UI Components
User interface for managing beta users and collecting validation data
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, Any, List
from support.beta_program import beta_program
from support.feedback_service import feedback_service

class BetaDashboard:
    """UI components for beta program management"""
    
    @staticmethod
    def render_beta_program_page():
        """Render the main beta program page"""
        st.header("🚀 Beta User Program")
        st.markdown("Manage beta users, collect feedback, and validate our product-market fit.")
        
        # Beta program navigation tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Overview", 
            "👥 Beta Users", 
            "💬 Feedback Sessions",
            "📖 Case Studies",
            "📈 Analytics"
        ])
        
        with tab1:
            BetaDashboard._render_overview()
        
        with tab2:
            BetaDashboard._render_beta_users()
        
        with tab3:
            BetaDashboard._render_feedback_sessions()
        
        with tab4:
            BetaDashboard._render_case_studies()
        
        with tab5:
            BetaDashboard._render_analytics()
    
    @staticmethod
    def _render_overview():
        """Render beta program overview"""
        st.subheader("📊 Beta Program Overview")
        
        # Get metrics
        metrics = beta_program.get_beta_program_metrics()
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Beta Users", metrics.get('total_beta_users', 0))
        
        with col2:
            st.metric("Active Beta Users", metrics.get('active_beta_users', 0))
        
        with col3:
            st.metric("Feedback Sessions", metrics.get('completed_feedback_sessions', 0))
        
        with col4:
            st.metric("Case Studies", metrics.get('total_case_studies', 0))
        
        # Progress towards goal
        target_beta_users = 100
        current_beta_users = metrics.get('total_beta_users', 0)
        progress = min(current_beta_users / target_beta_users, 1.0)
        
        st.markdown("### 🎯 Progress Towards Goal")
        st.progress(progress)
        st.markdown(f"**{current_beta_users} / {target_beta_users} beta users recruited** ({progress:.1%} complete)")
        
        # Recent activity
        st.markdown("### 📈 Recent Activity")
        
        # Get recent beta users
        recent_users = beta_program.get_beta_users(limit=5)
        
        if recent_users:
            st.markdown("**Recent Beta User Signups:**")
            for user in recent_users:
                st.markdown(f"• **{user['user_name']}** ({user['company_name'] or 'Individual'}) - {user['invitation_source']} - {user['joined_at'][:10]}")
        else:
            st.info("No beta users yet. Start recruiting!")
        
        # Quick actions
        st.markdown("### ⚡ Quick Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📧 Send Beta Invitations", type="primary"):
                st.session_state.show_invitation_modal = True
        
        with col2:
            if st.button("📞 Schedule Interview"):
                st.session_state.show_interview_modal = True
        
        with col3:
            if st.button("📝 Create Case Study"):
                st.session_state.show_case_study_modal = True
    
    @staticmethod
    def _render_beta_users():
        """Render beta users management"""
        st.subheader("👥 Beta Users Management")
        
        # Add new beta user
        with st.expander("➕ Invite New Beta User"):
            with st.form("invite_beta_user"):
                col1, col2 = st.columns(2)
                
                with col1:
                    user_email = st.text_input("User Email", placeholder="user@company.com")
                    invitation_source = st.selectbox(
                        "Invitation Source",
                        ["personal_network", "community", "referral", "social_media", "content_marketing", "other"]
                    )
                
                with col2:
                    company_name = st.text_input("Company Name (optional)")
                    notes = st.text_area("Notes", placeholder="Any additional context about this user...")
                
                if st.form_submit_button("📧 Send Invitation"):
                    if user_email:
                        # In a real implementation, you'd look up or create the user
                        # For now, we'll simulate this
                        st.success(f"✅ Beta invitation sent to {user_email}")
                        st.info("💡 In production, this would send an email with invitation code")
                    else:
                        st.error("Please provide a user email")
        
        # Beta users list
        st.markdown("### Current Beta Users")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_filter = st.selectbox(
                "Filter by Status",
                ["all", "invited", "active", "churned", "graduated"],
                index=0
            )
        
        with col2:
            source_filter = st.selectbox(
                "Filter by Source",
                ["all", "personal_network", "community", "referral", "social_media", "content_marketing", "other"],
                index=0
            )
        
        with col3:
            engagement_filter = st.selectbox(
                "Filter by Engagement",
                ["all", "low", "medium", "high"],
                index=0
            )
        
        # Get filtered beta users
        status = None if status_filter == "all" else status_filter
        beta_users = beta_program.get_beta_users(status=status)
        
        # Apply additional filters
        if source_filter != "all":
            beta_users = [u for u in beta_users if u['invitation_source'] == source_filter]
        
        if engagement_filter != "all":
            beta_users = [u for u in beta_users if u['engagement_level'] == engagement_filter]
        
        if beta_users:
            # Display beta users
            for user in beta_users:
                with st.expander(f"👤 {user['user_name']} - {user['company_name'] or 'Individual'}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"**Email:** {user['email']}")
                        st.markdown(f"**Status:** {user['status'].title()}")
                        st.markdown(f"**Joined:** {user['joined_at'][:10]}")
                    
                    with col2:
                        st.markdown(f"**Source:** {user['invitation_source'].replace('_', ' ').title()}")
                        st.markdown(f"**Engagement:** {user['engagement_level'].title()}")
                        if user['feedback_score']:
                            st.markdown(f"**Feedback Score:** {user['feedback_score']:.1f}/5.0")
                    
                    with col3:
                        st.markdown(f"**Invitation Code:** `{user['invitation_code']}`")
                        
                        # Quick actions
                        if st.button(f"📞 Schedule Interview", key=f"interview_{user['id']}"):
                            st.session_state.selected_beta_user = user['id']
                            st.session_state.show_interview_modal = True
                        
                        if st.button(f"📝 Create Case Study", key=f"case_study_{user['id']}"):
                            st.session_state.selected_beta_user = user['id']
                            st.session_state.show_case_study_modal = True
        else:
            st.info("No beta users found matching the selected filters.")
    
    @staticmethod
    def _render_feedback_sessions():
        """Render feedback sessions management"""
        st.subheader("💬 Feedback Sessions")
        
        # Schedule new feedback session
        with st.expander("📅 Schedule New Feedback Session"):
            with st.form("schedule_feedback_session"):
                col1, col2 = st.columns(2)
                
                with col1:
                    # Get beta users for selection
                    beta_users = beta_program.get_beta_users(status='active')
                    user_options = {f"{u['user_name']} ({u['company_name'] or 'Individual'})": u['id'] for u in beta_users}
                    
                    selected_user = st.selectbox("Select Beta User", list(user_options.keys()))
                    session_type = st.selectbox(
                        "Session Type",
                        ["interview", "survey", "usability_test", "focus_group"]
                    )
                
                with col2:
                    scheduled_date = st.date_input("Scheduled Date")
                    scheduled_time = st.time_input("Scheduled Time")
                    interviewer = st.text_input("Interviewer", placeholder="Your name")
                
                # Session questions
                st.markdown("**Interview Questions:**")
                questions_text = st.text_area(
                    "Questions (one per line)",
                    placeholder="What do you like most about the product?\nWhat challenges are you trying to solve?\nHow would you rate the pricing?",
                    height=100
                )
                
                if st.form_submit_button("📅 Schedule Session"):
                    if selected_user and interviewer:
                        scheduled_datetime = datetime.combine(scheduled_date, scheduled_time).isoformat()
                        questions = [{"question": q.strip()} for q in questions_text.split('\n') if q.strip()]
                        
                        result = beta_program.schedule_feedback_session(
                            beta_user_id=user_options[selected_user],
                            session_type=session_type,
                            scheduled_at=scheduled_datetime,
                            interviewer=interviewer,
                            questions=questions
                        )
                        
                        if result['success']:
                            st.success("✅ Feedback session scheduled successfully!")
                        else:
                            st.error(f"❌ Failed to schedule session: {result.get('error', 'Unknown error')}")
                    else:
                        st.error("Please fill in all required fields")
        
        # Pricing validation survey
        st.markdown("### 💰 Pricing Validation Survey")
        
        with st.expander("📊 Quick Pricing Survey"):
            st.markdown("Use this to quickly validate pricing with beta users:")
            
            pricing_questions = [
                "How much would you expect to pay for this service monthly?",
                "What's the maximum you would pay before considering alternatives?",
                "How does our current pricing compare to your expectations?",
                "What features would justify a higher price point?",
                "Would you prefer usage-based or flat-rate pricing?"
            ]
            
            for i, question in enumerate(pricing_questions, 1):
                st.markdown(f"**{i}.** {question}")
            
            if st.button("📧 Send Pricing Survey to All Active Beta Users"):
                st.success("✅ Pricing survey sent to all active beta users!")
                st.info("💡 In production, this would send personalized survey emails")
    
    @staticmethod
    def _render_case_studies():
        """Render case studies management"""
        st.subheader("📖 Case Studies & Testimonials")
        
        # Create new case study
        with st.expander("➕ Create New Case Study"):
            with st.form("create_case_study"):
                col1, col2 = st.columns(2)
                
                with col1:
                    # Get beta users for selection
                    beta_users = beta_program.get_beta_users(status='active')
                    user_options = {f"{u['user_name']} ({u['company_name'] or 'Individual'})": u['id'] for u in beta_users}
                    
                    selected_user = st.selectbox("Select Beta User", list(user_options.keys()))
                    title = st.text_input("Case Study Title", placeholder="How Company X Improved Hiring Efficiency by 50%")
                    company_name = st.text_input("Company Name")
                    industry = st.text_input("Industry", placeholder="Technology, Healthcare, Finance, etc.")
                
                with col2:
                    use_case = st.text_area("Use Case", placeholder="Describe how they use the product...")
                    challenge = st.text_area("Challenge", placeholder="What problem were they trying to solve?")
                
                solution = st.text_area("Solution", placeholder="How did our product help solve their challenge?")
                results = st.text_area("Results", placeholder="What outcomes did they achieve?")
                
                # Testimonial section
                st.markdown("**Testimonial:**")
                col1, col2 = st.columns(2)
                
                with col1:
                    testimonial = st.text_area("Testimonial Quote", placeholder="This product has transformed our hiring process...")
                    testimonial_author = st.text_input("Author Name", placeholder="John Smith")
                
                with col2:
                    testimonial_title = st.text_input("Author Title", placeholder="HR Director")
                    permission_to_publish = st.checkbox("Permission to publish publicly", value=False)
                
                if st.form_submit_button("📝 Create Case Study"):
                    if selected_user and title and company_name:
                        case_study_data = {
                            'title': title,
                            'company_name': company_name,
                            'industry': industry,
                            'use_case': use_case,
                            'challenge': challenge,
                            'solution': solution,
                            'results': results,
                            'testimonial': testimonial,
                            'testimonial_author': testimonial_author,
                            'testimonial_title': testimonial_title,
                            'permission_to_publish': permission_to_publish
                        }
                        
                        result = beta_program.create_case_study(
                            beta_user_id=user_options[selected_user],
                            case_study_data=case_study_data
                        )
                        
                        if result['success']:
                            st.success("✅ Case study created successfully!")
                        else:
                            st.error(f"❌ Failed to create case study: {result.get('error', 'Unknown error')}")
                    else:
                        st.error("Please fill in all required fields")
        
        # Published case studies
        st.markdown("### 📚 Published Case Studies")
        
        case_studies = beta_program.get_published_case_studies()
        
        if case_studies:
            for case_study in case_studies:
                with st.expander(f"📖 {case_study['title']}"):
                    st.markdown(f"**Company:** {case_study['company_name']}")
                    st.markdown(f"**Industry:** {case_study['industry']}")
                    
                    if case_study['use_case']:
                        st.markdown(f"**Use Case:** {case_study['use_case']}")
                    
                    if case_study['challenge']:
                        st.markdown(f"**Challenge:** {case_study['challenge']}")
                    
                    if case_study['solution']:
                        st.markdown(f"**Solution:** {case_study['solution']}")
                    
                    if case_study['results']:
                        st.markdown(f"**Results:** {case_study['results']}")
                    
                    if case_study['testimonial']:
                        st.markdown("**Testimonial:**")
                        st.markdown(f"> \"{case_study['testimonial']}\"")
                        st.markdown(f"> — **{case_study['testimonial_author']}**, {case_study['testimonial_title']}")
        else:
            st.info("No published case studies yet. Create some case studies and mark them for publication!")
    
    @staticmethod
    def _render_analytics():
        """Render beta program analytics"""
        st.subheader("📈 Beta Program Analytics")
        
        # Get metrics
        metrics = beta_program.get_beta_program_metrics()
        
        # Key metrics overview
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 👥 User Metrics")
            st.metric("Total Beta Users", metrics.get('total_beta_users', 0))
            st.metric("Active Beta Users", metrics.get('active_beta_users', 0))
            
            # Activation rate
            total = metrics.get('total_beta_users', 0)
            active = metrics.get('active_beta_users', 0)
            activation_rate = (active / total * 100) if total > 0 else 0
            st.metric("Activation Rate", f"{activation_rate:.1f}%")
        
        with col2:
            st.markdown("### 📊 Feedback Metrics")
            st.metric("Feedback Sessions", metrics.get('completed_feedback_sessions', 0))
            st.metric("Avg Satisfaction", f"{metrics.get('average_satisfaction_score', 0):.1f}/5.0")
            st.metric("Case Studies", metrics.get('total_case_studies', 0))
        
        # User acquisition sources
        st.markdown("### 📈 User Acquisition Sources")
        
        users_by_source = metrics.get('users_by_source', {})
        
        if users_by_source:
            # Create a simple bar chart representation
            for source, count in users_by_source.items():
                source_name = source.replace('_', ' ').title()
                percentage = (count / sum(users_by_source.values()) * 100) if users_by_source else 0
                st.markdown(f"**{source_name}:** {count} users ({percentage:.1f}%)")
                st.progress(percentage / 100)
        else:
            st.info("No user acquisition data available yet.")
        
        # Recommendations
        st.markdown("### 💡 Recommendations")
        
        total_users = metrics.get('total_beta_users', 0)
        
        if total_users < 25:
            st.warning("🎯 **Focus on Recruitment**: You have fewer than 25 beta users. Consider expanding your outreach through personal networks and communities.")
        elif total_users < 50:
            st.info("📈 **Scale Recruitment**: Good progress! Consider adding referral incentives and content marketing to accelerate growth.")
        elif total_users < 100:
            st.success("🚀 **Optimize Engagement**: Great progress! Focus on increasing engagement and collecting more detailed feedback.")
        else:
            st.success("🎉 **Goal Achieved**: Congratulations! You've reached your beta user target. Focus on graduation and case study creation.")
        
        # Feedback collection recommendations
        sessions = metrics.get('completed_feedback_sessions', 0)
        if sessions < total_users * 0.3:
            st.warning("💬 **Increase Feedback Collection**: Consider scheduling more feedback sessions. Aim for at least 30% of beta users to participate in interviews.")
        
        # Case study recommendations
        case_studies = metrics.get('total_case_studies', 0)
        if case_studies < 3:
            st.info("📖 **Create Case Studies**: Start documenting success stories. Aim for at least 3-5 compelling case studies for marketing.")

# Global instance
beta_dashboard = BetaDashboard()