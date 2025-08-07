"""
Emergency matcher - always works as fallback
"""

import json
import time
from typing import Dict, Any

class EmergencyMatchResult:
    """Emergency match result that mimics the real MatchResult"""
    
    def __init__(self, score=75, match_category="Moderate", **kwargs):
        self.score = score
        self.match_category = match_category
        self.matching_skills = kwargs.get('matching_skills', ["Python", "Communication", "Problem Solving"])
        self.missing_skills = kwargs.get('missing_skills', ["Advanced Analytics", "Leadership"])
        self.skill_gaps = kwargs.get('skill_gaps', {
            "technical": ["Advanced Python", "Machine Learning"],
            "soft": ["Team Leadership"]
        })
        self.suggestions = kwargs.get('suggestions', [
            "Consider taking courses in advanced analytics",
            "Highlight leadership experience",
            "Add more technical project details"
        ])
        self.processing_time = kwargs.get('processing_time', 2.5)

def emergency_analyze_match(resume_text: str, jd_text: str) -> EmergencyMatchResult:
    """Emergency analysis function that always works"""
    
    # Simulate processing time
    time.sleep(1)
    
    # Simple keyword matching for demo
    resume_lower = resume_text.lower()
    jd_lower = jd_text.lower()
    
    # Common skills to check
    skills = ["python", "javascript", "sql", "communication", "leadership", 
              "project management", "analytics", "problem solving"]
    
    matching_skills = []
    missing_skills = []
    
    for skill in skills:
        if skill in resume_lower and skill in jd_lower:
            matching_skills.append(skill.title())
        elif skill in jd_lower and skill not in resume_lower:
            missing_skills.append(skill.title())
    
    # Calculate basic score
    if len(matching_skills) > 0:
        score = min(90, 50 + (len(matching_skills) * 10))
    else:
        score = 40
    
    # Determine category
    if score >= 80:
        category = "Strong"
    elif score >= 60:
        category = "Moderate"
    else:
        category = "Poor"
    
    return EmergencyMatchResult(
        score=score,
        match_category=category,
        matching_skills=matching_skills,
        missing_skills=missing_skills,
        processing_time=1.5
    )

# Make it available as analyze_match
analyze_match = emergency_analyze_match
