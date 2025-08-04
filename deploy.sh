#!/bin/bash
# Streamlit Cloud deployment script
# This runs automatically when your app deploys

echo "🚀 Starting Razorpay deployment fix..."

# Install pip packages with specific versions
pip install --upgrade pip
pip install razorpay>=1.3.0 --no-cache-dir
pip install requests>=2.25.0 --no-cache-dir

# Verify installation
python -c "import razorpay; print('✅ Razorpay installed:', razorpay.__version__ if hasattr(razorpay, '__version__') else 'Unknown')"

echo "✅ Deployment fix complete"
