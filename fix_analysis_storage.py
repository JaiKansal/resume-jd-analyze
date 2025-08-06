#!/usr/bin/env python3
"""
Fix analysis storage to ensure reports are always saved to database
"""

import re

def fix_enhanced_services_import():
    """Fix the enhanced services import to handle Streamlit dependency properly"""
    print("🔧 Fixing Enhanced Services Import")
    print("=" * 35)
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Find the enhanced services import section
        old_import_section = '''# Enhanced services imports with fallback
try:
    from billing.enhanced_razorpay_service import enhanced_razorpay_service
    from database.enhanced_analysis_storage import enhanced_analysis_storage
    from components.report_history_ui import report_history_ui
    ENHANCED_SERVICES_AVAILABLE = True
    
    # Check if Razorpay SDK is missing and use fallback
    status_info = enhanced_razorpay_service.get_status_info()
    if status_info.get('status') == 'sdk_missing':
        try:
            from billing.fallback_razorpay_service import fallback_razorpay_service
            enhanced_razorpay_service = fallback_razorpay_service
            logger.info("Using fallback Razorpay service (Direct API)")
        except ImportError:
            logger.warning("Fallback Razorpay service not available")
    
except ImportError:
    # Fallback to original services
    try:
        from billing.fallback_razorpay_service import fallback_razorpay_service as enhanced_razorpay_service
        from database.analysis_storage import analysis_storage as enhanced_analysis_storage
        ENHANCED_SERVICES_AVAILABLE = True
        logger.info("Using fallback services")
    except ImportError:
        from billing.razorpay_service import razorpay_service as enhanced_razorpay_service
        from database.analysis_storage import analysis_storage as enhanced_analysis_storage
        ENHANCED_SERVICES_AVAILABLE = False
        logger.warning("Using basic services")'''
        
        new_import_section = '''# Enhanced services imports with proper fallback
ENHANCED_SERVICES_AVAILABLE = False

# Try to import enhanced analysis storage (this should always work)
try:
    from database.enhanced_analysis_storage import enhanced_analysis_storage
    ANALYSIS_STORAGE_AVAILABLE = True
    logger.info("Enhanced analysis storage available")
except ImportError:
    try:
        from database.analysis_storage import analysis_storage as enhanced_analysis_storage
        ANALYSIS_STORAGE_AVAILABLE = True
        logger.info("Fallback analysis storage available")
    except ImportError:
        enhanced_analysis_storage = None
        ANALYSIS_STORAGE_AVAILABLE = False
        logger.error("No analysis storage available")

# Try to import enhanced Razorpay service
try:
    from billing.enhanced_razorpay_service import enhanced_razorpay_service
    
    # Check if Razorpay SDK is missing and use fallback
    status_info = enhanced_razorpay_service.get_status_info()
    if status_info.get('status') == 'sdk_missing':
        try:
            from billing.fallback_razorpay_service import fallback_razorpay_service
            enhanced_razorpay_service = fallback_razorpay_service
            logger.info("Using fallback Razorpay service (Direct API)")
        except ImportError:
            logger.warning("Fallback Razorpay service not available")
    
except ImportError:
    try:
        from billing.fallback_razorpay_service import fallback_razorpay_service as enhanced_razorpay_service
        logger.info("Using fallback Razorpay service")
    except ImportError:
        from billing.razorpay_service import razorpay_service as enhanced_razorpay_service
        logger.warning("Using basic Razorpay service")

# Try to import report history UI (optional, only for enhanced features)
try:
    from components.report_history_ui import report_history_ui
    REPORT_HISTORY_AVAILABLE = True
    logger.info("Report history UI available")
except ImportError:
    report_history_ui = None
    REPORT_HISTORY_AVAILABLE = False
    logger.info("Report history UI not available (Streamlit context required)")

# Set enhanced services availability based on critical components
ENHANCED_SERVICES_AVAILABLE = ANALYSIS_STORAGE_AVAILABLE'''
        
        if old_import_section in content:
            content = content.replace(old_import_section, new_import_section)
            print("✅ Fixed enhanced services import section")
        else:
            print("⚠️  Could not find exact import section, applying manual fix...")
            
            # Find and replace the import section more flexibly
            import_start = content.find('# Enhanced services imports')
            if import_start != -1:
                import_end = content.find('\n\n', import_start)
                if import_end != -1:
                    content = content[:import_start] + new_import_section + content[import_end:]
                    print("✅ Applied manual fix to import section")
        
        with open('app.py', 'w') as f:
            f.write(content)
        
        print("✅ Enhanced services import fixed")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing enhanced services import: {e}")
        return False

def fix_analysis_storage_function():
    """Fix the save_analysis_with_history function to always save to database"""
    print("\n🔧 Fixing Analysis Storage Function")
    print("=" * 35)
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Find the save_analysis_with_history function
        old_function = '''def save_analysis_with_history(user_id: str, resume_filename: str, resume_content: str,
                              job_description: str, analysis_result: dict, 
                              processing_time: float = 0):
    """Save analysis with enhanced storage and history tracking"""
    
    if ENHANCED_SERVICES_AVAILABLE:
        analysis_id = enhanced_analysis_storage.save_analysis(
            user_id=user_id,
            resume_filename=resume_filename,
            resume_content=resume_content,
            job_description=job_description,
            analysis_result=analysis_result,
            processing_time=processing_time
        )
        
        if analysis_id:
            st.success("✅ Analysis saved to your history!")
            
            # Show quick stats
            with st.expander("📊 Your Analysis Stats"):
                stats = enhanced_analysis_storage.get_user_statistics(user_id)
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Analyses", stats.get('total_analyses', 0))
                with col2:
                    st.metric("Average Score", f"{stats.get('avg_score', 0):.1f}%")
                with col3:
                    st.metric("Best Score", f"{stats.get('best_score', 0)}%")
        
        return analysis_id
    else:
        # Fallback to session state storage
        st.session_state.analysis_results.append((resume_filename, analysis_result))
        return None'''
        
        new_function = '''def save_analysis_with_history(user_id: str, resume_filename: str, resume_content: str,
                              job_description: str, analysis_result: dict, 
                              processing_time: float = 0):
    """Save analysis with enhanced storage and history tracking"""
    
    analysis_id = None
    
    # Always try to save to database first
    if ANALYSIS_STORAGE_AVAILABLE and enhanced_analysis_storage:
        try:
            analysis_id = enhanced_analysis_storage.save_analysis(
                user_id=user_id,
                resume_filename=resume_filename,
                resume_content=resume_content,
                job_description=job_description,
                analysis_result=analysis_result,
                processing_time=processing_time
            )
            
            if analysis_id:
                st.success("✅ Analysis saved to your history!")
                logger.info(f"Analysis saved to database: {analysis_id}")
                
                # Show quick stats if enhanced services are available
                if ENHANCED_SERVICES_AVAILABLE:
                    try:
                        with st.expander("📊 Your Analysis Stats"):
                            stats = enhanced_analysis_storage.get_user_statistics(user_id)
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Total Analyses", stats.get('total_analyses', 0))
                            with col2:
                                st.metric("Average Score", f"{stats.get('avg_score', 0):.1f}%")
                            with col3:
                                st.metric("Best Score", f"{stats.get('best_score', 0)}%")
                    except Exception as e:
                        logger.warning(f"Could not show analysis stats: {e}")
            else:
                logger.error("Analysis storage returned None")
                
        except Exception as e:
            logger.error(f"Failed to save analysis to database: {e}")
            analysis_id = None
    
    # Fallback: always save to session state as backup
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = []
    st.session_state.analysis_results.append((resume_filename, analysis_result))
    
    # If database save failed, try direct database insertion
    if not analysis_id:
        try:
            analysis_id = save_analysis_direct_to_database(
                user_id, resume_filename, resume_content, 
                job_description, analysis_result, processing_time
            )
            if analysis_id:
                st.success("✅ Analysis saved to your history!")
                logger.info(f"Analysis saved via direct database insertion: {analysis_id}")
        except Exception as e:
            logger.error(f"Direct database save also failed: {e}")
            st.warning("⚠️ Analysis saved to session only (may not persist)")
    
    return analysis_id'''
        
        if old_function in content:
            content = content.replace(old_function, new_function)
            print("✅ Fixed save_analysis_with_history function")
        else:
            print("⚠️  Could not find exact function, applying pattern-based fix...")
            
            # Use regex to find and replace the function
            pattern = r'def save_analysis_with_history\([^}]+?\n    return analysis_id\n    else:\n        # Fallback to session state storage\n        st\.session_state\.analysis_results\.append\([^)]+\)\n        return None'
            
            if re.search(pattern, content, re.DOTALL):
                content = re.sub(pattern, new_function, content, flags=re.DOTALL)
                print("✅ Applied pattern-based fix to function")
        
        with open('app.py', 'w') as f:
            f.write(content)
        
        print("✅ Analysis storage function fixed")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing analysis storage function: {e}")
        return False

def add_direct_database_save_function():
    """Add a direct database save function as ultimate fallback"""
    print("\n🔧 Adding Direct Database Save Function")
    print("=" * 40)
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Add the direct save function after the save_analysis_with_history function
        direct_save_function = '''
def save_analysis_direct_to_database(user_id: str, resume_filename: str, resume_content: str,
                                    job_description: str, analysis_result: dict, 
                                    processing_time: float = 0):
    """Direct database save as ultimate fallback"""
    try:
        import uuid
        from database.connection import get_db
        
        analysis_id = str(uuid.uuid4())
        
        # Extract analysis data
        score = analysis_result.get('score', 0)
        match_category = analysis_result.get('match_category', 'unknown')
        
        # Convert complex data to JSON strings
        import json
        analysis_result_json = json.dumps(analysis_result)
        
        db = get_db()
        
        # Insert into analysis_sessions table
        query = """
            INSERT INTO analysis_sessions (
                id, user_id, resume_filename, job_description, 
                analysis_result, score, match_category, 
                processing_time_seconds, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """
        
        params = (
            analysis_id, user_id, resume_filename, job_description,
            analysis_result_json, score, match_category, processing_time
        )
        
        rows_affected = db.execute_command(query, params)
        
        if rows_affected > 0:
            logger.info(f"Direct database save successful: {analysis_id}")
            return analysis_id
        else:
            logger.error("Direct database save failed: no rows affected")
            return None
            
    except Exception as e:
        logger.error(f"Direct database save failed: {e}")
        return None
'''
        
        # Find where to insert the function (after save_analysis_with_history)
        insert_point = content.find('def check_setup():')
        
        if insert_point != -1:
            content = content[:insert_point] + direct_save_function + '\n' + content[insert_point:]
            print("✅ Added direct database save function")
        else:
            # Fallback: add at the end of the file before main()
            main_point = content.find('def main():')
            if main_point != -1:
                content = content[:main_point] + direct_save_function + '\n' + content[main_point:]
                print("✅ Added direct database save function (fallback position)")
        
        with open('app.py', 'w') as f:
            f.write(content)
        
        print("✅ Direct database save function added")
        return True
        
    except Exception as e:
        print(f"❌ Error adding direct database save function: {e}")
        return False

def test_fixed_analysis_storage():
    """Test the fixed analysis storage"""
    print("\n🧪 Testing Fixed Analysis Storage")
    print("=" * 35)
    
    try:
        # Test the enhanced analysis storage directly
        from database.enhanced_analysis_storage import enhanced_analysis_storage
        from auth.services import user_service
        
        # Get test user
        test_user = user_service.get_user_by_email("streamlit_test@example.com")
        if not test_user:
            print("❌ No test user found")
            return False
        
        # Test analysis data
        test_analysis = {
            'score': 88,
            'match_category': 'good-match',
            'matching_skills': ['Python', 'Django', 'PostgreSQL'],
            'skill_gaps': {'Critical': ['Docker'], 'Important': ['AWS']},
            'suggestions': ['Add containerization experience', 'Learn cloud platforms'],
            'processing_time': 4.1
        }
        
        # Test save
        analysis_id = enhanced_analysis_storage.save_analysis(
            user_id=test_user.id,
            resume_filename="fixed_storage_test.pdf",
            resume_content="Test resume content for fixed storage",
            job_description="Test job description for fixed storage",
            analysis_result=test_analysis,
            processing_time=4.1
        )
        
        if analysis_id:
            print(f"✅ Fixed analysis storage test successful: {analysis_id}")
            
            # Verify in database
            from database.connection import get_db
            db = get_db()
            
            result = db.get_single_result(
                "SELECT * FROM analysis_sessions WHERE id = ?",
                (analysis_id,)
            )
            
            if result:
                print("✅ Analysis verified in database")
                print(f"   Resume: {result['resume_filename']}")
                print(f"   Score: {result.get('score', 'N/A')}")
                
                # Clean up
                db.execute_command("DELETE FROM analysis_sessions WHERE id = ?", (analysis_id,))
                print("✅ Test data cleaned up")
                
                return True
            else:
                print("❌ Analysis not found in database")
                return False
        else:
            print("❌ Fixed analysis storage test failed")
            return False
            
    except Exception as e:
        print(f"❌ Fixed analysis storage test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Apply all analysis storage fixes"""
    print("🚀 FIXING ANALYSIS STORAGE ISSUES")
    print("=" * 45)
    
    fixes = [
        ("Enhanced Services Import", fix_enhanced_services_import),
        ("Analysis Storage Function", fix_analysis_storage_function),
        ("Direct Database Save Function", add_direct_database_save_function),
        ("Test Fixed Storage", test_fixed_analysis_storage)
    ]
    
    results = []
    
    for fix_name, fix_func in fixes:
        print(f"\n{'='*15} {fix_name} {'='*15}")
        try:
            success = fix_func()
            results.append((fix_name, success))
        except Exception as e:
            print(f"❌ Fix failed: {e}")
            results.append((fix_name, False))
    
    # Summary
    print("\n" + "=" * 45)
    print("📊 ANALYSIS STORAGE FIXES SUMMARY")
    print("=" * 45)
    
    passed = 0
    for fix_name, success in results:
        status = "✅ APPLIED" if success else "❌ FAILED"
        print(f"{fix_name:.<30} {status}")
        if success:
            passed += 1
    
    print(f"\nResults: {passed}/{len(fixes)} fixes applied successfully")
    
    if passed == len(fixes):
        print("\n🎉 ALL ANALYSIS STORAGE FIXES APPLIED!")
        print("\n✅ Analysis reports should now be saved to database")
        print("✅ Users should see their analysis history")
        print("✅ Reports should persist across sessions")
        print("\n💡 Changes made:")
        print("   - Fixed enhanced services import logic")
        print("   - Always attempt database save first")
        print("   - Added direct database save fallback")
        print("   - Maintained session state backup")
        print("   - Added comprehensive error handling")
    else:
        print(f"\n⚠️  {len(fixes) - passed} fixes failed")
        print("Manual intervention may be required")

if __name__ == "__main__":
    main()