#!/bin/bash

# Quick Deployment Script for Streamlit Cloud
# Resume + JD Analyzer

echo "🚀 Deploying Resume + JD Analyzer to Streamlit Cloud"
echo "=================================================="

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📝 Initializing git repository..."
    git init
fi

# Add all files
echo "📦 Adding files to git..."
git add .

# Create commit with timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo "💾 Creating commit..."
git commit -m "Deploy to Streamlit Cloud - $TIMESTAMP"

# Check if remote exists
if ! git remote get-url origin > /dev/null 2>&1; then
    echo ""
    echo "🔗 GitHub Repository Setup Required"
    echo "=================================="
    echo "1. Go to https://github.com/new"
    echo "2. Repository name: resume-jd-analyzer"
    echo "3. Make it PUBLIC (required for free Streamlit Cloud)"
    echo "4. Don't initialize with README"
    echo ""
    echo "Then run these commands:"
    echo "git remote add origin https://github.com/YOUR_USERNAME/resume-jd-analyzer.git"
    echo "git branch -M main"
    echo "git push -u origin main"
    echo ""
    echo "Replace YOUR_USERNAME with your actual GitHub username"
else
    echo "🚀 Pushing to GitHub..."
    git push
fi

echo ""
echo "✅ Code is ready for deployment!"
echo ""
echo "🌐 Next Steps:"
echo "1. Go to https://share.streamlit.io"
echo "2. Sign in with GitHub"
echo "3. Click 'New app'"
echo "4. Select your repository: resume-jd-analyzer"
echo "5. Main file: app.py"
echo "6. Add secrets (see streamlit_secrets_template.toml)"
echo "7. Deploy!"
echo ""
echo "📋 Required Secrets:"
echo "- PERPLEXITY_API_KEY: your_perplexity_key"
echo "- RAZORPAY_KEY_ID: rzp_live_gBOm5l3scvXYjP"
echo "- RAZORPAY_KEY_SECRET: your_razorpay_secret"
echo ""
echo "🎉 Your app will be live at: https://your-app-name.streamlit.app"