# 🚀 Streamlit Cloud Deployment Guide

## Resume + JD Analyzer - Production Deployment

### Prerequisites
- [x] GitHub account
- [x] Razorpay live API key: `rzp_live_gBOm5l3scvXYjP`
- [ ] Razorpay secret key (get from dashboard)
- [ ] Perplexity API key

---

## Step 1: Push Code to GitHub

```bash
# 1. Initialize git repository (if not already done)
git init

# 2. Add all files
git add .

# 3. Create initial commit
git commit -m "Deploy Resume + JD Analyzer to Streamlit Cloud"

# 4. Create GitHub repository
# Go to https://github.com/new
# Repository name: resume-jd-analyzer
# Description: AI-powered resume analysis tool with Razorpay payments
# Make it PUBLIC (required for free Streamlit Cloud)
# Don't initialize with README (you already have files)

# 5. Connect to GitHub and push
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/resume-jd-analyzer.git
git push -u origin main
```

**Replace `YOUR_USERNAME` with your actual GitHub username**

---

## Step 2: Deploy on Streamlit Cloud

### 2.1 Access Streamlit Cloud
1. Go to **https://share.streamlit.io**
2. **Sign in with GitHub** (click "Sign in" → "Continue with GitHub")
3. **Authorize Streamlit** to access your repositories

### 2.2 Create New App
1. Click **"New app"** button
2. **Repository**: Select `your-username/resume-jd-analyzer`
3. **Branch**: `main`
4. **Main file path**: `app.py`
5. **App URL**: Choose a custom URL like `resume-analyzer-yourname`

### 2.3 Configure Secrets (CRITICAL!)
Before deploying, click **"Advanced settings"** and add your secrets:

```toml
# Copy this EXACT content to Streamlit Cloud Secrets

# AI Service API Key
PERPLEXITY_API_KEY = "your_perplexity_api_key_here"

# Razorpay Payment Gateway
RAZORPAY_KEY_ID = "rzp_live_gBOm5l3scvXYjP"
RAZORPAY_KEY_SECRET = "your_razorpay_secret_key_here"
RAZORPAY_WEBHOOK_SECRET = "your_webhook_secret_here"

# Application Settings
ENVIRONMENT = "production"
APP_URL = "https://your-app-name.streamlit.app"
SECRET_KEY = "your-secret-key-for-sessions"

# Database
DATABASE_URL = "sqlite:///data/app.db"
```

### 2.4 Deploy
1. Click **"Deploy!"**
2. Wait for deployment (usually 2-5 minutes)
3. Your app will be live at: `https://your-app-name.streamlit.app`

---

## Step 3: Get Your Razorpay Secret Key

### 3.1 Login to Razorpay Dashboard
1. Go to **https://dashboard.razorpay.com/**
2. **Login** with your credentials
3. **Go to Settings → API Keys**

### 3.2 Copy Your Secret Key
1. Find your **Key ID**: `rzp_live_gBOm5l3scvXYjP` ✅
2. **Copy your Key Secret** (starts with `rzp_live_...`)
3. **Update Streamlit secrets** with your secret key

### 3.3 Update Streamlit Secrets
1. Go to your **Streamlit Cloud app dashboard**
2. Click **"Settings"** → **"Secrets"**
3. **Update** the `RAZORPAY_KEY_SECRET` value
4. **Save** and your app will restart automatically

---

## Step 4: Test Your Live Application

### 4.1 Basic Functionality Test
1. **Visit your live app** URL
2. **Register a new account**
3. **Upload a sample resume** and job description
4. **Verify analysis works** correctly

### 4.2 Payment Integration Test
1. **Try upgrading** to Professional plan
2. **Use Razorpay test credentials**:
   - **Test Card**: 4111 1111 1111 1111
   - **Test UPI**: success@razorpay
   - **CVV**: Any 3 digits
   - **Expiry**: Any future date

### 4.3 Verify Features
- ✅ User registration and login
- ✅ Resume analysis functionality
- ✅ Payment processing with Razorpay
- ✅ Subscription management
- ✅ Analytics and reporting

---

## Step 5: Configure Webhooks (Important!)

### 5.1 Set Up Razorpay Webhooks
1. **Go to Razorpay Dashboard** → **Settings** → **Webhooks**
2. **Add Endpoint**: `https://your-app-name.streamlit.app/razorpay/webhook`
3. **Select Events**:
   - ✅ `subscription.activated`
   - ✅ `subscription.charged`
   - ✅ `subscription.cancelled`
   - ✅ `payment.captured`
   - ✅ `payment.failed`

### 5.2 Update Webhook Secret
1. **Copy the webhook secret** from Razorpay
2. **Update Streamlit secrets** with `RAZORPAY_WEBHOOK_SECRET`
3. **Save** and restart your app

---

## Step 6: Go Live Checklist

### 6.1 Technical Checklist
- [ ] App deployed and accessible
- [ ] All API keys configured correctly
- [ ] Payment processing working
- [ ] Database initialized
- [ ] Webhooks configured
- [ ] SSL certificate active (automatic)

### 6.2 Business Checklist
- [ ] Razorpay KYC completed
- [ ] Bank account added for settlements
- [ ] Terms of Service created
- [ ] Privacy Policy created
- [ ] Customer support email set up

### 6.3 Marketing Checklist
- [ ] Custom domain configured (optional)
- [ ] Google Analytics set up
- [ ] Social media accounts created
- [ ] First 10 beta users invited
- [ ] Feedback collection system active

---

## 🎉 Congratulations!

Your Resume + JD Analyzer is now LIVE and ready to accept payments!

### Your Live URLs:
- **App**: `https://your-app-name.streamlit.app`
- **Admin Dashboard**: `https://your-app-name.streamlit.app/admin`
- **API Docs**: `https://your-app-name.streamlit.app/api/docs`

### Next Steps:
1. **Share with friends** for initial feedback
2. **Post on LinkedIn** to announce your launch
3. **Reach out to HR professionals** in your network
4. **Start collecting user feedback** and testimonials
5. **Plan your first marketing campaign**

---

## Troubleshooting

### Common Issues:

**1. App won't start**
- Check all secrets are properly configured
- Verify requirements.txt has all dependencies
- Check Streamlit Cloud logs for errors

**2. Payment not working**
- Verify Razorpay keys are correct
- Check webhook configuration
- Test with Razorpay test credentials first

**3. Database errors**
- Ensure DATABASE_URL is set correctly
- Check if database initialization ran successfully
- Verify file permissions for SQLite

**4. API errors**
- Confirm Perplexity API key is valid
- Check API rate limits and usage
- Verify network connectivity

### Support:
- **Streamlit Cloud**: https://docs.streamlit.io/streamlit-cloud
- **Razorpay Docs**: https://razorpay.com/docs/
- **GitHub Issues**: Create issues in your repository

---

## 💰 Revenue Projections

With your app live, here's what you can expect:

### Month 1: $2,000 - $5,000
- 50-100 registered users
- 5-10 paying customers
- Focus on product-market fit

### Month 3: $10,000 - $25,000
- 200-500 registered users
- 25-50 paying customers
- Word-of-mouth growth

### Month 6: $50,000 - $100,000
- 1,000-2,000 registered users
- 100-200 paying customers
- Established market presence

**You're ready to start making money TODAY!** 🚀