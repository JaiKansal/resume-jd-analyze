# Usage Examples and Best Practices

This document provides comprehensive examples and best practices for using the Resume + Job Description Matcher AI effectively.

## 📚 Table of Contents

1. [Basic Usage Examples](#basic-usage-examples)
2. [Advanced Usage Patterns](#advanced-usage-patterns)
3. [API Integration Examples](#api-integration-examples)
4. [Batch Processing](#batch-processing)
5. [Cost Optimization Tips](#cost-optimization-tips)
6. [Best Practices](#best-practices)
7. [Common Use Cases](#common-use-cases)
8. [Troubleshooting Examples](#troubleshooting-examples)

## 🚀 Basic Usage Examples

### Example 1: First-Time User Setup

```bash
# 1. Set up your environment
export PERPLEXITY_API_KEY='pplx-your-api-key-here'

# 2. Run the application
python -m resume_matcher_ai.main

# 3. Follow the interactive prompts
# Enter resume path: /Users/john/Documents/resume.pdf
# Paste job description: [paste the full job posting]
```

### Example 2: Using with Different File Paths

```bash
# Absolute path
/Users/john/Documents/MyResume.pdf

# Relative path (from current directory)
./resumes/john_doe_resume.pdf

# Path with spaces (use quotes)
"/Users/john/My Documents/Resume 2024.pdf"

# Home directory shortcut
~/Documents/resume.pdf
```

### Example 3: Job Description Input Formats

**Format 1: Complete Job Posting**
```
Senior Software Engineer - Tech Startup

About the Role:
We are seeking a Senior Software Engineer to join our growing team...

Responsibilities:
• Design and develop scalable web applications
• Collaborate with cross-functional teams
• Mentor junior developers

Requirements:
• 5+ years of software development experience
• Proficiency in Python, JavaScript, and React
• Experience with AWS and Docker
• Strong problem-solving skills

Preferred Qualifications:
• Experience with Kubernetes
• Knowledge of GraphQL
• Bachelor's degree in Computer Science
```

**Format 2: Requirements-Focused**
```
Software Engineer Position

Required Skills:
- Python programming (3+ years)
- React.js and modern JavaScript
- RESTful API development
- Database design (PostgreSQL/MySQL)
- Git version control
- Agile development methodologies

Experience Requirements:
- 3-5 years in web development
- Experience with cloud platforms (AWS preferred)
- Previous startup experience is a plus
```

## 🔧 Advanced Usage Patterns

### Example 1: Programmatic Analysis

```python
#!/usr/bin/env python3
"""
Advanced programmatic usage example
"""
import os
from resume_matcher_ai.matcher import analyze_match
from resume_matcher_ai.resume_parser import extract_text_from_pdf, clean_resume_text
from resume_matcher_ai.jd_parser import parse_jd_text
from resume_matcher_ai.utils import get_usage_statistics, get_cost_optimization_stats

def analyze_resume_job_match(resume_path, job_description):
    """
    Analyze a single resume against a job description
    
    Args:
        resume_path: Path to PDF resume file
        job_description: Job description text
        
    Returns:
        Dictionary with analysis results
    """
    try:
        # Extract and clean resume text
        print(f"📄 Processing resume: {os.path.basename(resume_path)}")
        resume_text = extract_text_from_pdf(resume_path)
        cleaned_resume = clean_resume_text(resume_text)
        
        # Parse job description
        print("📋 Parsing job description...")
        jd_data = parse_jd_text(job_description)
        
        # Perform analysis
        print("🤖 Analyzing compatibility...")
        result = analyze_match(cleaned_resume, jd_data.__dict__)
        
        # Return structured results
        return {
            'success': True,
            'resume_file': os.path.basename(resume_path),
            'score': result.score,
            'category': result.match_category,
            'matching_skills': result.matching_skills,
            'missing_skills': result.missing_skills,
            'skill_gaps': result.skill_gaps,
            'suggestions': result.suggestions,
            'processing_time': result.processing_time,
            'word_count': len(cleaned_resume.split()),
            'jd_title': jd_data.title
        }
        
    except Exception as e:
        return {
            'success': False,
            'resume_file': os.path.basename(resume_path),
            'error': str(e)
        }

# Usage example
if __name__ == "__main__":
    resume_path = "sample_resume.pdf"
    job_description = """
    Senior Python Developer
    
    We are looking for an experienced Python developer...
    
    Requirements:
    - 5+ years Python experience
    - Django or Flask framework knowledge
    - PostgreSQL database experience
    - AWS cloud platform experience
    - Strong problem-solving skills
    """
    
    result = analyze_resume_job_match(resume_path, job_description)
    
    if result['success']:
        print(f"\n✅ Analysis Complete!")
        print(f"Score: {result['score']}% ({result['category']})")
        print(f"Matching Skills: {len(result['matching_skills'])}")
        print(f"Missing Skills: {len(result['missing_skills'])}")
        print(f"Processing Time: {result['processing_time']:.2f}s")
    else:
        print(f"\n❌ Analysis Failed: {result['error']}")
```

### Example 2: Resume Optimization Workflow

```python
#!/usr/bin/env python3
"""
Resume optimization workflow example
"""
import json
from datetime import datetime
from resume_matcher_ai.matcher import analyze_match
from resume_matcher_ai.resume_parser import extract_text_from_pdf, clean_resume_text
from resume_matcher_ai.jd_parser import parse_jd_text

class ResumeOptimizer:
    def __init__(self):
        self.analysis_history = []
    
    def analyze_and_track(self, resume_path, job_description, version_name="v1"):
        """Analyze resume and track improvements over time"""
        
        # Perform analysis
        resume_text = extract_text_from_pdf(resume_path)
        cleaned_resume = clean_resume_text(resume_text)
        jd_data = parse_jd_text(job_description)
        result = analyze_match(cleaned_resume, jd_data.__dict__)
        
        # Track analysis
        analysis_record = {
            'timestamp': datetime.now().isoformat(),
            'version': version_name,
            'score': result.score,
            'category': result.match_category,
            'matching_skills_count': len(result.matching_skills),
            'missing_skills_count': len(result.missing_skills),
            'critical_gaps': len(result.skill_gaps.get('Critical', [])),
            'important_gaps': len(result.skill_gaps.get('Important', [])),
            'suggestions_count': len(result.suggestions),
            'processing_time': result.processing_time
        }
        
        self.analysis_history.append(analysis_record)
        return result, analysis_record
    
    def compare_versions(self):
        """Compare different resume versions"""
        if len(self.analysis_history) < 2:
            print("Need at least 2 analyses to compare")
            return
        
        latest = self.analysis_history[-1]
        previous = self.analysis_history[-2]
        
        score_change = latest['score'] - previous['score']
        skills_change = latest['matching_skills_count'] - previous['matching_skills_count']
        gaps_change = latest['critical_gaps'] - previous['critical_gaps']
        
        print(f"\n📊 RESUME IMPROVEMENT ANALYSIS")
        print(f"{'='*50}")
        print(f"Version Comparison: {previous['version']} → {latest['version']}")
        print(f"Score Change: {score_change:+d}% ({previous['score']}% → {latest['score']}%)")
        print(f"Matching Skills: {skills_change:+d} ({previous['matching_skills_count']} → {latest['matching_skills_count']})")
        print(f"Critical Gaps: {gaps_change:+d} ({previous['critical_gaps']} → {latest['critical_gaps']})")
        
        if score_change > 0:
            print("✅ Improvement detected! Your resume is getting better.")
        elif score_change == 0:
            print("➡️  No change in score. Consider implementing more suggestions.")
        else:
            print("⚠️  Score decreased. Review recent changes.")
    
    def save_history(self, filename="resume_optimization_history.json"):
        """Save analysis history to file"""
        with open(filename, 'w') as f:
            json.dump(self.analysis_history, f, indent=2)
        print(f"📁 Analysis history saved to {filename}")

# Usage example
optimizer = ResumeOptimizer()

# Analyze original resume
job_desc = "Senior Software Engineer position requiring Python, React, AWS..."
result1, record1 = optimizer.analyze_and_track("resume_v1.pdf", job_desc, "Original")

# Analyze improved resume after implementing suggestions
result2, record2 = optimizer.analyze_and_track("resume_v2.pdf", job_desc, "After Suggestions")

# Compare improvements
optimizer.compare_versions()
optimizer.save_history()
```

## 🔌 API Integration Examples

### Example 1: Web Application Integration

```python
#!/usr/bin/env python3
"""
Flask web application integration example
"""
from flask import Flask, request, jsonify, render_template
import tempfile
import os
from resume_matcher_ai.matcher import analyze_match
from resume_matcher_ai.resume_parser import extract_text_from_pdf, clean_resume_text
from resume_matcher_ai.jd_parser import parse_jd_text

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/analyze', methods=['POST'])
def analyze_resume():
    try:
        # Get uploaded file and job description
        resume_file = request.files['resume']
        job_description = request.form['job_description']
        
        if not resume_file or not job_description:
            return jsonify({'error': 'Missing resume file or job description'}), 400
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            resume_file.save(temp_file.name)
            temp_path = temp_file.name
        
        try:
            # Process the resume
            resume_text = extract_text_from_pdf(temp_path)
            cleaned_resume = clean_resume_text(resume_text)
            jd_data = parse_jd_text(job_description)
            
            # Analyze match
            result = analyze_match(cleaned_resume, jd_data.__dict__)
            
            # Return results
            return jsonify({
                'success': True,
                'score': result.score,
                'category': result.match_category,
                'matching_skills': result.matching_skills,
                'missing_skills': result.missing_skills,
                'skill_gaps': result.skill_gaps,
                'suggestions': result.suggestions,
                'processing_time': result.processing_time
            })
            
        finally:
            # Clean up temporary file
            os.unlink(temp_path)
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

### Example 2: REST API Service

```python
#!/usr/bin/env python3
"""
FastAPI REST service example
"""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import tempfile
import os
from resume_matcher_ai.matcher import analyze_match
from resume_matcher_ai.resume_parser import extract_text_from_pdf, clean_resume_text
from resume_matcher_ai.jd_parser import parse_jd_text

app = FastAPI(title="Resume Matcher API", version="1.0.0")

@app.post("/analyze")
async def analyze_resume_endpoint(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    """
    Analyze resume compatibility with job description
    
    Args:
        resume: PDF resume file
        job_description: Job description text
        
    Returns:
        Analysis results with score, skills, gaps, and suggestions
    """
    
    if not resume.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        content = await resume.read()
        temp_file.write(content)
        temp_path = temp_file.name
    
    try:
        # Process the analysis
        resume_text = extract_text_from_pdf(temp_path)
        cleaned_resume = clean_resume_text(resume_text)
        jd_data = parse_jd_text(job_description)
        
        result = analyze_match(cleaned_resume, jd_data.__dict__)
        
        return {
            "analysis_id": f"analysis_{int(time.time())}",
            "resume_filename": resume.filename,
            "job_title": jd_data.title,
            "compatibility": {
                "score": result.score,
                "category": result.match_category,
                "processing_time": result.processing_time
            },
            "skills": {
                "matching": result.matching_skills,
                "missing": result.missing_skills,
                "gaps_by_priority": result.skill_gaps
            },
            "recommendations": result.suggestions,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "word_count": len(cleaned_resume.split()),
                "jd_length": len(job_description)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    
    finally:
        # Clean up temporary file
        os.unlink(temp_path)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Resume Matcher API"}

# Run with: uvicorn api_service:app --reload
```

## 📦 Batch Processing

### Example 1: Multiple Resumes, Single Job

```python
#!/usr/bin/env python3
"""
Batch process multiple resumes against a single job description
"""
import os
import csv
from datetime import datetime
from resume_matcher_ai.matcher import analyze_match
from resume_matcher_ai.resume_parser import extract_text_from_pdf, clean_resume_text
from resume_matcher_ai.jd_parser import parse_jd_text

def batch_analyze_resumes(resume_folder, job_description, output_file="batch_results.csv"):
    """
    Analyze multiple resumes against a single job description
    
    Args:
        resume_folder: Folder containing PDF resume files
        job_description: Job description text
        output_file: CSV file to save results
    """
    
    print(f"🚀 Starting batch analysis...")
    print(f"📁 Resume folder: {resume_folder}")
    print(f"📄 Output file: {output_file}")
    
    # Parse job description once
    jd_data = parse_jd_text(job_description)
    print(f"📋 Job title: {jd_data.title}")
    
    results = []
    pdf_files = [f for f in os.listdir(resume_folder) if f.endswith('.pdf')]
    
    print(f"📊 Found {len(pdf_files)} PDF files to process")
    
    for i, filename in enumerate(pdf_files, 1):
        resume_path = os.path.join(resume_folder, filename)
        print(f"\n[{i}/{len(pdf_files)}] Processing: {filename}")
        
        try:
            # Extract and analyze
            resume_text = extract_text_from_pdf(resume_path)
            cleaned_resume = clean_resume_text(resume_text)
            result = analyze_match(cleaned_resume, jd_data.__dict__)
            
            # Store results
            results.append({
                'filename': filename,
                'score': result.score,
                'category': result.match_category,
                'matching_skills_count': len(result.matching_skills),
                'missing_skills_count': len(result.missing_skills),
                'critical_gaps': len(result.skill_gaps.get('Critical', [])),
                'important_gaps': len(result.skill_gaps.get('Important', [])),
                'processing_time': result.processing_time,
                'top_suggestion': result.suggestions[0] if result.suggestions else 'No suggestions',
                'analysis_timestamp': datetime.now().isoformat()
            })
            
            print(f"   ✅ Score: {result.score}% ({result.match_category})")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            results.append({
                'filename': filename,
                'score': 0,
                'category': 'Error',
                'error': str(e),
                'analysis_timestamp': datetime.now().isoformat()
            })
    
    # Sort by score (highest first)
    results.sort(key=lambda x: x.get('score', 0), reverse=True)
    
    # Save to CSV
    if results:
        fieldnames = results[0].keys()
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        print(f"\n📊 BATCH ANALYSIS COMPLETE")
        print(f"📁 Results saved to: {output_file}")
        print(f"🏆 Top 3 candidates:")
        
        for i, result in enumerate(results[:3], 1):
            if result.get('score', 0) > 0:
                print(f"   {i}. {result['filename']}: {result['score']}% ({result['category']})")
    
    return results

# Usage example
job_description = """
Senior Software Engineer - Python/React

We are seeking a Senior Software Engineer with strong Python and React experience...

Requirements:
- 5+ years of software development experience
- Expert-level Python programming
- Modern React.js development
- RESTful API design and development
- PostgreSQL or MySQL database experience
- AWS cloud platform experience
- Git version control
- Agile development methodologies

Preferred:
- Docker containerization
- Kubernetes orchestration
- GraphQL API development
- TypeScript experience
"""

# Run batch analysis
results = batch_analyze_resumes("./candidate_resumes", job_description)
```

### Example 2: Single Resume, Multiple Jobs

```python
#!/usr/bin/env python3
"""
Analyze a single resume against multiple job descriptions
"""
import json
from resume_matcher_ai.matcher import analyze_match
from resume_matcher_ai.resume_parser import extract_text_from_pdf, clean_resume_text
from resume_matcher_ai.jd_parser import parse_jd_text

def analyze_resume_multiple_jobs(resume_path, job_descriptions, output_file="job_matches.json"):
    """
    Analyze a single resume against multiple job descriptions
    
    Args:
        resume_path: Path to PDF resume file
        job_descriptions: Dictionary of {job_id: job_description_text}
        output_file: JSON file to save results
    """
    
    print(f"📄 Processing resume: {resume_path}")
    
    # Extract resume once
    resume_text = extract_text_from_pdf(resume_path)
    cleaned_resume = clean_resume_text(resume_text)
    
    results = {}
    
    for job_id, job_desc in job_descriptions.items():
        print(f"\n🔍 Analyzing job: {job_id}")
        
        try:
            jd_data = parse_jd_text(job_desc)
            result = analyze_match(cleaned_resume, jd_data.__dict__)
            
            results[job_id] = {
                'job_title': jd_data.title,
                'score': result.score,
                'category': result.match_category,
                'matching_skills': result.matching_skills,
                'skill_gaps': result.skill_gaps,
                'top_suggestions': result.suggestions[:3],  # Top 3 suggestions
                'processing_time': result.processing_time
            }
            
            print(f"   ✅ {jd_data.title}: {result.score}% ({result.match_category})")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            results[job_id] = {'error': str(e)}
    
    # Save results
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Display summary
    print(f"\n📊 JOB MATCH SUMMARY")
    print(f"{'='*50}")
    
    # Sort jobs by score
    scored_jobs = [(job_id, data) for job_id, data in results.items() if 'score' in data]
    scored_jobs.sort(key=lambda x: x[1]['score'], reverse=True)
    
    for job_id, data in scored_jobs:
        print(f"{data['job_title']}: {data['score']}% ({data['category']})")
    
    return results

# Usage example
job_descriptions = {
    "senior_python_dev": """
    Senior Python Developer
    Requirements: 5+ years Python, Django, PostgreSQL, AWS
    """,
    
    "fullstack_engineer": """
    Full Stack Engineer
    Requirements: Python, React, Node.js, MongoDB, Docker
    """,
    
    "data_scientist": """
    Data Scientist
    Requirements: Python, pandas, scikit-learn, SQL, statistics
    """,
    
    "devops_engineer": """
    DevOps Engineer
    Requirements: AWS, Docker, Kubernetes, Python, CI/CD
    """
}

results = analyze_resume_multiple_jobs("my_resume.pdf", job_descriptions)
```

## 💰 Cost Optimization Tips

### Example 1: Monitor Usage and Costs

```python
#!/usr/bin/env python3
"""
Cost monitoring and optimization example
"""
from resume_matcher_ai.utils import get_usage_statistics, get_cost_optimization_stats

def monitor_usage():
    """Monitor API usage and costs"""
    
    # Get usage statistics
    stats = get_usage_statistics(days=30)
    
    print("📊 USAGE STATISTICS (Last 30 Days)")
    print("="*50)
    print(f"Total API Calls: {stats['total_calls']}")
    print(f"Successful Calls: {stats['successful_calls']}")
    print(f"Failed Calls: {stats['failed_calls']}")
    print(f"Total Tokens Used: {stats['total_tokens']:,}")
    print(f"Total Cost: ${stats['total_cost']:.4f}")
    print(f"Average Processing Time: {stats['average_processing_time']:.2f}s")
    
    if stats['total_calls'] > 0:
        success_rate = (stats['successful_calls'] / stats['total_calls']) * 100
        avg_tokens_per_call = stats['total_tokens'] / stats['successful_calls'] if stats['successful_calls'] > 0 else 0
        avg_cost_per_call = stats['total_cost'] / stats['successful_calls'] if stats['successful_calls'] > 0 else 0
        
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Average Tokens per Call: {avg_tokens_per_call:.0f}")
        print(f"Average Cost per Call: ${avg_cost_per_call:.4f}")
    
    # Get optimization statistics
    opt_stats = get_cost_optimization_stats()
    
    print(f"\n💰 COST OPTIMIZATION")
    print("="*50)
    print(f"Estimated Tokens Saved: {opt_stats['total_tokens_saved']:,}")
    print(f"Estimated Cost Saved: ${opt_stats['total_cost_saved']:.4f}")
    print(f"Optimization Effectiveness: {opt_stats['optimization_effectiveness']:.1f}%")
    
    print(f"\n💡 RECOMMENDATIONS:")
    for rec in opt_stats['recommendations']:
        print(f"   • {rec}")

# Run monitoring
monitor_usage()
```

### Example 2: Optimize Input Sizes

```python
#!/usr/bin/env python3
"""
Input optimization for cost reduction
"""
from resume_matcher_ai.utils import estimate_token_usage

def optimize_inputs(resume_text, job_description):
    """
    Optimize inputs to reduce token usage while maintaining quality
    
    Args:
        resume_text: Original resume text
        job_description: Original job description text
        
    Returns:
        Optimized texts and token estimates
    """
    
    # Estimate original token usage
    original_resume_tokens = estimate_token_usage(resume_text)
    original_jd_tokens = estimate_token_usage(job_description)
    total_original = original_resume_tokens + original_jd_tokens
    
    print(f"📊 ORIGINAL TOKEN ESTIMATES")
    print(f"Resume: {original_resume_tokens:,} tokens")
    print(f"Job Description: {original_jd_tokens:,} tokens")
    print(f"Total: {total_original:,} tokens")
    print(f"Estimated Cost: ${(total_original / 1000) * 0.001:.4f}")
    
    # Apply optimizations
    from resume_matcher_ai.utils import _smart_truncate_resume, _smart_truncate_jd
    
    optimized_resume = _smart_truncate_resume(resume_text, 6000)  # ~1500 tokens
    optimized_jd = _smart_truncate_jd(job_description, 3000)     # ~750 tokens
    
    # Estimate optimized token usage
    opt_resume_tokens = estimate_token_usage(optimized_resume)
    opt_jd_tokens = estimate_token_usage(optimized_jd)
    total_optimized = opt_resume_tokens + opt_jd_tokens
    
    print(f"\n📊 OPTIMIZED TOKEN ESTIMATES")
    print(f"Resume: {opt_resume_tokens:,} tokens ({original_resume_tokens - opt_resume_tokens:+,})")
    print(f"Job Description: {opt_jd_tokens:,} tokens ({original_jd_tokens - opt_jd_tokens:+,})")
    print(f"Total: {total_optimized:,} tokens ({total_original - total_optimized:+,})")
    print(f"Estimated Cost: ${(total_optimized / 1000) * 0.001:.4f}")
    
    savings = total_original - total_optimized
    cost_savings = (savings / 1000) * 0.001
    
    print(f"\n💰 SAVINGS")
    print(f"Tokens Saved: {savings:,} ({(savings/total_original)*100:.1f}%)")
    print(f"Cost Saved: ${cost_savings:.4f}")
    
    return optimized_resume, optimized_jd

# Usage example
with open("long_resume.txt", "r") as f:
    resume_text = f.read()

job_description = """
[Very long job description with lots of details...]
"""

optimized_resume, optimized_jd = optimize_inputs(resume_text, job_description)
```

## 🎯 Best Practices

### 1. Resume Preparation

**✅ Good Resume Practices:**
- Use clear, readable fonts
- Include contact information
- List skills explicitly
- Quantify achievements with metrics
- Use industry-standard terminology
- Keep formatting simple and clean

**❌ Avoid:**
- Scanned images without OCR
- Password-protected PDFs
- Overly complex formatting
- Missing contact information
- Vague job descriptions

### 2. Job Description Input

**✅ Good Job Description Practices:**
- Include complete job posting
- Copy requirements and qualifications sections
- Include preferred skills
- Add company context if relevant
- Specify experience requirements

**❌ Avoid:**
- Partial job descriptions
- Only company names or URLs
- Extremely long descriptions (>10,000 words)
- Job descriptions in foreign languages

### 3. Analysis Interpretation

**Understanding Scores:**
- **70-100%**: Strong match, apply with confidence
- **50-69%**: Good potential, implement key suggestions
- **30-49%**: Moderate fit, significant improvements needed
- **0-29%**: Poor match, consider skill development

**Using Suggestions:**
- Prioritize high-impact recommendations
- Implement 1-2 changes at a time
- Re-analyze after major changes
- Focus on quantifiable improvements

## 🔧 Common Use Cases

### Use Case 1: Job Seeker Optimization

```python
# Scenario: Job seeker wants to optimize resume for specific role
resume_path = "current_resume.pdf"
target_job = """
Senior Data Scientist position requiring Python, machine learning,
and statistical analysis experience...
"""

# Analyze current state
result = analyze_resume_job_match(resume_path, target_job)

# Identify top improvements
critical_gaps = result['skill_gaps']['Critical']
top_suggestions = result['suggestions'][:3]

print("🎯 OPTIMIZATION PLAN:")
print(f"Current Score: {result['score']}%")
print(f"Critical Skills to Add: {', '.join(critical_gaps)}")
print(f"Top 3 Actions: {top_suggestions}")
```

### Use Case 2: Recruiter Screening

```python
# Scenario: Recruiter screening multiple candidates
candidates = ["candidate1.pdf", "candidate2.pdf", "candidate3.pdf"]
job_req = "Software Engineer position requirements..."

results = []
for candidate in candidates:
    result = analyze_resume_job_match(candidate, job_req)
    results.append(result)

# Rank candidates
results.sort(key=lambda x: x['score'], reverse=True)

print("🏆 CANDIDATE RANKING:")
for i, result in enumerate(results, 1):
    print(f"{i}. {result['resume_file']}: {result['score']}%")
```

### Use Case 3: Career Transition Analysis

```python
# Scenario: Professional considering career change
current_resume = "marketing_professional.pdf"
target_roles = {
    "Product Manager": "Product management role requiring...",
    "Data Analyst": "Data analysis position requiring...",
    "UX Designer": "UX design role requiring..."
}

print("🔄 CAREER TRANSITION ANALYSIS:")
for role, job_desc in target_roles.items():
    result = analyze_resume_job_match(current_resume, job_desc)
    print(f"{role}: {result['score']}% match")
    
    if result['score'] < 50:
        critical_skills = result['skill_gaps']['Critical']
        print(f"   Skills to develop: {', '.join(critical_skills[:3])}")
```

## 🚨 Troubleshooting Examples

### Problem 1: Low Scores Despite Good Match

```python
# Possible causes and solutions:
# 1. Resume uses different terminology than job description
# 2. Skills are embedded in experience descriptions
# 3. Resume lacks explicit skills section

# Solution: Add skills section with job description keywords
suggestions = [
    "Add a 'Technical Skills' section with explicit skill names",
    "Use terminology from the job description",
    "Quantify achievements with specific metrics",
    "Include relevant certifications and training"
]
```

### Problem 2: API Errors

```python
# Common API issues and solutions:
try:
    result = analyze_match(resume_text, jd_data)
except Exception as e:
    error_msg = str(e).lower()
    
    if "rate limit" in error_msg:
        print("⏳ Rate limit hit. Wait 60 seconds and retry.")
        time.sleep(60)
        result = analyze_match(resume_text, jd_data)
    
    elif "api key" in error_msg:
        print("🔑 Check your API key configuration")
        # Verify API key setup
    
    elif "network" in error_msg:
        print("🌐 Check internet connection")
        # Implement retry logic
```

### Problem 3: PDF Processing Issues

```python
# PDF processing troubleshooting:
def troubleshoot_pdf(pdf_path):
    """Diagnose PDF processing issues"""
    
    if not os.path.exists(pdf_path):
        return "File not found"
    
    if not pdf_path.endswith('.pdf'):
        return "Not a PDF file"
    
    try:
        text = extract_text_from_pdf(pdf_path)
        if not text.strip():
            return "PDF contains no extractable text (may be scanned)"
        
        if len(text) < 100:
            return "PDF contains very little text"
        
        return "PDF processing should work"
        
    except Exception as e:
        return f"PDF processing error: {str(e)}"

# Usage
diagnosis = troubleshoot_pdf("problematic_resume.pdf")
print(f"Diagnosis: {diagnosis}")
```

---

This comprehensive guide should help you make the most of the Resume + Job Description Matcher AI. For additional support, refer to the main README.md file or check the error messages for specific guidance.