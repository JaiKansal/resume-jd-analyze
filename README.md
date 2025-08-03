# Resume + Job Description Matcher AI

An intelligent AI-powered tool that analyzes the compatibility between resumes and job descriptions, providing quantitative matching scores, skill gap analysis, and actionable improvement recommendations.

## 🚀 Features

- **Smart Compatibility Analysis**: Get 0-100% compatibility scores with detailed explanations
- **Skill Matching**: Identify skills that align between your resume and job requirements
- **Gap Analysis**: Discover missing skills categorized by priority (Critical/Important/Nice-to-have)
- **Actionable Recommendations**: Receive specific, implementable suggestions to improve your resume
- **Cost-Optimized AI**: Intelligent token usage optimization to minimize API costs
- **Enhanced Error Handling**: Comprehensive error recovery and user guidance
- **Usage Tracking**: Monitor API usage and costs with built-in analytics

## 📋 Requirements

- Python 3.8 or higher
- Perplexity API key (get one at [perplexity.ai](https://www.perplexity.ai/))
- PDF resume file
- Internet connection

## 🛠️ Installation

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd resume-matcher-ai
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your API key**
   
   **Option A: Environment Variable (Recommended)**
   ```bash
   # macOS/Linux
   export PERPLEXITY_API_KEY='your-api-key-here'
   
   # Windows
   set PERPLEXITY_API_KEY=your-api-key-here
   ```
   
   **Option B: Create .env file**
   ```bash
   cp .env.example .env
   # Edit .env and add your API key
   echo "PERPLEXITY_API_KEY=your-api-key-here" > .env
   ```

## 🎯 Quick Start

1. **Run the application**
   ```bash
   python -m resume_matcher_ai.main
   ```

2. **Follow the prompts**
   - Enter the path to your PDF resume
   - Paste the job description text
   - Review your analysis results

## 📖 Usage Examples

### Basic Usage

```bash
$ python -m resume_matcher_ai.main

============================================================
Resume + Job Description Matcher
============================================================

Welcome! This tool analyzes the compatibility between resumes and job descriptions.
You'll receive a compatibility score, matching skills, gaps, and improvement suggestions.

----------------------------------------
INPUT COLLECTION
----------------------------------------

1. Resume File (attempt 1/5):
Enter the path to your resume PDF file (or 'quit' to exit): /path/to/your/resume.pdf
📄 Extracting text from PDF...
🧹 Cleaning extracted text...
✅ Validating resume content...
✅ Resume file validated: /path/to/your/resume.pdf

2. Job Description (attempt 1/3):
Please paste the job description text below.
You can paste multiple lines. When finished, press Enter on an empty line.
(or type 'quit' to exit)

Senior Software Engineer

We are seeking a Senior Software Engineer to join our growing team...
[paste your job description here]

✅ Job description received and validated (1247 characters)

Analyzing resume and job description...
This may take up to 30 seconds...
```

### Sample Output

```
======================================================================
🎯 RESUME + JOB DESCRIPTION ANALYSIS RESULTS
======================================================================

┌─ 📊 COMPATIBILITY ANALYSIS
│
│ 🟢 MATCH SCORE: 78% [███████░░░] STRONG
│ 🏷️  CATEGORY: Strong Match
│
│ ✨ EXCELLENT! Your resume demonstrates strong alignment with this role.
│    You meet most key requirements and show relevant experience.
└─────────────────────────────────────────────────────────────────

┌─ ✅ MATCHING SKILLS ANALYSIS
│
│ 📈 FOUND 12 MATCHING SKILLS
│
│ 🎯 Your Matching Skills:
│   1. Python
│   2. JavaScript
│   3. React
│   4. Node.js
│   5. AWS
│   6. Docker
│   7. Git
│   8. Agile
│   ... plus 4 additional matching skills
│
│ 💪 EXCELLENT skill alignment! You demonstrate 12 relevant competencies.
│    This strong foundation positions you well for this role.
└─────────────────────────────────────────────────────────────────

┌─ ❌ SKILL GAPS & OPPORTUNITIES
│
│ 📊 IDENTIFIED 3 SKILL GAPS TO ADDRESS
│
│ 🟡 IMPORTANT GAPS (2 skills):
│   VALUABLE skills that strengthen your candidacy
│
│   • Kubernetes
│   • GraphQL
│
│ 🟢 NICE-TO-HAVE GAPS (1 skill):
│   BONUS skills that would be advantageous
│
│   • TypeScript
│
│ 🎯 PRIORITY ACTION PLAN:
│   1. FOCUS: Highlight or develop 2 important skills
│   2. STRATEGY: Emphasize related experience or seek skill development
└─────────────────────────────────────────────────────────────────

┌─ 💡 ACTIONABLE IMPROVEMENT RECOMMENDATIONS
│
│ 📝 4 STRATEGIC RECOMMENDATIONS:
│
│ 🔥 RECOMMENDATION 1 (HIGH IMPACT):
│   Add Kubernetes experience to your DevOps skills section.
│   Include specific examples of container orchestration projects.
│
│ ⭐ RECOMMENDATION 2 (IMPORTANT):
│   Incorporate GraphQL API development experience.
│   Mention any REST to GraphQL migration projects.
│
│ 💫 RECOMMENDATION 3 (VALUABLE):
│   Quantify your achievements with specific metrics.
│   Use phrases like "Improved performance by 40%" or "Reduced deployment time by 60%".
│
│ ✓ RECOMMENDATION 4 (HELPFUL):
│   Add TypeScript to your technical skills.
│   Highlight type-safe development practices.
│
│ 🚀 IMPLEMENTATION STRATEGY:
│   • Start with HIGH IMPACT recommendation for maximum benefit
│   • Implement 1-2 changes at a time for manageable progress
│   • Focus on specific, measurable improvements
│   • Review and update your resume after each change
│
│ ⏱️  TIMELINE: Aim to implement top 3 recommendations within 1-2 weeks
└─────────────────────────────────────────────────────────────────
```

## ⚙️ Configuration Options

Create a `.env` file to customize the application:

```env
# Required
PERPLEXITY_API_KEY=your-api-key-here

# Optional Configuration
API_TIMEOUT=30                    # API request timeout in seconds
MAX_TOKENS=3000                   # Maximum tokens per API request
ENABLE_USAGE_TRACKING=true        # Track API usage and costs
COST_ALERT_THRESHOLD=10.00        # Alert when monthly costs exceed this amount
DEBUG_MODE=false                  # Enable debug logging
```

## 📊 Usage Analytics

The application automatically tracks your API usage and costs:

```python
from resume_matcher_ai.utils import get_usage_statistics

# Get usage stats for the last 30 days
stats = get_usage_statistics(days=30)
print(f"Total API calls: {stats['total_calls']}")
print(f"Total cost: ${stats['total_cost']:.4f}")
print(f"Average processing time: {stats['average_processing_time']:.2f}s")
```

## 🔧 Advanced Usage

### Programmatic Usage

```python
from resume_matcher_ai.matcher import analyze_match
from resume_matcher_ai.resume_parser import extract_text_from_pdf, clean_resume_text
from resume_matcher_ai.jd_parser import parse_jd_text

# Extract resume text
resume_text = extract_text_from_pdf("path/to/resume.pdf")
cleaned_resume = clean_resume_text(resume_text)

# Parse job description
jd_data = parse_jd_text(job_description_text)

# Analyze match
result = analyze_match(cleaned_resume, jd_data.__dict__)

print(f"Compatibility Score: {result.score}%")
print(f"Match Category: {result.match_category}")
print(f"Matching Skills: {result.matching_skills}")
print(f"Suggestions: {result.suggestions}")
```

### Batch Processing

```python
import os
from resume_matcher_ai.matcher import analyze_match
from resume_matcher_ai.resume_parser import extract_text_from_pdf, clean_resume_text
from resume_matcher_ai.jd_parser import parse_jd_text

def batch_analyze_resumes(resume_folder, job_description):
    """Analyze multiple resumes against a single job description"""
    results = []
    
    jd_data = parse_jd_text(job_description)
    
    for filename in os.listdir(resume_folder):
        if filename.endswith('.pdf'):
            resume_path = os.path.join(resume_folder, filename)
            
            try:
                resume_text = extract_text_from_pdf(resume_path)
                cleaned_resume = clean_resume_text(resume_text)
                
                result = analyze_match(cleaned_resume, jd_data.__dict__)
                results.append({
                    'filename': filename,
                    'score': result.score,
                    'category': result.match_category,
                    'processing_time': result.processing_time
                })
                
            except Exception as e:
                print(f"Error processing {filename}: {e}")
    
    # Sort by score (highest first)
    results.sort(key=lambda x: x['score'], reverse=True)
    return results

# Usage
results = batch_analyze_resumes("./resumes", job_description_text)
for result in results:
    print(f"{result['filename']}: {result['score']}% ({result['category']})")
```

## 🚨 Troubleshooting

### Common Issues

**1. API Key Issues**
```
❌ ERROR: PERPLEXITY_API_KEY environment variable is not set.
```
**Solution**: Set your API key as described in the installation section.

**2. PDF Reading Issues**
```
❌ ERROR: PDF appears to be empty or contains no extractable text.
```
**Solutions**:
- Ensure the PDF contains selectable text (not just images)
- Try re-saving the PDF from the original document
- Check if the PDF is password-protected

**3. Rate Limit Exceeded**
```
❌ ERROR: Rate limit exceeded. Please wait 60 seconds before retrying.
```
**Solutions**:
- Wait for the specified time before retrying
- Consider upgrading your Perplexity API plan
- Use shorter resume or job description text

**4. Network Issues**
```
❌ ERROR: Failed to connect to Perplexity API.
```
**Solutions**:
- Check your internet connection
- Verify that api.perplexity.ai is accessible
- Check firewall settings

### Getting Help

1. **Check the error message**: The application provides detailed error messages with specific solutions
2. **Review the logs**: Enable debug mode for more detailed logging
3. **Verify your setup**: Ensure all dependencies are installed and API key is valid
4. **Test with sample files**: Try with a simple PDF and job description first

## 🔒 Privacy & Security

- **No Data Storage**: Resume content is not stored permanently
- **Secure API Communication**: All API calls use HTTPS encryption
- **Local Processing**: Text extraction and cleaning happen locally
- **Usage Tracking**: Only anonymous usage statistics are tracked locally

## 💰 Cost Management

The application includes several cost optimization features:

- **Smart Token Usage**: Intelligent text truncation and prompt optimization
- **Usage Tracking**: Monitor your API costs in real-time
- **Cost Alerts**: Get notified when you approach spending thresholds
- **Efficient Processing**: Optimized API calls to minimize token usage

Typical costs:
- **Small resume + job description**: ~$0.002-0.005 per analysis
- **Large resume + job description**: ~$0.005-0.010 per analysis
- **Monthly usage (50 analyses)**: ~$0.25-0.50

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines for details on:
- Code style and standards
- Testing requirements
- Pull request process
- Issue reporting

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Perplexity AI** for providing the intelligent analysis capabilities
- **PyMuPDF** for reliable PDF text extraction
- **Python Community** for excellent libraries and tools

## 📞 Support

For support and questions:
- Check the troubleshooting section above
- Review the error messages for specific guidance
- Ensure your environment is properly configured
- Test with sample files to isolate issues

---

**Made with ❤️ for job seekers and recruiters everywhere**