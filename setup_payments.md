# Payment Setup Guide

## 1. Stripe Account Setup

### Create Stripe Account
1. Go to https://stripe.com and click "Start now"
2. Enter your email and create password
3. Verify your email address

### Business Information
1. **Business type**: Choose "Individual" or "Company"
2. **Business details**: 
   - Business name: "Resume + JD Analyzer" (or your company name)
   - Industry: "Software"
   - Website: Your domain (or leave blank initially)
3. **Personal information**: Your legal name, address, SSN/Tax ID
4. **Bank account**: Add your bank account for payouts

### Get API Keys
1. Go to Dashboard → Developers → API keys
2. Copy your **Publishable key** and **Secret key**
3. For testing, use the test keys first

## 2. Configure Your Application

### Set Environment Variables
```bash
# Add to your .env file or export directly
export STRIPE_SECRET_KEY="sk_test_..." # Your secret key
export STRIPE_PUBLISHABLE_KEY="pk_test_..." # Your publishable key
export STRIPE_WEBHOOK_SECRET="whsec_..." # Webhook secret (after setup)
```

### Test Mode vs Live Mode
- **Test Mode**: Use test keys (sk_test_..., pk_test_...)
- **Live Mode**: Use live keys (sk_live_..., pk_live_...) for real payments

## 3. Webhook Setup (Important!)

### Create Webhook Endpoint
1. In Stripe Dashboard → Developers → Webhooks
2. Click "Add endpoint"
3. Endpoint URL: `https://yourdomain.com/stripe/webhook`
4. Select events:
   - `customer.subscription.created`
   - `customer.subscription.updated` 
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`

### Get Webhook Secret
1. After creating webhook, click on it
2. Copy the "Signing secret" (starts with whsec_...)
3. Add to your environment variables

## 4. Pricing Configuration

Your app already has these prices configured:
- **Free**: $0/month (3 analyses)
- **Professional**: $19/month ($190/year)
- **Business**: $99/month ($990/year) 
- **Enterprise**: $500/month ($5000/year)

## 5. Tax Settings (Important!)

### US Sales Tax
1. Go to Stripe Dashboard → Settings → Tax
2. Enable automatic tax collection
3. Configure tax rates for your state

### International VAT
1. Enable VAT collection for EU customers
2. Set up tax rates for different countries

## 6. Payout Schedule

### Default Settings
- **Frequency**: Daily (can change to weekly/monthly)
- **Payout time**: 2 business days after payment
- **Minimum payout**: $1

### Bank Account Verification
- Stripe will make 2 small deposits
- Verify amounts in your bank account
- This enables automatic payouts

## 7. Testing Payments

### Test Credit Cards
```
Visa: 4242 4242 4242 4242
Mastercard: 5555 5555 5555 4444
Declined: 4000 0000 0000 0002
```

### Test Subscription Flow
1. Start your app: `streamlit run app.py`
2. Register a test user
3. Try upgrading to Professional plan
4. Use test credit card numbers
5. Check Stripe dashboard for test payments

## 8. Go Live Checklist

### Before Accepting Real Payments
- [ ] Complete Stripe account verification
- [ ] Add real bank account
- [ ] Set up webhooks
- [ ] Test all payment flows
- [ ] Switch to live API keys
- [ ] Update webhook URL to production domain
- [ ] Configure tax settings
- [ ] Set up email notifications

### Legal Requirements
- [ ] Terms of Service
- [ ] Privacy Policy  
- [ ] Refund Policy
- [ ] Business registration (if required)
- [ ] Sales tax registration (if required)