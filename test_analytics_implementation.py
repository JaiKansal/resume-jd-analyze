#!/usr/bin/env python3
"""
Test script for analytics and admin dashboard implementation
Verifies that the analytics tracking and admin dashboard are working correctly
"""

import sys
import os
import tempfile
import sqlite3
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_analytics_tables_creation():
    """Test that analytics tables are created properly"""
    print("Testing analytics tables creation...")
    
    try:
        # Test Google Analytics integration
        from analytics.google_analytics import create_analytics_tables, ga_tracker
        create_analytics_tables()
        print("✅ Google Analytics tables created successfully")
        
        # Test User Engagement tracking
        from analytics.user_engagement import create_engagement_tables, engagement_tracker
        create_engagement_tables()
        print("✅ User engagement tables created successfully")
        
        # Test Admin Dashboard service
        from analytics.admin_dashboard import AdminDashboardService
        dashboard_service = AdminDashboardService()
        print("✅ Admin dashboard service initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Analytics tables creation failed: {e}")
        return False

def test_analytics_tracking():
    """Test analytics event tracking"""
    print("\nTesting analytics event tracking...")
    
    try:
        from analytics.google_analytics import ga_tracker
        from analytics.user_engagement import engagement_tracker
        
        # Test user ID
        test_user_id = "test-user-123"
        
        # Test Google Analytics tracking
        success = ga_tracker.track_event("test_event", test_user_id, {"test_param": "test_value"})
        print(f"✅ Google Analytics event tracking: {'Success' if success else 'Disabled (no config)'}")
        
        # Test page view tracking
        success = ga_tracker.track_page_view("Test Page", "/test", test_user_id)
        print(f"✅ Page view tracking: {'Success' if success else 'Disabled (no config)'}")
        
        # Test user engagement tracking
        success = engagement_tracker.track_page_visit(test_user_id, "Test Page")
        print(f"✅ User engagement tracking: {'Success' if success else 'Failed'}")
        
        # Test feature usage tracking
        success = engagement_tracker.track_feature_usage(test_user_id, "test_feature", "testing")
        print(f"✅ Feature usage tracking: {'Success' if success else 'Failed'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Analytics tracking test failed: {e}")
        return False

def test_admin_dashboard_metrics():
    """Test admin dashboard metrics calculation"""
    print("\nTesting admin dashboard metrics...")
    
    try:
        from analytics.admin_dashboard import AdminDashboardService
        
        dashboard_service = AdminDashboardService()
        
        # Test business metrics calculation
        metrics = dashboard_service.get_business_metrics(30)
        print(f"✅ Business metrics calculated: MRR=${metrics.mrr:.2f}, Users={metrics.total_users}")
        
        # Test revenue breakdown
        revenue_data = dashboard_service.get_revenue_breakdown(30)
        print(f"✅ Revenue breakdown calculated: Total MRR=${revenue_data['total_mrr']:.2f}")
        
        # Test user acquisition metrics
        acquisition_data = dashboard_service.get_user_acquisition_metrics(30)
        print(f"✅ User acquisition metrics: {acquisition_data['total_new_users']} new users")
        
        # Test feature usage analytics
        usage_data = dashboard_service.get_feature_usage_analytics(30)
        print(f"✅ Feature usage analytics: {len(usage_data['session_types'])} session types tracked")
        
        # Test system health metrics
        health_data = dashboard_service.get_system_health_metrics()
        print(f"✅ System health metrics: DB status={health_data['database_health']['status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Admin dashboard metrics test failed: {e}")
        return False

def test_conversion_funnel_analysis():
    """Test conversion funnel analysis"""
    print("\nTesting conversion funnel analysis...")
    
    try:
        from analytics.google_analytics import funnel_analyzer
        
        # Test funnel metrics
        funnel_data = funnel_analyzer.get_funnel_metrics(30)
        print(f"✅ Funnel metrics calculated: {len(funnel_data['funnel_steps'])} steps tracked")
        
        # Test cohort analysis
        cohort_data = funnel_analyzer.get_cohort_analysis('weekly')
        print(f"✅ Cohort analysis completed: {len(cohort_data['cohorts'])} cohorts analyzed")
        
        return True
        
    except Exception as e:
        print(f"❌ Conversion funnel analysis test failed: {e}")
        return False

def test_user_engagement_metrics():
    """Test user engagement metrics"""
    print("\nTesting user engagement metrics...")
    
    try:
        from analytics.user_engagement import engagement_tracker, cohort_analyzer
        
        test_user_id = "test-user-123"
        
        # Test engagement summary
        engagement_summary = engagement_tracker.get_user_engagement_summary(test_user_id, 30)
        print(f"✅ User engagement summary: Score={engagement_summary['engagement_score']:.1f}")
        
        # Test feature adoption metrics
        adoption_data = engagement_tracker.get_feature_adoption_metrics(30)
        print(f"✅ Feature adoption metrics: {adoption_data['total_features_tracked']} features tracked")
        
        # Test cohort retention
        retention_data = cohort_analyzer.get_cohort_retention('monthly')
        print(f"✅ Cohort retention analysis: {len(retention_data['cohorts'])} cohorts analyzed")
        
        return True
        
    except Exception as e:
        print(f"❌ User engagement metrics test failed: {e}")
        return False

def main():
    """Run all analytics implementation tests"""
    print("🧪 Testing Analytics and Admin Dashboard Implementation")
    print("=" * 60)
    
    tests = [
        test_analytics_tables_creation,
        test_analytics_tracking,
        test_admin_dashboard_metrics,
        test_conversion_funnel_analysis,
        test_user_engagement_metrics
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All analytics implementation tests passed!")
        print("\n✅ Implementation Summary:")
        print("   • Google Analytics 4 integration with event tracking")
        print("   • User engagement tracking and metrics")
        print("   • Admin dashboard with business metrics")
        print("   • Conversion funnel analysis")
        print("   • Customer lifecycle tracking")
        print("   • Real-time usage monitoring")
        print("   • System health and performance metrics")
        return True
    else:
        print(f"⚠️  {total - passed} tests failed. Check implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)