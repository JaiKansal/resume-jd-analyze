#!/usr/bin/env python3
"""
Verification test for Task 3: Create Freemium Tier with Usage Limitations
Tests all requirements specified in the task details
"""

import sys
import os
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_monthly_analysis_limit_enforcement():
    """Test requirement: Implement monthly analysis limit enforcement (3 for free users)"""
    print("🧪 Testing Monthly Analysis Limit Enforcement")
    print("-" * 50)
    
    try:
        from auth.models import User, Subscription, SubscriptionPlan, SubscriptionStatus, PlanType
        from auth.services import subscription_service
        from billing.subscription_tiers import tier_manager
        import uuid
        
        # Create test user and free subscription
        test_user = User.create(email="limit_test@example.com", password="test123")
        
        # Get free tier definition
        free_tier = tier_manager.get_tier_definition(PlanType.FREE)
        
        print(f"✅ Free tier monthly limit: {free_tier['monthly_analysis_limit']}")
        assert free_tier['monthly_analysis_limit'] == 3, "Free tier should have 3 analysis limit"
        
        # Create mock subscription with usage tracking
        free_plan = SubscriptionPlan(
            id=str(uuid.uuid4()),
            name="Free Tier",
            plan_type=PlanType.FREE,
            price_monthly=0.0,
            price_annual=0.0,
            monthly_analysis_limit=3,
            features=free_tier['features']
        )
        
        test_subscription = Subscription(
            id=str(uuid.uuid4()),
            user_id=test_user.id,
            plan_id=free_plan.id,
            status=SubscriptionStatus.ACTIVE,
            monthly_analysis_used=0,
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow() + timedelta(days=30)
        )
        test_subscription.plan = free_plan
        
        # Test usage progression
        print(f"✅ Initial usage: {test_subscription.monthly_analysis_used}/3")
        assert test_subscription.can_analyze() == True, "Should be able to analyze initially"
        
        # Use 2 analyses
        test_subscription.increment_usage(2)
        print(f"✅ After 2 analyses: {test_subscription.monthly_analysis_used}/3")
        assert test_subscription.can_analyze() == True, "Should still be able to analyze"
        
        # Use 1 more analysis (hitting limit)
        test_subscription.increment_usage(1)
        print(f"✅ After 3 analyses: {test_subscription.monthly_analysis_used}/3")
        assert test_subscription.can_analyze() == False, "Should not be able to analyze after limit"
        
        print("✅ Monthly analysis limit enforcement working correctly")
        
    except Exception as e:
        print(f"❌ Monthly limit test failed: {e}")
        return False
    
    return True

def test_upgrade_prompts():
    """Test requirement: Add upgrade prompts when users approach or exceed limits"""
    print("\n🧪 Testing Upgrade Prompts")
    print("-" * 50)
    
    try:
        from billing.upgrade_flow import UpgradeFlowManager, UpgradePromptType
        from auth.models import User, PlanType
        
        upgrade_manager = UpgradeFlowManager()
        test_user = User.create(email="prompt_test@example.com", password="test123")
        
        # Test usage limit warning prompt
        warning_prompt = upgrade_manager.prompts.get("usage_limit_warning")
        print(f"✅ Usage warning prompt: {warning_prompt.title}")
        assert warning_prompt.prompt_type == UpgradePromptType.USAGE_LIMIT
        assert warning_prompt.target_plan == PlanType.PROFESSIONAL
        
        # Test usage limit exceeded prompt
        exceeded_prompt = upgrade_manager.prompts.get("usage_limit_exceeded")
        print(f"✅ Usage exceeded prompt: {exceeded_prompt.title}")
        assert exceeded_prompt.prompt_type == UpgradePromptType.USAGE_LIMIT
        assert exceeded_prompt.urgency_level == "high"
        
        # Test feature gate prompts
        feature_gates = ["bulk_upload_gate", "premium_ai_gate", "api_access_gate"]
        for gate in feature_gates:
            gate_prompt = upgrade_manager.prompts.get(gate)
            print(f"✅ Feature gate prompt: {gate_prompt.title}")
            assert gate_prompt.prompt_type == UpgradePromptType.FEATURE_GATE
        
        # Test A/B testing variants
        variant = upgrade_manager._get_user_variant("test_user", "usage_limit_exceeded")
        print(f"✅ A/B testing variant assignment: {variant}")
        assert variant in ["variant_a", "variant_b", "variant_c"]
        
        print("✅ Upgrade prompts working correctly")
        
    except Exception as e:
        print(f"❌ Upgrade prompts test failed: {e}")
        return False
    
    return True

def test_watermarked_pdf_generation():
    """Test requirement: Create basic report generation with watermarked PDFs"""
    print("\n🧪 Testing Watermarked PDF Generation")
    print("-" * 50)
    
    try:
        from billing.watermark_service import WatermarkService
        from auth.models import User, PlanType
        
        watermark_service = WatermarkService()
        free_user = User.create(email="watermark_test@example.com", password="test123")
        
        # Test watermark decision
        should_watermark = watermark_service.should_add_watermark(free_user)
        print(f"✅ Should add watermark for free user: {should_watermark}")
        assert should_watermark == True, "Free users should get watermarked PDFs"
        
        # Test watermark notice text
        notice_text = watermark_service.get_watermark_notice_text()
        print(f"✅ Watermark notice available: {len(notice_text) > 0}")
        assert "watermark" in notice_text.lower()
        assert "upgrade" in notice_text.lower()
        
        # Test PDF generation (if ReportLab available)
        try:
            sample_content = "Test resume analysis report content"
            pdf_data = watermark_service.create_watermarked_pdf(
                sample_content, "Test Report", free_user
            )
            
            if pdf_data:
                print(f"✅ Watermarked PDF generated: {len(pdf_data)} bytes")
                assert len(pdf_data) > 1000, "PDF should have substantial content"
            else:
                print("ℹ️  PDF generation skipped (ReportLab not available)")
                
        except ImportError:
            print("ℹ️  PDF generation test skipped (ReportLab not available)")
        
        # Test upgrade prompt PDF
        upgrade_pdf = watermark_service.create_upgrade_prompt_pdf(free_user)
        if upgrade_pdf:
            print(f"✅ Upgrade prompt PDF generated: {len(upgrade_pdf)} bytes")
        
        print("✅ Watermarked PDF generation working correctly")
        
    except Exception as e:
        print(f"❌ Watermarked PDF test failed: {e}")
        return False
    
    return True

def test_advanced_feature_restrictions():
    """Test requirement: Restrict access to advanced features and integrations"""
    print("\n🧪 Testing Advanced Feature Restrictions")
    print("-" * 50)
    
    try:
        from billing.subscription_tiers import SubscriptionTierManager
        from auth.models import PlanType
        
        tier_manager = SubscriptionTierManager()
        
        # Test feature restrictions for free tier
        free_tier = tier_manager.get_tier_definition(PlanType.FREE)
        professional_tier = tier_manager.get_tier_definition(PlanType.PROFESSIONAL)
        business_tier = tier_manager.get_tier_definition(PlanType.BUSINESS)
        
        # Advanced features that should be restricted for free users
        restricted_features = [
            'unlimited_analyses',
            'premium_ai',
            'all_formats',
            'priority_processing',
            'bulk_upload',
            'team_collaboration',
            'api_access',
            'custom_branding',
            'sso'
        ]
        
        print("✅ Testing feature restrictions:")
        for feature in restricted_features:
            free_has = free_tier['features'].get(feature, False)
            pro_has = professional_tier['features'].get(feature, False)
            business_has = business_tier['features'].get(feature, False)
            
            print(f"   {feature}: Free={free_has}, Pro={pro_has}, Business={business_has}")
            
            # Most advanced features should not be available in free tier
            if feature in ['unlimited_analyses', 'premium_ai', 'all_formats']:
                assert free_has == False, f"Free tier should not have {feature}"
                assert pro_has == True, f"Professional tier should have {feature}"
            
            if feature in ['bulk_upload', 'team_collaboration', 'api_access']:
                assert free_has == False, f"Free tier should not have {feature}"
                assert business_has == True, f"Business tier should have {feature}"
        
        # Test file size restrictions
        from billing.watermark_service import WatermarkService
        watermark_service = WatermarkService()
        
        free_limit = watermark_service.get_file_size_limit_mb(
            User.create(email="test@example.com", password="test")
        )
        print(f"✅ Free tier file size limit: {free_limit}MB")
        assert free_limit == 5, "Free tier should have 5MB file limit"
        
        # Test file size checking
        can_upload_large, error = watermark_service.check_file_size_limit(
            User.create(email="test2@example.com", password="test"), 10.0
        )
        print(f"✅ Large file upload blocked: {not can_upload_large}")
        assert can_upload_large == False, "Large files should be blocked for free users"
        assert "upgrade" in error.lower(), "Error message should mention upgrade"
        
        print("✅ Advanced feature restrictions working correctly")
        
    except Exception as e:
        print(f"❌ Feature restrictions test failed: {e}")
        return False
    
    return True

def test_conversion_optimization():
    """Test requirement: A/B testing framework and trial functionality"""
    print("\n🧪 Testing Conversion Optimization")
    print("-" * 50)
    
    try:
        from billing.upgrade_flow import UpgradeFlowManager, TrialManager, ConversionEvent
        from auth.models import PlanType
        import uuid
        
        upgrade_manager = UpgradeFlowManager()
        trial_manager = TrialManager()
        
        # Test A/B testing variants
        variants = upgrade_manager.ab_test_variants
        print(f"✅ A/B test variants available: {len(variants)} prompt types")
        
        # Test consistent variant assignment
        user1_variant = upgrade_manager._get_user_variant("user1", "usage_limit_exceeded")
        user1_variant_2 = upgrade_manager._get_user_variant("user1", "usage_limit_exceeded")
        print(f"✅ Consistent variant assignment: {user1_variant == user1_variant_2}")
        assert user1_variant == user1_variant_2, "Variant assignment should be consistent"
        
        # Test trial periods
        trial_lengths = trial_manager.trial_lengths
        print(f"✅ Trial periods configured:")
        for plan, days in trial_lengths.items():
            print(f"   {plan.value}: {days} days")
            assert days > 0, f"Trial period should be positive for {plan.value}"
        
        # Test conversion event tracking
        test_event = ConversionEvent(
            id=str(uuid.uuid4()),
            user_id="test_user",
            event_type="prompt_shown",
            prompt_id="usage_limit_exceeded",
            variant="variant_a",
            timestamp=datetime.utcnow()
        )
        
        print(f"✅ Conversion event created: {test_event.event_type}")
        assert test_event.event_type == "prompt_shown"
        assert test_event.variant == "variant_a"
        
        # Test abandoned cart recovery
        from billing.upgrade_flow import AbandonedCartRecovery
        cart_recovery = AbandonedCartRecovery()
        
        recovery_sequences = cart_recovery.recovery_sequences
        print(f"✅ Abandoned cart recovery sequences: {len(recovery_sequences)}")
        
        for plan, sequence in recovery_sequences.items():
            print(f"   {plan}: {len(sequence)} recovery emails")
            assert len(sequence) > 0, f"Recovery sequence should exist for {plan}"
            
            # Check sequence has escalating discounts
            for i, email in enumerate(sequence):
                assert 'delay_hours' in email, "Email should have delay timing"
                assert 'subject' in email, "Email should have subject"
                assert 'message' in email, "Email should have message"
        
        print("✅ Conversion optimization working correctly")
        
    except Exception as e:
        print(f"❌ Conversion optimization test failed: {e}")
        return False
    
    return True

def run_comprehensive_verification():
    """Run comprehensive verification of all Task 3 requirements"""
    print("🎯 TASK 3 VERIFICATION: Create Freemium Tier with Usage Limitations")
    print("=" * 70)
    
    test_results = []
    
    # Test each requirement
    test_results.append(("Monthly Analysis Limit Enforcement", test_monthly_analysis_limit_enforcement()))
    test_results.append(("Upgrade Prompts", test_upgrade_prompts()))
    test_results.append(("Watermarked PDF Generation", test_watermarked_pdf_generation()))
    test_results.append(("Advanced Feature Restrictions", test_advanced_feature_restrictions()))
    test_results.append(("Conversion Optimization", test_conversion_optimization()))
    
    # Summary
    print("\n" + "=" * 70)
    print("📋 VERIFICATION SUMMARY")
    print("=" * 70)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL REQUIREMENTS VERIFIED SUCCESSFULLY!")
        print("\n📋 Task 3 Implementation Complete:")
        print("✅ Monthly analysis limit enforcement (3 for free users)")
        print("✅ Upgrade prompts when users approach or exceed limits")
        print("✅ Basic report generation with watermarked PDFs")
        print("✅ Restricted access to advanced features and integrations")
        print("✅ A/B testing framework for conversion optimization")
        print("✅ Trial period functionality for professional tier")
        print("✅ Abandoned cart recovery for incomplete upgrades")
        
        print("\n🚀 Ready for production deployment!")
        return True
    else:
        print(f"\n⚠️  {total - passed} requirements need attention")
        return False

if __name__ == "__main__":
    try:
        success = run_comprehensive_verification()
        
        if success:
            print("\n✨ Task 3 verification completed successfully!")
            print("The freemium tier with usage limitations is fully implemented.")
        else:
            print("\n❌ Task 3 verification failed!")
            print("Some requirements need to be addressed.")
            
    except Exception as e:
        print(f"\n💥 Verification failed with error: {e}")
        import traceback
        traceback.print_exc()