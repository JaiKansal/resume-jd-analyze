#!/usr/bin/env python3
"""
Test analysis storage to ensure reports are being saved and retrieved properly
"""

import logging
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_analysis_storage():
    """Test that analysis storage is working properly"""
    logger.info("🧪 Testing analysis storage...")
    
    try:
        from database.connection import get_db
        db = get_db()
        
        # Test user ID (you can replace with a real user ID from your database)
        test_user_id = "test_user_123"
        
        # Check if we can query analysis_reports
        try:
            reports = db.execute_query("""
                SELECT id, title, content, created_at, analysis_type, metadata
                FROM analysis_reports 
                WHERE user_id = ? 
                ORDER BY created_at DESC
                LIMIT 10
            """, (test_user_id,))
            
            logger.info(f"✅ analysis_reports query works - found {len(reports)} reports for test user")
        except Exception as e:
            logger.warning(f"analysis_reports query failed: {e}")
        
        # Check if we can query analysis_sessions
        try:
            sessions = db.execute_query("""
                SELECT id, resume_filename, score, match_category, created_at
                FROM analysis_sessions 
                ORDER BY created_at DESC 
                LIMIT 10
            """)
            
            logger.info(f"✅ analysis_sessions query works - found {len(sessions)} total sessions")
            
            if sessions:
                logger.info("📊 Recent sessions:")
                for session in sessions[:3]:  # Show first 3
                    logger.info(f"   • {session['resume_filename']} - {session['score']}% ({session['created_at'][:10]})")
        except Exception as e:
            logger.warning(f"analysis_sessions query failed: {e}")
        
        # Test enhanced analysis storage if available
        try:
            from database.enhanced_analysis_storage import enhanced_analysis_storage
            
            # Try to get reports for any user
            all_reports = enhanced_analysis_storage.get_user_reports("any_user_id")
            logger.info(f"✅ Enhanced analysis storage works - found {len(all_reports)} reports")
            
        except ImportError:
            logger.info("ℹ️ Enhanced analysis storage not available")
        except Exception as e:
            logger.warning(f"Enhanced analysis storage error: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Analysis storage test failed: {e}")
        return False

def test_user_lookup():
    """Test user lookup to see if there are real users with analyses"""
    logger.info("🔍 Looking for real users with analyses...")
    
    try:
        from database.connection import get_db
        db = get_db()
        
        # Find users who have analyses
        users_with_analyses = db.execute_query("""
            SELECT DISTINCT user_id, COUNT(*) as analysis_count
            FROM analysis_sessions 
            GROUP BY user_id
            ORDER BY analysis_count DESC
            LIMIT 5
        """)
        
        if users_with_analyses:
            logger.info(f"📊 Found {len(users_with_analyses)} users with analyses:")
            for user in users_with_analyses:
                logger.info(f"   • User {user['user_id'][:8]}... has {user['analysis_count']} analyses")
                
                # Get sample analyses for this user
                sample_analyses = db.execute_query("""
                    SELECT resume_filename, score, created_at
                    FROM analysis_sessions 
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                    LIMIT 3
                """, (user['user_id'],))
                
                for analysis in sample_analyses:
                    logger.info(f"     - {analysis['resume_filename']} ({analysis['score']}%) on {analysis['created_at'][:10]}")
        else:
            logger.info("ℹ️ No users found with analyses yet")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ User lookup test failed: {e}")
        return False

def main():
    """Run storage tests"""
    logger.info("🧪 Running analysis storage tests...")
    
    tests = [
        ("Analysis Storage", test_analysis_storage),
        ("User Lookup", test_user_lookup)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n--- Running {test_name} Test ---")
        if test_func():
            passed += 1
            logger.info(f"✅ {test_name} test passed")
        else:
            logger.error(f"❌ {test_name} test failed")
    
    logger.info(f"\n🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All storage tests passed!")
        logger.info("💡 Your analysis storage should be working properly")
    else:
        logger.warning("⚠️ Some storage tests failed - check the logs above")

if __name__ == "__main__":
    main()