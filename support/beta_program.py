"""
Beta User Program Management
Handles beta user recruitment, tracking, and validation
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
from database.connection import get_db

class BetaProgramManager:
    """Service for managing beta user program"""
    
    def __init__(self):
        self.db = get_db()
        self._ensure_beta_tables()
    
    def _ensure_beta_tables(self):
        """Ensure beta program tables exist"""
        try:
            # Beta users table
            self.db.execute_command("""
                CREATE TABLE IF NOT EXISTS beta_users (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    invitation_code TEXT UNIQUE,
                    invited_by TEXT,
                    invitation_source TEXT, -- personal_network, community, referral, etc.
                    joined_at TEXT DEFAULT (datetime('now')),
                    status TEXT CHECK (status IN ('invited', 'active', 'churned', 'graduated')) DEFAULT 'invited',
                    feedback_score REAL,
                    usage_score REAL,
                    engagement_level TEXT CHECK (engagement_level IN ('low', 'medium', 'high')) DEFAULT 'medium',
                    graduation_date TEXT,
                    notes TEXT,
                    metadata TEXT, -- JSON
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (invited_by) REFERENCES users(id) ON DELETE SET NULL
                )
            """)
            
            # Beta feedback sessions table
            self.db.execute_command("""
                CREATE TABLE IF NOT EXISTS beta_feedback_sessions (
                    id TEXT PRIMARY KEY,
                    beta_user_id TEXT NOT NULL,
                    session_type TEXT CHECK (session_type IN ('interview', 'survey', 'usability_test', 'focus_group')) NOT NULL,
                    scheduled_at TEXT,
                    completed_at TEXT,
                    duration_minutes INTEGER,
                    interviewer TEXT,
                    questions TEXT, -- JSON
                    responses TEXT, -- JSON
                    insights TEXT, -- Key insights from the session
                    satisfaction_score REAL,
                    likelihood_to_recommend INTEGER CHECK (likelihood_to_recommend >= 0 AND likelihood_to_recommend <= 10),
                    pricing_feedback TEXT, -- JSON
                    feature_requests TEXT, -- JSON
                    status TEXT CHECK (status IN ('scheduled', 'completed', 'cancelled', 'no_show')) DEFAULT 'scheduled',
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (beta_user_id) REFERENCES beta_users(id) ON DELETE CASCADE
                )
            """)
            
            # Case studies table
            self.db.execute_command("""
                CREATE TABLE IF NOT EXISTS case_studies (
                    id TEXT PRIMARY KEY,
                    beta_user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    company_name TEXT,
                    industry TEXT,
                    use_case TEXT,
                    challenge TEXT,
                    solution TEXT,
                    results TEXT,
                    metrics TEXT, -- JSON - quantitative results
                    testimonial TEXT,
                    testimonial_author TEXT,
                    testimonial_title TEXT,
                    permission_to_publish BOOLEAN DEFAULT FALSE,
                    published BOOLEAN DEFAULT FALSE,
                    published_at TEXT,
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (beta_user_id) REFERENCES beta_users(id) ON DELETE CASCADE
                )
            """)
            
            # Beta program metrics table
            self.db.execute_command("""
                CREATE TABLE IF NOT EXISTS beta_program_metrics (
                    id TEXT PRIMARY KEY,
                    date TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    category TEXT,
                    metadata TEXT, -- JSON
                    created_at TEXT DEFAULT (datetime('now'))
                )
            """)
            
            # Create indexes
            self.db.execute_command("CREATE INDEX IF NOT EXISTS idx_beta_users_user_id ON beta_users(user_id)")
            self.db.execute_command("CREATE INDEX IF NOT EXISTS idx_beta_users_status ON beta_users(status)")
            self.db.execute_command("CREATE INDEX IF NOT EXISTS idx_beta_users_invitation_code ON beta_users(invitation_code)")
            
            self.db.execute_command("CREATE INDEX IF NOT EXISTS idx_beta_feedback_sessions_beta_user_id ON beta_feedback_sessions(beta_user_id)")
            self.db.execute_command("CREATE INDEX IF NOT EXISTS idx_beta_feedback_sessions_session_type ON beta_feedback_sessions(session_type)")
            
            self.db.execute_command("CREATE INDEX IF NOT EXISTS idx_case_studies_beta_user_id ON case_studies(beta_user_id)")
            self.db.execute_command("CREATE INDEX IF NOT EXISTS idx_case_studies_published ON case_studies(published)")
            
        except Exception as e:
            print(f"Error creating beta program tables: {e}")
    
    def invite_beta_user(self, user_id: str, invitation_source: str, 
                        invited_by: str = None, notes: str = None) -> Dict[str, Any]:
        """Invite a user to the beta program"""
        try:
            beta_id = str(uuid.uuid4())
            invitation_code = self._generate_invitation_code()
            
            self.db.execute_command("""
                INSERT INTO beta_users 
                (id, user_id, invitation_code, invited_by, invitation_source, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (beta_id, user_id, invitation_code, invited_by, invitation_source, notes))
            
            return {
                'success': True,
                'beta_id': beta_id,
                'invitation_code': invitation_code,
                'message': 'Beta invitation created successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def activate_beta_user(self, invitation_code: str, user_id: str) -> Dict[str, Any]:
        """Activate a beta user with invitation code"""
        try:
            # Find beta invitation
            beta_user = self.db.get_single_result("""
                SELECT id, user_id, status FROM beta_users 
                WHERE invitation_code = ?
            """, (invitation_code,))
            
            if not beta_user:
                return {'success': False, 'error': 'Invalid invitation code'}
            
            if beta_user['status'] != 'invited':
                return {'success': False, 'error': 'Invitation already used or expired'}
            
            # Activate beta user
            self.db.execute_command("""
                UPDATE beta_users 
                SET status = 'active', joined_at = ?
                WHERE invitation_code = ?
            """, (datetime.utcnow().isoformat(), invitation_code))
            
            return {
                'success': True,
                'beta_id': beta_user['id'],
                'message': 'Beta access activated successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_beta_users(self, status: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get beta users with optional status filter"""
        try:
            query = """
                SELECT bu.id, bu.user_id, bu.invitation_code, bu.invitation_source,
                       bu.joined_at, bu.status, bu.engagement_level, bu.feedback_score,
                       u.first_name, u.last_name, u.email, u.company_name
                FROM beta_users bu
                LEFT JOIN users u ON bu.user_id = u.id
            """
            params = []
            
            if status:
                query += " WHERE bu.status = ?"
                params.append(status)
            
            query += " ORDER BY bu.joined_at DESC LIMIT ?"
            params.append(limit)
            
            results = self.db.execute_query(query, tuple(params))
            
            beta_users = []
            for row in results:
                beta_users.append({
                    'id': row['id'],
                    'user_id': row['user_id'],
                    'invitation_code': row['invitation_code'],
                    'invitation_source': row['invitation_source'],
                    'joined_at': row['joined_at'],
                    'status': row['status'],
                    'engagement_level': row['engagement_level'],
                    'feedback_score': row['feedback_score'],
                    'user_name': f"{row['first_name']} {row['last_name']}" if row['first_name'] else 'Unknown',
                    'email': row['email'],
                    'company_name': row['company_name']
                })
            
            return beta_users
            
        except Exception as e:
            print(f"Error getting beta users: {e}")
            return []
    
    def schedule_feedback_session(self, beta_user_id: str, session_type: str,
                                 scheduled_at: str, interviewer: str = None,
                                 questions: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Schedule a feedback session with a beta user"""
        try:
            session_id = str(uuid.uuid4())
            
            self.db.execute_command("""
                INSERT INTO beta_feedback_sessions 
                (id, beta_user_id, session_type, scheduled_at, interviewer, questions)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                beta_user_id,
                session_type,
                scheduled_at,
                interviewer,
                json.dumps(questions or [])
            ))
            
            return {
                'success': True,
                'session_id': session_id,
                'message': 'Feedback session scheduled successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def complete_feedback_session(self, session_id: str, responses: Dict[str, Any],
                                 insights: str = None, satisfaction_score: float = None,
                                 likelihood_to_recommend: int = None) -> Dict[str, Any]:
        """Complete a feedback session with responses"""
        try:
            self.db.execute_command("""
                UPDATE beta_feedback_sessions 
                SET status = 'completed', completed_at = ?, responses = ?, 
                    insights = ?, satisfaction_score = ?, likelihood_to_recommend = ?
                WHERE id = ?
            """, (
                datetime.utcnow().isoformat(),
                json.dumps(responses),
                insights,
                satisfaction_score,
                likelihood_to_recommend,
                session_id
            ))
            
            return {
                'success': True,
                'message': 'Feedback session completed successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_case_study(self, beta_user_id: str, case_study_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a case study from a beta user"""
        try:
            case_study_id = str(uuid.uuid4())
            
            self.db.execute_command("""
                INSERT INTO case_studies 
                (id, beta_user_id, title, company_name, industry, use_case,
                 challenge, solution, results, metrics, testimonial, 
                 testimonial_author, testimonial_title, permission_to_publish)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                case_study_id,
                beta_user_id,
                case_study_data.get('title'),
                case_study_data.get('company_name'),
                case_study_data.get('industry'),
                case_study_data.get('use_case'),
                case_study_data.get('challenge'),
                case_study_data.get('solution'),
                case_study_data.get('results'),
                json.dumps(case_study_data.get('metrics', {})),
                case_study_data.get('testimonial'),
                case_study_data.get('testimonial_author'),
                case_study_data.get('testimonial_title'),
                case_study_data.get('permission_to_publish', False)
            ))
            
            return {
                'success': True,
                'case_study_id': case_study_id,
                'message': 'Case study created successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_published_case_studies(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get published case studies"""
        try:
            results = self.db.execute_query("""
                SELECT cs.id, cs.title, cs.company_name, cs.industry, cs.use_case,
                       cs.challenge, cs.solution, cs.results, cs.testimonial,
                       cs.testimonial_author, cs.testimonial_title, cs.published_at,
                       bu.user_id
                FROM case_studies cs
                LEFT JOIN beta_users bu ON cs.beta_user_id = bu.id
                WHERE cs.published = 1 AND cs.permission_to_publish = 1
                ORDER BY cs.published_at DESC
                LIMIT ?
            """, (limit,))
            
            case_studies = []
            for row in results:
                case_studies.append({
                    'id': row['id'],
                    'title': row['title'],
                    'company_name': row['company_name'],
                    'industry': row['industry'],
                    'use_case': row['use_case'],
                    'challenge': row['challenge'],
                    'solution': row['solution'],
                    'results': row['results'],
                    'testimonial': row['testimonial'],
                    'testimonial_author': row['testimonial_author'],
                    'testimonial_title': row['testimonial_title'],
                    'published_at': row['published_at']
                })
            
            return case_studies
            
        except Exception as e:
            print(f"Error getting published case studies: {e}")
            return []
    
    def get_beta_program_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get beta program metrics"""
        try:
            start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            # Total beta users
            total_result = self.db.get_single_result("""
                SELECT COUNT(*) as count FROM beta_users
            """)
            total_beta_users = total_result['count'] if total_result else 0
            
            # Active beta users
            active_result = self.db.get_single_result("""
                SELECT COUNT(*) as count FROM beta_users WHERE status = 'active'
            """)
            active_beta_users = active_result['count'] if active_result else 0
            
            # Beta users by source
            source_results = self.db.execute_query("""
                SELECT invitation_source, COUNT(*) as count
                FROM beta_users
                GROUP BY invitation_source
            """)
            users_by_source = {row['invitation_source']: row['count'] for row in source_results}
            
            # Feedback sessions completed
            sessions_result = self.db.get_single_result("""
                SELECT COUNT(*) as count FROM beta_feedback_sessions 
                WHERE status = 'completed' AND completed_at >= ?
            """, (start_date,))
            completed_sessions = sessions_result['count'] if sessions_result else 0
            
            # Average satisfaction score
            satisfaction_result = self.db.get_single_result("""
                SELECT AVG(satisfaction_score) as avg_score FROM beta_feedback_sessions 
                WHERE status = 'completed' AND satisfaction_score IS NOT NULL
            """)
            avg_satisfaction = satisfaction_result['avg_score'] if satisfaction_result and satisfaction_result['avg_score'] else 0
            
            # Case studies created
            case_studies_result = self.db.get_single_result("""
                SELECT COUNT(*) as count FROM case_studies
            """)
            total_case_studies = case_studies_result['count'] if case_studies_result else 0
            
            return {
                'total_beta_users': total_beta_users,
                'active_beta_users': active_beta_users,
                'users_by_source': users_by_source,
                'completed_feedback_sessions': completed_sessions,
                'average_satisfaction_score': float(avg_satisfaction) if avg_satisfaction else 0,
                'total_case_studies': total_case_studies,
                'period_days': days
            }
            
        except Exception as e:
            print(f"Error getting beta program metrics: {e}")
            return {}
    
    def _generate_invitation_code(self) -> str:
        """Generate a unique invitation code"""
        import random
        import string
        
        # Generate a random 8-character code
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        # Check if code already exists
        existing = self.db.get_single_result("""
            SELECT id FROM beta_users WHERE invitation_code = ?
        """, (code,))
        
        if existing:
            return self._generate_invitation_code()  # Recursive call if code exists
        
        return code

# Global instance
beta_program = BetaProgramManager()