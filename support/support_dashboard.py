"""
Support Dashboard UI Components
User interface for support tickets, knowledge base, and help
"""

import streamlit as st
from datetime import datetime
from typing import Dict, Any, List
from support.ticket_service import ticket_service
from support.knowledge_base import knowledge_base
from support.feedback_service import feedback_service

class SupportDashboard:
    """UI components for customer support dashboard"""
    
    @staticmethod
    def render_support_page():
        """Render the main support page"""
        st.header("🎧 Customer Support")
        st.markdown("Get help, browse our knowledge base, or contact support.")
        
        # Support navigation tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📚 Knowledge Base", 
            "🎫 My Tickets", 
            "💬 Contact Support",
            "📊 My Feedback"
        ])
        
        with tab1:
            SupportDashboard._render_knowledge_base()
        
        with tab2:
            SupportDashboard._render_user_tickets()
        
        with tab3:
            SupportDashboard._render_contact_support()
        
        with tab4:
            SupportDashboard._render_user_feedback()
    
    @staticmethod
    def _render_knowledge_base():
        """Render knowledge base section"""
        st.subheader("📚 Knowledge Base")
        st.markdown("Find answers to common questions and learn how to use our platform.")
        
        # Search functionality
        col1, col2 = st.columns([3, 1])
        
        with col1:
            search_query = st.text_input(
                "Search articles",
                placeholder="Search for help articles...",
                key="kb_search"
            )
        
        with col2:
            if st.button("🔍 Search", type="primary"):
                if search_query.strip():
                    search_results = knowledge_base.search_articles(search_query)
                    st.session_state.kb_search_results = search_results
        
        # Show search results if available
        if hasattr(st.session_state, 'kb_search_results') and st.session_state.kb_search_results:
            st.markdown("### Search Results")
            for article in st.session_state.kb_search_results:
                with st.expander(f"📄 {article['title']}"):
                    st.markdown(article['excerpt'])
                    if st.button(f"Read Full Article", key=f"read_{article['id']}"):
                        st.session_state.selected_article = article['slug']
                        st.rerun()
        
        # Show selected article
        if hasattr(st.session_state, 'selected_article'):
            article = knowledge_base.get_article_by_slug(
                st.session_state.selected_article,
                st.session_state.get('current_user', {}).get('id')
            )
            
            if article:
                st.markdown("---")
                st.markdown(f"# {article['title']}")
                st.markdown(f"*Category: {article['category']} | Views: {article['view_count']}*")
                st.markdown(article['content'])
                
                # Article rating
                st.markdown("---")
                st.markdown("**Was this article helpful?**")
                col1, col2, col3 = st.columns([1, 1, 2])
                
                with col1:
                    if st.button("👍 Yes", key=f"helpful_{article['id']}"):
                        knowledge_base.rate_article_helpful(article['id'], True)
                        st.success("Thank you for your feedback!")
                
                with col2:
                    if st.button("👎 No", key=f"not_helpful_{article['id']}"):
                        knowledge_base.rate_article_helpful(article['id'], False)
                        st.info("Thank you for your feedback! Consider contacting support for more help.")
                
                with col3:
                    if st.button("🔙 Back to Articles"):
                        if hasattr(st.session_state, 'selected_article'):
                            del st.session_state.selected_article
                        st.rerun()
        
        # Categories and popular articles
        if not hasattr(st.session_state, 'selected_article'):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📂 Browse by Category")
                categories = knowledge_base.get_categories()
                
                for category in categories:
                    if st.button(f"📁 {category}", key=f"cat_{category}"):
                        articles = knowledge_base.get_published_articles(category=category)
                        st.session_state.category_articles = articles
                        st.session_state.selected_category = category
                        st.rerun()
            
            with col2:
                st.markdown("### 🔥 Popular Articles")
                popular_articles = knowledge_base.get_popular_articles()
                
                for article in popular_articles:
                    if st.button(f"📄 {article['title']}", key=f"pop_{article['id']}"):
                        st.session_state.selected_article = article['slug']
                        st.rerun()
        
        # Show category articles
        if hasattr(st.session_state, 'category_articles'):
            st.markdown(f"### Articles in {st.session_state.selected_category}")
            
            for article in st.session_state.category_articles:
                with st.expander(f"📄 {article['title']}"):
                    st.markdown(article['excerpt'])
                    if st.button(f"Read Article", key=f"cat_read_{article['id']}"):
                        st.session_state.selected_article = article['slug']
                        st.rerun()
            
            if st.button("🔙 Back to Categories"):
                if hasattr(st.session_state, 'category_articles'):
                    del st.session_state.category_articles
                    del st.session_state.selected_category
                st.rerun()
    
    @staticmethod
    def _render_user_tickets():
        """Render user's support tickets"""
        st.subheader("🎫 My Support Tickets")
        
        user = st.session_state.get('current_user')
        if not user:
            st.error("Please sign in to view your support tickets.")
            return
        
        # Get user tickets
        tickets = ticket_service.get_user_tickets(user.id)
        
        if not tickets:
            st.info("You don't have any support tickets yet.")
            st.markdown("Need help? Use the 'Contact Support' tab to create a new ticket.")
            return
        
        # Display tickets
        for ticket in tickets:
            status_color = {
                'open': '🟢',
                'in_progress': '🟡', 
                'waiting_customer': '🟠',
                'resolved': '✅',
                'closed': '⚫'
            }.get(ticket['status'], '❓')
            
            with st.expander(f"{status_color} {ticket['ticket_number']}: {ticket['subject']}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"**Status:** {ticket['status'].replace('_', ' ').title()}")
                    st.markdown(f"**Priority:** {ticket['priority'].title()}")
                
                with col2:
                    st.markdown(f"**Category:** {ticket['category'] or 'General'}")
                    st.markdown(f"**Created:** {ticket['created_at'][:10]}")
                
                with col3:
                    if ticket['resolved_at']:
                        st.markdown(f"**Resolved:** {ticket['resolved_at'][:10]}")
                
                # Show ticket messages
                messages = ticket_service.get_ticket_messages(ticket['id'], user.id)
                
                if messages:
                    st.markdown("**Conversation:**")
                    for message in messages:
                        sender_icon = "👤" if message['sender_type'] == 'customer' else "🎧" if message['sender_type'] == 'agent' else "🤖"
                        
                        st.markdown(f"{sender_icon} **{message['sender_name']}** - {message['created_at'][:16]}")
                        st.markdown(f"> {message['content']}")
                        st.markdown("")
                
                # Add reply if ticket is not closed
                if ticket['status'] not in ['resolved', 'closed']:
                    with st.form(f"reply_{ticket['id']}"):
                        reply_content = st.text_area(
                            "Add a reply:",
                            placeholder="Type your message here...",
                            key=f"reply_content_{ticket['id']}"
                        )
                        
                        if st.form_submit_button("📤 Send Reply"):
                            if reply_content.strip():
                                result = ticket_service.add_message(
                                    ticket['id'], 
                                    user.id, 
                                    reply_content,
                                    'customer'
                                )
                                
                                if result['success']:
                                    st.success("Reply sent successfully!")
                                    st.rerun()
                                else:
                                    st.error(f"Failed to send reply: {result.get('error', 'Unknown error')}")
                            else:
                                st.warning("Please enter a message before sending.")
    
    @staticmethod
    def _render_contact_support():
        """Render contact support form"""
        st.subheader("💬 Contact Support")
        st.markdown("Need help? Create a support ticket and we'll get back to you within 24 hours.")
        
        user = st.session_state.get('current_user')
        if not user:
            st.error("Please sign in to contact support.")
            return
        
        with st.form("contact_support"):
            col1, col2 = st.columns(2)
            
            with col1:
                category = st.selectbox(
                    "Category",
                    ["Technical Issue", "Billing Question", "Account Problem", 
                     "Feature Request", "Bug Report", "General Question"],
                    help="Select the category that best describes your issue"
                )
            
            with col2:
                priority = st.selectbox(
                    "Priority",
                    ["low", "medium", "high", "urgent"],
                    index=1,
                    format_func=lambda x: {
                        "low": "🟢 Low - General question",
                        "medium": "🟡 Medium - Standard issue", 
                        "high": "🟠 High - Important problem",
                        "urgent": "🔴 Urgent - Critical issue"
                    }[x]
                )
            
            subject = st.text_input(
                "Subject",
                placeholder="Brief description of your issue",
                help="Provide a clear, concise subject line"
            )
            
            description = st.text_area(
                "Description",
                placeholder="Please describe your issue in detail. Include any error messages, steps to reproduce, and what you expected to happen.",
                height=150,
                help="The more details you provide, the better we can help you"
            )
            
            # Additional context
            with st.expander("📋 Additional Information (Optional)"):
                st.markdown("**Current Plan:** " + getattr(user, 'plan_type', 'Unknown'))
                st.markdown("**User ID:** " + str(user.id))
                
                include_usage = st.checkbox(
                    "Include my recent usage data to help with troubleshooting",
                    value=True
                )
            
            col1, col2 = st.columns(2)
            
            with col1:
                submit_ticket = st.form_submit_button("🎫 Create Support Ticket", type="primary")
            
            with col2:
                if st.form_submit_button("📞 Request Phone Call"):
                    st.info("Phone support is available for Business and Enterprise plans. We'll contact you within 4 hours.")
            
            if submit_ticket:
                if not subject.strip() or not description.strip():
                    st.error("Please provide both a subject and description for your support ticket.")
                else:
                    # Add usage data if requested
                    full_description = description
                    if include_usage:
                        full_description += f"\n\n--- System Information ---\n"
                        full_description += f"User Plan: {getattr(user, 'plan_type', 'Unknown')}\n"
                        full_description += f"User ID: {user.id}\n"
                        full_description += f"Timestamp: {datetime.utcnow().isoformat()}\n"
                    
                    result = ticket_service.create_ticket(
                        user_id=user.id,
                        subject=subject,
                        description=full_description,
                        category=category,
                        priority=priority
                    )
                    
                    if result['success']:
                        st.success(f"✅ Support ticket {result['ticket_number']} created successfully!")
                        st.info("We'll respond within 24 hours. You can track your ticket in the 'My Tickets' tab.")
                        
                        # Clear form
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to create support ticket: {result.get('error', 'Unknown error')}")
    
    @staticmethod
    def _render_user_feedback():
        """Render user's feedback history"""
        st.subheader("📊 My Feedback")
        
        user = st.session_state.get('current_user')
        if not user:
            st.error("Please sign in to view your feedback.")
            return
        
        feedback_list = feedback_service.get_user_feedback(user.id)
        
        if not feedback_list:
            st.info("You haven't submitted any feedback yet.")
            st.markdown("Use the feedback button in the sidebar to share your thoughts!")
            return
        
        # Display feedback
        for feedback in feedback_list:
            feedback_icon = {
                'general_feedback': '💭',
                'bug_report': '🐛',
                'feature_request': '✨',
                'rating': '⭐'
            }.get(feedback['feedback_type'], '💬')
            
            status_color = {
                'new': '🟡',
                'reviewed': '🔵',
                'in_progress': '🟠',
                'resolved': '✅',
                'closed': '⚫'
            }.get(feedback['status'], '❓')
            
            with st.expander(f"{feedback_icon} {feedback['title'] or feedback['feedback_type'].replace('_', ' ').title()}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Type:** {feedback['feedback_type'].replace('_', ' ').title()}")
                    st.markdown(f"**Category:** {feedback['category'] or 'General'}")
                
                with col2:
                    st.markdown(f"**Status:** {status_color} {feedback['status'].replace('_', ' ').title()}")
                    st.markdown(f"**Submitted:** {feedback['created_at'][:10]}")
                
                if feedback['rating']:
                    st.markdown(f"**Rating:** {'⭐' * feedback['rating']}")
                
                if feedback['description']:
                    st.markdown("**Description:**")
                    st.markdown(f"> {feedback['description']}")

# Global instance
support_dashboard = SupportDashboard()