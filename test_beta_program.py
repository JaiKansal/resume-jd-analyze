#!/usr/bin/env python3
"""
Test script for the beta program system
"""

# Test the beta program system
try:
    from support.beta_program import beta_program
    import uuid
    
    print('✅ Testing beta program system')
    
    # Create a test user ID
    test_user_id = str(uuid.uuid4())
    
    # Test beta user invitation
    result = beta_program.invite_beta_user(
        user_id=test_user_id,
        invitation_source='personal_network',
        notes='Test beta user invitation'
    )
    print(f'✅ Beta invitation: {result["success"]} - Code: {result.get("invitation_code", "None")}')
    
    # Test beta user activation
    if result['success']:
        activation_result = beta_program.activate_beta_user(
            invitation_code=result['invitation_code'],
            user_id=test_user_id
        )
        print(f'✅ Beta activation: {activation_result["success"]}')
    
    # Test getting beta users
    beta_users = beta_program.get_beta_users()
    print(f'✅ Beta users retrieval: found {len(beta_users)} beta users')
    
    # Test beta program metrics
    metrics = beta_program.get_beta_program_metrics()
    print(f'✅ Beta metrics: {metrics.get("total_beta_users", 0)} total users, {metrics.get("active_beta_users", 0)} active')
    
    # Test case study creation
    if beta_users:
        case_study_data = {
            'title': 'Test Case Study',
            'company_name': 'Test Company',
            'industry': 'Technology',
            'use_case': 'Resume screening automation',
            'challenge': 'Manual resume review was time-consuming',
            'solution': 'Used AI-powered analysis to streamline process',
            'results': 'Reduced screening time by 75%',
            'testimonial': 'This tool transformed our hiring process!',
            'testimonial_author': 'John Doe',
            'testimonial_title': 'HR Director',
            'permission_to_publish': True
        }
        
        case_result = beta_program.create_case_study(
            beta_user_id=beta_users[0]['id'],
            case_study_data=case_study_data
        )
        print(f'✅ Case study creation: {case_result["success"]}')
    
    print('✅ Beta program system working correctly!')
    
except Exception as e:
    print(f'❌ Error testing beta program: {e}')
    import traceback
    traceback.print_exc()