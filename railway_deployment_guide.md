# 🚀 Railway Deployment Guide - Private Repository

## Resume + JD Analyzer - Secure Production Deployment

### Why Railway Over Streamlit Cloud?
- ✅ **Private repositories** supported
- ✅ **Better performance** and reliability  
- ✅ **Professional grade** infrastructure
- ✅ **Custom domains** included
- ✅ **Database hosting** available
- ✅ **Only $5-15/month**

---

## Step 1: Install Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Or using curl
curl -fsSL https://railway.app/install.sh | sh

# Verify installation
railway --version
```

---

## Step 2: Create Railway Account

1. Go to **https://railway.app**
2. **Sign up** with GitHub (but keep repo private)
3. **Verify** your email

---

## Step 3: Deploy Your App

```bash
# Login to Railway
railway login

# Initialize Railway project
railway init

# Set environment variables
railway variables set PERPLEXITY_API_KEY=your_perplexity_key_here
railway variables set RAZORPAY_KEY_ID=rzp_live_gBOm5l3scvXYjP
railway variables set RAZORPAY_KEY_SECRET=your_razorpay_secret_key_here
railway variables set ENVIRONMENT=production
railway variables set PORT=8501

# Deploy your app
railway up

# Get your live URL
railway domain
```

---

## Step 4: Configure Custom Domain (Optional)

```bash
# Add custom domain
railway domain add yourdomain.com

# Railway will provide SSL certificate automatically
```

---

## Step 5: Set Up Database (If Needed)

```bash
# Add PostgreSQL database
railway add postgresql

# Railway will automatically set DATABASE_URL
```

---

## Alternative: Keep Repository Private

If you prefer Streamlit Cloud, here's how to protect your IP:

### Method 1: Code Obfuscation
```python
# Create a separate private package for core logic
# Only expose the UI layer in public repo

# In your public app.py:
try:
    from private_analyzer import analyze_resume  # Private module
except ImportError:
    # Fallback to basic analysis
    from basic_analyzer import analyze_resume
```

### Method 2: API-Based Architecture
```python
# Deploy core logic as private API
# Public app only handles UI and calls your private API

import requests

def analyze_resume(resume_text, jd_text):
    response = requests.post(
        "https://your-private-api.com/analyze",
        json={"resume": resume_text, "jd": jd_text},
        headers={"Authorization": f"Bearer {API_KEY}"}
    )
    return response.json()
```

### Method 3: Environment-Based Logic
```python
# Keep sensitive logic in environment variables
import os

# Core analysis logic stored as environment variable
ANALYSIS_LOGIC = os.getenv('ANALYSIS_LOGIC', 'basic')

if ANALYSIS_LOGIC == 'advanced':
    # Use your proprietary algorithm
    pass
else:
    # Use basic fallback
    pass
```

---

## 💰 Cost Comparison

| Platform | Cost | Privacy | Performance | Scalability |
|----------|------|---------|-------------|-------------|
| **Railway** | $5-15/month | ✅ Private | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Streamlit Cloud** | $20/month | ✅ Private | ⭐⭐⭐ | ⭐⭐⭐ |
| **Streamlit Free** | FREE | ❌ Public | ⭐⭐ | ⭐⭐ |

---

## 🎯 Recommended Approach

### **For Maximum IP Protection:**
1. **Deploy to Railway** ($5-15/month)
2. **Keep repository private**
3. **Use environment variables** for sensitive config
4. **Separate core logic** into private modules

### **For Budget-Conscious:**
1. **Use Streamlit Cloud free** with code obfuscation
2. **Keep core AI logic** in environment variables
3. **Use API-based architecture** for sensitive parts

---

## 🚀 Quick Railway Deployment

Want to deploy to Railway right now? Here's the fastest way:

```bash
# 1. Install Railway CLI
curl -fsSL https://railway.app/install.sh | sh

# 2. Login and deploy
railway login
railway init resume-jd-analyzer
railway up

# 3. Set your environment variables
railway variables set RAZORPAY_KEY_ID=rzp_live_gBOm5l3scvXYjP
railway variables set RAZORPAY_KEY_SECRET=your_secret_key_here
railway variables set PERPLEXITY_API_KEY=your_perplexity_key_here

# 4. Your app will be live!
railway domain
```

**Your app will be live in 5 minutes with full IP protection!**

---

## 🔒 IP Protection Checklist

- [ ] Repository kept private
- [ ] API keys in environment variables only
- [ ] Core algorithms obfuscated or separated
- [ ] No hardcoded business logic in public code
- [ ] Database credentials secured
- [ ] Webhook secrets protected
- [ ] Custom domain with SSL

**With Railway, you get professional deployment + IP protection for just $5-15/month!**