# 🇮🇳 Razorpay Setup Guide for Resume + JD Analyzer

## Why Razorpay for Indian Businesses?

### ✅ **Perfect for India**
- **RBI Compliant** - Fully regulated Indian payment gateway
- **Low Fees** - 2% domestic, 3% international (vs Stripe's 4.9%)
- **Local Payment Methods** - UPI, Net Banking, Wallets, EMI
- **INR Support** - No currency conversion fees
- **Same Day Settlements** - Get money faster

### 💰 **Cost Comparison**
| Transaction | Razorpay | Stripe | PayU | Savings |
|-------------|----------|--------|------|---------|
| ₹1,499 (Professional) | ₹30 | ₹73 | ₹43 | ₹43/month |
| ₹7,999 (Business) | ₹160 | ₹392 | ₹260 | ₹232/month |
| ₹39,999 (Enterprise) | ₹800 | ₹1,960 | ₹1,300 | ₹1,160/month |

**Annual Savings: ₹5,000 - ₹14,000 per customer!**

## 🚀 **Step-by-Step Setup**

### **Step 1: Create Razorpay Account**

1. **Visit** https://razorpay.com
2. **Click** "Sign Up" → "I'm a Business"
3. **Enter Details**:
   - Business Email
   - Mobile Number
   - Business Name: "Resume + JD Analyzer" (or your company name)

### **Step 2: Complete KYC Verification**

**Required Documents:**
- ✅ **PAN Card** (Individual or Business)
- ✅ **Bank Account Details** (Current/Savings account)
- ✅ **Address Proof** (Aadhaar, Passport, Utility Bill)
- ✅ **Business Proof** (GST Certificate, Shop License) - *if applicable*

**Verification Time:** 2-3 business days

### **Step 3: Get API Credentials**

1. **Login** to Razorpay Dashboard
2. **Go to** Settings → API Keys
3. **Generate** Test Keys first
4. **Copy** Key ID and Key Secret

```bash
# Test Credentials (for development)
RAZORPAY_KEY_ID="rzp_test_xxxxxxxxxx"
RAZORPAY_KEY_SECRET="xxxxxxxxxxxxxxxxxx"

# Live Credentials (after KYC approval)
RAZORPAY_KEY_ID="rzp_live_xxxxxxxxxx"  
RAZORPAY_KEY_SECRET="xxxxxxxxxxxxxxxxxx"
```

### **Step 4: Configure Your Application**

```bash
# Set environment variables
export RAZORPAY_KEY_ID="rzp_test_xxxxxxxxxx"
export RAZORPAY_KEY_SECRET="xxxxxxxxxxxxxxxxxx"
export RAZORPAY_WEBHOOK_SECRET="xxxxxxxxxxxxxxxxxx"

# Test the integration
python3 -c "
from billing.razorpay_service import razorpay_service
print('Razorpay Status:', 'Connected' if razorpay_service.client else 'Not Connected')
"
```

### **Step 5: Set Up Webhooks**

1. **Go to** Settings → Webhooks in Razorpay Dashboard
2. **Add Endpoint**: `https://yourdomain.com/razorpay/webhook`
3. **Select Events**:
   - ✅ `subscription.activated`
   - ✅ `subscription.charged`
   - ✅ `subscription.cancelled`
   - ✅ `payment.captured`
   - ✅ `payment.failed`

4. **Copy Webhook Secret** and add to environment variables

### **Step 6: Configure Pricing (Already Done!)**

Your app automatically uses Indian pricing:

| Plan | Monthly (INR) | Annual (INR) | USD Equivalent |
|------|---------------|--------------|----------------|
| **Free** | ₹0 | ₹0 | $0 |
| **Professional** | ₹1,499 | ₹14,990 | ~$18 |
| **Business** | ₹7,999 | ₹79,990 | ~$96 |
| **Enterprise** | ₹39,999 | ₹399,990 | ~$480 |

*Prices optimized for Indian purchasing power*

## 💳 **Payment Methods Available**

### **For Indian Customers**
- 💳 **Credit/Debit Cards** - Visa, Mastercard, RuPay, Amex
- 📱 **UPI** - Google Pay, PhonePe, Paytm, BHIM
- 🏦 **Net Banking** - All major Indian banks
- 👛 **Wallets** - Paytm, Mobikwik, Freecharge
- 📊 **EMI** - No-cost EMI options available

### **For International Customers**
- 💳 **International Cards** - Visa, Mastercard
- 🌐 **Higher Processing Fee** - 3% (still cheaper than alternatives)

## 🧪 **Testing Your Integration**

### **Test Card Numbers**
```
# Successful Payment
Card: 4111 1111 1111 1111
CVV: Any 3 digits
Expiry: Any future date

# Failed Payment  
Card: 4000 0000 0000 0002
CVV: Any 3 digits
Expiry: Any future date

# UPI Testing
UPI ID: success@razorpay
```

### **Test Your App**
```bash
# 1. Start your application
streamlit run app.py

# 2. Register a test user
# 3. Try upgrading to Professional plan
# 4. Use test card numbers above
# 5. Check Razorpay dashboard for test payments
```

## 🏦 **Bank Account Setup**

### **Settlement Account**
1. **Add Bank Account** in Razorpay Dashboard
2. **Verify Account** - Razorpay will make small deposits
3. **Confirm Amounts** to activate settlements

### **Settlement Schedule**
- **Default**: Daily settlements
- **Timing**: T+2 days (2 business days after payment)
- **Minimum**: ₹10 (can be changed)
- **Same Day**: Available for verified businesses

## 📊 **Dashboard & Analytics**

### **Key Metrics to Track**
- **Total Revenue** - Monthly Recurring Revenue (MRR)
- **Success Rate** - Payment success percentage
- **Customer Acquisition** - New subscribers per month
- **Churn Rate** - Cancelled subscriptions

### **Razorpay Dashboard Features**
- 📈 **Real-time Analytics** - Revenue, transactions, success rates
- 💰 **Settlement Reports** - Track payouts to your bank
- 👥 **Customer Management** - View customer payment history
- 🔄 **Subscription Management** - Handle recurring payments
- 📧 **Smart Collect** - Send payment links via email/SMS

## 🚨 **Important Compliance**

### **GST Registration**
- **Required if** annual turnover > ₹20 lakhs
- **GST Rate** - 18% on software services
- **Razorpay** handles GST calculation automatically

### **Income Tax**
- **TDS** - 2% TDS on payments > ₹40,000 per year per customer
- **Advance Tax** - Pay quarterly based on income
- **ITR Filing** - Include Razorpay income in tax returns

### **Business Registration**
- **Sole Proprietorship** - Use personal PAN
- **Private Limited** - Get CIN and business PAN
- **LLP** - Get LLP registration

## 🎯 **Go-Live Checklist**

### **Before Accepting Real Payments**
- [ ] Complete Razorpay KYC verification
- [ ] Add and verify bank account
- [ ] Test all payment flows with test cards
- [ ] Set up webhooks and test them
- [ ] Switch to live API keys
- [ ] Configure GST settings (if applicable)
- [ ] Set up settlement schedule
- [ ] Create Terms of Service and Privacy Policy

### **Legal Documents Required**
- [ ] **Terms of Service** - User agreement
- [ ] **Privacy Policy** - Data handling policy
- [ ] **Refund Policy** - Cancellation terms
- [ ] **Pricing Page** - Clear pricing display

## 🚀 **Launch Strategy**

### **Week 1: Soft Launch**
- [ ] Deploy with Razorpay test mode
- [ ] Get 5-10 friends to test payments
- [ ] Fix any issues found
- [ ] Switch to live mode

### **Week 2: Beta Launch**
- [ ] Announce to personal network
- [ ] Target 25-50 beta users
- [ ] Collect feedback and testimonials
- [ ] Optimize conversion funnel

### **Month 1: Public Launch**
- [ ] Content marketing (LinkedIn, Twitter)
- [ ] Community engagement (Reddit, Discord)
- [ ] Reach out to HR professionals
- [ ] Target ₹25,000-50,000 MRR

## 💡 **Pro Tips for Success**

### **Pricing Strategy**
- **Start with current prices** - They're optimized for Indian market
- **Offer annual discounts** - 17% savings encourages longer commitments
- **Free trial** - 14-day trial for Professional plan
- **Money-back guarantee** - 30-day refund policy builds trust

### **Customer Acquisition**
- **LinkedIn outreach** - Target HR professionals and recruiters
- **Content marketing** - Write about hiring trends, resume tips
- **Referral program** - Give 1 month free for successful referrals
- **Community building** - Join HR and recruiting communities

### **Retention Strategy**
- **Onboarding** - Guide new users through first analysis
- **Customer success** - Proactive support for high-value customers
- **Feature updates** - Regular improvements based on feedback
- **Case studies** - Showcase customer success stories

## 📞 **Getting Help**

### **Razorpay Support**
- **Email**: support@razorpay.com
- **Phone**: 080-68727374
- **Chat**: Available in dashboard
- **Docs**: https://razorpay.com/docs/

### **Technical Issues**
- Check Razorpay dashboard logs
- Verify webhook signatures
- Test with different payment methods
- Monitor settlement reports

## 🎉 **You're Ready to Launch!**

With Razorpay integration, you can:
- ✅ Accept payments from Indian customers with 0% currency conversion
- ✅ Offer UPI, cards, net banking, and wallet payments
- ✅ Save 40-60% on payment processing fees
- ✅ Get faster settlements (T+2 vs T+7 for international gateways)
- ✅ Provide better customer experience with local payment methods

**Next Step**: Create your Razorpay account and start the KYC process today!

---

**Need help?** The Razorpay integration is already built into your app. Just add your API keys and you're ready to start accepting payments! 🚀