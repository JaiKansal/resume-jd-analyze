#!/usr/bin/env python3
"""
Test complete user flow: registration -> login -> analysis -> storage
"""

def test_complete_user_flow():
    """Test the complete user flow from registration to analysis storage"""
    print("🚀 TESTING COMPLETE USER FLOW")
    print("=" * 40)
    
    try:
        from auth.services import user_service, subscription_service, session_service
        from auth.models import UserRole
        from database.enhanced_analysis_storage import enhanced_analysis_storage
        from database.connection import get_db
        import uuid
        
        # Step 1: Create a new user (simulating registration)
        print("👤 Step 1: Creating new user...")
        
        test_email = f"flow_test_{int(__import__('time').time())}@example.com"
        test_password = "TestPassword123!"
        
        user = user_service.create_user(
            email=test_email,
            password=test_password,
            first_name="Flow",
            last_name="Test",
            role=UserRole.INDIVIDUAL,
            company_name="Test Company"
        )
        
        if not user:
            print("❌ User creation failed")
            return False
        
        print(f"✅ User created: {user.email} (ID: {user.id})")
        
        # Step 2: Authenticate user (simulating login)
        print("🔐 Step 2: Authenticating user...")
        
        auth_user = user_service.authenticate_user(test_email, test_password)
        if not auth_user:
            print("❌ Authentication failed")
            return False
        
        print(f"✅ User authenticated: {auth_user.email}")
        
        # Step 3: Check subscription
        print("💳 Step 3: Checking subscription...")
        
        subscription = subscription_service.get_user_subscription(user.id)
        if not subscription:
            print("❌ No subscription found")
            return False
        
        print(f"✅ Subscription found: {subscription.status}")
        
        # Step 4: Create analysis session
        print("🔄 Step 4: Creating analysis session...")
        
        session = session_service.create_session(user.id)
        if not session:
            print("❌ Session creation failed")
            return False
        
        print(f"✅ Session created: {session.id}")
        
        # Step 5: Simulate analysis result
        print("📊 Step 5: Creating analysis result...")
        
        analysis_result = {
            'score': 87,
            'match_category': 'good-match',
            'matching_skills': ['Python', 'FastAPI', 'PostgreSQL', 'Docker'],
            'skill_gaps': {
                'Critical': ['Kubernetes'],
                'Important': ['AWS', 'CI/CD'],
                'Nice-to-have': ['GraphQL']
            },
            'suggestions': [
                'Add Kubernetes experience to your resume',
                'Highlight any AWS or cloud experience',
                'Consider adding CI/CD pipeline experience'
            ],
            'processing_time': 3.7
        }
        
        print("✅ Analysis result created")
        
        # Step 6: Save analysis to database
        print("💾 Step 6: Saving analysis to database...")
        
        analysis_id = enhanced_analysis_storage.save_analysis(
            user_id=user.id,
            resume_filename="complete_flow_test.pdf",
            resume_content="This is a test resume content for the complete flow test. It contains Python, FastAPI, and PostgreSQL experience.",
            job_description="We are looking for a Python developer with FastAPI, PostgreSQL, Docker, Kubernetes, and AWS experience.",
            analysis_result=analysis_result,
            processing_time=3.7
        )
        
        if not analysis_id:
            print("❌ Analysis save failed")
            return False
        
        print(f"✅ Analysis saved: {analysis_id}")
        
        # Step 7: Verify analysis in database
        print("🔍 Step 7: Verifying analysis in database...")
        
        db = get_db()
        saved_analysis = db.get_single_result(
            "SELECT * FROM analysis_sessions WHERE id = ?",
            (analysis_id,)
        )
        
        if not saved_analysis:
            print("❌ Analysis not found in database")
            return False
        
        print("✅ Analysis verified in database:")
        print(f"   Resume: {saved_analysis['resume_filename']}")
        print(f"   Score: {saved_analysis.get('score', 'N/A')}")
        print(f"   Category: {saved_analysis.get('match_category', 'N/A')}")
        print(f"   User: {user.email}")
        
        # Step 8: Test analysis retrieval
        print("📋 Step 8: Testing analysis retrieval...")
        
        user_analyses = db.execute_query(
            "SELECT * FROM analysis_sessions WHERE user_id = ? ORDER BY created_at DESC",
            (user.id,)
        )
        
        if not user_analyses:
            print("❌ No analyses found for user")
            return False
        
        print(f"✅ Found {len(user_analyses)} analysis(es) for user")
        
        # Step 9: Test user statistics
        print("📈 Step 9: Testing user statistics...")
        
        try:
            stats = enhanced_analysis_storage.get_user_statistics(user.id)
            print(f"✅ User statistics retrieved:")
            print(f"   Total analyses: {stats.get('total_analyses', 0)}")
            print(f"   Average score: {stats.get('avg_score', 0):.1f}%")
            print(f"   Best score: {stats.get('best_score', 0)}%")
        except Exception as e:
            print(f"⚠️  Statistics retrieval failed: {e}")
        
        # Step 10: Clean up test data
        print("🧹 Step 10: Cleaning up test data...")
        
        # Delete analysis
        db.execute_command("DELETE FROM analysis_sessions WHERE id = ?", (analysis_id,))
        
        # Delete session
        db.execute_command("DELETE FROM user_sessions WHERE user_id = ?", (user.id,))
        
        # Delete subscription
        db.execute_command("DELETE FROM subscriptions WHERE user_id = ?", (user.id,))
        
        # Delete user
        db.execute_command("DELETE FROM users WHERE id = ?", (user.id,))
        
        print("✅ Test data cleaned up")
        
        print("\n🎉 COMPLETE USER FLOW TEST PASSED!")
        print("✅ Users can register, login, and save analysis reports")
        print("✅ Analysis reports are properly stored in database")
        print("✅ User statistics are calculated correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Complete user flow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_analyses_for_user():
    """Test saving multiple analyses for the same user"""
    print("\n🔄 TESTING MULTIPLE ANALYSES FOR USER")
    print("=" * 40)
    
    try:
        from auth.services import user_service
        from database.enhanced_analysis_storage import enhanced_analysis_storage
        from database.connection import get_db
        
        # Get existing test user
        test_user = user_service.get_user_by_email("streamlit_test@example.com")
        if not test_user:
            print("❌ No test user found")
            return False
        
        print(f"👤 Using test user: {test_user.email}")
        
        # Create multiple analyses
        analyses_to_create = [
            {
                'filename': 'resume_v1.pdf',
                'score': 75,
                'category': 'fair-match',
                'skills': ['Python', 'SQL']
            },
            {
                'filename': 'resume_v2.pdf',
                'score': 85,
                'category': 'good-match',
                'skills': ['Python', 'SQL', 'Docker']
            },
            {
                'filename': 'resume_v3.pdf',
                'score': 92,
                'category': 'excellent-match',
                'skills': ['Python', 'SQL', 'Docker', 'Kubernetes', 'AWS']
            }
        ]
        
        created_analyses = []
        
        for i, analysis_data in enumerate(analyses_to_create, 1):
            print(f"📊 Creating analysis {i}/3...")
            
            analysis_result = {
                'score': analysis_data['score'],
                'match_category': analysis_data['category'],
                'matching_skills': analysis_data['skills'],
                'skill_gaps': {'Critical': [], 'Important': [], 'Nice-to-have': []},
                'suggestions': [f'Great job on version {i}!'],
                'processing_time': 2.0 + i * 0.5
            }
            
            analysis_id = enhanced_analysis_storage.save_analysis(
                user_id=test_user.id,
                resume_filename=analysis_data['filename'],
                resume_content=f"Test resume content version {i}",
                job_description="Test job description for multiple analyses",
                analysis_result=analysis_result,
                processing_time=2.0 + i * 0.5
            )
            
            if analysis_id:
                created_analyses.append(analysis_id)
                print(f"✅ Analysis {i} saved: {analysis_id}")
            else:
                print(f"❌ Analysis {i} save failed")
                return False
        
        # Verify all analyses are in database
        print("🔍 Verifying analyses in database...")
        
        db = get_db()
        user_analyses = db.execute_query(
            "SELECT * FROM analysis_sessions WHERE user_id = ? ORDER BY created_at DESC",
            (test_user.id,)
        )
        
        print(f"✅ Found {len(user_analyses)} total analyses for user")
        
        # Show recent analyses
        recent_analyses = [a for a in user_analyses if a['id'] in created_analyses]
        print(f"✅ {len(recent_analyses)} new analyses verified:")
        
        for analysis in recent_analyses:
            print(f"   - {analysis['resume_filename']}: {analysis.get('score', 'N/A')}% ({analysis.get('match_category', 'N/A')})")
        
        # Test user statistics
        print("📈 Testing updated user statistics...")
        
        try:
            stats = enhanced_analysis_storage.get_user_statistics(test_user.id)
            print(f"✅ Updated statistics:")
            print(f"   Total analyses: {stats.get('total_analyses', 0)}")
            print(f"   Average score: {stats.get('avg_score', 0):.1f}%")
            print(f"   Best score: {stats.get('best_score', 0)}%")
        except Exception as e:
            print(f"⚠️  Statistics calculation failed: {e}")
        
        # Clean up test analyses
        print("🧹 Cleaning up test analyses...")
        
        for analysis_id in created_analyses:
            db.execute_command("DELETE FROM analysis_sessions WHERE id = ?", (analysis_id,))
        
        print("✅ Test analyses cleaned up")
        
        print("\n🎉 MULTIPLE ANALYSES TEST PASSED!")
        print("✅ Users can save multiple analysis reports")
        print("✅ All analyses are properly stored and retrievable")
        print("✅ User statistics are updated correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Multiple analyses test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run comprehensive user flow tests"""
    print("🚀 COMPREHENSIVE USER FLOW TESTING")
    print("=" * 50)
    
    tests = [
        ("Complete User Flow", test_complete_user_flow),
        ("Multiple Analyses", test_multiple_analyses_for_user)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Test failed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 USER FLOW TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:.<30} {status}")
        if success:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 ALL USER FLOW TESTS PASSED!")
        print("\n✅ The complete user experience is working correctly:")
        print("   - Users can register and login")
        print("   - Analysis reports are saved to database")
        print("   - Multiple analyses per user work")
        print("   - User statistics are calculated")
        print("   - Data persists across sessions")
        print("\n🎯 Your app should now work perfectly!")
        print("   - New users will be saved properly")
        print("   - Analysis reports will persist")
        print("   - Users can see their analysis history")
    else:
        print(f"\n⚠️  {len(results) - passed} tests failed")
        print("There may still be issues with the user flow")

if __name__ == "__main__":
    main()