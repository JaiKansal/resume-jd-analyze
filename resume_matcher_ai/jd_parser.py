"""
Job description parsing and processing functionality
"""
import re
from typing import Dict, List, Any, Optional
from .utils import JobDescription


def parse_jd_text(jd_text: str) -> JobDescription:
    """
    Clean and structure JD content into a JobDescription object
    
    Args:
        jd_text: Raw job description text
        
    Returns:
        JobDescription object with structured data
        
    Raises:
        ValueError: If job description is invalid or too short
        TypeError: If input is not a string
    """
    # Comprehensive input validation
    _validate_job_description_input(jd_text)
    
    # Clean the text
    cleaned_text = _clean_jd_text(jd_text)
    
    # Extract job title
    title = _extract_job_title(cleaned_text)
    
    # Extract requirements
    requirements = extract_requirements(cleaned_text)
    
    # Extract skills and categorize them
    all_skills = _extract_skills_from_text(cleaned_text)
    categorized_skills = categorize_skills(all_skills)
    
    # Extract experience level
    experience_level = _extract_experience_level(cleaned_text)
    
    # Extract key responsibilities
    responsibilities = _extract_responsibilities(cleaned_text)
    
    return JobDescription(
        raw_text=jd_text,
        title=title,
        requirements=requirements,
        technical_skills=categorized_skills.get('technical', []),
        soft_skills=categorized_skills.get('soft', []),
        experience_level=experience_level,
        key_responsibilities=responsibilities
    )


def extract_requirements(jd_text: str) -> List[str]:
    """
    Identify key requirements and skills from job description
    
    Args:
        jd_text: Job description text
        
    Returns:
        List of extracted requirements
    """
    if not jd_text:
        return []
    
    requirements = []
    
    # Common requirement section headers - improved patterns
    requirement_patterns = [
        r'(?i)required\s+skills?:\s*\n(.+?)(?=\n\s*[A-Z][^:]*:|$)',
        r'(?i)requirements?:\s*\n(.+?)(?=\n\s*[A-Z][^:]*:|$)',
        r'(?i)must\s+have:\s*\n(.+?)(?=\n\s*[A-Z][^:]*:|$)',
        r'(?i)essential\s+(?:skills?|requirements?):\s*\n(.+?)(?=\n\s*[A-Z][^:]*:|$)',
        r'(?i)minimum\s+(?:requirements?|qualifications?):\s*\n(.+?)(?=\n\s*[A-Z][^:]*:|$)'
    ]
    
    # Extract from requirement sections
    for pattern in requirement_patterns:
        matches = re.findall(pattern, jd_text, re.DOTALL | re.MULTILINE)
        for match in matches:
            req_items = _parse_bullet_points(match)
            requirements.extend(req_items)
    
    # Extract experience requirements
    exp_patterns = [
        r'(\d+\+?\s*years?\s+(?:of\s+)?experience[^.]*)',
        r'(minimum\s+of\s+\d+\s+years?[^.]*)',
        r'(\d+\+?\s*years?\s+in[^.]*)',
        r'(bachelor\'?s?\s+degree[^.]*)',
        r'(master\'?s?\s+degree[^.]*)',
        r'(phd\s+(?:degree)?[^.]*)'
    ]
    
    for pattern in exp_patterns:
        matches = re.findall(pattern, jd_text, re.IGNORECASE)
        requirements.extend([match.strip() for match in matches])
    
    # Clean and deduplicate requirements
    cleaned_requirements = []
    seen = set()
    
    for req in requirements:
        req = req.strip()
        if req and len(req) > 5 and req.lower() not in seen:
            cleaned_requirements.append(req)
            seen.add(req.lower())
    
    return cleaned_requirements[:20]  # Limit to top 20 requirements


def categorize_skills(skills: List[str]) -> Dict[str, List[str]]:
    """
    Separate technical vs soft skills
    
    Args:
        skills: List of skills to categorize
        
    Returns:
        Dictionary with 'technical' and 'soft' skill lists
    """
    if not skills:
        return {'technical': [], 'soft': []}
    
    # Technical skill keywords and patterns
    technical_keywords = {
        # Programming languages
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust',
        'swift', 'kotlin', 'scala', 'r', 'matlab', 'sql', 'html', 'css', 'sass', 'less',
        
        # Frameworks and libraries
        'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'spring', 'laravel',
        'rails', 'asp.net', '.net', 'jquery', 'bootstrap', 'tailwind', 'next.js', 'nuxt.js',
        
        # Databases
        'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'cassandra', 'dynamodb',
        'oracle', 'sqlite', 'mariadb', 'neo4j', 'influxdb',
        
        # Cloud and DevOps
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'gitlab', 'github', 'terraform',
        'ansible', 'chef', 'puppet', 'vagrant', 'nginx', 'apache', 'linux', 'unix', 'bash',
        
        # Tools and technologies
        'git', 'svn', 'jira', 'confluence', 'slack', 'postman', 'swagger', 'graphql', 'rest',
        'api', 'microservices', 'ci/cd', 'tdd', 'bdd', 'agile', 'scrum', 'kanban',
        
        # Testing
        'jest', 'mocha', 'chai', 'cypress', 'selenium', 'junit', 'pytest', 'rspec',
        
        # Data and Analytics
        'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'spark', 'hadoop', 'kafka',
        'tableau', 'power bi', 'excel', 'powerpoint'
    }
    
    # Soft skill keywords
    soft_keywords = {
        'communication', 'leadership', 'teamwork', 'collaboration', 'problem-solving',
        'analytical', 'creative', 'innovative', 'adaptable', 'flexible', 'organized',
        'detail-oriented', 'time management', 'project management', 'mentoring',
        'presentation', 'negotiation', 'customer service', 'interpersonal', 'emotional intelligence',
        'critical thinking', 'decision making', 'conflict resolution', 'multitasking',
        'self-motivated', 'proactive', 'reliable', 'accountable', 'initiative'
    }
    
    technical_skills = []
    soft_skills = []
    
    for skill in skills:
        skill_lower = skill.lower().strip()
        
        # Check if it's a technical skill
        is_technical = False
        for tech_keyword in technical_keywords:
            if tech_keyword in skill_lower or skill_lower in tech_keyword:
                is_technical = True
                break
        
        # Check for technical patterns
        if not is_technical:
            technical_patterns = [
                r'\b\d+\+?\s*years?\b',  # "3+ years"
                r'\bapi\b', r'\bsdk\b', r'\bide\b', r'\borm\b', r'\bmvc\b',
                r'\bui/ux\b', r'\bfrontend\b', r'\bbackend\b', r'\bfull.?stack\b',
                r'\bdatabase\b', r'\bcloud\b', r'\bdevops\b', r'\bmobile\b',
                r'\bweb\s+development\b', r'\bsoftware\s+development\b',
                r'\bversion\s+control\b', r'\bunit\s+testing\b'
            ]
            
            for pattern in technical_patterns:
                if re.search(pattern, skill_lower):
                    is_technical = True
                    break
        
        if is_technical:
            technical_skills.append(skill)
        else:
            # Check if it's a soft skill
            is_soft = False
            for soft_keyword in soft_keywords:
                if soft_keyword in skill_lower or skill_lower in soft_keyword:
                    is_soft = True
                    break
            
            # Check for soft skill patterns
            if not is_soft:
                soft_patterns = [
                    r'\bstrong\b', r'\bexcellent\b', r'\beffective\b',
                    r'\bability\s+to\b', r'\bskills?\s+in\b',
                    r'\bexperience\s+working\s+with\b'
                ]
                
                for pattern in soft_patterns:
                    if re.search(pattern, skill_lower):
                        is_soft = True
                        break
            
            if is_soft:
                soft_skills.append(skill)
            else:
                # Default ambiguous skills to technical if they contain certain indicators
                if any(indicator in skill_lower for indicator in ['experience', 'knowledge', 'proficiency', 'familiarity']):
                    technical_skills.append(skill)
                else:
                    soft_skills.append(skill)
    
    return {
        'technical': technical_skills,
        'soft': soft_skills
    }


def _clean_jd_text(jd_text: str) -> str:
    """Clean and normalize job description text"""
    if not jd_text:
        return ""
    
    # Remove excessive whitespace but preserve line breaks for section parsing
    text = re.sub(r'[ \t]+', ' ', jd_text.strip())
    
    # Normalize line breaks for better parsing
    text = re.sub(r'\r\n', '\n', text)
    text = re.sub(r'\r', '\n', text)
    
    # Remove excessive punctuation
    text = re.sub(r'[.]{3,}', '...', text)
    text = re.sub(r'[-]{3,}', '---', text)
    
    return text


def _extract_job_title(jd_text: str) -> str:
    """Extract job title from job description"""
    if not jd_text:
        return "Unknown Position"
    
    # Common patterns for job titles
    title_patterns = [
        r'^([^:\n]+?)(?:\s*-\s*[^:\n]+)?(?:\n|$)',  # First line before dash or newline
        r'(?i)(?:job\s+title|position|role):\s*([^\n]+)',
        r'(?i)we\s+are\s+(?:seeking|looking\s+for|hiring)\s+(?:a|an)\s+([^.]+?)(?:\s+to\s+join|\.|$)',
        r'(?i)([A-Z][^:\n]*(?:engineer|developer|manager|analyst|scientist|specialist|coordinator|director|lead))',
    ]
    
    for pattern in title_patterns:
        match = re.search(pattern, jd_text, re.MULTILINE)
        if match:
            title = match.group(1).strip()
            # Clean up the title
            title = re.sub(r'\s+', ' ', title)
            title = re.sub(r'^(job\s+title|position|role):\s*', '', title, flags=re.IGNORECASE)
            # Remove common prefixes that aren't part of the title
            title = re.sub(r'^(we\s+are\s+seeking\s+(?:a|an)\s+)', '', title, flags=re.IGNORECASE)
            if len(title) > 3 and len(title) < 100:
                return title
    
    # Fallback: try to find a title-like string in the first few lines
    lines = jd_text.split('\n')[:5]
    for line in lines:
        line = line.strip()
        if (len(line) > 3 and len(line) < 100 and 
            not line.lower().startswith(('company', 'location', 'department', 'we are', 'job description'))):
            return line
    
    return "Unknown Position"


def _extract_experience_level(jd_text: str) -> str:
    """Extract experience level requirements"""
    if not jd_text:
        return "Not specified"
    
    # Patterns for experience levels - prioritize years of experience over degrees
    exp_patterns = [
        (r'(\d+)\+?\s*years?\s+(?:of\s+)?experience', lambda m: f"{m.group(1)}+ years"),
        (r'minimum\s+of\s+(\d+)\s+years?', lambda m: f"{m.group(1)}+ years"),
        (r'(\d+)-(\d+)\s+years?', lambda m: f"{m.group(1)}-{m.group(2)} years"),
        (r'(?i)(entry.level|junior)', lambda m: "Entry Level"),
        (r'(?i)(senior|lead)', lambda m: "Senior Level"),
        (r'(?i)(mid.level|intermediate)', lambda m: "Mid Level"),
        (r'(?i)phd\s+(?:degree)?', lambda m: "PhD Degree"),
        (r'(?i)master\'?s?\s+degree', lambda m: "Master's Degree"),
        (r'(?i)bachelor\'?s?\s+degree', lambda m: "Bachelor's Degree"),
    ]
    
    for pattern, formatter in exp_patterns:
        match = re.search(pattern, jd_text)
        if match:
            return formatter(match)
    
    return "Not specified"


def _extract_responsibilities(jd_text: str) -> List[str]:
    """Extract key responsibilities from job description"""
    if not jd_text:
        return []
    
    responsibilities = []
    
    # Common responsibility section headers - improved pattern to handle multiline sections
    resp_patterns = [
        r'(?i)(?:key\s+)?responsibilities:\s*\n(.+?)(?=\n\s*[A-Z][a-z\s]+:|\n\s*$|$)',
        r'(?i)duties:\s*\n(.+?)(?=\n\s*[A-Z][a-z\s]+:|\n\s*$|$)',
        r'(?i)what\s+you\'?ll\s+do:\s*\n(.+?)(?=\n\s*[A-Z][a-z\s]+:|\n\s*$|$)',
        r'(?i)job\s+duties:\s*\n(.+?)(?=\n\s*[A-Z][a-z\s]+:|\n\s*$|$)',
        r'(?i)role\s+overview:\s*\n(.+?)(?=\n\s*[A-Z][a-z\s]+:|\n\s*$|$)'
    ]
    
    for pattern in resp_patterns:
        matches = re.findall(pattern, jd_text, re.DOTALL | re.MULTILINE)
        for match in matches:
            resp_items = _parse_bullet_points(match)
            responsibilities.extend(resp_items)
    
    # Clean and limit responsibilities
    cleaned_responsibilities = []
    for resp in responsibilities:
        resp = resp.strip()
        if resp and len(resp) > 10:
            cleaned_responsibilities.append(resp)
    
    return cleaned_responsibilities[:10]  # Limit to top 10 responsibilities


def _extract_skills_from_text(jd_text: str) -> List[str]:
    """Extract all skills mentioned in the job description"""
    if not jd_text:
        return []
    
    skills = []
    
    # Extract from skills sections - improved patterns
    skill_patterns = [
        r'(?i)required\s+skills?:\s*\n(.+?)(?=\n\s*[A-Z][^:]*:|$)',
        r'(?i)preferred\s+skills?:\s*\n(.+?)(?=\n\s*[A-Z][^:]*:|$)',
        r'(?i)technical\s+skills?:\s*\n(.+?)(?=\n\s*[A-Z][^:]*:|$)',
        r'(?i)qualifications?:\s*\n(.+?)(?=\n\s*[A-Z][^:]*:|$)',
        r'(?i)must\s+have:\s*\n(.+?)(?=\n\s*[A-Z][^:]*:|$)',
        r'(?i)nice\s+to\s+have:\s*\n(.+?)(?=\n\s*[A-Z][^:]*:|$)',
        r'(?i)technologies?:\s*\n(.+?)(?=\n\s*[A-Z][^:]*:|$)'
    ]
    
    for pattern in skill_patterns:
        matches = re.findall(pattern, jd_text, re.DOTALL | re.MULTILINE)
        for match in matches:
            skill_items = _parse_bullet_points(match)
            skills.extend(skill_items)
    
    # Extract skills from requirements and responsibilities
    requirements = extract_requirements(jd_text)
    for req in requirements:
        # Extract technology names and skills from requirements
        tech_matches = re.findall(r'\b([A-Z][a-z]*(?:\.[a-z]+)?|[A-Z]{2,})\b', req)
        skills.extend(tech_matches)
    
    # Also extract common technology names directly from the text
    # This helps with unstructured job descriptions
    tech_patterns = [
        r'\b(Python|Java|JavaScript|TypeScript|C\+\+|C#|PHP|Ruby|Go|Rust|Swift|Kotlin)\b',
        r'\b(React|Angular|Vue|Node\.js|Express|Django|Flask|Spring|Laravel)\b',
        r'\b(MySQL|PostgreSQL|MongoDB|Redis|Docker|Kubernetes|AWS|Azure|GCP)\b',
        r'\b(Git|HTML|CSS|SQL|API|REST|GraphQL|JSON|XML)\b'
    ]
    
    for pattern in tech_patterns:
        matches = re.findall(pattern, jd_text, re.IGNORECASE)
        skills.extend(matches)
    
    # Clean and deduplicate skills
    cleaned_skills = []
    seen = set()
    
    for skill in skills:
        skill = skill.strip()
        if skill and len(skill) > 2 and skill.lower() not in seen:
            cleaned_skills.append(skill)
            seen.add(skill.lower())
    
    return cleaned_skills


def _validate_job_description_input(jd_text: str) -> None:
    """
    Comprehensive validation of job description input
    
    Args:
        jd_text: Job description text to validate
        
    Raises:
        TypeError: If input is not a string
        ValueError: If job description is invalid with specific reasons
    """
    # Check if input is provided
    if jd_text is None:
        raise ValueError("Job description cannot be None. Please provide job description text.")
    
    # Check if input is a string
    if not isinstance(jd_text, str):
        raise TypeError(
            f"Job description must be a string, got {type(jd_text).__name__}. "
            f"Please provide the job description as text."
        )
    
    # Check if input is empty or only whitespace
    if not jd_text.strip():
        raise ValueError(
            "Job description cannot be empty or contain only whitespace. "
            "Please provide a detailed job description with requirements, responsibilities, and qualifications."
        )
    
    # Check minimum length
    cleaned_text = jd_text.strip()
    if len(cleaned_text) < 50:
        raise ValueError(
            f"Job description is too short ({len(cleaned_text)} characters, minimum 50 required). "
            f"Please provide a more detailed job description that includes:\n"
            f"• Job title and role overview\n"
            f"• Key responsibilities\n"
            f"• Required skills and qualifications\n"
            f"• Experience requirements"
        )
    
    # Check for reasonable maximum length (to prevent API issues)
    max_length = 50000  # 50K characters should be more than enough
    if len(cleaned_text) > max_length:
        raise ValueError(
            f"Job description is too long ({len(cleaned_text)} characters, maximum {max_length} allowed). "
            f"Please provide a more concise job description or split it into multiple analyses."
        )
    
    # Check for meaningful content (not just repeated characters or gibberish)
    words = cleaned_text.split()
    if len(words) < 10:
        raise ValueError(
            f"Job description contains too few words ({len(words)} words, minimum 10 required). "
            f"Please provide a more detailed job description."
        )
    
    # Check for reasonable word length distribution (detect gibberish)
    avg_word_length = sum(len(word) for word in words) / len(words)
    if avg_word_length < 2 or avg_word_length > 20:
        raise ValueError(
            "Job description appears to contain invalid content. "
            "Please ensure you've pasted a real job description with proper words and sentences."
        )
    
    # Check for basic job description indicators
    jd_lower = cleaned_text.lower()
    job_indicators = [
        'job', 'position', 'role', 'responsibilities', 'requirements', 'qualifications',
        'experience', 'skills', 'candidate', 'applicant', 'hire', 'work', 'company',
        'team', 'department', 'duties', 'tasks', 'seeking', 'looking for'
    ]
    
    indicator_count = sum(1 for indicator in job_indicators if indicator in jd_lower)
    if indicator_count < 3:
        raise ValueError(
            "The text doesn't appear to be a job description. "
            "Please ensure you've pasted a complete job posting that includes job requirements, "
            "responsibilities, and qualifications."
        )
    
    # Check for suspicious patterns that might indicate copy-paste errors
    suspicious_patterns = [
        r'^[^a-zA-Z]*$',  # Only non-alphabetic characters
        r'(.)\1{20,}',    # Same character repeated 20+ times
        r'^https?://',    # Starts with URL
        r'^\d+$',         # Only numbers
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, cleaned_text):
            raise ValueError(
                "The job description appears to contain invalid or incomplete content. "
                "Please ensure you've pasted the complete job description text, not just a URL or partial content."
            )


def _parse_bullet_points(text: str) -> List[str]:
    """Parse bullet points from text sections"""
    if not text:
        return []
    
    items = []
    
    # First, try to split by newlines and clean each line
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        if line:
            # Remove bullet markers from the beginning of lines
            line = re.sub(r'^[-•*]\s*', '', line)
            line = re.sub(r'^\d+\.\s*', '', line)
            line = re.sub(r'^[a-zA-Z]\.\s*', '', line)
            if line.strip():
                cleaned_lines.append(line.strip())
    
    items = cleaned_lines
    
    # Clean items
    cleaned_items = []
    for item in items:
        # Remove trailing punctuation and clean up
        item = re.sub(r'[.,:;]+$', '', item.strip())
        if len(item) > 5:
            cleaned_items.append(item)
    
    return cleaned_items