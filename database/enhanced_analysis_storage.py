"""
Enhanced Analysis Storage with Report History and Persistence
"""

import sqlite3
import json
import uuid
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

try:
    from auth.models import User
except ImportError:
    # Fallback for testing
    User = None

class EnhancedAnalysisStorage:
    """Enhanced service for storing and retrieving analysis results with history"""
    
    def __init__(self):
        self.db_path = 'data/app.db'
        self.ensure_database()
    
    def ensure_database(self):
        """Ensure database and tables exist with enhanced schema"""
        Path('data').mkdir(exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Use existing analysis_sessions table structure
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                team_id TEXT,
                session_type VARCHAR(50) DEFAULT 'single',
                resume_count INTEGER DEFAULT 1,
                job_description_count INTEGER DEFAULT 1,
                processing_time_seconds REAL,
                api_cost_usd REAL,
                tokens_used INTEGER,
                status VARCHAR(20) DEFAULT 'completed',
                error_message TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Add additional columns for enhanced functionality if they don't exist
            try:
                cursor.execute("ALTER TABLE analysis_sessions ADD COLUMN resume_filename TEXT")
            except:
                pass
            
            try:
                cursor.execute("ALTER TABLE analysis_sessions ADD COLUMN resume_hash TEXT")
            except:
                pass
            
            try:
                cursor.execute("ALTER TABLE analysis_sessions ADD COLUMN job_description TEXT")
            except:
                pass
            
            try:
                cursor.execute("ALTER TABLE analysis_sessions ADD COLUMN job_description_hash TEXT")
            except:
                pass
            
            try:
                cursor.execute("ALTER TABLE analysis_sessions ADD COLUMN analysis_result TEXT")
            except:
                pass
            
            try:
                cursor.execute("ALTER TABLE analysis_sessions ADD COLUMN score INTEGER")
            except:
                pass
            
            try:
                cursor.execute("ALTER TABLE analysis_sessions ADD COLUMN match_category TEXT")
            except:
                pass
            
            try:
                cursor.execute("ALTER TABLE analysis_sessions ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            except:
                pass
            
            # Create report_downloads table to track downloads
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS report_downloads (
                id TEXT PRIMARY KEY,
                analysis_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                report_type TEXT NOT NULL,
                report_format TEXT NOT NULL,
                download_count INTEGER DEFAULT 1,
                first_downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (analysis_id) REFERENCES analysis_sessions(id)
            )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_analysis_user_id ON analysis_sessions(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_analysis_created_at ON analysis_sessions(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_analysis_score ON analysis_sessions(score)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_report_downloads_user_id ON report_downloads(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_report_downloads_analysis_id ON report_downloads(analysis_id)")
            
            conn.commit()
    
    def _generate_content_hash(self, content: str) -> str:
        """Generate hash for content to detect duplicates"""
        return hashlib.md5(content.encode()).hexdigest()
    
    def save_analysis(self, user_id: str, resume_filename: str, resume_content: str,
                     job_description: str, analysis_result: Dict[str, Any], 
                     processing_time: float = 0, api_cost: float = 0, tokens_used: int = 0) -> str:
        """Save analysis result to database with enhanced metadata"""
        try:
            analysis_id = str(uuid.uuid4())
            resume_hash = self._generate_content_hash(resume_content) if resume_content else None
            jd_hash = self._generate_content_hash(job_description)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                INSERT INTO analysis_sessions 
                (id, user_id, resume_filename, resume_hash, job_description, job_description_hash,
                 analysis_result, score, match_category, processing_time_seconds, api_cost_usd, 
                 tokens_used, status, session_type, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    analysis_id,
                    user_id,
                    resume_filename,
                    resume_hash,
                    job_description,
                    jd_hash,
                    json.dumps(analysis_result),
                    analysis_result.get('score', 0),
                    analysis_result.get('match_category', 'Unknown'),
                    processing_time,
                    api_cost,
                    tokens_used,
                    'completed',
                    'single',
                    json.dumps({
                        'resume_size': len(resume_content) if resume_content else 0,
                        'jd_size': len(job_description),
                        'timestamp': datetime.utcnow().isoformat()
                    })
                ))
                
                conn.commit()
                return analysis_id
                
        except Exception as e:
            print(f"Error saving analysis: {e}")
            return None
    
    def get_user_analyses(self, user_id: str, limit: int = 50, include_content: bool = False) -> List[Dict[str, Any]]:
        """Get all analyses for a user with optional content inclusion"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Select fields based on whether content is needed
                if include_content:
                    fields = "*"
                else:
                    fields = """id, user_id, resume_filename, score, match_category, 
                               processing_time_seconds, created_at, updated_at"""
                
                cursor.execute(f"""
                SELECT {fields} FROM analysis_sessions 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
                """, (user_id, limit))
                
                rows = cursor.fetchall()
                
                analyses = []
                for row in rows:
                    analysis = dict(row)
                    
                    # Parse JSON fields if present
                    if 'analysis_result' in analysis and analysis['analysis_result']:
                        analysis['analysis_result'] = json.loads(analysis['analysis_result'])
                    if 'metadata' in analysis and analysis['metadata']:
                        analysis['metadata'] = json.loads(analysis['metadata'])
                    
                    # Get download history for this analysis
                    analysis['download_history'] = self.get_download_history(analysis['id'])
                    
                    analyses.append(analysis)
                
                return analyses
                
        except Exception as e:
            print(f"Error getting user analyses: {e}")
            return []
    
    def get_analysis_by_id(self, analysis_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get specific analysis by ID with full content"""
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
                    
                    # Parse JSON fields
                    if analysis['analysis_result']:
                        analysis['analysis_result'] = json.loads(analysis['analysis_result'])
                    if analysis['metadata']:
                        analysis['metadata'] = json.loads(analysis['metadata'])
                    
                    # Get download history
                    analysis['download_history'] = self.get_download_history(analysis_id)
                    
                    return analysis
                
                return None
                
        except Exception as e:
            print(f"Error getting analysis by ID: {e}")
            return None
    
    def record_download(self, analysis_id: str, user_id: str, report_type: str, report_format: str):
        """Record a report download"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if download record exists
                cursor.execute("""
                SELECT id, download_count FROM report_downloads 
                WHERE analysis_id = ? AND user_id = ? AND report_type = ? AND report_format = ?
                """, (analysis_id, user_id, report_type, report_format))
                
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing record
                    cursor.execute("""
                    UPDATE report_downloads 
                    SET download_count = download_count + 1, last_downloaded_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """, (existing[0],))
                else:
                    # Create new record
                    cursor.execute("""
                    INSERT INTO report_downloads 
                    (id, analysis_id, user_id, report_type, report_format)
                    VALUES (?, ?, ?, ?, ?)
                    """, (str(uuid.uuid4()), analysis_id, user_id, report_type, report_format))
                
                conn.commit()
                
        except Exception as e:
            print(f"Error recording download: {e}")
    
    def get_download_history(self, analysis_id: str) -> List[Dict[str, Any]]:
        """Get download history for an analysis"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                SELECT report_type, report_format, download_count, 
                       first_downloaded_at, last_downloaded_at
                FROM report_downloads 
                WHERE analysis_id = ?
                ORDER BY last_downloaded_at DESC
                """, (analysis_id,))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            print(f"Error getting download history: {e}")
            return []
    
    def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get user analysis statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Basic stats
                cursor.execute("""
                SELECT 
                    COUNT(*) as total_analyses,
                    AVG(score) as avg_score,
                    MAX(score) as best_score,
                    MIN(score) as worst_score,
                    SUM(processing_time_seconds) as total_processing_time,
                    SUM(api_cost_usd) as total_api_cost
                FROM analysis_sessions 
                WHERE user_id = ?
                """, (user_id,))
                
                stats = dict(cursor.fetchone()) if cursor.fetchone() else {}
                
                # Download stats
                cursor.execute("""
                SELECT 
                    COUNT(DISTINCT analysis_id) as analyses_downloaded,
                    SUM(download_count) as total_downloads
                FROM report_downloads 
                WHERE user_id = ?
                """, (user_id,))
                
                download_stats = dict(cursor.fetchone()) if cursor.fetchone() else {}
                
                return {**stats, **download_stats}
                
        except Exception as e:
            print(f"Error getting user statistics: {e}")
            return {}
    
    def delete_analysis(self, analysis_id: str, user_id: str) -> bool:
        """Delete an analysis and its download history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete download history first
                cursor.execute("""
                DELETE FROM report_downloads 
                WHERE analysis_id = ? AND user_id = ?
                """, (analysis_id, user_id))
                
                # Delete analysis
                cursor.execute("""
                DELETE FROM analysis_sessions 
                WHERE id = ? AND user_id = ?
                """, (analysis_id, user_id))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"Error deleting analysis: {e}")
            return False
    
    def find_similar_analyses(self, user_id: str, resume_hash: str = None, 
                            jd_hash: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Find similar analyses based on content hashes"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                conditions = ["user_id = ?"]
                params = [user_id]
                
                if resume_hash:
                    conditions.append("resume_hash = ?")
                    params.append(resume_hash)
                
                if jd_hash:
                    conditions.append("job_description_hash = ?")
                    params.append(jd_hash)
                
                query = f"""
                SELECT id, resume_filename, score, match_category, created_at
                FROM analysis_sessions 
                WHERE {' AND '.join(conditions)}
                ORDER BY created_at DESC 
                LIMIT ?
                """
                params.append(limit)
                
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            print(f"Error finding similar analyses: {e}")
            return []

# Global instance
enhanced_analysis_storage = EnhancedAnalysisStorage()

# Backward compatibility
analysis_storage = enhanced_analysis_storage
