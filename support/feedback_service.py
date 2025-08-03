"""
Feedback Collection Service
Handles in-app feedback, surveys, and user feedback management
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
from database.connection import get_db

class FeedbackService:
    """Service for managing user feedback and surveys"""
    
    def submit_feedback(self, user_id: str, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit user feedback"""
        try:
            db = get_db()
            feedback_id = str(uuid.uuid4())
            
            db.execute_command("""
                INSERT INTO feedback_submissions 
                (id, user_id, feedback_type, category, title, description, rating, 
                 page_url, user_agent, browser_info, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                feedback_id,
                user_id,
                feedback_data.get('feedback_type', 'general_feedback'),
                feedback_data.get('category'),
                feedback_data.get('title'),
                feedback_data.get('description'),
                feedback_data.get('rating'),
                feedback_data.get('page_url'),
                feedback_data.get('user_agent'),
                json.dumps(feedback_data.get('browser_info', {})),
                json.dumps(feedback_data.get('metadata', {}))
            ))
            
            return {
                'success': True,
                'feedback_id': feedback_id,
                'message': 'Feedback submitted successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_user_feedback(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get feedback submitted by a user"""
        try:
            db = get_db()
            
            results = db.execute_query("""
                SELECT id, feedback_type, category, title, description, rating,
                       status, created_at
                FROM feedback_submissions
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, limit))
            
            feedback_list = []
            for row in results:
                feedback_list.append({
                    'id': str(row['id']),
                    'feedback_type': row['feedback_type'],
                    'category': row['category'],
                    'title': row['title'],
                    'description': row['description'],
                    'rating': row['rating'],
                    'status': row['status'],
                    'created_at': row['created_at']
                })
            
            return feedback_list
            
        except Exception as e:
            print(f"Error getting user feedback: {e}")
            return []
    
    def create_survey(self, user_id: str, survey_type: str, trigger_event: str, 
                     questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a satisfaction survey for a user"""
        try:
            db = get_db()
            survey_id = str(uuid.uuid4())
            
            db.execute_command("""
                INSERT INTO satisfaction_surveys 
                (id, user_id, survey_type, trigger_event, questions)
                VALUES (?, ?, ?, ?, ?)
            """, (
                survey_id,
                user_id,
                survey_type,
                trigger_event,
                json.dumps(questions)
            ))
            
            return {
                'success': True,
                'survey_id': survey_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def submit_survey_response(self, survey_id: str, responses: Dict[str, Any]) -> Dict[str, Any]:
        """Submit survey responses"""
        try:
            db = get_db()
            
            # Calculate overall score based on responses
            overall_score = self._calculate_survey_score(responses)
            
            db.execute_command("""
                UPDATE satisfaction_surveys 
                SET responses = ?, overall_score = ?, completed_at = ?
                WHERE id = ?
            """, (
                json.dumps(responses),
                overall_score,
                datetime.utcnow().isoformat(),
                survey_id
            ))
            
            return {
                'success': True,
                'overall_score': overall_score
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_feedback_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get feedback analytics for the specified period"""
        try:
            db = get_db()
            start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            # Total feedback count
            total_result = db.get_single_result("""
                SELECT COUNT(*) as count FROM feedback_submissions 
                WHERE created_at >= ?
            """, (start_date,))
            total_feedback = total_result['count'] if total_result else 0
            
            # Feedback by type
            type_results = db.execute_query("""
                SELECT feedback_type, COUNT(*) as count
                FROM feedback_submissions 
                WHERE created_at >= ?
                GROUP BY feedback_type
            """, (start_date,))
            feedback_by_type = {row['feedback_type']: row['count'] for row in type_results}
            
            # Average rating
            rating_result = db.get_single_result("""
                SELECT AVG(rating) as avg_rating FROM feedback_submissions 
                WHERE created_at >= ? AND rating IS NOT NULL
            """, (start_date,))
            avg_rating = rating_result['avg_rating'] if rating_result and rating_result['avg_rating'] else 0
            
            # Feedback by status
            status_results = db.execute_query("""
                SELECT status, COUNT(*) as count
                FROM feedback_submissions 
                WHERE created_at >= ?
                GROUP BY status
            """, (start_date,))
            feedback_by_status = {row['status']: row['count'] for row in status_results}
            
            return {
                'total_feedback': total_feedback,
                'feedback_by_type': feedback_by_type,
                'average_rating': float(avg_rating) if avg_rating else 0,
                'feedback_by_status': feedback_by_status,
                'period_days': days
            }
            
        except Exception as e:
            print(f"Error getting feedback analytics: {e}")
            return {}
    
    def _calculate_survey_score(self, responses: Dict[str, Any]) -> float:
        """Calculate overall survey score from responses"""
        scores = []
        
        for question_id, response in responses.items():
            if isinstance(response, (int, float)) and 1 <= response <= 10:
                scores.append(response)
            elif isinstance(response, dict) and 'score' in response:
                scores.append(response['score'])
        
        return sum(scores) / len(scores) if scores else 0.0

# Global instance
feedback_service = FeedbackService()