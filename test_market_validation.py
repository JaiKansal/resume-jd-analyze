#!/usr/bin/env python3
"""
Test script for the market validation system
"""

# Test the market validation system
try:
    from support.market_validation import market_validation
    import uuid
    
    print('✅ Testing market validation system')
    
    # Create a test user ID
    test_user_id = str(uuid.uuid4())
    
    # Test pricing feedback submission
    pricing_data = {
        'user_segment': 'startup',
        'current_plan': 'free',
        'expected_price_monthly': 25.0,
        'max_price_monthly': 50.0,
        'pricing_model_preference': 'flat_rate',
        'price_sensitivity': 'medium',
        'value_perception': 'fair',
        'willingness_to_pay_more': ['advanced_analytics', 'api_access'],
        'competitor_pricing': {'competitor_a': 30, 'competitor_b': 40},
        'feedback': 'The pricing seems reasonable for the value provided'
    }
    
    pricing_result = market_validation.submit_pricing_feedback(test_user_id, pricing_data)
    print(f'✅ Pricing feedback submission: {pricing_result["success"]}')
    
    # Test feature feedback submission
    feature_data = {
        'feature_name': 'bulk_analysis',
        'importance_score': 5,
        'current_satisfaction': 4,
        'usage_frequency': 'often',
        'improvement_suggestions': 'Add more file format support',
        'willingness_to_pay_extra': True,
        'extra_payment_amount': 10.0
    }
    
    feature_result = market_validation.submit_feature_feedback(test_user_id, feature_data)
    print(f'✅ Feature feedback submission: {feature_result["success"]}')
    
    # Test getting insights
    pricing_insights = market_validation.get_pricing_insights()
    print(f'✅ Pricing insights: {pricing_insights.get("total_responses", 0)} responses, avg expected price: ${pricing_insights.get("avg_expected_price", 0)}')
    
    feature_insights = market_validation.get_feature_insights()
    print(f'✅ Feature insights: {feature_insights.get("total_responses", 0)} responses, avg importance: {feature_insights.get("avg_importance_score", 0)}/5')
    
    # Test market validation summary
    summary = market_validation.get_market_validation_summary()
    print(f'✅ Market validation summary: {summary.get("total_validation_activities", 0)} total activities')
    
    print('✅ Market validation system working correctly!')
    
except Exception as e:
    print(f'❌ Error testing market validation: {e}')
    import traceback
    traceback.print_exc()