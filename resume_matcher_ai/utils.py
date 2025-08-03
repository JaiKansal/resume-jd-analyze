"""
Shared utilities and configuration management
"""
import os
import re
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from dataclasses import dataclass, asdict
from typing import List
from pathlib import Path

@dataclass
class MatchResult:
    """Data class for match analysis results"""
    score: int  # 0-100 compatibility percentage
    match_category: str  # "Poor", "Moderate", "Strong"
    matching_skills: List[str]  # Skills found in both documents
    missing_skills: List[str]  # Skills in JD but not resume
    skill_gaps: Dict[str, List[str]]  # Gap category -> skills mapping
    suggestions: List[str]  # Improvement recommendations
    processing_time: float  # Analysis duration in seconds

@dataclass
class JobDescription:
    """Data class for job description data"""
    raw_text: str
    title: str
    requirements: List[str]
    technical_skills: List[str]
    soft_skills: List[str]
    experience_level: str
    key_responsibilities: List[str]

@dataclass
class ResumeData:
    """Data class for resume data"""
    raw_text: str
    cleaned_text: str
    skills: List[str]
    experience: List[str]
    education: List[str]
    word_count: int

@dataclass
class UsageRecord:
    """Data class for tracking API usage"""
    timestamp: str
    tokens_used: int
    estimated_cost: float
    processing_time: float
    success: bool
    error_message: Optional[str] = None

def load_config() -> Dict[str, str]:
    """
    Load API keys and settings from environment variables and .env file
    
    Returns:
        Dictionary containing configuration values
    """
    # Try to load from .env file first
    _load_env_file()
    
    config = {}
    
    # Load Perplexity API key
    api_key = os.getenv('PERPLEXITY_API_KEY')
    if api_key:
        config['perplexity_api_key'] = api_key
    
    # Load other optional configuration
    config['api_base_url'] = os.getenv('PERPLEXITY_API_URL', 'https://api.perplexity.ai')
    config['max_tokens'] = os.getenv('MAX_TOKENS', '4000')
    config['timeout'] = os.getenv('API_TIMEOUT', '30')
    
    # Load usage tracking configuration
    config['enable_usage_tracking'] = os.getenv('ENABLE_USAGE_TRACKING', 'true').lower() == 'true'
    config['usage_log_file'] = os.getenv('USAGE_LOG_FILE', 'usage_log.json')
    config['cost_alert_threshold'] = float(os.getenv('COST_ALERT_THRESHOLD', '10.00'))
    
    # Load application configuration
    config['debug_mode'] = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    config['log_level'] = os.getenv('LOG_LEVEL', 'INFO')
    
    return config


def _load_env_file() -> None:
    """Load environment variables from .env file if it exists"""
    env_file = Path('.env')
    if env_file.exists():
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if key and not os.getenv(key):  # Don't override existing env vars
                            os.environ[key] = value
        except Exception as e:
            # Silently fail if .env file can't be read
            pass


def setup_environment() -> Dict[str, Any]:
    """
    Set up and validate the complete application environment
    
    Returns:
        Dictionary containing setup status and configuration
    """
    setup_result = {
        'success': True,
        'errors': [],
        'warnings': [],
        'config': {},
        'setup_steps': []
    }
    
    # Step 1: Load configuration
    try:
        config = load_config()
        setup_result['config'] = config
        setup_result['setup_steps'].append('✅ Configuration loaded successfully')
    except Exception as e:
        setup_result['errors'].append(f'Failed to load configuration: {str(e)}')
        setup_result['success'] = False
        return setup_result
    
    # Step 2: Validate API key
    api_key = config.get('perplexity_api_key')
    if not api_key:
        setup_result['errors'].append('Perplexity API key is not configured')
        setup_result['success'] = False
    else:
        setup_result['setup_steps'].append('✅ API key found in configuration')
        
        # Validate API key format and connectivity
        if validate_api_key(api_key):
            setup_result['setup_steps'].append('✅ API key validated successfully')
        else:
            setup_result['errors'].append('API key validation failed')
            setup_result['success'] = False
    
    # Step 3: Set up usage tracking
    if config.get('enable_usage_tracking', True):
        try:
            _initialize_usage_tracking(config.get('usage_log_file', 'usage_log.json'))
            setup_result['setup_steps'].append('✅ Usage tracking initialized')
        except Exception as e:
            setup_result['warnings'].append(f'Usage tracking setup failed: {str(e)}')
    
    # Step 4: Check cost threshold
    try:
        threshold = config.get('cost_alert_threshold', 10.00)
        if isinstance(threshold, (int, float)) and threshold > 0:
            setup_result['setup_steps'].append(f'✅ Cost alert threshold set to ${threshold:.2f}')
        else:
            setup_result['warnings'].append('Invalid cost alert threshold, using default $10.00')
    except Exception as e:
        setup_result['warnings'].append(f'Cost threshold validation failed: {str(e)}')
    
    return setup_result


def _initialize_usage_tracking(log_file: str) -> None:
    """Initialize usage tracking log file"""
    log_path = Path(log_file)
    
    # Create log file if it doesn't exist
    if not log_path.exists():
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, 'w') as f:
            json.dump([], f)


def track_api_usage(tokens_used: int, processing_time: float, success: bool, error_message: Optional[str] = None) -> None:
    """
    Track API usage for cost management and monitoring
    
    Args:
        tokens_used: Number of tokens consumed in the API call
        processing_time: Time taken for the API call in seconds
        success: Whether the API call was successful
        error_message: Error message if the call failed
    """
    config = load_config()
    
    if not config.get('enable_usage_tracking', True):
        return
    
    # Estimate cost (Perplexity pricing: ~$0.001 per 1K tokens)
    estimated_cost = (tokens_used / 1000) * 0.001
    
    # Create usage record
    usage_record = UsageRecord(
        timestamp=datetime.now().isoformat(),
        tokens_used=tokens_used,
        estimated_cost=estimated_cost,
        processing_time=processing_time,
        success=success,
        error_message=error_message
    )
    
    # Save to log file
    log_file = config.get('usage_log_file', 'usage_log.json')
    _save_usage_record(log_file, usage_record)
    
    # Check cost threshold
    _check_cost_threshold(log_file, config.get('cost_alert_threshold', 10.00))


def _save_usage_record(log_file: str, record: UsageRecord) -> None:
    """Save usage record to log file"""
    log_path = Path(log_file)
    
    try:
        # Read existing records
        if log_path.exists():
            with open(log_path, 'r') as f:
                records = json.load(f)
        else:
            records = []
        
        # Add new record
        records.append(asdict(record))
        
        # Keep only last 1000 records to prevent file from growing too large
        if len(records) > 1000:
            records = records[-1000:]
        
        # Save back to file
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, 'w') as f:
            json.dump(records, f, indent=2)
            
    except Exception as e:
        # Silently fail if logging fails - don't break the main application
        pass


def _check_cost_threshold(log_file: str, threshold: float) -> None:
    """Check if cost threshold has been exceeded and alert user"""
    try:
        log_path = Path(log_file)
        if not log_path.exists():
            return
        
        with open(log_path, 'r') as f:
            records = json.load(f)
        
        # Calculate costs for the last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_cost = 0.0
        
        for record in records:
            try:
                record_time = datetime.fromisoformat(record['timestamp'])
                if record_time >= thirty_days_ago and record.get('success', False):
                    recent_cost += record.get('estimated_cost', 0.0)
            except (ValueError, KeyError):
                continue
        
        # Alert if threshold exceeded
        if recent_cost >= threshold:
            print(f"\n⚠️  COST ALERT: You've used approximately ${recent_cost:.2f} in API costs over the last 30 days.")
            print(f"   This exceeds your threshold of ${threshold:.2f}.")
            print(f"   Consider monitoring your usage or adjusting your threshold.\n")
            
    except Exception as e:
        # Silently fail if cost checking fails
        pass


def get_usage_statistics(days: int = 30) -> Dict[str, Any]:
    """
    Get usage statistics for the specified number of days
    
    Args:
        days: Number of days to look back (default: 30)
        
    Returns:
        Dictionary containing usage statistics
    """
    config = load_config()
    log_file = config.get('usage_log_file', 'usage_log.json')
    log_path = Path(log_file)
    
    stats = {
        'total_calls': 0,
        'successful_calls': 0,
        'failed_calls': 0,
        'total_tokens': 0,
        'total_cost': 0.0,
        'average_processing_time': 0.0,
        'period_days': days,
        'period_start': (datetime.now() - timedelta(days=days)).isoformat(),
        'period_end': datetime.now().isoformat()
    }
    
    if not log_path.exists():
        return stats
    
    try:
        with open(log_path, 'r') as f:
            records = json.load(f)
        
        # Filter records for the specified period
        cutoff_date = datetime.now() - timedelta(days=days)
        processing_times = []
        
        for record in records:
            try:
                record_time = datetime.fromisoformat(record['timestamp'])
                if record_time >= cutoff_date:
                    stats['total_calls'] += 1
                    
                    if record.get('success', False):
                        stats['successful_calls'] += 1
                        stats['total_tokens'] += record.get('tokens_used', 0)
                        stats['total_cost'] += record.get('estimated_cost', 0.0)
                    else:
                        stats['failed_calls'] += 1
                    
                    processing_time = record.get('processing_time', 0.0)
                    if processing_time > 0:
                        processing_times.append(processing_time)
                        
            except (ValueError, KeyError):
                continue
        
        # Calculate average processing time
        if processing_times:
            stats['average_processing_time'] = sum(processing_times) / len(processing_times)
            
    except Exception as e:
        # Return empty stats if file can't be read
        pass
    
    return stats


def display_setup_instructions() -> None:
    """Display comprehensive setup instructions for new users"""
    print("=" * 70)
    print("🚀 RESUME MATCHER AI - SETUP INSTRUCTIONS")
    print("=" * 70)
    print()
    
    print("📋 QUICK SETUP GUIDE:")
    print()
    
    print("1️⃣  GET YOUR PERPLEXITY API KEY")
    print("   • Visit: https://www.perplexity.ai/")
    print("   • Sign up for an account")
    print("   • Navigate to API settings")
    print("   • Generate a new API key")
    print()
    
    print("2️⃣  CONFIGURE YOUR ENVIRONMENT")
    print("   Option A - Environment Variable (Recommended):")
    print("   export PERPLEXITY_API_KEY='your-api-key-here'")
    print()
    print("   Option B - Create .env file:")
    print("   • Copy .env.example to .env")
    print("   • Edit .env and add your API key")
    print("   • PERPLEXITY_API_KEY=your-api-key-here")
    print()
    
    print("3️⃣  VERIFY YOUR SETUP")
    print("   • Run the application again")
    print("   • The system will validate your API key")
    print("   • You should see a ✅ success message")
    print()
    
    print("4️⃣  OPTIONAL CONFIGURATION")
    print("   • Set usage tracking: ENABLE_USAGE_TRACKING=true")
    print("   • Set cost alerts: COST_ALERT_THRESHOLD=10.00")
    print("   • Adjust API timeout: API_TIMEOUT=30")
    print()
    
    print("💡 TROUBLESHOOTING:")
    print("   • Ensure your API key starts with 'pplx-'")
    print("   • Check your internet connection")
    print("   • Verify your Perplexity account has API access")
    print("   • Make sure you have sufficient API credits")
    print()
    
    print("📞 NEED HELP?")
    print("   • Check the .env.example file for configuration options")
    print("   • Ensure all required dependencies are installed")
    print("   • Verify your Python environment is properly set up")
    print()
    
    print("=" * 70)

def validate_api_key(api_key: str) -> bool:
    """
    Check Perplexity API key validity with comprehensive validation
    
    Args:
        api_key: The API key to validate
        
    Returns:
        True if the API key appears to be valid, False otherwise
    """
    if not api_key or not isinstance(api_key, str):
        return False
    
    # Remove any whitespace
    api_key = api_key.strip()
    
    # Basic format validation - Perplexity API keys typically start with 'pplx-'
    if not api_key.startswith('pplx-'):
        return False
    
    # Check minimum length (typical API keys are longer than 20 characters)
    if len(api_key) < 20:
        return False
    
    # Check for reasonable maximum length (API keys shouldn't be extremely long)
    if len(api_key) > 200:
        return False
    
    # Check for valid characters (API keys typically contain alphanumeric and some special chars)
    import re
    if not re.match(r'^pplx-[a-zA-Z0-9_\-]+$', api_key):
        return False
    
    # Test API key with a minimal request (with enhanced error handling)
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'Resume-Matcher-AI/1.0'
        }
        
        # Make a minimal test request to validate the key
        test_payload = {
            'model': 'sonar',
            'messages': [{'role': 'user', 'content': 'test'}],
            'max_tokens': 1
        }
        
        response = requests.post(
            'https://api.perplexity.ai/chat/completions',
            headers=headers,
            json=test_payload,
            timeout=10
        )
        
        # Detailed status code handling
        if response.status_code == 200:
            return True
        elif response.status_code == 401:
            # Unauthorized - invalid API key
            return False
        elif response.status_code == 403:
            # Forbidden - might be valid key but no permissions or billing issue
            # We'll consider this as valid key but with account issues
            return True
        elif response.status_code == 429:
            # Rate limited - key is valid but hitting limits
            return True
        elif response.status_code >= 500:
            # Server errors - assume key is valid, server issue
            return True
        else:
            # Other status codes - assume key is valid for now
            return True
        
    except requests.exceptions.Timeout:
        # Timeout doesn't mean the key is invalid
        return True
    except requests.exceptions.ConnectionError:
        # Connection issues don't mean the key is invalid
        return True
    except requests.exceptions.SSLError:
        # SSL issues don't mean the key is invalid
        return True
    except requests.RequestException:
        # Other network issues don't mean the key is invalid
        return True
    except Exception:
        # Any other unexpected error - assume key might be valid
        return True

def format_prompt(resume_text: str, jd_text: str) -> str:
    """Create optimized prompts for Perplexity API integration with enhanced token efficiency"""
    # Clean and truncate texts to fit within token limits
    resume_text = _clean_text_for_prompt(resume_text)
    jd_text = _clean_text_for_prompt(jd_text)
    
    # Enhanced truncation with intelligent content preservation
    max_resume_chars = 6000  # Reduced from 8000 to ~1500 tokens for cost optimization
    max_jd_chars = 3000      # Reduced from 4000 to ~750 tokens for cost optimization
    
    # Smart truncation that preserves key sections
    resume_text = _smart_truncate_resume(resume_text, max_resume_chars)
    jd_text = _smart_truncate_jd(jd_text, max_jd_chars)
    
    prompt = f"""You are an expert HR analyst. Analyze the compatibility between this resume and job description.

RESUME:
{resume_text}

JOB DESCRIPTION:
{jd_text}

Please provide a detailed analysis in the following JSON format:
{{
    "compatibility_score": <integer 0-100>,
    "matching_skills": [<list of skills found in both documents with exact text from both>],
    "missing_skills": [<list of skills in JD but not in resume>],
    "skill_gaps": {{
        "Critical": [<skills absolutely essential for the role, mentioned frequently or emphasized in JD>],
        "Important": [<skills that would significantly strengthen candidacy>],
        "Nice-to-have": [<skills that are beneficial but not essential>]
    }},
    "suggestions": [<list of 3-5 specific actionable recommendations with exact phrases to add>],
    "analysis_summary": "<brief explanation of the score and key findings>"
}}

ANALYSIS REQUIREMENTS:
1. For matching_skills: Show exact text from both resume and job description
2. For skill_gaps: Prioritize by frequency and emphasis in the job description
3. For suggestions: Be specific and include recommended phrases or sections to add
4. If score > 70%: Focus on optimization suggestions rather than major changes
5. If no missing skills: Leave skill_gaps categories empty (will display "All key skills are present")

Focus on:
1. Technical skills, soft skills, and experience alignment
2. Industry-specific knowledge and certifications
3. Role requirements and responsibilities match
4. Career progression and experience level fit
5. Keywords and terminology usage

SUGGESTION GUIDELINES:
- Include specific phrases like "Led cross-functional teams" or "Implemented solutions that resulted in"
- Recommend specific resume sections to add (e.g., "Core Competencies", "Technical Proficiencies")
- Focus on adding missing skills, improving keyword usage, and enhancing experience descriptions
- Provide at least 3 actionable recommendations
- For strong matches (70%+), suggest optimizations rather than major overhauls"""
    
    return prompt


def handle_rate_limits(response: requests.Response) -> None:
    """Manage API rate limiting"""
    if response.status_code == 429:
        # Extract retry-after header if available
        retry_after = response.headers.get('Retry-After', '60')
        try:
            wait_time = int(retry_after)
        except ValueError:
            wait_time = 60
        
        raise Exception(f"Rate limit exceeded. Please wait {wait_time} seconds before retrying.")
    
    elif response.status_code == 401:
        raise Exception("Invalid API key. Please check your PERPLEXITY_API_KEY environment variable.")
    
    elif response.status_code >= 500:
        raise Exception("Perplexity API server error. Please try again later.")
    
    elif response.status_code != 200:
        raise Exception(f"API request failed with status {response.status_code}: {response.text}")


def get_match_category(score: int) -> str:
    """Categorize match score into Poor/Moderate/Strong"""
    if score < 30:
        return "Poor Match"
    elif score <= 70:
        return "Moderate Match"
    else:
        return "Strong Match"


def _clean_text_for_prompt(text: str) -> str:
    """Clean text for use in API prompts"""
    if not text:
        return ""
    
    # Remove excessive whitespace and normalize line breaks
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters that might interfere with JSON parsing
    text = re.sub(r'[^\w\s\-.,;:()\[\]{}/@#$%&*+=<>?!"]', ' ', text)
    
    # Remove excessive punctuation
    text = re.sub(r'[.]{3,}', '...', text)
    text = re.sub(r'[-]{3,}', '---', text)
    
    return text.strip()


def _smart_truncate_resume(resume_text: str, max_chars: int) -> str:
    """
    Intelligently truncate resume text while preserving key sections
    
    Args:
        resume_text: The resume text to truncate
        max_chars: Maximum character limit
        
    Returns:
        Truncated resume text with key sections preserved
    """
    if len(resume_text) <= max_chars:
        return resume_text
    
    # Define key sections to prioritize (case-insensitive)
    key_sections = [
        r'(experience|work experience|employment|professional experience)[\s\S]*?(?=\n[A-Z]|\n\n|$)',
        r'(skills|technical skills|core competencies|expertise)[\s\S]*?(?=\n[A-Z]|\n\n|$)',
        r'(education|academic background)[\s\S]*?(?=\n[A-Z]|\n\n|$)',
        r'(summary|professional summary|profile|objective)[\s\S]*?(?=\n[A-Z]|\n\n|$)'
    ]
    
    # Try to extract key sections
    preserved_sections = []
    remaining_text = resume_text
    
    for section_pattern in key_sections:
        matches = re.finditer(section_pattern, remaining_text, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            section_text = match.group(0).strip()
            if section_text and len(section_text) > 50:  # Only preserve substantial sections
                preserved_sections.append(section_text)
                # Remove this section from remaining text to avoid duplication
                remaining_text = remaining_text.replace(section_text, '', 1)
    
    # Combine preserved sections
    result = '\n\n'.join(preserved_sections)
    
    # If we still have space, add some of the remaining text
    if len(result) < max_chars * 0.8:  # Use 80% for preserved sections
        remaining_space = max_chars - len(result) - 10  # Leave some buffer
        if remaining_space > 100 and remaining_text.strip():
            # Add the beginning of remaining text
            additional_text = remaining_text.strip()[:remaining_space]
            # Try to end at a sentence boundary
            last_period = additional_text.rfind('.')
            if last_period > remaining_space * 0.7:  # If we can find a good break point
                additional_text = additional_text[:last_period + 1]
            result += '\n\n' + additional_text + '...'
    
    # Final truncation if still too long
    if len(result) > max_chars:
        result = result[:max_chars - 3] + '...'
    
    return result


def _smart_truncate_jd(jd_text: str, max_chars: int) -> str:
    """
    Intelligently truncate job description while preserving key information
    
    Args:
        jd_text: The job description text to truncate
        max_chars: Maximum character limit
        
    Returns:
        Truncated job description with key information preserved
    """
    if len(jd_text) <= max_chars:
        return jd_text
    
    # Define key sections to prioritize in job descriptions
    key_patterns = [
        r'(requirements?|qualifications?|required skills?)[\s\S]*?(?=\n[A-Z]|\n\n|$)',
        r'(responsibilities?|duties|role|what you.ll do)[\s\S]*?(?=\n[A-Z]|\n\n|$)',
        r'(skills?|technical skills?|must have)[\s\S]*?(?=\n[A-Z]|\n\n|$)',
        r'(experience|years? of experience)[\s\S]*?(?=\n[A-Z]|\n\n|$)'
    ]
    
    # Try to extract key sections
    preserved_sections = []
    remaining_text = jd_text
    
    for pattern in key_patterns:
        matches = re.finditer(pattern, remaining_text, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            section_text = match.group(0).strip()
            if section_text and len(section_text) > 30:  # Only preserve substantial sections
                preserved_sections.append(section_text)
                remaining_text = remaining_text.replace(section_text, '', 1)
    
    # Combine preserved sections
    result = '\n\n'.join(preserved_sections)
    
    # If we still have space, add job title and company info from the beginning
    if len(result) < max_chars * 0.7:  # Use 70% for key sections
        remaining_space = max_chars - len(result) - 10
        if remaining_space > 50:
            # Add the beginning of the original text (likely contains title/company)
            beginning_text = jd_text[:remaining_space]
            # Try to end at a sentence or line boundary
            last_period = beginning_text.rfind('.')
            last_newline = beginning_text.rfind('\n')
            break_point = max(last_period, last_newline)
            
            if break_point > remaining_space * 0.6:
                beginning_text = beginning_text[:break_point + 1]
            
            # Only add if it's not already in preserved sections
            if beginning_text.strip() not in result:
                result = beginning_text + '\n\n' + result
    
    # Final truncation if still too long
    if len(result) > max_chars:
        result = result[:max_chars - 3] + '...'
    
    return result


def optimize_api_payload(payload: Dict) -> Dict:
    """
    Optimize API payload to reduce token usage and cost
    
    Args:
        payload: Original API payload
        
    Returns:
        Optimized payload with reduced token usage
    """
    optimized_payload = payload.copy()
    
    # Reduce max_tokens for cost optimization while maintaining quality
    current_max_tokens = optimized_payload.get('max_tokens', 4000)
    optimized_max_tokens = min(current_max_tokens, 3000)  # Reduced from 4000 to 3000
    optimized_payload['max_tokens'] = optimized_max_tokens
    
    # Optimize temperature for more focused responses (reduces need for retries)
    optimized_payload['temperature'] = 0.1  # Very low for consistent, focused responses
    
    # Optimize top_p for better token efficiency
    optimized_payload['top_p'] = 0.8  # Slightly reduced from 0.9 for more focused responses
    
    # Use more efficient model if available
    current_model = optimized_payload.get('model', '')
    if 'pro' in current_model:
        # Switch to basic model for cost optimization while maintaining quality
        optimized_payload['model'] = 'sonar'
    
    return optimized_payload


def estimate_token_usage(text: str) -> int:
    """
    Estimate token usage for text input
    
    Args:
        text: Input text
        
    Returns:
        Estimated number of tokens
    """
    if not text:
        return 0
    
    # Rough estimation: 1 token ≈ 4 characters for English text
    # This is a conservative estimate that tends to overestimate slightly
    base_estimate = len(text) // 4
    
    # Adjust for common patterns that affect tokenization
    # More spaces and punctuation typically mean more tokens
    space_count = text.count(' ')
    punctuation_count = len(re.findall(r'[.,;:!?()[\]{}"\'-]', text))
    
    # Add adjustment for spaces and punctuation
    adjustment = (space_count + punctuation_count) * 0.1
    
    return int(base_estimate + adjustment)


def get_cost_optimization_stats() -> Dict[str, Any]:
    """
    Get statistics about cost optimization effectiveness
    
    Returns:
        Dictionary containing optimization statistics
    """
    config = load_config()
    log_file = config.get('usage_log_file', 'usage_log.json')
    log_path = Path(log_file)
    
    stats = {
        'total_tokens_saved': 0,
        'total_cost_saved': 0.0,
        'average_tokens_per_request': 0,
        'optimization_effectiveness': 0.0,
        'recommendations': []
    }
    
    if not log_path.exists():
        return stats
    
    try:
        with open(log_path, 'r') as f:
            records = json.load(f)
        
        if not records:
            return stats
        
        # Calculate average tokens per request
        successful_records = [r for r in records if r.get('success', False)]
        if successful_records:
            total_tokens = sum(r.get('tokens_used', 0) for r in successful_records)
            stats['average_tokens_per_request'] = total_tokens / len(successful_records)
        
        # Estimate tokens saved through optimization (compared to unoptimized baseline)
        baseline_tokens_per_request = 5000  # Estimated baseline without optimization
        if stats['average_tokens_per_request'] > 0:
            tokens_saved_per_request = max(0, baseline_tokens_per_request - stats['average_tokens_per_request'])
            stats['total_tokens_saved'] = tokens_saved_per_request * len(successful_records)
            stats['total_cost_saved'] = (stats['total_tokens_saved'] / 1000) * 0.001
            stats['optimization_effectiveness'] = (tokens_saved_per_request / baseline_tokens_per_request) * 100
        
        # Generate recommendations based on usage patterns
        if stats['average_tokens_per_request'] > 3500:
            stats['recommendations'].append("Consider further prompt optimization to reduce token usage")
        if stats['average_tokens_per_request'] > 4000:
            stats['recommendations'].append("Input texts may be too long - consider more aggressive truncation")
        if len(successful_records) > 50 and stats['total_cost_saved'] < 0.05:
            stats['recommendations'].append("Optimization impact is minimal - consider reviewing truncation strategies")
        
        if not stats['recommendations']:
            stats['recommendations'].append("Token usage is well optimized")
            
    except Exception as e:
        # Return empty stats if file can't be read
        pass
    
    return stats


def display_performance_report() -> None:
    """
    Display a comprehensive performance and cost report
    """
    print("=" * 70)
    print("📊 RESUME MATCHER AI - PERFORMANCE REPORT")
    print("=" * 70)
    
    # Usage statistics
    usage_stats = get_usage_statistics(days=30)
    print(f"\n📈 USAGE STATISTICS (Last 30 Days)")
    print(f"{'─' * 40}")
    print(f"Total API Calls: {usage_stats['total_calls']:,}")
    print(f"Successful Calls: {usage_stats['successful_calls']:,}")
    print(f"Failed Calls: {usage_stats['failed_calls']:,}")
    
    if usage_stats['total_calls'] > 0:
        success_rate = (usage_stats['successful_calls'] / usage_stats['total_calls']) * 100
        print(f"Success Rate: {success_rate:.1f}%")
    
    print(f"Total Tokens Used: {usage_stats['total_tokens']:,}")
    print(f"Total Cost: ${usage_stats['total_cost']:.4f}")
    print(f"Average Processing Time: {usage_stats['average_processing_time']:.2f}s")
    
    if usage_stats['successful_calls'] > 0:
        avg_tokens = usage_stats['total_tokens'] / usage_stats['successful_calls']
        avg_cost = usage_stats['total_cost'] / usage_stats['successful_calls']
        print(f"Average Tokens per Call: {avg_tokens:.0f}")
        print(f"Average Cost per Call: ${avg_cost:.4f}")
    
    # Cost optimization statistics
    opt_stats = get_cost_optimization_stats()
    print(f"\n💰 COST OPTIMIZATION")
    print(f"{'─' * 40}")
    print(f"Estimated Tokens Saved: {opt_stats['total_tokens_saved']:,}")
    print(f"Estimated Cost Saved: ${opt_stats['total_cost_saved']:.4f}")
    print(f"Optimization Effectiveness: {opt_stats['optimization_effectiveness']:.1f}%")
    
    # Performance benchmarks
    print(f"\n⚡ PERFORMANCE BENCHMARKS")
    print(f"{'─' * 40}")
    
    if usage_stats['average_processing_time'] > 0:
        if usage_stats['average_processing_time'] < 10:
            perf_rating = "🚀 EXCELLENT"
        elif usage_stats['average_processing_time'] < 20:
            perf_rating = "⚡ GOOD"
        elif usage_stats['average_processing_time'] < 30:
            perf_rating = "⏱️  ACCEPTABLE"
        else:
            perf_rating = "🐌 NEEDS IMPROVEMENT"
        
        print(f"Processing Speed: {perf_rating}")
        print(f"Target: <30 seconds (Requirement 1.3)")
        print(f"Current: {usage_stats['average_processing_time']:.2f} seconds")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS")
    print(f"{'─' * 40}")
    
    recommendations = opt_stats.get('recommendations', [])
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
    
    # Additional performance tips
    if usage_stats['average_processing_time'] > 25:
        print(f"• Consider using shorter resume or job description texts")
        print(f"• Check your internet connection speed")
    
    if usage_stats['total_cost'] > 5.0:
        print(f"• Monitor your monthly spending - you're approaching higher usage")
        print(f"• Consider implementing more aggressive text truncation")
    
    if usage_stats['failed_calls'] > usage_stats['successful_calls'] * 0.1:
        print(f"• High failure rate detected - check your API key and network")
        print(f"• Review error logs for common issues")
    
    print(f"\n🎯 SYSTEM HEALTH")
    print(f"{'─' * 40}")
    
    # Overall health score
    health_score = 100
    
    if usage_stats['total_calls'] > 0:
        success_rate = (usage_stats['successful_calls'] / usage_stats['total_calls']) * 100
        if success_rate < 90:
            health_score -= (90 - success_rate)
    
    if usage_stats['average_processing_time'] > 30:
        health_score -= 20
    elif usage_stats['average_processing_time'] > 20:
        health_score -= 10
    
    if opt_stats['optimization_effectiveness'] < 20:
        health_score -= 10
    
    health_score = max(0, min(100, health_score))
    
    if health_score >= 90:
        health_status = "🟢 EXCELLENT"
    elif health_score >= 75:
        health_status = "🟡 GOOD"
    elif health_score >= 60:
        health_status = "🟠 FAIR"
    else:
        health_status = "🔴 NEEDS ATTENTION"
    
    print(f"Overall Health: {health_status} ({health_score:.0f}/100)")
    
    print("=" * 70)


def cleanup_old_usage_logs(days_to_keep: int = 90) -> None:
    """
    Clean up old usage log entries to prevent file from growing too large
    
    Args:
        days_to_keep: Number of days of logs to retain
    """
    config = load_config()
    log_file = config.get('usage_log_file', 'usage_log.json')
    log_path = Path(log_file)
    
    if not log_path.exists():
        return
    
    try:
        with open(log_path, 'r') as f:
            records = json.load(f)
        
        if not records:
            return
        
        # Filter records to keep only recent ones
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        filtered_records = []
        
        for record in records:
            try:
                record_time = datetime.fromisoformat(record['timestamp'])
                if record_time >= cutoff_date:
                    filtered_records.append(record)
            except (ValueError, KeyError):
                # Keep records with invalid timestamps to be safe
                filtered_records.append(record)
        
        # Save filtered records back to file
        if len(filtered_records) < len(records):
            with open(log_path, 'w') as f:
                json.dump(filtered_records, f, indent=2)
            
            removed_count = len(records) - len(filtered_records)
            print(f"🧹 Cleaned up {removed_count} old usage log entries")
        
    except Exception as e:
        # Silently fail if cleanup fails - don't break the main application
        pass