#!/usr/bin/env python3
"""
Enhanced Analysis Service
Comprehensive analysis storage and retrieval system
"""

import os
import json
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class AnalysisResult:
    """Complete analysis result structure"""
    id: str
    user_id: str
    resume_filename: str
    job_description: str
    resume_content: str
    analysis_type: str
    match_score: float
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    keywords_matched: List[str]
    keywords_missing: List[str]
    sections_analysis: Dict[str, Any]
    pdf_report_path: Optional[str] = None
    processing_time_seconds: Optional[float] = None
    api_cost_usd: Optional[float] = None
    tokens_used: Optional[int] = None
    status: str = "completed"
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class EnhancedAnalysisService:
    """Enhanced service for comprehensive analysis storage and retrieval"""
    
    def __init__(self):
        self.database_url = self._get_database_url()
    
    def _get_database_url(self):
        """Get DATABASE_URL from environment or Streamlit secrets"""
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            return database_url
        
        try:
            import streamlit as st
            database_url = st.secrets.get('DATABASE_URL')
            if database_url:
                os.environ['DATABASE_URL'] = database_url
                return database_url
        except:
            pass
        
        return None
    
    def _get_connection(self):
        """Get database connection"""
        import psycopg2
        from psycopg2.extras import RealDictCursor
        return psycopg2.connect(self.database_url, cursor_factory=RealDictCursor)
    
    def save_analysis(self, analysis_result: AnalysisResult) -> bool:
        """Save complete analysis result to database"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Prepare data for insertion
                current_time = datetime.now()
                analysis_result.created_at = analysis_result.created_at or current_time
                analysis_result.updated_at = current_time
                
                # Convert lists and dicts to JSON strings
                strengths_json = json.dumps(analysis_result.strengths)
                weaknesses_json = json.dumps(analysis_result.weaknesses)
                recommendations_json = json.dumps(analysis_result.recommendations)
                keywords_matched_json = json.dumps(analysis_result.keywords_matched)
                keywords_missing_json = json.dumps(analysis_result.keywords_missing)
                sections_analysis_json = json.dumps(analysis_result.sections_analysis)
                
                # Insert comprehensive analysis data
                insert_query = """
                    INSERT INTO analysis_sessions (
                        id, user_id, resume_filename, job_description, resume_content,
                        analysis_type, match_score, strengths, weaknesses, recommendations,
                        keywords_matched, keywords_missing, sections_analysis,
                        pdf_report_path, processing_time_seconds, api_cost_usd, tokens_used,
                        status, error_message, created_at, updated_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """
                
                cursor.execute(insert_query, (
                    analysis_result.id, analysis_result.user_id, analysis_result.resume_filename,
                    analysis_result.job_description, analysis_result.resume_content,
                    analysis_result.analysis_type, analysis_result.match_score,
                    strengths_json, weaknesses_json, recommendations_json,
                    keywords_matched_json, keywords_missing_json, sections_analysis_json,
                    analysis_result.pdf_report_path, analysis_result.processing_time_seconds,
                    analysis_result.api_cost_usd, analysis_result.tokens_used,
                    analysis_result.status, analysis_result.error_message,
                    analysis_result.created_at, analysis_result.updated_at
                ))
                
                conn.commit()
                logger.info(f"✅ Analysis saved successfully: {analysis_result.id}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to save analysis: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_user_analyses(self, user_id: str, limit: int = 50) -> List[AnalysisResult]:
        """Get all analyses for a user"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT * FROM analysis_sessions 
                    WHERE user_id = %s 
                    ORDER BY created_at DESC 
                    LIMIT %s
                """
                
                cursor.execute(query, (user_id, limit))
                rows = cursor.fetchall()
                
                analyses = []
                for row in rows:
                    analysis = self._row_to_analysis_result(row)
                    if analysis:
                        analyses.append(analysis)
                
                logger.info(f"✅ Retrieved {len(analyses)} analyses for user {user_id}")
                return analyses
                
        except Exception as e:
            logger.error(f"❌ Failed to get user analyses: {e}")
            return []
    
    def get_analysis_by_id(self, analysis_id: str) -> Optional[AnalysisResult]:
        """Get specific analysis by ID"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM analysis_sessions WHERE id = %s"
                cursor.execute(query, (analysis_id,))
                row = cursor.fetchone()
                
                if row:
                    analysis = self._row_to_analysis_result(row)
                    logger.info(f"✅ Retrieved analysis: {analysis_id}")
                    return analysis
                else:
                    logger.warning(f"⚠️ Analysis not found: {analysis_id}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Failed to get analysis by ID: {e}")
            return None
    
    def update_analysis(self, analysis_id: str, updates: Dict[str, Any]) -> bool:
        """Update specific fields of an analysis"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Build dynamic update query
                set_clauses = []
                values = []
                
                for field, value in updates.items():
                    if field in ['strengths', 'weaknesses', 'recommendations', 
                               'keywords_matched', 'keywords_missing', 'sections_analysis']:
                        # Convert lists/dicts to JSON
                        value = json.dumps(value)
                    
                    set_clauses.append(f"{field} = %s")
                    values.append(value)
                
                # Add updated_at
                set_clauses.append("updated_at = %s")
                values.append(datetime.now())
                values.append(analysis_id)
                
                query = f"""
                    UPDATE analysis_sessions 
                    SET {', '.join(set_clauses)}
                    WHERE id = %s
                """
                
                cursor.execute(query, values)
                conn.commit()
                
                logger.info(f"✅ Analysis updated: {analysis_id}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to update analysis: {e}")
            return False
    
    def delete_analysis(self, analysis_id: str, user_id: str) -> bool:
        """Delete an analysis (with user verification)"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                query = "DELETE FROM analysis_sessions WHERE id = %s AND user_id = %s"
                cursor.execute(query, (analysis_id, user_id))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    logger.info(f"✅ Analysis deleted: {analysis_id}")
                    return True
                else:
                    logger.warning(f"⚠️ Analysis not found or unauthorized: {analysis_id}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Failed to delete analysis: {e}")
            return False
    
    def get_user_analysis_stats(self, user_id: str) -> Dict[str, Any]:
        """Get analysis statistics for a user"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Get comprehensive stats
                stats_query = """
                    SELECT 
                        COUNT(*) as total_analyses,
                        AVG(match_score) as avg_match_score,
                        MAX(match_score) as best_match_score,
                        MIN(match_score) as lowest_match_score,
                        SUM(api_cost_usd) as total_api_cost,
                        SUM(tokens_used) as total_tokens_used,
                        COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_analyses,
                        COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_analyses
                    FROM analysis_sessions 
                    WHERE user_id = %s
                """
                
                cursor.execute(stats_query, (user_id,))
                stats = cursor.fetchone()
                
                # Get recent activity
                recent_query = """
                    SELECT created_at, match_score, status
                    FROM analysis_sessions 
                    WHERE user_id = %s 
                    ORDER BY created_at DESC 
                    LIMIT 10
                """
                
                cursor.execute(recent_query, (user_id,))
                recent_analyses = cursor.fetchall()
                
                return {
                    'total_analyses': stats['total_analyses'] or 0,
                    'avg_match_score': float(stats['avg_match_score'] or 0),
                    'best_match_score': float(stats['best_match_score'] or 0),
                    'lowest_match_score': float(stats['lowest_match_score'] or 0),
                    'total_api_cost': float(stats['total_api_cost'] or 0),
                    'total_tokens_used': stats['total_tokens_used'] or 0,
                    'completed_analyses': stats['completed_analyses'] or 0,
                    'failed_analyses': stats['failed_analyses'] or 0,
                    'recent_analyses': [dict(row) for row in recent_analyses]
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to get user stats: {e}")
            return {}
    
    def _row_to_analysis_result(self, row: Dict[str, Any]) -> Optional[AnalysisResult]:
        """Convert database row to AnalysisResult object"""
        try:
            # Parse JSON fields safely
            def safe_json_parse(json_str, default=None):
                if json_str:
                    try:
                        return json.loads(json_str)
                    except:
                        return default or []
                return default or []
            
            return AnalysisResult(
                id=row['id'],
                user_id=row['user_id'],
                resume_filename=row.get('resume_filename', ''),
                job_description=row.get('job_description', ''),
                resume_content=row.get('resume_content', ''),
                analysis_type=row.get('analysis_type', 'resume_jd_match'),
                match_score=float(row.get('match_score', 0)),
                strengths=safe_json_parse(row.get('strengths'), []),
                weaknesses=safe_json_parse(row.get('weaknesses'), []),
                recommendations=safe_json_parse(row.get('recommendations'), []),
                keywords_matched=safe_json_parse(row.get('keywords_matched'), []),
                keywords_missing=safe_json_parse(row.get('keywords_missing'), []),
                sections_analysis=safe_json_parse(row.get('sections_analysis'), {}),
                pdf_report_path=row.get('pdf_report_path'),
                processing_time_seconds=row.get('processing_time_seconds'),
                api_cost_usd=row.get('api_cost_usd'),
                tokens_used=row.get('tokens_used'),
                status=row.get('status', 'completed'),
                error_message=row.get('error_message'),
                created_at=row.get('created_at'),
                updated_at=row.get('updated_at')
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to convert row to AnalysisResult: {e}")
            return None

# Global service instance
enhanced_analysis_service = EnhancedAnalysisService()

def create_analysis_result(user_id: str, resume_filename: str, job_description: str, 
                         resume_content: str, analysis_data: Dict[str, Any]) -> AnalysisResult:
    """Helper function to create AnalysisResult from analysis data"""
    return AnalysisResult(
        id=str(uuid.uuid4()),
        user_id=user_id,
        resume_filename=resume_filename,
        job_description=job_description,
        resume_content=resume_content,
        analysis_type=analysis_data.get('analysis_type', 'resume_jd_match'),
        match_score=analysis_data.get('match_score', 0.0),
        strengths=analysis_data.get('strengths', []),
        weaknesses=analysis_data.get('weaknesses', []),
        recommendations=analysis_data.get('recommendations', []),
        keywords_matched=analysis_data.get('keywords_matched', []),
        keywords_missing=analysis_data.get('keywords_missing', []),
        sections_analysis=analysis_data.get('sections_analysis', {}),
        processing_time_seconds=analysis_data.get('processing_time_seconds'),
        api_cost_usd=analysis_data.get('api_cost_usd'),
        tokens_used=analysis_data.get('tokens_used')
    )