"""
Analysis Storage Service
Handles persistent storage of analysis results and reports
"""

import sqlite3
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from auth.models import User

class AnalysisStorage:
    """Service for storing and retrieving analysis results"""
    
    def __init__(self):
        self.db_path = 'data/app.db'
        self.ensure_database()
    
    def ensure_database(self):
        """Ensure database and tables exist"""
        Path('data').mkdir(exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create analysis sessions table if not exists
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                resume_filename TEXT,
                job_description TEXT,
                analysis_result TEXT,
                score INTEGER,
                match_category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            conn.commit()
    
    def save_analysis(self, user_id: str, resume_filename: str, 
                     job_description: str, analysis_result: Dict[str, Any]) -> str:
        """Save analysis result to database"""
        try:
            analysis_id = str(uuid.uuid4())
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                INSERT INTO analysis_sessions 
                (id, user_id, resume_filename, job_description, analysis_result, score, match_category)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    analysis_id,
                    user_id,
                    resume_filename,
                    job_description,
                    json.dumps(analysis_result),
                    analysis_result.get('score', 0),
                    analysis_result.get('match_category', 'Unknown')
                ))
                
                conn.commit()
                return analysis_id
                
        except Exception as e:
            print(f"Error saving analysis: {e}")
            return None
    
    def get_user_analyses(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all analyses for a user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                SELECT * FROM analysis_sessions 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
                """, (user_id, limit))
                
                rows = cursor.fetchall()
                
                analyses = []
                for row in rows:
                    analysis = dict(row)
                    # Parse JSON result
                    if analysis['analysis_result']:
                        analysis['analysis_result'] = json.loads(analysis['analysis_result'])
                    analyses.append(analysis)
                
                return analyses
                
        except Exception as e:
            print(f"Error getting user analyses: {e}")
            return []
    
    def get_analysis_by_id(self, analysis_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get specific analysis by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                SELECT * FROM analysis_sessions 
                WHERE id = ? AND user_id = ?
                """, (analysis_id, user_id))
                
                row = cursor.fetchone()
                
                if row:
                    analysis = dict(row)
                    if analysis['analysis_result']:
                        analysis['analysis_result'] = json.loads(analysis['analysis_result'])
                    return analysis
                
                return None
                
        except Exception as e:
            print(f"Error getting analysis by ID: {e}")
            return None
    
    def delete_analysis(self, analysis_id: str, user_id: str) -> bool:
        """Delete an analysis"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                DELETE FROM analysis_sessions 
                WHERE id = ? AND user_id = ?
                """, (analysis_id, user_id))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"Error deleting analysis: {e}")
            return False

# Global instance
analysis_storage = AnalysisStorage()