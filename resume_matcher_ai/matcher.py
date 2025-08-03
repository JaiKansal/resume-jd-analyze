"""
Core matching logic and Perplexity API integration
"""
import json
import time
import requests
from typing import Dict, List, Optional
from .utils import (
    MatchResult, 
    load_config, 
    validate_api_key, 
    format_prompt, 
    handle_rate_limits,
    get_match_category,
    track_api_usage
)

def analyze_match(resume_text: str, jd_data: Dict) -> MatchResult:
    """Orchestrate the matching process"""
    start_time = time.time()
    
    try:
        # Create structured prompt for analysis
        jd_text = jd_data.get('raw_text', '')
        prompt = format_prompt(resume_text, jd_text)
        
        # Call Perplexity API
        api_response = call_perplexity_api(prompt)
        
        # Parse the structured response
        parsed_data = _parse_api_response(api_response)
        
        # Extract components from parsed response
        score = parsed_data.get('compatibility_score', 0)
        matching_skills = parsed_data.get('matching_skills', [])
        missing_skills = parsed_data.get('missing_skills', [])
        
        # Enhanced gap analysis with prioritization (Requirements 4.2, 4.3)
        skill_gaps = identify_skill_gaps_by_priority(resume_text, jd_data, api_response)
        
        # Enhanced suggestion generation (Requirements 5.1, 5.2, 5.3, 5.4)
        suggestions = generate_enhanced_suggestions(resume_text, jd_data, skill_gaps, score, api_response)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Create and return MatchResult
        return MatchResult(
            score=score,
            match_category=get_match_category(score),
            matching_skills=matching_skills,
            missing_skills=missing_skills,
            skill_gaps=skill_gaps,
            suggestions=suggestions,
            processing_time=processing_time
        )
        
    except Exception as e:
        # Return error result with processing time
        processing_time = time.time() - start_time
        return MatchResult(
            score=0,
            match_category="Error",
            matching_skills=[],
            missing_skills=[],
            skill_gaps={'Critical': [], 'Important': [], 'Nice-to-have': []},
            suggestions=[f"Analysis failed: {str(e)}"],
            processing_time=processing_time
        )

def call_perplexity_api(prompt: str) -> str:
    """
    Interface with Perplexity API with comprehensive error handling and retry logic
    
    Args:
        prompt: The prompt to send to the API
        
    Returns:
        API response content
        
    Raises:
        Exception: Various API-related errors with helpful guidance
    """
    # Track start time for usage tracking
    start_time = time.time()
    
    # Validate API configuration
    config = load_config()
    api_key = config.get('perplexity_api_key')
    
    if not api_key:
        raise Exception(
            "PERPLEXITY_API_KEY environment variable is not set.\n\n"
            "To fix this:\n"
            "1. Get an API key from https://www.perplexity.ai/\n"
            "2. Set the environment variable:\n"
            "   export PERPLEXITY_API_KEY='your-key-here'\n"
            "3. Restart this application\n\n"
            "For more help, visit: https://docs.perplexity.ai/docs/getting-started"
        )
    
    # Validate API key format and accessibility
    try:
        if not validate_api_key(api_key):
            raise Exception(
                "Invalid Perplexity API key format or the key is not accessible.\n\n"
                "Please check:\n"
                "1. Your API key is correct and starts with 'pplx-'\n"
                "2. The key has not expired\n"
                "3. Your account has sufficient credits\n"
                "4. The key has the necessary permissions\n\n"
                "You can verify your API key at: https://www.perplexity.ai/settings/api"
            )
    except requests.RequestException:
        # If validation fails due to network issues, continue but warn
        print("⚠️  Warning: Could not validate API key due to network issues. Proceeding anyway...")
    
    # Prepare API request
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'User-Agent': 'Resume-Matcher-AI/1.0'
    }
    
    payload = {
        'model': 'sonar-pro',
        'messages': [
            {
                'role': 'system',
                'content': 'You are an expert HR analyst specializing in resume and job description matching. Provide accurate, structured analysis in the requested JSON format.'
            },
            {
                'role': 'user',
                'content': prompt
            }
        ],
        'max_tokens': int(config.get('max_tokens', '4000')),
        'temperature': 0.1,  # Low temperature for consistent, factual responses
        'top_p': 0.9
    }
    
    # Apply cost optimization to the payload
    from .utils import optimize_api_payload
    payload = optimize_api_payload(payload)
    
    api_url = f"{config.get('api_base_url', 'https://api.perplexity.ai')}/chat/completions"
    timeout = int(config.get('timeout', '30'))
    
    # Make API request with comprehensive error handling
    try:
        response = _make_api_request_with_retry(api_url, headers, payload, timeout)
        
        # Handle various HTTP status codes
        _handle_api_response_status(response)
        
        # Parse and validate response
        try:
            response_data = response.json()
        except json.JSONDecodeError as e:
            raise Exception(
                f"Failed to parse API response as JSON.\n"
                f"This may indicate a temporary service issue.\n"
                f"Response status: {response.status_code}\n"
                f"Response preview: {response.text[:200]}...\n\n"
                f"Please try again in a few moments."
            )
        
        # Validate response structure
        if 'choices' not in response_data:
            raise Exception(
                f"Invalid API response format: missing 'choices' field.\n"
                f"Response: {response_data}\n\n"
                f"This may indicate an API service issue. Please try again."
            )
        
        if not response_data['choices'] or len(response_data['choices']) == 0:
            raise Exception(
                f"API response contains no choices.\n"
                f"This may indicate an issue with the request or API service.\n"
                f"Please try again with a shorter prompt if the issue persists."
            )
        
        # Extract content
        choice = response_data['choices'][0]
        if 'message' not in choice or 'content' not in choice['message']:
            raise Exception(
                f"Invalid API response structure: missing message content.\n"
                f"Response: {response_data}\n\n"
                f"Please try again."
            )
        
        content = choice['message']['content']
        
        if not content or not content.strip():
            raise Exception(
                "API returned empty content. This may indicate a processing issue.\n"
                "Please try again with a different prompt or check your API quota."
            )
        
        # Track successful API usage
        try:
            usage_data = response_data.get('usage', {})
            tokens_used = usage_data.get('total_tokens', 0)
            
            # If no usage data, estimate tokens (rough estimate: 1 token ≈ 4 characters)
            if tokens_used == 0:
                estimated_tokens = (len(prompt) + len(content)) // 4
                tokens_used = max(estimated_tokens, 100)  # Minimum reasonable estimate
            
            processing_time = time.time() - start_time if 'start_time' in locals() else 0
            track_api_usage(tokens_used, processing_time, True)
        except Exception:
            # Don't fail the main operation if usage tracking fails
            pass
        
        return content
        
    except requests.exceptions.Timeout:
        raise Exception(
            f"API request timed out after {timeout} seconds.\n\n"
            f"This could be due to:\n"
            f"• High API load\n"
            f"• Network connectivity issues\n"
            f"• Large prompt size\n\n"
            f"Solutions:\n"
            f"• Try again in a few moments\n"
            f"• Check your internet connection\n"
            f"• Consider using a shorter resume or job description"
        )
    
    except requests.exceptions.ConnectionError as e:
        raise Exception(
            f"Failed to connect to Perplexity API.\n\n"
            f"This could be due to:\n"
            f"• Internet connectivity issues\n"
            f"• DNS resolution problems\n"
            f"• Firewall blocking the connection\n"
            f"• API service temporarily unavailable\n\n"
            f"Solutions:\n"
            f"• Check your internet connection\n"
            f"• Try accessing https://api.perplexity.ai in your browser\n"
            f"• Check if you're behind a corporate firewall\n"
            f"• Wait a few minutes and try again\n\n"
            f"Technical details: {str(e)}"
        )
    
    except requests.exceptions.RequestException as e:
        raise Exception(
            f"API request failed due to a network error.\n\n"
            f"Error details: {str(e)}\n\n"
            f"Solutions:\n"
            f"• Check your internet connection\n"
            f"• Try again in a few moments\n"
            f"• Contact support if the issue persists"
        )
    
    except Exception as e:
        # Track failed API usage
        try:
            processing_time = time.time() - start_time
            # Estimate tokens for failed request (just the prompt)
            estimated_tokens = len(prompt) // 4
            track_api_usage(estimated_tokens, processing_time, False, str(e))
        except Exception:
            # Don't fail if usage tracking fails
            pass
        
        # Catch any other unexpected errors
        error_msg = str(e)
        if "rate limit" in error_msg.lower():
            # Re-raise rate limit errors as-is (they have good messages)
            raise
        elif "api key" in error_msg.lower():
            # Re-raise API key errors as-is
            raise
        else:
            # Wrap other errors with context
            raise Exception(
                f"Unexpected error during API call: {error_msg}\n\n"
                f"Please try again. If the problem persists, this may indicate:\n"
                f"• A temporary service issue\n"
                f"• An issue with your API configuration\n"
                f"• A problem with the input data\n\n"
                f"Contact support if you continue to see this error."
            )

def calculate_score(api_response: str) -> int:
    """Generate 0-100% compatibility score from API response"""
    try:
        parsed_data = _parse_api_response(api_response)
        score = parsed_data.get('compatibility_score', 0)
        
        # Ensure score is within valid range
        if isinstance(score, (int, float)):
            return max(0, min(100, int(score)))
        else:
            return 0
            
    except Exception:
        return 0

def identify_gaps(resume_text: str, jd_data: Dict, api_response: str) -> List[str]:
    """Find missing skills and experience from API response"""
    try:
        parsed_data = _parse_api_response(api_response)
        missing_skills = parsed_data.get('missing_skills', [])
        
        # Ensure we return a list of strings
        if isinstance(missing_skills, list):
            return [str(skill) for skill in missing_skills if skill]
        else:
            return []
            
    except Exception:
        return []

def identify_skill_gaps_by_priority(resume_text: str, jd_data: Dict, api_response: str) -> Dict[str, List[str]]:
    """
    Categorize missing skills by priority (Critical/Important/Nice-to-have)
    Implements Requirements 4.2 and 4.3
    """
    try:
        parsed_data = _parse_api_response(api_response)
        skill_gaps = parsed_data.get('skill_gaps', {})
        
        # Ensure we have all required categories
        result = {
            'Critical': [],
            'Important': [],
            'Nice-to-have': []
        }
        
        # Populate from API response
        for category in result.keys():
            if category in skill_gaps and isinstance(skill_gaps[category], list):
                result[category] = [str(skill) for skill in skill_gaps[category] if skill]
        
        # If no gaps are identified, check if we should display the "all skills present" message
        total_gaps = sum(len(skills) for skills in result.values())
        if total_gaps == 0:
            # This will be handled in the display logic to show "All key skills are present in resume"
            pass
        
        return result
        
    except Exception:
        # Return empty structure on error
        return {
            'Critical': [],
            'Important': [],
            'Nice-to-have': []
        }

def generate_suggestions(gaps: List[str], api_response: str) -> List[str]:
    """Create improvement recommendations from API response"""
    try:
        parsed_data = _parse_api_response(api_response)
        suggestions = parsed_data.get('suggestions', [])
        
        # Ensure we return a list of strings
        if isinstance(suggestions, list):
            return [str(suggestion) for suggestion in suggestions if suggestion]
        else:
            return []
            
    except Exception:
        return []

def generate_enhanced_suggestions(resume_text: str, jd_data: Dict, skill_gaps: Dict[str, List[str]], score: int, api_response: str) -> List[str]:
    """
    Generate enhanced, specific suggestions for resume improvement
    Implements Requirements 5.1, 5.2, 5.3, and 5.4
    """
    try:
        parsed_data = _parse_api_response(api_response)
        base_suggestions = parsed_data.get('suggestions', [])
        
        # Start with API-generated suggestions
        suggestions = []
        if isinstance(base_suggestions, list):
            suggestions.extend([str(suggestion) for suggestion in base_suggestions if suggestion])
        
        # Ensure we have at least 3 suggestions (Requirement 5.1)
        if len(suggestions) < 3:
            suggestions.extend(_generate_fallback_suggestions(skill_gaps, score))
        
        # Enhance suggestions based on score and gaps
        enhanced_suggestions = _enhance_suggestions_with_specifics(suggestions, skill_gaps, score)
        
        # Ensure we have at least 3 suggestions
        while len(enhanced_suggestions) < 3:
            enhanced_suggestions.append("Consider reviewing and updating your resume format and structure for better readability.")
        
        # Limit to reasonable number of suggestions (5-7 max)
        return enhanced_suggestions[:7]
        
    except Exception:
        # Fallback suggestions if everything fails
        return _generate_fallback_suggestions(skill_gaps, score)

def _generate_fallback_suggestions(skill_gaps: Dict[str, List[str]], score: int) -> List[str]:
    """Generate fallback suggestions when API suggestions are not available"""
    suggestions = []
    
    # Critical skills suggestions
    if skill_gaps.get('Critical'):
        critical_skills = ', '.join(skill_gaps['Critical'][:3])  # Limit to first 3
        suggestions.append(f"Add critical skills to your resume: {critical_skills}. Include specific examples of how you've used these skills in previous roles.")
    
    # Important skills suggestions
    if skill_gaps.get('Important'):
        important_skills = ', '.join(skill_gaps['Important'][:2])  # Limit to first 2
        suggestions.append(f"Consider highlighting these important skills: {important_skills}. Add them to your skills section and mention them in your experience descriptions.")
    
    # Score-based suggestions (Requirement 5.4)
    if score > 70:  # Strong match - optimization suggestions
        suggestions.append("Your resume already shows strong alignment. Consider adding quantifiable achievements and metrics to strengthen your impact statements.")
        suggestions.append("Optimize keyword usage by incorporating more industry-specific terminology from the job description throughout your experience sections.")
    elif score >= 30:  # Moderate match
        suggestions.append("Enhance your experience descriptions by using more action verbs and specific examples that demonstrate the required skills.")
        suggestions.append("Add a professional summary section that highlights your most relevant qualifications for this specific role.")
    else:  # Poor match
        suggestions.append("Consider restructuring your resume to better highlight experiences that align with the job requirements.")
        suggestions.append("Add relevant certifications, training, or projects that demonstrate the skills mentioned in the job description.")
    
    # General improvement suggestions
    if len(suggestions) < 3:
        suggestions.extend([
            "Include specific metrics and quantifiable achievements in your experience descriptions (e.g., 'Increased efficiency by 25%').",
            "Tailor your professional summary to directly address the key requirements mentioned in the job description.",
            "Use industry-specific keywords and terminology that appear in the job posting throughout your resume."
        ])
    
    return suggestions[:5]  # Return up to 5 suggestions

def _enhance_suggestions_with_specifics(suggestions: List[str], skill_gaps: Dict[str, List[str]], score: int) -> List[str]:
    """Enhance suggestions with specific, actionable details (Requirement 5.3)"""
    enhanced = []
    
    for suggestion in suggestions:
        # Make suggestions more specific and actionable
        if "skill" in suggestion.lower() and not any(gap in suggestion for gaps in skill_gaps.values() for gap in gaps):
            # Add specific skills to generic skill suggestions
            if skill_gaps.get('Critical'):
                suggestion += f" Focus particularly on: {', '.join(skill_gaps['Critical'][:2])}."
        
        # Add recommended phrases for experience enhancement
        if "experience" in suggestion.lower() or "description" in suggestion.lower():
            suggestion += " Use phrases like 'Led cross-functional teams', 'Implemented solutions that resulted in', or 'Collaborated with stakeholders to achieve'."
        
        # Add specific sections recommendations
        if "section" in suggestion.lower() or "summary" in suggestion.lower():
            suggestion += " Consider adding sections like 'Core Competencies', 'Technical Proficiencies', or 'Key Achievements' if not already present."
        
        enhanced.append(suggestion)
    
    return enhanced

def _handle_api_response_status(response: requests.Response) -> None:
    """
    Handle various HTTP status codes with specific error messages
    
    Args:
        response: The HTTP response from the API
        
    Raises:
        Exception: Various API errors with helpful guidance
    """
    if response.status_code == 200:
        return  # Success
    
    elif response.status_code == 400:
        raise Exception(
            f"Bad request (400): The API request was malformed.\n"
            f"This may be due to:\n"
            f"• Invalid prompt format\n"
            f"• Prompt too long\n"
            f"• Invalid parameters\n\n"
            f"Please try with a shorter resume or job description."
        )
    
    elif response.status_code == 401:
        raise Exception(
            f"Unauthorized (401): Invalid API key.\n\n"
            f"Please check:\n"
            f"1. Your API key is correct\n"
            f"2. The key hasn't expired\n"
            f"3. You have the necessary permissions\n\n"
            f"You can verify your API key at: https://www.perplexity.ai/settings/api"
        )
    
    elif response.status_code == 403:
        raise Exception(
            f"Forbidden (403): Access denied.\n\n"
            f"This could be due to:\n"
            f"• Insufficient API permissions\n"
            f"• Account restrictions\n"
            f"• Billing issues\n\n"
            f"Please check your account status at: https://www.perplexity.ai/settings/api"
        )
    
    elif response.status_code == 429:
        # Extract rate limit information if available
        retry_after = response.headers.get('Retry-After', '60')
        reset_time = response.headers.get('X-RateLimit-Reset', 'unknown')
        
        try:
            wait_time = int(retry_after)
        except (ValueError, TypeError):
            wait_time = 60
        
        raise Exception(
            f"Rate limit exceeded (429).\n\n"
            f"You've made too many requests. Please wait {wait_time} seconds before trying again.\n\n"
            f"Rate limit details:\n"
            f"• Retry after: {retry_after} seconds\n"
            f"• Reset time: {reset_time}\n\n"
            f"Consider:\n"
            f"• Upgrading your API plan for higher limits\n"
            f"• Spacing out your requests\n"
            f"• Using shorter prompts to reduce token usage"
        )
    
    elif response.status_code == 500:
        raise Exception(
            f"Internal server error (500): The API service is experiencing issues.\n\n"
            f"This is a temporary problem with the Perplexity API.\n"
            f"Please try again in a few minutes.\n\n"
            f"If the problem persists, check the Perplexity status page."
        )
    
    elif response.status_code == 502:
        raise Exception(
            f"Bad gateway (502): API gateway error.\n\n"
            f"The API service is temporarily unavailable.\n"
            f"Please try again in a few minutes."
        )
    
    elif response.status_code == 503:
        raise Exception(
            f"Service unavailable (503): The API is temporarily down for maintenance.\n\n"
            f"Please try again later.\n"
            f"Check the Perplexity status page for updates."
        )
    
    elif response.status_code == 504:
        raise Exception(
            f"Gateway timeout (504): The API request timed out.\n\n"
            f"This could be due to:\n"
            f"• High server load\n"
            f"• Complex prompt processing\n"
            f"• Network issues\n\n"
            f"Solutions:\n"
            f"• Try again with a shorter prompt\n"
            f"• Wait a few minutes and retry\n"
            f"• Check your internet connection"
        )
    
    else:
        # Handle any other status codes
        try:
            error_details = response.json()
            error_message = error_details.get('error', {}).get('message', 'Unknown error')
        except:
            error_message = response.text[:200] if response.text else 'No error details available'
        
        raise Exception(
            f"API request failed with status {response.status_code}.\n\n"
            f"Error details: {error_message}\n\n"
            f"Please try again. If the problem persists, contact support."
        )


def _make_api_request_with_retry(url: str, headers: Dict, payload: Dict, timeout: int, max_retries: int = 3) -> requests.Response:
    """
    Make API request with comprehensive retry logic for transient failures
    
    Args:
        url: API endpoint URL
        headers: Request headers
        payload: Request payload
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts
        
    Returns:
        HTTP response object
        
    Raises:
        Exception: If all retry attempts fail
    """
    last_exception = None
    retry_delays = [1, 2, 4]  # Exponential backoff: 1s, 2s, 4s
    
    for attempt in range(max_retries):
        try:
            # Log retry attempt (except for first attempt)
            if attempt > 0:
                print(f"🔄 Retrying API request (attempt {attempt + 1}/{max_retries})...")
            
            # Make the request
            response = requests.post(url, headers=headers, json=payload, timeout=timeout)
            
            # Handle different response scenarios
            if response.status_code == 200:
                # Success - return immediately
                if attempt > 0:
                    print("✅ API request succeeded after retry")
                return response
            
            elif response.status_code == 429:
                # Rate limit - don't retry, let the caller handle it
                return response
            
            elif response.status_code in [401, 403]:
                # Authentication/authorization errors - don't retry
                return response
            
            elif response.status_code >= 500 and attempt < max_retries - 1:
                # Server errors - retry with backoff
                delay = retry_delays[min(attempt, len(retry_delays) - 1)]
                print(f"⚠️  Server error ({response.status_code}). Retrying in {delay} seconds...")
                time.sleep(delay)
                continue
            
            elif response.status_code == 502 and attempt < max_retries - 1:
                # Bad gateway - often transient, retry
                delay = retry_delays[min(attempt, len(retry_delays) - 1)]
                print(f"⚠️  Bad gateway error. Retrying in {delay} seconds...")
                time.sleep(delay)
                continue
            
            elif response.status_code == 503 and attempt < max_retries - 1:
                # Service unavailable - retry with longer delay
                delay = retry_delays[min(attempt, len(retry_delays) - 1)] * 2
                print(f"⚠️  Service unavailable. Retrying in {delay} seconds...")
                time.sleep(delay)
                continue
            
            elif response.status_code == 504 and attempt < max_retries - 1:
                # Gateway timeout - retry
                delay = retry_delays[min(attempt, len(retry_delays) - 1)]
                print(f"⚠️  Gateway timeout. Retrying in {delay} seconds...")
                time.sleep(delay)
                continue
            
            else:
                # Other status codes or final attempt - return response
                return response
            
        except requests.exceptions.Timeout as e:
            last_exception = e
            if attempt < max_retries - 1:
                delay = retry_delays[min(attempt, len(retry_delays) - 1)]
                print(f"⚠️  Request timeout. Retrying in {delay} seconds...")
                time.sleep(delay)
                continue
            
        except requests.exceptions.ConnectionError as e:
            last_exception = e
            if attempt < max_retries - 1:
                delay = retry_delays[min(attempt, len(retry_delays) - 1)]
                print(f"⚠️  Connection error. Retrying in {delay} seconds...")
                time.sleep(delay)
                continue
        
        except requests.exceptions.RequestException as e:
            last_exception = e
            # For other request exceptions, check if it's worth retrying
            error_str = str(e).lower()
            
            # Don't retry for certain errors
            if any(keyword in error_str for keyword in ['ssl', 'certificate', 'hostname', 'dns']):
                # SSL, certificate, hostname, or DNS errors - don't retry
                raise e
            
            if attempt < max_retries - 1:
                delay = retry_delays[min(attempt, len(retry_delays) - 1)]
                print(f"⚠️  Request error: {str(e)[:100]}... Retrying in {delay} seconds...")
                time.sleep(delay)
                continue
    
    # If all retries failed, raise the last exception with context
    if last_exception:
        raise Exception(
            f"API request failed after {max_retries} attempts.\n"
            f"Last error: {str(last_exception)}\n\n"
            f"This could indicate:\n"
            f"• Persistent network connectivity issues\n"
            f"• API service outage\n"
            f"• Firewall or proxy blocking requests\n\n"
            f"Please check your internet connection and try again later."
        )
    else:
        raise Exception(
            f"API request failed after {max_retries} attempts with no specific error captured."
        )

def _parse_api_response(api_response: str) -> Dict:
    """Parse structured JSON response from Perplexity API"""
    try:
        # Try to find JSON in the response
        # Sometimes the API returns text before/after the JSON
        json_start = api_response.find('{')
        json_end = api_response.rfind('}') + 1
        
        if json_start == -1 or json_end == 0:
            raise ValueError("No JSON found in API response")
        
        json_str = api_response[json_start:json_end]
        parsed_data = json.loads(json_str)
        
        # Validate required fields and provide defaults
        result = {
            'compatibility_score': parsed_data.get('compatibility_score', 0),
            'matching_skills': parsed_data.get('matching_skills', []),
            'missing_skills': parsed_data.get('missing_skills', []),
            'skill_gaps': parsed_data.get('skill_gaps', {}),
            'suggestions': parsed_data.get('suggestions', []),
            'analysis_summary': parsed_data.get('analysis_summary', '')
        }
        
        # Ensure skill_gaps has the expected structure
        if not isinstance(result['skill_gaps'], dict):
            result['skill_gaps'] = {}
        
        # Ensure all required categories exist in skill_gaps
        for category in ['Critical', 'Important', 'Nice-to-have']:
            if category not in result['skill_gaps']:
                result['skill_gaps'][category] = []
        
        return result
        
    except (json.JSONDecodeError, ValueError) as e:
        # If JSON parsing fails, try to extract information using text parsing
        return _fallback_text_parsing(api_response)

def _fallback_text_parsing(api_response: str) -> Dict:
    """Fallback text parsing when JSON parsing fails"""
    # This is a basic fallback that tries to extract some information
    # even when the API doesn't return proper JSON
    
    result = {
        'compatibility_score': 0,
        'matching_skills': [],
        'missing_skills': [],
        'skill_gaps': {'Critical': [], 'Important': [], 'Nice-to-have': []},
        'suggestions': [],
        'analysis_summary': 'Failed to parse structured response'
    }
    
    # Try to extract a score if mentioned in text
    import re
    score_match = re.search(r'(\d{1,3})%|\bscore[:\s]*(\d{1,3})', api_response.lower())
    if score_match:
        score = int(score_match.group(1) or score_match.group(2))
        result['compatibility_score'] = max(0, min(100, score))
    
    # Add the raw response as a suggestion for debugging
    result['suggestions'] = [f"Raw API response (parsing failed): {api_response[:200]}..."]
    
    return result