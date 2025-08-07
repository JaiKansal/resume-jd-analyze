"""
Resume Matcher AI Package
Core functionality for resume and job description matching
"""

__version__ = "1.0.0"

# Import core components to make them available at package level
try:
    from .utils import MatchResult, JobDescription, ResumeData, UsageRecord
    from .matcher import analyze_match
    from .protected_matcher import analyze_match_protected
    from .resume_parser import extract_text_from_pdf, clean_resume_text
    from .jd_parser import parse_jd_text
    
    __all__ = [
        'MatchResult',
        'JobDescription', 
        'ResumeData',
        'UsageRecord',
        'analyze_match',
        'analyze_match_protected',
        'extract_text_from_pdf',
        'clean_resume_text',
        'parse_jd_text'
    ]
    
except ImportError as e:
    # If imports fail, create minimal fallbacks
    print(f"Warning: Some resume_matcher_ai imports failed: {e}")
    
    class MatchResult:
        def __init__(self, score=0, match_category="Unknown", **kwargs):
            self.score = score
            self.match_category = match_category
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    def analyze_match(*args, **kwargs):
        return MatchResult(score=50, match_category="Moderate")
    
    def analyze_match_protected(*args, **kwargs):
        return analyze_match(*args, **kwargs)
