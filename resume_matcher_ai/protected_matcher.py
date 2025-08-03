"""
Protected Resume Matcher - IP Protection Layer
This module provides basic functionality for public repo while keeping advanced logic protected
"""

import os
import json
import requests
from typing import Dict, List, Any
from .utils import MatchResult

def get_analysis_mode() -> str:
    """Get analysis mode from environment"""
    return os.getenv('ANALYSIS_MODE', 'basic')

def get_advanced_config() -> Dict[str, Any]:
    """Load advanced configuration from environment variables"""
    config_str = os.getenv('ADVANCED_CONFIG')
    if config_str:
        try:
            return json.loads(config_str)
        except:
            pass
    return {}

def basic_keyword_analysis(resume_text: str, jd_data: Dict) -> MatchResult:
    """
    Basic keyword-based analysis for public viewing
    This is a simplified version - advanced logic is environment-protected
    """
    # Extract basic keywords from job description
    jd_text = jd_data.get('raw_text', '')
    
    # Simple keyword extraction
    common_skills = [
        'python', 'java', 'javascript', 'react', 'node.js', 'sql', 'aws',
        'machine learning', 'data analysis', 'project management', 'agile',
        'communication', 'leadership', 'teamwork', 'problem solving'
    ]
    
    # Find matches
    resume_lower = resume_text.lower()
    jd_lower = jd_text.lower()
    
    matching_skills = []
    for skill in common_skills:
        if skill in resume_lower and skill in jd_lower:
            matching_skills.append({
                'skill': skill,
                'resume': f"Found '{skill}' in resume",
                'job_description': f"Required '{skill}' in job"
            })
    
    # Calculate basic score
    score = min(len(matching_skills) * 15, 100)  # Simple scoring
    
    # Determine match category
    if score >= 70:
        match_category = "Strong Match"
    elif score >= 40:
        match_category = "Moderate Match"
    else:
        match_category = "Poor Match"
    
    # Generate basic suggestions
    suggestions = [
        "Add more relevant keywords from the job description",
        "Highlight your experience with mentioned technologies",
        "Include specific achievements and metrics"
    ]
    
    # Basic skill gaps
    missing_skills = []
    for skill in common_skills:
        if skill in jd_lower and skill not in resume_lower:
            missing_skills.append(skill)
    
    skill_gaps = {
        'Critical': missing_skills[:3],
        'Important': missing_skills[3:6],
        'Nice-to-have': missing_skills[6:9]
    }
    
    return MatchResult(
        score=score,
        match_category=match_category,
        matching_skills=matching_skills,
        skill_gaps=skill_gaps,
        suggestions=suggestions,
        processing_time=1.0  # Simulated processing time
    )

def advanced_ai_analysis(resume_text: str, jd_data: Dict) -> MatchResult:
    """
    Advanced AI-powered analysis - uses environment-protected logic
    """
    # Get advanced configuration
    config = get_advanced_config()
    api_endpoint = os.getenv('ADVANCED_API_ENDPOINT')
    api_key = os.getenv('ADVANCED_API_KEY')
    
    if api_endpoint and api_key:
        # Use private API for advanced analysis
        try:
            response = requests.post(
                f"{api_endpoint}/analyze",
                json={
                    'resume': resume_text,
                    'job_description': jd_data,
                    'config': config
                },
                headers={'Authorization': f'Bearer {api_key}'},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return MatchResult(
                    score=data['score'],
                    match_category=data['match_category'],
                    matching_skills=data['matching_skills'],
                    skill_gaps=data['skill_gaps'],
                    suggestions=data['suggestions'],
                    processing_time=data['processing_time']
                )
        except Exception as e:
            print(f"Advanced API failed: {e}")
    
    # Fallback to basic analysis
    return basic_keyword_analysis(resume_text, jd_data)

def analyze_match_protected(resume_text: str, jd_data: Dict) -> MatchResult:
    """
    Main analysis function with IP protection
    Uses advanced analysis if available, falls back to basic
    """
    analysis_mode = get_analysis_mode()
    
    if analysis_mode == 'advanced':
        return advanced_ai_analysis(resume_text, jd_data)
    else:
        return basic_keyword_analysis(resume_text, jd_data)

# Environment variable examples for advanced users:
"""
Set these environment variables for advanced functionality:

ANALYSIS_MODE=advanced
ADVANCED_CONFIG={"use_ai": true, "model": "gpt-4", "detailed_analysis": true}
ADVANCED_API_ENDPOINT=https://your-private-api.com
ADVANCED_API_KEY=your-secret-api-key

For Streamlit Cloud, add these to your secrets:
ANALYSIS_MODE = "advanced"
ADVANCED_CONFIG = '{"use_ai": true, "model": "gpt-4"}'
ADVANCED_API_ENDPOINT = "https://your-private-api.com"
ADVANCED_API_KEY = "your-secret-api-key"
"""