#!/usr/bin/env python3
"""
Core billing system test for Resume + JD Analyzer
Tests subscription tiers, pricing logic, and usage tracking without database dependencies
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from auth.models import PlanType, SubscriptionStatus
from billing.subscription_tiers import SubscriptionTierManager, UsageTracker

class TestSubscriptionTiers(unittest.TestCase):
    """Test subscription tier management and pricing logic"""
    
    def setUp(self):
        """Set up test environment"""
        self.tier_manager = SubscriptionTierManager()
    
    def test_tier_definitions(self):
        """Test subscription tier definitions"""
        print("\n🧪 Testing subscription tier definitions...")
        
        # Test free tier
        free_tier = self.tier_manager.get_tier_definition(PlanType.FREE)
        self.assertEqual(free_tier['price_monthly'], 0.0)
        self.assertEqual(free_tier['monthly_analysis_limit'], 3)
        self.assertTrue(free_tier['features']['basic_analysis'])
        self.assertFalse(free_tier['features']['unlimited_analyses'])
        print("✅ Free tier definition correct")
        
        # Test professional tier
        pro_tier = self.tier_manager.get_tier_definition(PlanType.PROFESSIONAL)
        self.assertEqual(pro_tier['price_monthly'], 19.0)
        self.assertEqual(pro_tier['monthly_analysis_limit'], -1)  # Unlimited
        self.assertTrue(pro_tier['features']['unlimited_analyses'])
        self.assertTrue(pro_tier['features']['premium_ai'])
        print("✅ Professional tier definition correct")
        
        # Test business tier
        business_tier = self.tier_manager.get_tier_definition(PlanType.BUSINESS)
        self.assertEqual(business_tier['price_monthly'], 99.0)
        self.assertTrue(business_tier['features']['team_collaboration'])
        self.assertTrue(business_tier['features']['bulk_upload'])
        print("✅ Business tier definition correct")
        
        # Test enterprise tier
        enterprise_tier = self.tier_manager.get_tier_definition(PlanType.ENTERPRISE)
        self.assertEqual(enterprise_tier['price_monthly'], 500.0)
        self.assertTrue(enterprise_tier['features']['sso'])
        self.assertTrue(enterprise_tier['features']['unlimited_seats'])
        print("✅ Enterprise tier definition correct")
    
    def test_pricing_calculation(self):
        """Test pricing calculation with regional adjustments"""
        print("\n🧪 Testing pricing calculations...")
        
        # Test US pricing (base)
        us_pricing = self.tier_manager.calculate_pricing(PlanType.PROFESSIONAL, 'monthly', 1, 'US')
        self.assertEqual(us_pricing['adjusted_price'], 19.0)
        self.assertEqual(us_pricing['regional_multiplier'], 1.0)
        self.assertEqual(us_pricing['currency'], 'USD')
        print("✅ US pricing calculation correct")
        
        # Test UK pricing (85% of US)
        uk_pricing = self.tier_manager.calculate_pricing(PlanType.PROFESSIONAL, 'monthly', 1, 'UK')
        expected_price = 19.0 * 0.85
        self.assertEqual(uk_pricing['adjusted_price'], expected_price)
        self.assertEqual(uk_pricing['regional_multiplier'], 0.85)
        self.assertEqual(uk_pricing['currency'], 'GBP')
        print("✅ UK pricing calculation correct")
        
        # Test India pricing (60% of US)
        in_pricing = self.tier_manager.calculate_pricing(PlanType.PROFESSIONAL, 'monthly', 1, 'IN')
        expected_price = 19.0 * 0.6
        self.assertEqual(in_pricing['adjusted_price'], expected_price)
        self.assertEqual(in_pricing['regional_multiplier'], 0.6)
        self.assertEqual(in_pricing['currency'], 'INR')
        print("✅ India pricing calculation correct")
        
        # Test annual pricing with savings
        annual_pricing = self.tier_manager.calculate_pricing(PlanType.PROFESSIONAL, 'annual', 1, 'US')
        self.assertEqual(annual_pricing['adjusted_price'], 190.0)
        expected_savings = 19.0 * 12 - 190.0
        self.assertEqual(annual_pricing['annual_savings'], expected_savings)
        print("✅ Annual pricing calculation correct")
    
    def test_business_seat_pricing(self):
        """Test business tier seat-based pricing"""
        print("\n🧪 Testing business seat pricing...")
        
        # Test base 5 seats
        base_pricing = self.tier_manager.calculate_pricing(PlanType.BUSINESS, 'monthly', 5, 'US')
        self.assertEqual(base_pricing['adjusted_price'], 99.0)
        print("✅ Base 5 seats pricing correct")
        
        # Test additional seats
        extra_seats_pricing = self.tier_manager.calculate_pricing(PlanType.BUSINESS, 'monthly', 8, 'US')
        expected_price = 99.0 + (3 * 15)  # 3 additional seats at $15 each
        self.assertEqual(extra_seats_pricing['adjusted_price'], expected_price)
        print("✅ Additional seats pricing correct")
    
    def test_upgrade_path_validation(self):
        """Test upgrade path validation"""
        print("\n🧪 Testing upgrade path validation...")
        
        # Valid upgrades
        self.assertTrue(self.tier_manager.can_upgrade_to(PlanType.FREE, PlanType.PROFESSIONAL))
        self.assertTrue(self.tier_manager.can_upgrade_to(PlanType.PROFESSIONAL, PlanType.BUSINESS))
        self.assertTrue(self.tier_manager.can_upgrade_to(PlanType.BUSINESS, PlanType.ENTERPRISE))
        print("✅ Valid upgrade paths work")
        
        # Invalid upgrades (downgrades)
        self.assertFalse(self.tier_manager.can_upgrade_to(PlanType.PROFESSIONAL, PlanType.FREE))
        self.assertFalse(self.tier_manager.can_upgrade_to(PlanType.ENTERPRISE, PlanType.BUSINESS))
        print("✅ Invalid upgrade paths blocked")
        
        # Same tier
        self.assertFalse(self.tier_manager.can_upgrade_to(PlanType.PROFESSIONAL, PlanType.PROFESSIONAL))
        print("✅ Same tier upgrade blocked")
    
    def test_all_tiers_retrieval(self):
        """Test getting all tier definitions"""
        print("\n🧪 Testing all tiers retrieval...")
        
        all_tiers = self.tier_manager.get_all_tiers()
        self.assertEqual(len(all_tiers), 4)
        
        # Check order (should be Free, Professional, Business, Enterprise)
        tier_types = [tier['plan_type'] for tier in all_tiers]
        expected_order = [PlanType.FREE, PlanType.PROFESSIONAL, PlanType.BUSINESS, PlanType.ENTERPRISE]
        self.assertEqual(tier_types, expected_order)
        print("✅ All tiers retrieved in correct order")
        
        # Check all tiers have required fields
        for tier in all_tiers:
            self.assertIn('name', tier)
            self.assertIn('price_monthly', tier)
            self.assertIn('features', tier)
            self.assertIn('description', tier)
            self.assertIn('target_audience', tier)
        print("✅ All tiers have required fields")

class TestFeatureAccess(unittest.TestCase):
    """Test feature access logic"""
    
    def setUp(self):
        """Set up test environment"""
        self.tier_manager = SubscriptionTierManager()
    
    def test_free_tier_features(self):
        """Test free tier feature access"""
        print("\n🧪 Testing free tier features...")
        
        free_features = self.tier_manager.get_tier_definition(PlanType.FREE)['features']
        
        # Should have basic features
        self.assertTrue(free_features['basic_analysis'])
        self.assertTrue(free_features['pdf_download'])
        self.assertTrue(free_features['basic_reports'])
        print("✅ Free tier has basic features")
        
        # Should not have premium features
        self.assertFalse(free_features['unlimited_analyses'])
        self.assertFalse(free_features['premium_ai'])
        self.assertFalse(free_features['team_collaboration'])
        self.assertFalse(free_features['api_access'])
        print("✅ Free tier lacks premium features")
        
        # Should have limitations
        self.assertTrue(free_features['watermarked_pdfs'])
        self.assertTrue(free_features['limited_file_size'])
        print("✅ Free tier has expected limitations")
    
    def test_professional_tier_features(self):
        """Test professional tier feature access"""
        print("\n🧪 Testing professional tier features...")
        
        pro_features = self.tier_manager.get_tier_definition(PlanType.PROFESSIONAL)['features']
        
        # Should have all free features plus professional features
        self.assertTrue(pro_features['basic_analysis'])
        self.assertTrue(pro_features['unlimited_analyses'])
        self.assertTrue(pro_features['premium_ai'])
        self.assertTrue(pro_features['all_formats'])
        self.assertTrue(pro_features['priority_processing'])
        print("✅ Professional tier has expected features")
        
        # Should not have watermarks
        self.assertFalse(pro_features['watermarked_pdfs'])
        self.assertFalse(pro_features['limited_file_size'])
        print("✅ Professional tier removes limitations")
        
        # Should not have business features
        self.assertFalse(pro_features['team_collaboration'])
        self.assertFalse(pro_features['bulk_upload'])
        self.assertFalse(pro_features['api_access'])
        print("✅ Professional tier lacks business features")
    
    def test_business_tier_features(self):
        """Test business tier feature access"""
        print("\n🧪 Testing business tier features...")
        
        business_features = self.tier_manager.get_tier_definition(PlanType.BUSINESS)['features']
        
        # Should have all professional features plus business features
        self.assertTrue(business_features['unlimited_analyses'])
        self.assertTrue(business_features['premium_ai'])
        self.assertTrue(business_features['team_collaboration'])
        self.assertTrue(business_features['bulk_upload'])
        self.assertTrue(business_features['analytics_dashboard'])
        self.assertTrue(business_features['api_access'])
        print("✅ Business tier has expected features")
        
        # Should not have enterprise features
        self.assertFalse(business_features['sso'])
        self.assertFalse(business_features['unlimited_seats'])
        self.assertFalse(business_features['white_label'])
        print("✅ Business tier lacks enterprise features")
    
    def test_enterprise_tier_features(self):
        """Test enterprise tier feature access"""
        print("\n🧪 Testing enterprise tier features...")
        
        enterprise_features = self.tier_manager.get_tier_definition(PlanType.ENTERPRISE)['features']
        
        # Should have all features
        self.assertTrue(enterprise_features['unlimited_analyses'])
        self.assertTrue(enterprise_features['team_collaboration'])
        self.assertTrue(enterprise_features['api_access'])
        self.assertTrue(enterprise_features['sso'])
        self.assertTrue(enterprise_features['unlimited_seats'])
        self.assertTrue(enterprise_features['white_label'])
        self.assertTrue(enterprise_features['custom_features'])
        self.assertTrue(enterprise_features['dedicated_support'])
        print("✅ Enterprise tier has all features")

class TestUsageLimits(unittest.TestCase):
    """Test usage limits and tracking"""
    
    def setUp(self):
        """Set up test environment"""
        self.tier_manager = SubscriptionTierManager()
    
    def test_analysis_limits(self):
        """Test analysis limits for different tiers"""
        print("\n🧪 Testing analysis limits...")
        
        # Free tier: 3 analyses per month
        free_tier = self.tier_manager.get_tier_definition(PlanType.FREE)
        self.assertEqual(free_tier['monthly_analysis_limit'], 3)
        print("✅ Free tier has 3 analysis limit")
        
        # Professional tier: unlimited
        pro_tier = self.tier_manager.get_tier_definition(PlanType.PROFESSIONAL)
        self.assertEqual(pro_tier['monthly_analysis_limit'], -1)
        print("✅ Professional tier has unlimited analyses")
        
        # Business tier: unlimited
        business_tier = self.tier_manager.get_tier_definition(PlanType.BUSINESS)
        self.assertEqual(business_tier['monthly_analysis_limit'], -1)
        print("✅ Business tier has unlimited analyses")
        
        # Enterprise tier: unlimited
        enterprise_tier = self.tier_manager.get_tier_definition(PlanType.ENTERPRISE)
        self.assertEqual(enterprise_tier['monthly_analysis_limit'], -1)
        print("✅ Enterprise tier has unlimited analyses")
    
    def test_api_limits(self):
        """Test API call limits for different tiers"""
        print("\n🧪 Testing API limits...")
        
        # Free and Professional: no API access
        self.assertEqual(self.tier_manager._get_api_limit(PlanType.FREE), 0)
        self.assertEqual(self.tier_manager._get_api_limit(PlanType.PROFESSIONAL), 0)
        print("✅ Free and Professional tiers have no API access")
        
        # Business: 1000 calls per month
        self.assertEqual(self.tier_manager._get_api_limit(PlanType.BUSINESS), 1000)
        print("✅ Business tier has 1000 API calls limit")
        
        # Enterprise: unlimited
        self.assertEqual(self.tier_manager._get_api_limit(PlanType.ENTERPRISE), -1)
        print("✅ Enterprise tier has unlimited API calls")

def run_core_tests():
    """Run all core billing tests"""
    print("🧪 Running Core Billing System Tests...")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestSubscriptionTiers,
        TestFeatureAccess,
        TestUsageLimits
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=0)  # Reduced verbosity since we have custom prints
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ All core billing tests passed!")
        print(f"📊 Ran {result.testsRun} tests successfully")
        print("\n🎯 Key Features Verified:")
        print("  • Subscription tier definitions and pricing")
        print("  • Regional pricing adjustments (PPP)")
        print("  • Feature access control by tier")
        print("  • Usage limits and API restrictions")
        print("  • Upgrade path validation")
        print("  • Seat-based pricing for business tier")
    else:
        print("❌ Some tests failed!")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        
        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"- {test}")
        
        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"- {test}")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_core_tests()
    sys.exit(0 if success else 1)