# Setup Guide - Resume + Job Description Matcher AI

This comprehensive setup guide will help you get the Resume + Job Description Matcher AI up and running quickly and efficiently.

## 📋 Prerequisites

Before you begin, ensure you have the following:

- **Python 3.8 or higher** installed on your system
- **Internet connection** for API calls
- **Perplexity API account** (free tier available)
- **PDF resume files** to analyze

## 🚀 Quick Setup (5 minutes)

### Step 1: Get Your API Key

1. Visit [perplexity.ai](https://www.perplexity.ai/)
2. Sign up for a free account
3. Navigate to **Settings** → **API**
4. Generate a new API key
5. Copy the key (it starts with `pplx-`)

### Step 2: Install Dependencies

```bash
# Install required Python packages
pip install -r requirements.txt
```

### Step 3: Configure API Key

**Option A: Environment Variable (Recommended)**
```bash
# macOS/Linux
export PERPLEXITY_API_KEY='pplx-your-api-key-here'

# Windows Command Prompt
set PERPLEXITY_API_KEY=pplx-your-api-key-here

# Windows PowerShell
$env:PERPLEXITY_API_KEY='pplx-your-api-key-here'
```

**Option B: Create .env File**
```bash
# Copy the example file
cp .env.example .env

# Edit .env file and add your API key
echo "PERPLEXITY_API_KEY=pplx-your-api-key-here" > .env
```

### Step 4: Test Installation

```bash
# Run the application
python -m resume_matcher_ai.main

# You should see the welcome screen
```

## 🔧 Detailed Setup Instructions

### Python Installation

**macOS:**
```bash
# Using Homebrew
brew install python3

# Using pyenv (recommended for version management)
brew install pyenv
pyenv install 3.11.0
pyenv global 3.11.0
```

**Windows:**
1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer and check "Add Python to PATH"
3. Verify installation: `python --version`

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### Virtual Environment Setup (Recommended)

```bash
# Create virtual environment
python -m venv resume_matcher_env

# Activate virtual environment
# macOS/Linux:
source resume_matcher_env/bin/activate

# Windows:
resume_matcher_env\Scripts\activate

# Install dependencies in virtual environment
pip install -r requirements.txt
```

### Dependency Installation

The application requires several Python packages:

```bash
# Core dependencies
pip install PyMuPDF>=1.23.0    # PDF text extraction
pip install requests>=2.31.0   # HTTP requests for API calls
pip install python-dotenv>=1.0.0  # Environment variable management

# Optional dependencies for enhanced features
pip install pandas>=2.0.0      # Data analysis (for batch processing)
pip install matplotlib>=3.7.0  # Visualization (for usage analytics)
```

### API Key Configuration Options

#### Option 1: Environment Variables

**Permanent Setup (Recommended):**

**macOS/Linux - Add to shell profile:**
```bash
# Add to ~/.bashrc, ~/.zshrc, or ~/.profile
echo 'export PERPLEXITY_API_KEY="pplx-your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

**Windows - System Environment Variables:**
1. Open System Properties → Advanced → Environment Variables
2. Add new system variable:
   - Name: `PERPLEXITY_API_KEY`
   - Value: `pplx-your-api-key-here`
3. Restart command prompt

#### Option 2: .env File Configuration

Create a `.env` file in the project root:

```env
# Required Configuration
PERPLEXITY_API_KEY=pplx-your-api-key-here

# Optional Configuration
API_TIMEOUT=30                    # API request timeout in seconds
MAX_TOKENS=3000                   # Maximum tokens per API request
ENABLE_USAGE_TRACKING=true        # Track API usage and costs
COST_ALERT_THRESHOLD=10.00        # Alert when monthly costs exceed this amount
DEBUG_MODE=false                  # Enable debug logging
LOG_LEVEL=INFO                    # Logging level (DEBUG, INFO, WARNING, ERROR)

# Advanced Configuration
PERPLEXITY_API_URL=https://api.perplexity.ai  # API base URL
USAGE_LOG_FILE=usage_log.json     # Usage tracking log file
```

#### Option 3: Runtime Configuration

```python
# Set API key programmatically
import os
os.environ['PERPLEXITY_API_KEY'] = 'pplx-your-api-key-here'

# Then run your analysis
from resume_matcher_ai.main import main
main()
```

## ✅ Verification and Testing

### Step 1: Verify Installation

```bash
# Check Python version
python --version  # Should be 3.8+

# Check package installation
python -c "import fitz; print('PyMuPDF installed successfully')"
python -c "import requests; print('Requests installed successfully')"
python -c "from dotenv import load_dotenv; print('python-dotenv installed successfully')"
```

### Step 2: Test API Connection

```bash
# Run the built-in setup verification
python -c "
from resume_matcher_ai.utils import setup_environment
result = setup_environment()
if result['success']:
    print('✅ Setup successful!')
    for step in result['setup_steps']:
        print(step)
else:
    print('❌ Setup failed:')
    for error in result['errors']:
        print(f'  • {error}')
"
```

### Step 3: Test with Sample Files

```bash
# Test with provided sample files
python -m resume_matcher_ai.main

# When prompted, use:
# Resume file: sample_resume.pdf (if available)
# Job description: Contents of sample_jd.txt (if available)
```

## 🔍 Troubleshooting Setup Issues

### Common Issues and Solutions

#### Issue 1: "Module not found" errors

```bash
# Solution: Ensure you're in the correct directory and dependencies are installed
pwd  # Should be in the project root directory
pip list | grep -E "(PyMuPDF|requests|python-dotenv)"

# If packages are missing:
pip install -r requirements.txt
```

#### Issue 2: API key not recognized

```bash
# Check if API key is set
echo $PERPLEXITY_API_KEY  # macOS/Linux
echo %PERPLEXITY_API_KEY%  # Windows

# If empty, set the API key:
export PERPLEXITY_API_KEY='pplx-your-actual-key-here'
```

#### Issue 3: Permission errors

```bash
# macOS/Linux: Fix permissions
chmod +x resume_matcher_ai/main.py

# Windows: Run as administrator if needed
```

#### Issue 4: PDF processing errors

```bash
# Install additional dependencies if needed
pip install --upgrade PyMuPDF

# On Linux, you might need:
sudo apt-get install libmupdf-dev
```

#### Issue 5: Network/firewall issues

```bash
# Test API connectivity
curl -H "Authorization: Bearer pplx-your-key" https://api.perplexity.ai/chat/completions

# If blocked, check firewall settings or use a different network
```

### Advanced Troubleshooting

#### Enable Debug Mode

```bash
# Set debug mode in .env file
echo "DEBUG_MODE=true" >> .env

# Or set environment variable
export DEBUG_MODE=true

# Run with verbose output
python -m resume_matcher_ai.main
```

#### Check System Requirements

```python
# Run system check script
python -c "
import sys
import platform
print(f'Python version: {sys.version}')
print(f'Platform: {platform.platform()}')
print(f'Architecture: {platform.architecture()}')

# Check available memory
import psutil
print(f'Available memory: {psutil.virtual_memory().available / (1024**3):.1f} GB')
"
```

## 🔧 Advanced Configuration

### Custom Configuration File

Create a `config.py` file for advanced settings:

```python
# config.py
import os

class Config:
    # API Configuration
    PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')
    API_BASE_URL = os.getenv('PERPLEXITY_API_URL', 'https://api.perplexity.ai')
    API_TIMEOUT = int(os.getenv('API_TIMEOUT', '30'))
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', '3000'))
    
    # Processing Configuration
    MAX_RESUME_SIZE = 50 * 1024 * 1024  # 50MB
    MAX_JD_LENGTH = 50000  # 50K characters
    
    # Cost Management
    ENABLE_USAGE_TRACKING = os.getenv('ENABLE_USAGE_TRACKING', 'true').lower() == 'true'
    COST_ALERT_THRESHOLD = float(os.getenv('COST_ALERT_THRESHOLD', '10.00'))
    
    # Logging
    DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        if not cls.PERPLEXITY_API_KEY:
            raise ValueError("PERPLEXITY_API_KEY is required")
        
        if not cls.PERPLEXITY_API_KEY.startswith('pplx-'):
            raise ValueError("Invalid API key format")
        
        return True

# Usage in your code
from config import Config
Config.validate()
```

### Docker Setup (Optional)

Create a `Dockerfile` for containerized deployment:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libmupdf-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Run the application
CMD ["python", "-m", "resume_matcher_ai.main"]
```

Build and run with Docker:

```bash
# Build the image
docker build -t resume-matcher-ai .

# Run the container
docker run -it --rm \
  -e PERPLEXITY_API_KEY=pplx-your-key-here \
  -v $(pwd)/resumes:/app/resumes \
  resume-matcher-ai
```

## 📊 Performance Optimization

### System Requirements

**Minimum Requirements:**
- Python 3.8+
- 2GB RAM
- 1GB free disk space
- Internet connection (1 Mbps+)

**Recommended Requirements:**
- Python 3.11+
- 4GB RAM
- 2GB free disk space
- Stable internet connection (5 Mbps+)

### Performance Tuning

```bash
# Optimize Python for performance
export PYTHONOPTIMIZE=1

# Use faster JSON library (optional)
pip install orjson

# Enable multiprocessing for batch operations
export PYTHONHASHSEED=0
```

## 🔐 Security Best Practices

### API Key Security

1. **Never commit API keys to version control**
   ```bash
   # Add to .gitignore
   echo ".env" >> .gitignore
   echo "*.key" >> .gitignore
   ```

2. **Use environment variables in production**
   ```bash
   # Production deployment
   export PERPLEXITY_API_KEY=$(cat /secure/path/to/api.key)
   ```

3. **Rotate API keys regularly**
   - Generate new keys monthly
   - Update all environments
   - Monitor usage for anomalies

### File Security

```bash
# Set appropriate file permissions
chmod 600 .env  # Only owner can read/write
chmod 755 resume_matcher_ai/  # Standard directory permissions
```

## 📞 Getting Help

If you encounter issues during setup:

1. **Check the error message** - Most errors include specific solutions
2. **Review this setup guide** - Ensure all steps were followed
3. **Check system requirements** - Verify Python version and dependencies
4. **Test with sample data** - Use simple inputs to isolate issues
5. **Enable debug mode** - Get more detailed error information

### Support Resources

- **Documentation**: README.md and USAGE_EXAMPLES.md
- **Error Messages**: The application provides detailed error guidance
- **System Check**: Use the built-in setup verification tools
- **Community**: Check for similar issues and solutions

## ✅ Setup Checklist

Use this checklist to ensure proper setup:

- [ ] Python 3.8+ installed and accessible
- [ ] Virtual environment created and activated (recommended)
- [ ] Dependencies installed from requirements.txt
- [ ] Perplexity API account created
- [ ] API key obtained and configured
- [ ] Environment variables set or .env file created
- [ ] Setup verification completed successfully
- [ ] Test run completed with sample data
- [ ] Error handling tested (try invalid inputs)
- [ ] Usage tracking configured (optional)
- [ ] Debug mode tested (optional)

## 🎉 Next Steps

Once setup is complete:

1. **Read the Usage Examples** - See USAGE_EXAMPLES.md for detailed examples
2. **Try Different Scenarios** - Test with various resume and job combinations
3. **Explore Advanced Features** - Batch processing, API integration, etc.
4. **Monitor Usage** - Keep track of API costs and usage patterns
5. **Optimize Performance** - Fine-tune settings for your use case

---

**Congratulations! You're now ready to use the Resume + Job Description Matcher AI effectively.**