#!/usr/bin/env python3
"""
Test analysis storage functionality
"""

def test_enhanced_services():
    """Test if enhanced services are available"""
    print("🔍 TESTING ENHANCED SERVICES AVAILABILITY")
    print("=" * 45)
    
    try:
        # Test enhanced analysis storage import
        print("🔄 Testing enhanced analysis storage import...")
        from database.enhanced_analysis_storage import enhanced_analysis_storage
        print("✅ Enhanced analysis storage imported successfully")
        
        # Test report history UI import
        print("🔄 Testing report history UI import...")
        from components.report_history_ui import report_history_ui
        print("✅ Report history UI imported successfully")
        
        print("✅ ENHANCED_SERVICES_AVAILABLE should be True")
        return True
        
    except ImportError as e:
        print(f"❌ Enhanced services import failed: {e}")
        
        # Test fallback services
        print("🔄 Testing fallback services...")
        try:
            from database.analysis_storage import analysis_storage
            print("✅ Fallback analysis storage available")
            return False
        except ImportError as e2:
            print(f"❌ Fallback services also failed: {e2}")
            return False

def test_analysis_storage_functionality():
    """Test analysis storage functionality"""
    print("\n🔍 TESTING ANALYSIS STORAGE FUNCTIONALITY")
    print("=" * 45)
    
    try:
        # Import the same way the app does
        try:
            from database.enhanced_analysis_storage import enhanced_analysis_storage
            storage = enhanced_analysis_storage
            print("✅ Using enhanced analysis storage")
        except ImportError:
            try:
                from database.analysis_storage import analysis_storage
                storage = analysis_storage
                print("✅ Using fallback analysis storage")
            except ImportError:
                print("❌ No analysis storage available")
                return False
        
        # Test saving an analysis
        print("🔄 Testing analysis save...")
        
        # Get a test user
        from auth.services import user_service
        test_user = user_service.get_user_by_email("streamlit_test@example.com")
        
        if not test_user:
            print("❌ No test user found")
            return False
        
        # Test analysis data
        test_analysis = {
            'score': 85,
            'match_category': 'good-match',
            'matching_skills': ['Python', 'JavaScript', 'SQL'],
            'skill_gaps': {'Critical': ['Machine Learning'], 'Important': ['Docker']},
            'suggestions': ['Add ML experience', 'Learn containerization'],
            'processing_time': 2.5
        }
        
        analysis_id = storage.save_analysis(
            user_id=test_user.id,
            resume_filename="test_analysis_storage.pdf",
            resume_content="Test resume content",
            job_description="Test job description",
            analysis_result=test_analysis,
            processing_time=2.5
        )
        
        if analysis_id:
            print(f"✅ Analysis saved successfully: {analysis_id}")
            
            # Test retrieval
            print("🔄 Testing analysis retrieval...")
            
            # Check if it's in the database
            from database.connection import get_db
            db = get_db()
            
            result = db.get_single_result(
                "SELECT * FROM analysis_sessions WHERE id = ?",
                (analysis_id,)
            )
            
            if result:
                print("✅ Analysis found in database")
                print(f"   Resume: {result['resume_filename']}")
                print(f"   Score: {result.get('score', 'N/A')}")
                print(f"   User: {test_user.email}")
                
                # Clean up test data
                db.execute_command("DELETE FROM analysis_sessions WHERE id = ?", (analysis_id,))
                print("✅ Test data cleaned up")
                
                return True
            else:
                print("❌ Analysis not found in database")
                return False
        else:
            print("❌ Analysis save failed")
            return False
            
    except Exception as e:
        print(f"❌ Analysis storage test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_analysis_flow():
    """Test the complete analysis flow as used in the app"""
    print("\n🔍 TESTING COMPLETE APP ANALYSIS FLOW")
    print("=" * 40)
    
    try:
        # Import app modules
        import sys
        sys.path.append('.')
        
        # Test the save_analysis_with_history function
        print("🔄 Testing save_analysis_with_history function...")
        
        # Get test user
        from auth.services import user_service
        test_user = user_service.get_user_by_email("streamlit_test@example.com")
        
        if not test_user:
            print("❌ No test user found")
            return False
        
        # Mock analysis result
        test_result = {
            'score': 92,
            'match_category': 'excellent-match',
            'matching_skills': ['Python', 'React', 'AWS'],
            'skill_gaps': {'Critical': [], 'Important': ['Kubernetes']},
            'suggestions': ['Consider adding Kubernetes experience'],
            'processing_time': 3.2
        }
        
        # Test without Streamlit context (will fail but we can see the logic)
        print("🔄 Testing analysis save logic...")
        
        # Check ENHANCED_SERVICES_AVAILABLE
        try:
            from database.enhanced_analysis_storage import enhanced_analysis_storage
            from components.report_history_ui import report_history_ui
            enhanced_available = True
            print("✅ Enhanced services available")
        except ImportError:
            enhanced_available = False
            print("⚠️  Enhanced services not available")
        
        if enhanced_available:
            # Test enhanced storage directly
            analysis_id = enhanced_analysis_storage.save_analysis(
                user_id=test_user.id,
                resume_filename="app_flow_test.pdf",
                resume_content="Test resume content for app flow",
                job_description="Test job description for app flow",
                analysis_result=test_result,
                processing_time=3.2
            )
            
            if analysis_id:
                print(f"✅ Enhanced analysis storage working: {analysis_id}")
                
                # Clean up
                from database.connection import get_db
                db = get_db()
                db.execute_command("DELETE FROM analysis_sessions WHERE id = ?", (analysis_id,))
                print("✅ Test data cleaned up")
                
                return True
            else:
                print("❌ Enhanced analysis storage failed")
                return False
        else:
            print("⚠️  Would fall back to session state storage")
            return False
            
    except Exception as e:
        print(f"❌ App analysis flow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all analysis storage tests"""
    print("🚀 COMPREHENSIVE ANALYSIS STORAGE TEST")
    print("=" * 50)
    
    tests = [
        ("Enhanced Services Availability", test_enhanced_services),
        ("Analysis Storage Functionality", test_analysis_storage_functionality),
        ("App Analysis Flow", test_app_analysis_flow)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*15} {test_name} {'='*15}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Test failed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 ANALYSIS STORAGE TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:.<35} {status}")
        if success:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 ALL ANALYSIS STORAGE TESTS PASSED!")
        print("✅ Analysis storage should work correctly in the app")
    else:
        print(f"\n⚠️  {len(results) - passed} tests failed")
        print("💡 This explains why analysis reports aren't being saved!")
        
        if passed == 0:
            print("\n🔧 RECOMMENDED FIXES:")
            print("1. Check if enhanced_analysis_storage module exists")
            print("2. Verify database schema for analysis_sessions table")
            print("3. Test analysis storage functionality manually")
            print("4. Add fallback to direct database storage")

if __name__ == "__main__":
    main()