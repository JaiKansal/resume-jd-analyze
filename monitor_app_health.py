#!/usr/bin/env python3
"""
Monitor app health - users, analyses, and database status
"""

import sqlite3
import time
from datetime import datetime, timedelta

def show_app_health_dashboard():
    """Show comprehensive app health dashboard"""
    print("🏥 RESUME + JD ANALYZER - HEALTH DASHBOARD")
    print("=" * 60)
    
    db_path = 'data/app.db'
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Overall statistics
        print("📊 OVERALL STATISTICS")
        print("-" * 25)
        
        # Users
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE is_active = 1")
        active_users = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM users")
        total_users = cursor.fetchone()['count']
        
        print(f"👥 Users: {active_users} active / {total_users} total")
        
        # Analyses
        cursor.execute("SELECT COUNT(*) as count FROM analysis_sessions")
        total_analyses = cursor.fetchone()['count']
        
        cursor.execute("""
            SELECT COUNT(*) as count FROM analysis_sessions 
            WHERE created_at > datetime('now', '-24 hours')
        """)
        recent_analyses = cursor.fetchone()['count']
        
        print(f"📊 Analyses: {total_analyses} total, {recent_analyses} in last 24h")
        
        # Subscriptions
        cursor.execute("SELECT COUNT(*) as count FROM subscriptions WHERE status = 'active'")
        active_subscriptions = cursor.fetchone()['count']
        
        print(f"💳 Active Subscriptions: {active_subscriptions}")
        
        # Sessions
        cursor.execute("SELECT COUNT(*) as count FROM user_sessions WHERE is_active = 1")
        active_sessions = cursor.fetchone()['count']
        
        print(f"🔐 Active Sessions: {active_sessions}")
        
        # Recent activity
        print(f"\n🕒 RECENT ACTIVITY (Last 24 hours)")
        print("-" * 35)
        
        # New users
        cursor.execute("""
            SELECT COUNT(*) as count FROM users 
            WHERE created_at > datetime('now', '-24 hours')
        """)
        new_users = cursor.fetchone()['count']
        
        if new_users > 0:
            print(f"👤 New users: {new_users}")
            
            cursor.execute("""
                SELECT email, first_name, last_name, created_at 
                FROM users 
                WHERE created_at > datetime('now', '-24 hours')
                ORDER BY created_at DESC
                LIMIT 5
            """)
            
            recent_users = cursor.fetchall()
            for user in recent_users:
                print(f"   - {user['email']} ({user['first_name']} {user['last_name']}) at {user['created_at']}")
        else:
            print("👤 New users: 0")
        
        # Recent analyses
        if recent_analyses > 0:
            print(f"\n📄 Recent analyses: {recent_analyses}")
            
            cursor.execute("""
                SELECT a.resume_filename, a.score, a.match_category, a.created_at, u.email
                FROM analysis_sessions a
                LEFT JOIN users u ON a.user_id = u.id
                WHERE a.created_at > datetime('now', '-24 hours')
                ORDER BY a.created_at DESC
                LIMIT 5
            """)
            
            recent_analysis_list = cursor.fetchall()
            for analysis in recent_analysis_list:
                score = analysis['score'] or 'N/A'
                category = analysis['match_category'] or 'N/A'
                print(f"   - {analysis['resume_filename']} by {analysis['email']}: {score}% ({category})")
        else:
            print(f"\n📄 Recent analyses: 0")
        
        # User engagement
        print(f"\n📈 USER ENGAGEMENT")
        print("-" * 20)
        
        # Users with analyses
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) as count 
            FROM analysis_sessions
        """)
        users_with_analyses = cursor.fetchone()['count']
        
        engagement_rate = (users_with_analyses / total_users * 100) if total_users > 0 else 0
        print(f"🎯 Users with analyses: {users_with_analyses}/{total_users} ({engagement_rate:.1f}%)")
        
        # Average analyses per user
        if users_with_analyses > 0:
            avg_analyses = total_analyses / users_with_analyses
            print(f"📊 Average analyses per active user: {avg_analyses:.1f}")
        
        # Top users by analysis count
        cursor.execute("""
            SELECT u.email, u.first_name, u.last_name, COUNT(a.id) as analysis_count
            FROM users u
            LEFT JOIN analysis_sessions a ON u.id = a.user_id
            GROUP BY u.id
            HAVING analysis_count > 0
            ORDER BY analysis_count DESC
            LIMIT 5
        """)
        
        top_users = cursor.fetchall()
        if top_users:
            print(f"\n🏆 TOP USERS BY ANALYSES:")
            for user in top_users:
                print(f"   - {user['email']}: {user['analysis_count']} analyses")
        
        # System health
        print(f"\n🔧 SYSTEM HEALTH")
        print("-" * 18)
        
        # Database size
        import os
        db_size = os.path.getsize(db_path) / (1024 * 1024)  # MB
        print(f"💾 Database size: {db_size:.2f} MB")
        
        # Table health
        tables = ['users', 'subscriptions', 'analysis_sessions', 'user_sessions']
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
            count = cursor.fetchone()['count']
            print(f"📋 {table}: {count} records")
        
        # Performance indicators
        print(f"\n⚡ PERFORMANCE INDICATORS")
        print("-" * 28)
        
        # Average analysis score
        cursor.execute("SELECT AVG(score) as avg_score FROM analysis_sessions WHERE score IS NOT NULL")
        avg_score_result = cursor.fetchone()
        avg_score = avg_score_result['avg_score'] if avg_score_result['avg_score'] else 0
        print(f"📊 Average analysis score: {avg_score:.1f}%")
        
        # Score distribution
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN score >= 90 THEN 1 END) as excellent,
                COUNT(CASE WHEN score >= 70 AND score < 90 THEN 1 END) as good,
                COUNT(CASE WHEN score >= 50 AND score < 70 THEN 1 END) as fair,
                COUNT(CASE WHEN score < 50 THEN 1 END) as poor
            FROM analysis_sessions 
            WHERE score IS NOT NULL
        """)
        
        distribution = cursor.fetchone()
        if distribution:
            print(f"🎯 Score distribution:")
            print(f"   - Excellent (90%+): {distribution['excellent']}")
            print(f"   - Good (70-89%): {distribution['good']}")
            print(f"   - Fair (50-69%): {distribution['fair']}")
            print(f"   - Poor (<50%): {distribution['poor']}")
        
        conn.close()
        
        # Status summary
        print(f"\n🚦 OVERALL STATUS")
        print("-" * 18)
        
        status_indicators = []
        
        if active_users > 0:
            status_indicators.append("✅ Users active")
        else:
            status_indicators.append("⚠️  No active users")
        
        if total_analyses > 0:
            status_indicators.append("✅ Analyses being performed")
        else:
            status_indicators.append("⚠️  No analyses yet")
        
        if active_subscriptions > 0:
            status_indicators.append("✅ Subscriptions active")
        else:
            status_indicators.append("⚠️  No active subscriptions")
        
        if engagement_rate > 50:
            status_indicators.append("✅ Good user engagement")
        elif engagement_rate > 20:
            status_indicators.append("⚠️  Moderate user engagement")
        else:
            status_indicators.append("❌ Low user engagement")
        
        for indicator in status_indicators:
            print(f"   {indicator}")
        
        # Overall health score
        health_score = 0
        if active_users > 0:
            health_score += 25
        if total_analyses > 0:
            health_score += 25
        if engagement_rate > 20:
            health_score += 25
        if recent_analyses > 0:
            health_score += 25
        
        print(f"\n🏥 HEALTH SCORE: {health_score}/100")
        
        if health_score >= 75:
            print("🎉 App is healthy and functioning well!")
        elif health_score >= 50:
            print("⚠️  App is functioning but could use improvement")
        else:
            print("❌ App needs attention - low activity detected")
        
    except Exception as e:
        print(f"❌ Error generating health dashboard: {e}")

def monitor_real_time():
    """Monitor app in real-time"""
    print("🔄 REAL-TIME APP MONITORING")
    print("=" * 35)
    print("Monitoring for changes... Press Ctrl+C to stop")
    print("-" * 35)
    
    last_stats = {}
    
    try:
        while True:
            conn = sqlite3.connect('data/app.db')
            cursor = conn.cursor()
            
            # Get current stats
            cursor.execute("SELECT COUNT(*) as count FROM users")
            user_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) as count FROM analysis_sessions")
            analysis_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) as count FROM user_sessions WHERE is_active = 1")
            session_count = cursor.fetchone()[0]
            
            current_stats = {
                'users': user_count,
                'analyses': analysis_count,
                'sessions': session_count
            }
            
            # Check for changes
            if last_stats:
                changes = []
                for key, value in current_stats.items():
                    if key in last_stats and last_stats[key] != value:
                        changes.append(f"{key}: {last_stats[key]} → {value}")
                
                if changes:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"[{timestamp}] CHANGES: {', '.join(changes)}")
                    
                    # Show details for new analyses
                    if current_stats['analyses'] > last_stats.get('analyses', 0):
                        cursor.execute("""
                            SELECT a.resume_filename, u.email, a.score, a.created_at
                            FROM analysis_sessions a
                            LEFT JOIN users u ON a.user_id = u.id
                            ORDER BY a.created_at DESC
                            LIMIT 1
                        """)
                        
                        latest = cursor.fetchone()
                        if latest:
                            print(f"    📄 New analysis: {latest[0]} by {latest[1]} ({latest[2]}%)")
            
            last_stats = current_stats
            conn.close()
            
            # Show current status
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] Status: {user_count} users, {analysis_count} analyses, {session_count} sessions", end='\r')
            
            time.sleep(5)  # Check every 5 seconds
            
    except KeyboardInterrupt:
        print(f"\n\n✅ Monitoring stopped")

def main():
    """Main function"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'monitor':
        monitor_real_time()
    else:
        show_app_health_dashboard()
        print(f"\n💡 For real-time monitoring, run:")
        print(f"   python3 monitor_app_health.py monitor")

if __name__ == "__main__":
    main()