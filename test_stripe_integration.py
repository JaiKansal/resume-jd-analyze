#!/usr/bin/env python3
"""
Test Stripe integration and billing system for Resume + JD Analyzer
Tests subscription management, usage tracking, and webhook handling
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from auth.models import User, PlanType, SubscriptionStatus
from auth.services import user_service, subscription_service
from billing.stripe_service import stripe_service
from billing.subscription_tiers import tier_manager, usage_tracker
from billing.usage_tracker import usage_monitor, billing_system
from billing.webhook_handler import webhook_handler

class TestStripeIntegration(unittest.TestCase):
    """Test Stripe payment processing integration"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock Stripe API key
        os.environ['STRIPE_SECRET_KEY'] = 'sk_test_mock_key'
        os.environ['STRIPE_WEBHOOK_SECRET'] = 'whsec_mock_secret'
        
        # Create test user
        self.test_user = User.create(
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User"
        )
    
    @patch('stripe.Customer.create')
    def test_create_stripe_customer(self, mock_create):
        """Test Stripe customer creation"""
        # Mock Stripe response
        mock_create.return_value = Mock(id='cus_test123')
        
        # Create customer
        customer_id = stripe_service.create_customer(self.test_user)
        
        # Verify
        self.assertEqual(customer_id, 'cus_test123')
        mock_create.assert_called_once()
        
        # Check call arguments
        call_args = mock_create.call_args[1]
        self.assertEqual(call_args['email'], self.test_user.email)
        self.assertEqual(call_args['name'], self.test_user.get_full_name())
    
    @patch('stripe.Subscription.create')
    @patch('billing.stripe_service.StripeService._get_or_create_customer')
    def test_create_subscription(self, mock_get_customer, mock_create_sub):
        """Test Stripe subscription creation"""
        # Mock responses
        mock_get_customer.return_value = 'cus_test123'
        mock_create_sub.return_value = Mock(
            id='sub_test123',
            status='active',
            current_period_start=1640995200,  # 2022-01-01
            current_period_end=1643673600,    # 2022-02-01
            latest_invoice=Mock(
                payment_intent=Mock(client_secret='pi_test_secret')
            )
        )
        
        # Create subscription
        result = stripe_service.create_subscription(
            user_id=self.test_user.id,
            plan_id='plan_professional',
            payment_method_id='pm_test123'
        )
        
        # Verify
        self.assertIsNotNone(result)
        self.assertEqual(result['subscription_id'], 'sub_test123')
        self.assertEqual(result['status'], 'active')
        self.assertIn('client_secret', result)
    
    @patch('stripe.PaymentIntent.create')
    def test_create_payment_intent(self, mock_create):
        """Test payment intent creation"""
        # Mock response
        mock_create.return_value = Mock(
            id='pi_test123',
            client_secret='pi_test123_secret'
        )
        
        # Create payment intent
        result = stripe_service.create_payment_intent(
            amount=1900,  # $19.00
            customer_id='cus_test123'
        )
        
        # Verify
        self.assertIsNotNone(result)
        self.assertEqual(result['payment_intent_id'], 'pi_test123')
        self.assertEqual(result['client_secret'], 'pi_test123_secret')

class TestSubscriptionTiers(unittest.TestCase):
    """Test subscription tier management and pricing logic"""
    
    def test_tier_definitions(self):
        """Test subscription tier definitions"""
        # Test free tier
        free_tier = tier_manager.get_tier_definition(PlanType.FREE)
        self.assertEqual(free_tier['price_monthly'], 0.0)
        self.assertEqual(free_tier['monthly_analysis_limit'], 3)
        self.assertTrue(free_tier['features']['basic_analysis'])
        self.assertFalse(free_tier['features']['unlimited_analyses'])
        
        # Test professional tier
        pro_tier = tier_manager.get_tier_definition(PlanType.PROFESSIONAL)
        self.assertEqual(pro_tier['price_monthly'], 19.0)
        self.assertEqual(pro_tier['monthly_analysis_limit'], -1)  # Unlimited
        self.assertTrue(pro_tier['features']['unlimited_analyses'])
        self.assertTrue(pro_tier['features']['premium_ai'])
        
        # Test business tier
        business_tier = tier_manager.get_tier_definition(PlanType.BUSINESS)
        self.assertEqual(business_tier['price_monthly'], 99.0)
        self.assertTrue(business_tier['features']['team_collaboration'])
        self.assertTrue(business_tier['features']['bulk_upload'])
        
        # Test enterprise tier
        enterprise_tier = tier_manager.get_tier_definition(PlanType.ENTERPRISE)
        self.assertEqual(enterprise_tier['price_monthly'], 500.0)
        self.assertTrue(enterprise_tier['features']['sso'])
        self.assertTrue(enterprise_tier['features']['unlimited_seats'])
    
    def test_feature_access_check(self):
        """Test feature access checking"""
        # Mock user with professional subscription
        with patch('auth.services.subscription_service.get_user_subscription') as mock_get_sub:
            mock_subscription = Mock()
            mock_subscription.plan.plan_type = PlanType.PROFESSIONAL
            mock_get_sub.return_value = mock_subscription
            
            # Test feature access
            self.assertTrue(tier_manager.check_feature_access('user123', 'premium_ai'))
            self.assertTrue(tier_manager.check_feature_access('user123', 'unlimited_analyses'))
            self.assertFalse(tier_manager.check_feature_access('user123', 'team_collaboration'))
            self.assertFalse(tier_manager.check_feature_access('user123', 'sso'))
    
    def test_pricing_calculation(self):
        """Test pricing calculation with regional adjustments"""
        # Test US pricing (base)
        us_pricing = tier_manager.calculate_pricing(PlanType.PROFESSIONAL, 'monthly', 1, 'US')
        self.assertEqual(us_pricing['adjusted_price'], 19.0)
        self.assertEqual(us_pricing['regional_multiplier'], 1.0)
        
        # Test UK pricing (85% of US)
        uk_pricing = tier_manager.calculate_pricing(PlanType.PROFESSIONAL, 'monthly', 1, 'UK')
        self.assertEqual(uk_pricing['adjusted_price'], 19.0 * 0.85)
        self.assertEqual(uk_pricing['regional_multiplier'], 0.85)
        
        # Test India pricing (60% of US)
        in_pricing = tier_manager.calculate_pricing(PlanType.PROFESSIONAL, 'monthly', 1, 'IN')
        self.assertEqual(in_pricing['adjusted_price'], 19.0 * 0.6)
        self.assertEqual(in_pricing['regional_multiplier'], 0.6)
        
        # Test annual pricing with savings
        annual_pricing = tier_manager.calculate_pricing(PlanType.PROFESSIONAL, 'annual', 1, 'US')
        self.assertEqual(annual_pricing['adjusted_price'], 190.0)
        self.assertEqual(annual_pricing['annual_savings'], 19.0 * 12 - 190.0)
    
    def test_upgrade_recommendations(self):
        """Test upgrade recommendations"""
        with patch('auth.services.subscription_service.get_user_subscription') as mock_get_sub:
            # Mock free user near limit
            mock_subscription = Mock()
            mock_subscription.plan.plan_type = PlanType.FREE
            mock_subscription.plan.monthly_analysis_limit = 3
            mock_subscription.monthly_analysis_used = 3
            mock_get_sub.return_value = mock_subscription
            
            recommendations = tier_manager.get_upgrade_recommendations('user123')
            self.assertGreater(len(recommendations), 0)
            
            # Check for usage limit recommendation
            usage_rec = next((r for r in recommendations if r['reason'] == 'usage_limit'), None)
            self.assertIsNotNone(usage_rec)
            self.assertEqual(usage_rec['suggested_plan'], PlanType.PROFESSIONAL)

class TestUsageTracking(unittest.TestCase):
    """Test usage tracking and billing system"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_user_id = 'user123'
    
    @patch('billing.usage_tracker.RealTimeUsageMonitor._track_usage_event')
    @patch('auth.services.subscription_service.increment_user_usage')
    @patch('auth.services.analytics_service.track_analysis_session')
    def test_track_analysis_session(self, mock_track_session, mock_increment, mock_track_event):
        """Test analysis session tracking"""
        # Track session
        result = usage_monitor.track_analysis_session(
            user_id=self.test_user_id,
            session_type='single',
            resume_count=1,
            processing_time=15.5,
            api_cost=0.25
        )
        
        # Verify
        self.assertTrue(result)
        mock_increment.assert_called_once_with(self.test_user_id, 1)
        mock_track_event.assert_called_once()
        mock_track_session.assert_called_once()
    
    def test_usage_limit_checking(self):
        """Test usage limit enforcement"""
        with patch('auth.services.subscription_service.get_user_subscription') as mock_get_sub:
            # Mock subscription with limits
            mock_subscription = Mock()
            mock_subscription.is_active.return_value = True
            mock_subscription.plan.monthly_analysis_limit = 3
            mock_subscription.monthly_analysis_used = 2
            mock_get_sub.return_value = mock_subscription
            
            # Test within limits
            can_analyze, reason = usage_monitor.check_usage_limits(self.test_user_id, 1)
            self.assertTrue(can_analyze)
            self.assertIsNone(reason)
            
            # Test exceeding limits
            can_analyze, reason = usage_monitor.check_usage_limits(self.test_user_id, 2)
            self.assertFalse(can_analyze)
            self.assertIn('Insufficient analyses remaining', reason)
    
    def test_rate_limiting(self):
        """Test rate limiting enforcement"""
        with patch('billing.usage_tracker.RealTimeUsageMonitor._get_usage_count') as mock_count:
            # Test within rate limits
            mock_count.return_value = 5
            can_proceed, reason = usage_monitor.enforce_rate_limits(self.test_user_id, 'analysis')
            self.assertTrue(can_proceed)
            
            # Test exceeding minute limit
            mock_count.return_value = 15
            can_proceed, reason = usage_monitor.enforce_rate_limits(self.test_user_id, 'analysis')
            self.assertFalse(can_proceed)
            self.assertIn('Rate limit exceeded', reason)

class TestWebhookHandling(unittest.TestCase):
    """Test Stripe webhook handling"""
    
    def test_subscription_created_webhook(self):
        """Test subscription created webhook handling"""
        webhook_data = {
            'id': 'sub_test123',
            'customer': 'cus_test123',
            'status': 'active',
            'current_period_start': 1640995200,
            'current_period_end': 1643673600,
            'metadata': {'user_id': 'user123'}
        }
        
        with patch('auth.services.subscription_service.get_user_subscription') as mock_get_sub:
            mock_subscription = Mock()
            mock_get_sub.return_value = mock_subscription
            
            result = webhook_handler._handle_subscription_created(webhook_data)
            
            self.assertEqual(result['status'], 'processed')
            # Verify subscription was updated
            self.assertEqual(mock_subscription.stripe_subscription_id, 'sub_test123')
    
    def test_payment_succeeded_webhook(self):
        """Test payment succeeded webhook handling"""
        invoice_data = {
            'id': 'in_test123',
            'customer': 'cus_test123',
            'amount_paid': 1900,  # $19.00 in cents
            'payment_intent': 'pi_test123',
            'billing_reason': 'subscription_cycle'
        }
        
        with patch('billing.webhook_handler.StripeWebhookHandler._get_subscription_by_customer_id') as mock_get_sub:
            mock_subscription = Mock()
            mock_subscription.user_id = 'user123'
            mock_subscription.id = 'sub123'
            mock_get_sub.return_value = mock_subscription
            
            with patch('billing.webhook_handler.StripeWebhookHandler._track_revenue_event') as mock_track:
                result = webhook_handler._handle_payment_succeeded(invoice_data)
                
                self.assertEqual(result['status'], 'processed')
                mock_track.assert_called_once()
    
    def test_payment_failed_webhook(self):
        """Test payment failed webhook handling"""
        invoice_data = {
            'id': 'in_test123',
            'customer': 'cus_test123',
            'attempt_count': 1
        }
        
        with patch('billing.webhook_handler.StripeWebhookHandler._get_subscription_by_customer_id') as mock_get_sub:
            mock_subscription = Mock()
            mock_subscription.id = 'sub123'
            mock_get_sub.return_value = mock_subscription
            
            with patch('billing.usage_tracker.billing_system.handle_failed_payment') as mock_handle:
                result = webhook_handler._handle_payment_failed(invoice_data)
                
                self.assertEqual(result['status'], 'processed')
                mock_handle.assert_called_once_with('sub123', 1)

class TestBillingSystem(unittest.TestCase):
    """Test automated billing system"""
    
    def test_subscription_renewal(self):
        """Test subscription renewal processing"""
        with patch('auth.services.subscription_service.get_subscription_by_id') as mock_get_sub:
            mock_subscription = Mock()
            mock_subscription.user_id = 'user123'
            mock_subscription.id = 'sub123'
            mock_subscription.plan.price_monthly = 19.0
            mock_get_sub.return_value = mock_subscription
            
            with patch('auth.services.subscription_service.update_subscription') as mock_update:
                result = billing_system.process_subscription_renewal('sub123')
                
                self.assertTrue(result)
                mock_update.assert_called_once()
                # Verify usage was reset
                mock_subscription.reset_monthly_usage.assert_called_once()
    
    def test_failed_payment_handling(self):
        """Test failed payment handling with dunning management"""
        with patch('auth.services.subscription_service.get_subscription_by_id') as mock_get_sub:
            mock_subscription = Mock()
            mock_subscription.user_id = 'user123'
            mock_get_sub.return_value = mock_subscription
            
            with patch('auth.services.subscription_service.update_subscription') as mock_update:
                # Test first attempt
                result = billing_system.handle_failed_payment('sub123', 1)
                self.assertTrue(result)
                
                # Test final attempt (should cancel)
                result = billing_system.handle_failed_payment('sub123', 4)
                self.assertTrue(result)
                # Verify subscription was cancelled
                self.assertEqual(mock_subscription.status, SubscriptionStatus.CANCELLED)
    
    def test_prorated_calculation(self):
        """Test prorated amount calculation for plan changes"""
        # Mock subscription
        mock_subscription = Mock()
        mock_subscription.current_period_start = datetime(2024, 1, 1)
        mock_subscription.current_period_end = datetime(2024, 1, 31)
        mock_subscription.plan.price_monthly = 19.0
        
        # Test upgrade mid-month (15 days remaining)
        change_date = datetime(2024, 1, 16)
        prorated = billing_system.calculate_prorated_amount(
            mock_subscription, 99.0, change_date
        )
        
        # Should be positive (upgrade charge)
        self.assertGreater(prorated, 0)
        
        # Test downgrade
        prorated = billing_system.calculate_prorated_amount(
            mock_subscription, 0.0, change_date
        )
        
        # Should be 0 (no negative charges)
        self.assertEqual(prorated, 0)

def run_integration_tests():
    """Run all integration tests"""
    print("🧪 Running Stripe Integration Tests...")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestStripeIntegration,
        TestSubscriptionTiers,
        TestUsageTracking,
        TestWebhookHandling,
        TestBillingSystem
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All tests passed!")
        print(f"Ran {result.testsRun} tests successfully")
    else:
        print("❌ Some tests failed!")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        
        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"- {test}: {traceback}")
        
        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"- {test}: {traceback}")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_integration_tests()
    sys.exit(0 if success else 1)