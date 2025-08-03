#!/usr/bin/env python3
"""
Initialize default subscription plans in the database
"""

from database.connection import get_db
import json

def init_subscription_plans():
    """Initialize default subscription plans"""
    db = get_db()
    
    # Check if plans already exist
    existing_plans = db.execute_query("SELECT COUNT(*) as count FROM subscription_plans")
    if existing_plans[0]['count'] > 0:
        print("Subscription plans already exist")
        return True
    
    # Insert default subscription plans
    plans = [
        ('plan_free', 'Free Tier', 'free', 0.00, 0.00, 3, 
         json.dumps({
             'pdf_download': True, 
             'basic_reports': True, 
             'community_support': True, 
             'watermarked_pdfs': True
         })),
        ('plan_professional', 'Professional', 'professional', 19.00, 190.00, -1, 
         json.dumps({
             'unlimited_analyses': True, 
             'premium_ai': True, 
             'all_formats': True, 
             'priority_processing': True, 
             'email_support': True, 
             'resume_templates': True
         })),
        ('plan_business', 'Business', 'business', 99.00, 990.00, -1, 
         json.dumps({
             'team_collaboration': True, 
             'bulk_upload': True, 
             'analytics_dashboard': True, 
             'api_access': True, 
             'integration_support': True, 
             'phone_support': True, 
             'custom_branding': True, 
             'seats': 5
         })),
        ('plan_enterprise', 'Enterprise', 'enterprise', 500.00, 5000.00, -1, 
         json.dumps({
             'unlimited_seats': True, 
             'sso': True, 
             'custom_integrations': True, 
             'dedicated_support': True, 
             'sla_guarantee': True, 
             'on_premise': True, 
             'white_label': True, 
             'custom_features': True
         }))
    ]
    
    query = '''INSERT INTO subscription_plans (id, name, plan_type, price_monthly, price_annual, monthly_analysis_limit, features) VALUES (?, ?, ?, ?, ?, ?, ?)'''
    
    try:
        for plan in plans:
            db.execute_command(query, plan)
        
        print("✅ Default subscription plans inserted")
        
        # Verify
        plans = db.execute_query('SELECT id, name, plan_type, price_monthly FROM subscription_plans')
        print('Subscription plans:')
        for plan in plans:
            print(f'  - {plan["name"]} ({plan["plan_type"]}): ${plan["price_monthly"]}/month')
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to insert subscription plans: {e}")
        return False

if __name__ == "__main__":
    init_subscription_plans()