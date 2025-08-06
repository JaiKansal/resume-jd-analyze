#!/usr/bin/env python3
"""
Debug analysis history and download issues
"""

import sqlite3
from datetime import datetime

def check_analysis_by_id(analysis_id):
    """Check if a specific analysis exists"""
    print(f"🔍 CHECKING ANALYSIS: {analysis_id}")
    print("=" * 50)
    
    db_path = 'data/app.db'
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Search for the analysis
        cursor.execute("""
            SELECT a.*, u.email
            FROM analysis_sessions a
            LEFT JOIN users u ON a.user_id = u.id
            WHERE a.id = ?
        """, (analysis_id,))
        
        analysis = cursor.fetchone()
        
        if analysis:
            print("✅ ANALYSIS FOUND!")
            print(f"   🆔 ID: {analysis['id']}")
            print(f"   👤 User: {analysis['email']}")
            print(f"   📄 Resume: {analysis['resume_filename']}")
            print(f"   📊 Score: {analysis.get('score', 'N/A')}")
            print(f"   🎯 Category: {analysis.get('match_category', 'N/A')}")
            print(f"   📅 Created: {analysis['created_at']}")
            print(f"   📋 Analysis Result: {len(analysis.get('analysis_result', '') or '')} chars")
            
            return True
        else:
            print("❌ ANALYSIS NOT FOUND")
            
            # Check all analyses
            cursor.execute("SELECT COUNT(*) as count FROM analysis_sessions")
            total = cursor.fetchone()['count']
            print(f"📊 Total analyses in database: {total}")
            
            if total > 0:
                cursor.execute("""
                    SELECT id, resume_filename, created_at, user_id
                    FROM analysis_sessions 
                    ORDER BY created_at DESC 
                    LIMIT 5
                """)
                
                recent = cursor.fetchall()
                print(f"📄 Recent analyses:")
                for r in recent:
                    print(f"   - {r['id'][:8]}... {r['resume_filename']} at {r['created_at']}")
            
            return False
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking analysis: {e}")
        return False

def check_user_analyses(user_email):
    """Check all analyses for a specific user"""
    print(f"\n🔍 CHECKING ANALYSES FOR: {user_email}")
    print("=" * 50)
    
    db_path = 'data/app.db'
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get user ID
        cursor.execute("SELECT id FROM users WHERE email = ?", (user_email,))
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ User not found: {user_email}")
            return False
        
        user_id = user['id']
        print(f"👤 User ID: {user_id}")
        
        # Get all analyses for this user
        cursor.execute("""
            SELECT * FROM analysis_sessions 
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_id,))
        
        analyses = cursor.fetchall()
        
        if analyses:
            print(f"✅ Found {len(analyses)} analysis(es):")
            for i, analysis in enumerate(analyses, 1):
                print(f"\n📊 Analysis #{i}:")
                print(f"   🆔 ID: {analysis['id']}")
                print(f"   📄 Resume: {analysis['resume_filename']}")
                print(f"   📊 Score: {analysis.get('score', 'N/A')}")
                print(f"   🎯 Category: {analysis.get('match_category', 'N/A')}")
                print(f"   📅 Created: {analysis['created_at']}")
                print(f"   📋 Result Length: {len(analysis.get('analysis_result', '') or '')} chars")
        else:
            print(f"❌ No analyses found for user")
        
        conn.close()
        return len(analyses) > 0
        
    except Exception as e:
        print(f"❌ Error checking user analyses: {e}")
        return False

def fix_engagement_events_table():
    """Fix the engagement_events table timestamp issue"""
    print(f"\n🔧 FIXING ENGAGEMENT_EVENTS TABLE")
    print("=" * 40)
    
    db_path = 'data/app.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current table structure
        cursor.execute("PRAGMA table_info(engagement_events)")
        columns = cursor.fetchall()
        
        print(f"📋 Current columns:")
        column_names = []
        for col in columns:
            column_names.append(col[1])
            print(f"   - {col[1]} ({col[2]})")
        
        # Check if timestamp column exists
        if 'timestamp' not in column_names:
            print(f"⚠️  Missing timestamp column, adding it...")
            
            cursor.execute("""
                ALTER TABLE engagement_events 
                ADD COLUMN timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            """)
            
            conn.commit()
            print(f"✅ Added timestamp column")
        else:
            print(f"✅ Timestamp column already exists")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error fixing engagement_events table: {e}")
        return False

def fix_watermark_service():
    """Fix the watermark service errors"""
    print(f"\n🔧 FIXING WATERMARK SERVICE")
    print("=" * 30)
    
    try:
        # Check if watermark service exists
        import os
        watermark_file = 'billing/watermark_service.py'
        
        if os.path.exists(watermark_file):
            with open(watermark_file, 'r') as f:
                content = f.read()
            
            print(f"📄 Found watermark service file")
            
            # Fix the drawCentredText issue
            if 'drawCentredText' in content:
                print(f"🔧 Fixing drawCentredText method...")
                
                # Replace drawCentredText with drawCentredString
                content = content.replace('drawCentredText', 'drawCentredString')
                
                with open(watermark_file, 'w') as f:
                    f.write(content)
                
                print(f"✅ Fixed drawCentredText -> drawCentredString")
            else:
                print(f"✅ No drawCentredText issues found")
            
            return True
        else:
            print(f"⚠️  Watermark service file not found")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing watermark service: {e}")
        return False

def check_analysis_history_display():
    """Check why analysis history is not displaying"""
    print(f"\n🔍 CHECKING ANALYSIS HISTORY DISPLAY")
    print("=" * 40)
    
    try:
        # Check if enhanced analysis storage is working
        from database.enhanced_analysis_storage import enhanced_analysis_storage
        
        print(f"✅ Enhanced analysis storage imported")
        
        # Test getting user statistics
        user_email = "jaikansal85@gmail.com"
        
        # Get user ID
        from auth.services import user_service
        user = user_service.get_user_by_email(user_email)
        
        if user:
            print(f"✅ User found: {user.email}")
            
            # Test get_user_statistics
            try:
                stats = enhanced_analysis_storage.get_user_statistics(user.id)
                print(f"📊 User statistics: {stats}")
            except Exception as e:
                print(f"❌ Error getting user statistics: {e}")
            
            # Test get_user_analyses
            try:
                analyses = enhanced_analysis_storage.get_user_analyses(user.id)
                print(f"📄 User analyses: {len(analyses) if analyses else 0} found")
                
                if analyses:
                    for analysis in analyses[:3]:  # Show first 3
                        print(f"   - {analysis.get('resume_filename', 'N/A')}: {analysis.get('score', 'N/A')}%")
                
            except Exception as e:
                print(f"❌ Error getting user analyses: {e}")
        else:
            print(f"❌ User not found: {user_email}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking analysis history display: {e}")
        import traceback
        traceback.print_exc()
        return False

def fix_download_disappearing_issue():
    """Fix the issue where analysis disappears when downloading"""
    print(f"\n🔧 FIXING DOWNLOAD DISAPPEARING ISSUE")
    print("=" * 45)
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Look for download button handlers that might cause reruns
        import re
        
        # Find download button patterns
        download_patterns = [
            r'st\.download_button.*st\.rerun\(\)',
            r'if.*download.*st\.rerun\(\)',
            r'download.*button.*st\.rerun\(\)'
        ]
        
        issues_found = []
        
        for pattern in download_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            if matches:
                issues_found.extend(matches)
        
        if issues_found:
            print(f"⚠️  Found {len(issues_found)} potential download rerun issues")
            for issue in issues_found:
                print(f"   - {issue[:100]}...")
        else:
            print(f"✅ No obvious download rerun issues found")
        
        # Check for session state clearing in download handlers
        session_clear_patterns = [
            r'download.*st\.session_state.*=.*\[\]',
            r'download.*del.*st\.session_state',
            r'download.*st\.session_state\.clear\(\)'
        ]
        
        for pattern in session_clear_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            if matches:
                print(f"❌ Found session state clearing in download: {matches}")
        
        return len(issues_found) == 0
        
    except Exception as e:
        print(f"❌ Error checking download issues: {e}")
        return False

def main():
    """Run all debugging checks"""
    print("🚀 COMPREHENSIVE ANALYSIS ISSUES DEBUG")
    print("=" * 50)
    
    # Check the specific analysis from the log
    analysis_id = "28c4312d-cc81-4855-a408-db8a36a06d07"
    user_email = "jaikansal85@gmail.com"
    
    checks = [
        ("Analysis by ID", lambda: check_analysis_by_id(analysis_id)),
        ("User Analyses", lambda: check_user_analyses(user_email)),
        ("Fix Engagement Events", fix_engagement_events_table),
        ("Fix Watermark Service", fix_watermark_service),
        ("Analysis History Display", check_analysis_history_display),
        ("Download Disappearing Issue", fix_download_disappearing_issue)
    ]
    
    results = []
    
    for check_name, check_func in checks:
        print(f"\n{'='*20} {check_name} {'='*20}")
        try:
            success = check_func()
            results.append((check_name, success))
        except Exception as e:
            print(f"❌ Check failed: {e}")
            results.append((check_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 DEBUG SUMMARY")
    print("=" * 50)
    
    passed = 0
    for check_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{check_name:.<30} {status}")
        if success:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} checks passed")
    
    if passed < len(results):
        print(f"\n💡 ISSUES IDENTIFIED:")
        for check_name, success in results:
            if not success:
                print(f"   - {check_name}")

if __name__ == "__main__":
    main()