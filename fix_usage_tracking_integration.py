#!/usr/bin/env python3
"""
Fix Usage Tracking Integration
Ensure subscription usage is properly incremented after each analysis
"""

import os
from pathlib import Path

def fix_usage_tracking_in_app():
    """Fix usage tracking to properly increment subscription usage"""
    
    app_file = Path("app.py")
    
    with open(app_file, 'r') as f:
        content = f.read()
    
    # Add usage increment after successful analysis
    old_usage_tracking = '''                    # Track usage with billing system
                    from billing.usage_tracker import usage_monitor
                    usage_monitor.track_analysis_session('''
    
    new_usage_tracking = '''                    # Increment subscription usage count
                    from auth.services import subscription_service
                    subscription_service.increment_usage(user.id)
                    
                    # Track usage with billing system
                    from billing.usage_tracker import usage_monitor
                    usage_monitor.track_analysis_session('''
    
    if old_usage_tracking in content:
        content = content.replace(old_usage_tracking, new_usage_tracking)
        print("✅ Added subscription usage increment to single analysis")
    
    # Also fix bulk analysis usage tracking
    old_bulk_tracking = '''            # Track usage with billing system (includes usage increment)
            from billing.usage_tracker import usage_monitor
            usage_monitor.track_analysis_session('''
    
    new_bulk_tracking = '''            # Increment subscription usage count for bulk analysis
            from auth.services import subscription_service
            subscription_service.increment_usage(user.id)
            
            # Track usage with billing system (includes usage increment)
            from billing.usage_tracker import usage_monitor
            usage_monitor.track_analysis_session('''
    
    if old_bulk_tracking in content:
        content = content.replace(old_bulk_tracking, new_bulk_tracking)
        print("✅ Added subscription usage increment to bulk analysis")
    
    # Add usage display refresh function
    usage_refresh_function = '''
def get_user_usage_stats(user_id):
    """Get current usage statistics for display"""
    try:
        from auth.services import subscription_service
        return subscription_service.get_usage_stats(user_id)
    except Exception as e:
        logger.error(f"Failed to get usage stats: {e}")
        return {'used': 0, 'limit': 3, 'remaining': 3}

def display_usage_stats(user_id):
    """Display current usage statistics"""
    stats = get_user_usage_stats(user_id)
    
    if stats.get('unlimited', False):
        st.sidebar.success("✨ Unlimited Analyses")
    else:
        used = stats.get('used', 0)
        limit = stats.get('limit', 3)
        remaining = stats.get('remaining', 3)
        
        if remaining > 0:
            st.sidebar.info(f"📊 Analyses: {used}/{limit} used ({remaining} remaining)")
        else:
            st.sidebar.warning(f"⚠️ Analyses: {used}/{limit} used (Limit reached)")

'''
    
    # Add the function before the main function
    main_function_start = content.find("def main():")
    if main_function_start > 0:
        content = content[:main_function_start] + usage_refresh_function + "\n" + content[main_function_start:]
        print("✅ Added usage statistics functions")
    
    # Replace refresh_usage_display calls with the new function
    content = content.replace("refresh_usage_display(user.id)", "display_usage_stats(user.id)")
    print("✅ Updated usage display calls")
    
    with open(app_file, 'w') as f:
        f.write(content)
    
    print("✅ Usage tracking integration fixed")

if __name__ == "__main__":
    print("🚀 Fixing usage tracking integration...")
    fix_usage_tracking_in_app()
    print("🎉 Usage tracking fixes completed!")
    print("📊 Subscription usage will now be properly tracked and displayed!")