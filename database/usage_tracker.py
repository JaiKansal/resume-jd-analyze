"""
Usage Tracker Service
Handles persistent usage tracking that doesn't reset on login
"""

import sqlite3
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from pathlib import Path

class PersistentUsageTracker:
    """Persistent usage tracking that survives sessions"""
    
    def __init__(self):
        self.db_path = 'data/app.db'
        self.ensure_database()
    
    def ensure_database(self):
        """Ensure database and tables exist"""
        Path('data').mkdir(exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create usage tracking table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS usage_tracking (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                analysis_count INTEGER DEFAULT 0,
                period_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                period_end TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """)
            
            # Create index for better performance
            cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_usage_tracking_user_id 
            ON usage_tracking(user_id)
            """)
            
            conn.commit()
    
    def get_current_usage(self, user_id: str) -> Dict[str, Any]:
        """Get current usage for user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Get current month's usage
                current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                next_month_start = (current_month_start + timedelta(days=32)).replace(day=1)
                
                cursor.execute("""
                SELECT * FROM usage_tracking 
                WHERE user_id = ? 
                AND period_start >= ? 
                AND period_start < ?
                ORDER BY created_at DESC 
                LIMIT 1
                """, (user_id, current_month_start, next_month_start))
                
                row = cursor.fetchone()
                
                if row:
                    return {
                        'analysis_count': row['analysis_count'],
                        'period_start': row['period_start'],
                        'period_end': row['period_end'],
                        'remaining_days': self._get_remaining_days(row['period_end'])
                    }
                else:
                    # Create new usage record for this month
                    return self._create_monthly_usage_record(user_id)
                    
        except Exception as e:
            print(f"Error getting current usage: {e}")
            return {'analysis_count': 0, 'remaining_days': 30}
    
    def increment_usage(self, user_id: str) -> bool:
        """Increment usage count for user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get current month's usage record
                current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                next_month_start = (current_month_start + timedelta(days=32)).replace(day=1)
                
                cursor.execute("""
                SELECT id, analysis_count FROM usage_tracking 
                WHERE user_id = ? 
                AND period_start >= ? 
                AND period_start < ?
                ORDER BY created_at DESC 
                LIMIT 1
                """, (user_id, current_month_start, next_month_start))
                
                row = cursor.fetchone()
                
                if row:
                    # Update existing record
                    cursor.execute("""
                    UPDATE usage_tracking 
                    SET analysis_count = analysis_count + 1,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """, (row[0],))
                else:
                    # Create new record and increment
                    self._create_monthly_usage_record(user_id)
                    cursor.execute("""
                    UPDATE usage_tracking 
                    SET analysis_count = 1,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ? 
                    AND period_start >= ?
                    """, (user_id, current_month_start))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error incrementing usage: {e}")
            return False
    
    def _create_monthly_usage_record(self, user_id: str) -> Dict[str, Any]:
        """Create a new monthly usage record"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                record_id = str(uuid.uuid4())
                current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                next_month_start = (current_month_start + timedelta(days=32)).replace(day=1)
                
                cursor.execute("""
                INSERT INTO usage_tracking 
                (id, user_id, analysis_count, period_start, period_end)
                VALUES (?, ?, 0, ?, ?)
                """, (record_id, user_id, current_month_start, next_month_start))
                
                conn.commit()
                
                return {
                    'analysis_count': 0,
                    'period_start': current_month_start.isoformat(),
                    'period_end': next_month_start.isoformat(),
                    'remaining_days': self._get_remaining_days(next_month_start)
                }
                
        except Exception as e:
            print(f"Error creating monthly usage record: {e}")
            return {'analysis_count': 0, 'remaining_days': 30}
    
    def _get_remaining_days(self, period_end) -> int:
        """Get remaining days in current period"""
        try:
            if isinstance(period_end, str):
                period_end = datetime.fromisoformat(period_end.replace('Z', '+00:00'))
            
            remaining = period_end - datetime.now()
            return max(0, remaining.days)
        except:
            return 30
    
    def reset_usage_for_user(self, user_id: str) -> bool:
        """Reset usage for a specific user (admin function)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                next_month_start = (current_month_start + timedelta(days=32)).replace(day=1)
                
                cursor.execute("""
                UPDATE usage_tracking 
                SET analysis_count = 0,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ? 
                AND period_start >= ?
                """, (user_id, current_month_start))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error resetting usage: {e}")
            return False

# Global instance
persistent_usage_tracker = PersistentUsageTracker()