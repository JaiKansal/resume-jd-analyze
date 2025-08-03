"""
Feedback Widget UI Components
Streamlit components for collecting user feedback
"""

import streamlit as st
from datetime import datetime
from typing import Dict, Any, Optional
from support.feedback_service import feedback_service
from support.ticket_service import ticket_service

class FeedbackWidget:
    """UI components for feedback collection"""
    
    @staticmethod
    def render_feedback_button():
        """Render a floating feedback button"""
        # Add custom CSS for feedback button
        st.markdown("""
        <style>
        .feedback-button {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 50px;
            padding: 12px 20px;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            font-weight: bold;
        }
        .feedback-button:hover {
            background: #5a6fd8;
            transform: translateY(-2px);
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Initialize feedback modal state
        if 'show_feedback_modal' not in st.session_state:
            st.session_state.show_feedback_modal = False
        
        # Feedback button in sidebar
        if st.sidebar.button("💬 Give Feedback", help="Share your thoughts with us"):
            st.session_state.show_feedback_modal = True
        
        # Show feedback modal if triggered
        if st.session_state.show_feedback_modal:
            FeedbackWidget.render_feedback_modal()
    
    @staticmethod
    def render_feedback_modal():
        """Render feedback collection modal"""
        with st.container():
            st.markdown("### 💬 Share Your Feedback")
            st.markdown("Help us improve by sharing your thoughts!")
            
            with st.form("feedback_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    feedback_type = st.selectbox(
                        "Feedback Type",
                        ["general_feedback", "bug_report", "feature_request", "rating"],
                        format_func=lambda x: {
                            "general_feedback": "💭 General Feedback",
                            "bug_report": "🐛 Bug Report", 
                            "feature_request": "✨ Feature Request",
                            "rating": "⭐ Rating"
                        }[x]
                    )
                
                with col2:
                    category = st.selectbox(
                        "Category",
                        ["UI/UX", "Performance", "Features", "Billing", "Support", "Other"]
                    )
                
                title = st.text_input("Title (optional)", placeholder="Brief summary of your feedback")
                
                description = st.text_area(
                    "Description",
                    placeholder="Please describe your feedback in detail...",
                    height=100
                )
                
                # Rating for rating feedback type
                rating = None
                if feedback_type == "rating":
                    rating = st.slider("Overall Rating", 1, 5, 3, help="1 = Poor, 5 = Excellent")
                
                col1, col2, col3 = st.columns([1, 1, 1])
                
                with col1:
                    submit_feedback = st.form_submit_button("📤 Submit Feedback", type="primary")
                
                with col2:
                    create_ticket = st.form_submit_button("🎫 Create Support Ticket")
                
                with col3:
                    if st.form_submit_button("❌ Cancel"):
                        st.session_state.show_feedback_modal = False
                        st.rerun()
                
                if submit_feedback and description.strip():
                    user = st.session_state.get('current_user')
                    if user:
                        feedback_data = {
                            'feedback_type': feedback_type,
                            'category': category,
                            'title': title,
                            'description': description,
                            'rating': rating,
                            'page_url': st.session_state.get('current_page', ''),
                            'metadata': {
                                'timestamp': datetime.utcnow().isoformat(),
                                'user_plan': getattr(user, 'plan_type', 'unknown')
                            }
                        }
                        
                        result = feedback_service.submit_feedback(user.id, feedback_data)
                        
                        if result['success']:
                            st.success("✅ Thank you for your feedback! We appreciate your input.")
                            st.session_state.show_feedback_modal = False
                            st.rerun()
                        else:
                            st.error(f"❌ Failed to submit feedback: {result.get('error', 'Unknown error')}")
                    else:
                        st.error("❌ Please sign in to submit feedback")
                
                elif create_ticket and description.strip():
                    user = st.session_state.get('current_user')
                    if user:
                        ticket_title = title if title.strip() else f"{feedback_type.replace('_', ' ').title()}: {category}"
                        
                        result = ticket_service.create_ticket(
                            user_id=user.id,
                            subject=ticket_title,
                            description=description,
                            category=category,
                            priority='medium'
                        )
                        
                        if result['success']:
                            st.success(f"✅ Support ticket {result['ticket_number']} created! We'll respond within 24 hours.")
                            st.session_state.show_feedback_modal = False
                            st.rerun()
                        else:
                            st.error(f"❌ Failed to create ticket: {result.get('error', 'Unknown error')}")
                    else:
                        st.error("❌ Please sign in to create a support ticket")
                
                elif (submit_feedback or create_ticket) and not description.strip():
                    st.warning("⚠️ Please provide a description for your feedback")
    
    @staticmethod
    def render_quick_rating(page_name: str = "current_page"):
        """Render a quick rating widget for the current page"""
        st.markdown("---")
        st.markdown("**Was this helpful?**")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        rating_given = False
        
        with col1:
            if st.button("⭐", key=f"rating_1_{page_name}", help="1 star"):
                FeedbackWidget._submit_quick_rating(1, page_name)
                rating_given = True
        
        with col2:
            if st.button("⭐⭐", key=f"rating_2_{page_name}", help="2 stars"):
                FeedbackWidget._submit_quick_rating(2, page_name)
                rating_given = True
        
        with col3:
            if st.button("⭐⭐⭐", key=f"rating_3_{page_name}", help="3 stars"):
                FeedbackWidget._submit_quick_rating(3, page_name)
                rating_given = True
        
        with col4:
            if st.button("⭐⭐⭐⭐", key=f"rating_4_{page_name}", help="4 stars"):
                FeedbackWidget._submit_quick_rating(4, page_name)
                rating_given = True
        
        with col5:
            if st.button("⭐⭐⭐⭐⭐", key=f"rating_5_{page_name}", help="5 stars"):
                FeedbackWidget._submit_quick_rating(5, page_name)
                rating_given = True
        
        if rating_given:
            st.success("Thank you for your rating!")
    
    @staticmethod
    def _submit_quick_rating(rating: int, page_name: str):
        """Submit a quick rating"""
        user = st.session_state.get('current_user')
        if user:
            feedback_data = {
                'feedback_type': 'rating',
                'category': 'UI/UX',
                'title': f'Page Rating: {page_name}',
                'description': f'User rated {page_name} page {rating} stars',
                'rating': rating,
                'page_url': page_name,
                'metadata': {
                    'quick_rating': True,
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
            
            feedback_service.submit_feedback(user.id, feedback_data)
    
    @staticmethod
    def render_nps_survey():
        """Render Net Promoter Score survey"""
        if 'nps_survey_shown' not in st.session_state:
            st.session_state.nps_survey_shown = False
        
        # Show NPS survey occasionally (you might want to add logic for when to show this)
        if not st.session_state.nps_survey_shown and st.session_state.get('analysis_count', 0) >= 3:
            with st.expander("📊 Quick Survey - Help us improve!", expanded=True):
                st.markdown("**How likely are you to recommend Resume + JD Analyzer to a friend or colleague?**")
                
                nps_score = st.slider("", 0, 10, 5, 
                                    help="0 = Not at all likely, 10 = Extremely likely")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Submit", type="primary"):
                        user = st.session_state.get('current_user')
                        if user:
                            feedback_data = {
                                'feedback_type': 'rating',
                                'category': 'NPS',
                                'title': 'Net Promoter Score',
                                'description': f'NPS Score: {nps_score}',
                                'rating': nps_score,
                                'metadata': {
                                    'survey_type': 'nps',
                                    'timestamp': datetime.utcnow().isoformat()
                                }
                            }
                            
                            result = feedback_service.submit_feedback(user.id, feedback_data)
                            if result['success']:
                                st.success("Thank you for your feedback!")
                                st.session_state.nps_survey_shown = True
                                st.rerun()
                
                with col2:
                    if st.button("Maybe later"):
                        st.session_state.nps_survey_shown = True
                        st.rerun()

# Global instance
feedback_widget = FeedbackWidget()