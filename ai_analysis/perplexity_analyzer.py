"""
Real AI-powered resume analysis using Perplexity API
"""

import requests
import json
import logging
from typing import Dict, Any, List, Optional
import re

logger = logging.getLogger(__name__)

class PerplexityAnalyzer:
    """Real AI analysis using Perplexity API"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def analyze_resume(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        """Perform real AI analysis of resume against job description"""
        
        if not self.api_key:
            return self._fallback_analysis(resume_text, job_description)
        
        try:
            # Create comprehensive analysis prompt
            prompt = self._create_analysis_prompt(resume_text, job_description)
            
            # Call Perplexity API
            response = self._call_perplexity_api(prompt)
            
            if response:
                # Parse AI response into structured data
                return self._parse_ai_response(response, resume_text, job_description)
            else:
                return self._fallback_analysis(resume_text, job_description)
                
        except Exception as e:
            logger.error(f"Perplexity API error: {e}")
            return self._fallback_analysis(resume_text, job_description)
    
    def _create_analysis_prompt(self, resume_text: str, job_description: str) -> str:
        """Create comprehensive analysis prompt for AI"""
        
        prompt = f"""
You are an expert HR analyst and resume reviewer. Analyze the following resume against the job description and provide a comprehensive evaluation.

JOB DESCRIPTION:
{job_description}

RESUME:
{resume_text}

Please provide a detailed analysis in the following JSON format:

{{
    "overall_match_score": <number 0-100>,
    "skills_match_score": <number 0-100>,
    "experience_match_score": <number 0-100>,
    "education_match_score": <number 0-100>,
    "keyword_match_score": <number 0-100>,
    "detailed_analysis": {{
        "strengths": ["list of key strengths"],
        "weaknesses": ["list of areas for improvement"],
        "missing_skills": ["skills mentioned in JD but not in resume"],
        "relevant_experience": ["relevant experience found"],
        "education_alignment": "how education aligns with requirements"
    }},
    "recommendations": [
        "specific actionable recommendations"
    ],
    "key_insights": [
        "important insights about the match"
    ],
    "ats_compatibility": {{
        "score": <number 0-100>,
        "issues": ["potential ATS issues"]
    }}
}}

Focus on:
1. Technical skills alignment
2. Experience relevance and level
3. Education requirements match
4. Industry-specific keywords
5. ATS compatibility
6. Cultural fit indicators
7. Career progression alignment

Provide specific, actionable feedback based on the actual content.
"""
        return prompt
    
    def _call_perplexity_api(self, prompt: str) -> Optional[str]:
        """Make API call to Perplexity"""
        
        payload = {
            "model": "llama-3.1-sonar-large-128k-online",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert HR analyst specializing in resume evaluation and job matching. Provide detailed, accurate analysis in the requested JSON format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.2,
            "top_p": 0.9,
            "return_citations": False,
            "search_domain_filter": ["perplexity.ai"],
            "return_images": False,
            "return_related_questions": False,
            "search_recency_filter": "month",
            "top_k": 0,
            "stream": False,
            "presence_penalty": 0,
            "frequency_penalty": 1
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                logger.error(f"Perplexity API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"API call failed: {e}")
            return None
    
    def _parse_ai_response(self, ai_response: str, resume_text: str, job_description: str) -> Dict[str, Any]:
        """Parse AI response into structured analysis"""
        
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                analysis = json.loads(json_str)
                
                # Validate and clean the analysis
                return self._validate_analysis(analysis, resume_text, job_description)
            else:
                # If no JSON found, parse text response
                return self._parse_text_response(ai_response, resume_text, job_description)
                
        except Exception as e:
            logger.error(f"Failed to parse AI response: {e}")
            return self._fallback_analysis(resume_text, job_description)
    
    def _validate_analysis(self, analysis: Dict[str, Any], resume_text: str, job_description: str) -> Dict[str, Any]:
        """Validate and ensure analysis has all required fields"""
        
        # Ensure all scores are present and valid
        required_scores = ['overall_match_score', 'skills_match_score', 'experience_match_score', 
                          'education_match_score', 'keyword_match_score']
        
        for score_key in required_scores:
            if score_key not in analysis or not isinstance(analysis[score_key], (int, float)):
                analysis[score_key] = 50  # Default score
            else:
                # Ensure score is within bounds
                analysis[score_key] = max(0, min(100, int(analysis[score_key])))
        
        # Ensure detailed_analysis exists
        if 'detailed_analysis' not in analysis:
            analysis['detailed_analysis'] = {}
        
        # Ensure recommendations exist
        if 'recommendations' not in analysis or not isinstance(analysis['recommendations'], list):
            analysis['recommendations'] = ["Review and enhance your resume based on job requirements"]
        
        # Add metadata
        analysis['metadata'] = {
            'resume_length': len(resume_text),
            'jd_length': len(job_description),
            'analysis_type': 'ai_powered',
            'timestamp': str(pd.Timestamp.now())
        }
        
        return analysis
    
    def _parse_text_response(self, text_response: str, resume_text: str, job_description: str) -> Dict[str, Any]:
        """Parse text response when JSON parsing fails"""
        
        # Extract scores using regex
        scores = {}
        score_patterns = {
            'overall_match_score': r'overall.*?(\d+)%?',
            'skills_match_score': r'skills?.*?(\d+)%?',
            'experience_match_score': r'experience.*?(\d+)%?',
            'education_match_score': r'education.*?(\d+)%?',
            'keyword_match_score': r'keyword.*?(\d+)%?'
        }
        
        for key, pattern in score_patterns.items():
            match = re.search(pattern, text_response, re.IGNORECASE)
            scores[key] = int(match.group(1)) if match else 65
        
        # Extract recommendations
        recommendations = []
        rec_section = re.search(r'recommend.*?:(.*?)(?:\n\n|\Z)', text_response, re.IGNORECASE | re.DOTALL)
        if rec_section:
            rec_text = rec_section.group(1)
            recommendations = [line.strip('- •').strip() for line in rec_text.split('\n') if line.strip()]
        
        return {
            **scores,
            'detailed_analysis': {
                'ai_response': text_response,
                'strengths': [],
                'weaknesses': [],
                'missing_skills': [],
                'relevant_experience': [],
                'education_alignment': 'Analysis completed'
            },
            'recommendations': recommendations or ["Enhance resume based on job requirements"],
            'key_insights': ["AI analysis completed successfully"],
            'ats_compatibility': {'score': scores.get('keyword_match_score', 65), 'issues': []},
            'metadata': {
                'resume_length': len(resume_text),
                'jd_length': len(job_description),
                'analysis_type': 'ai_text_parsed',
                'timestamp': str(pd.Timestamp.now())
            }
        }
    
    def _fallback_analysis(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        """Fallback analysis when API is not available"""
        
        # Basic keyword matching analysis
        jd_words = set(job_description.lower().split())
        resume_words = set(resume_text.lower().split())
        
        # Calculate basic matches
        common_words = jd_words.intersection(resume_words)
        keyword_match = len(common_words) / len(jd_words) * 100 if jd_words else 0
        
        # Basic scoring
        base_score = min(85, max(35, keyword_match + 20))
        
        return {
            'overall_match_score': int(base_score),
            'skills_match_score': int(base_score - 5),
            'experience_match_score': int(base_score + 5),
            'education_match_score': int(base_score),
            'keyword_match_score': int(keyword_match),
            'detailed_analysis': {
                'strengths': [f"Found {len(common_words)} matching keywords"],
                'weaknesses': ["Limited analysis without AI API"],
                'missing_skills': ["Enable AI analysis for detailed insights"],
                'relevant_experience': ["Basic keyword matching performed"],
                'education_alignment': "Basic analysis completed"
            },
            'recommendations': [
                "Add Perplexity API key for detailed AI analysis",
                "Enhance resume with more job-specific keywords",
                "Review job requirements carefully"
            ],
            'key_insights': [
                f"Basic keyword analysis found {len(common_words)} matches",
                "Enable AI analysis for comprehensive insights"
            ],
            'ats_compatibility': {
                'score': int(keyword_match),
                'issues': ["Enable AI analysis for ATS compatibility check"]
            },
            'metadata': {
                'resume_length': len(resume_text),
                'jd_length': len(job_description),
                'analysis_type': 'basic_fallback',
                'timestamp': str(pd.Timestamp.now())
            }
        }

# Global analyzer instance
perplexity_analyzer = None

def get_analyzer(api_key: str = None) -> PerplexityAnalyzer:
    """Get or create analyzer instance"""
    global perplexity_analyzer
    if perplexity_analyzer is None or api_key:
        perplexity_analyzer = PerplexityAnalyzer(api_key)
    return perplexity_analyzer