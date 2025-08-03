#!/bin/bash

# Resume + JD Analyzer - Deployment Script
# This script helps deploy the web application quickly

set -e

echo "🎯 Resume + JD Analyzer - Deployment Script"
echo "============================================"

# Check if API key is set
if [ -z "$PERPLEXITY_API_KEY" ]; then
    echo "❌ PERPLEXITY_API_KEY environment variable is not set!"
    echo ""
    echo "Please set your API key:"
    echo "export PERPLEXITY_API_KEY='pplx-your-api-key-here'"
    echo ""
    echo "Get your API key from: https://www.perplexity.ai/settings/api"
    exit 1
fi

echo "✅ API key found: ${PERPLEXITY_API_KEY:0:10}...${PERPLEXITY_API_KEY: -4}"

# Check deployment method
echo ""
echo "Choose deployment method:"
echo "1) Local development server"
echo "2) Docker container"
echo "3) Docker Compose (with nginx)"
echo "4) Production setup"

read -p "Enter choice (1-4): " choice

case $choice in
    1)
        echo "🚀 Starting local development server..."
        
        # Install dependencies if needed
        if [ ! -d "venv" ]; then
            echo "📦 Creating virtual environment..."
            python3 -m venv venv
            source venv/bin/activate
            pip install -r requirements.txt
        else
            source venv/bin/activate
        fi
        
        # Create necessary directories
        mkdir -p uploads logs
        
        # Start Streamlit
        echo "🌐 Starting Streamlit on http://localhost:8501"
        streamlit run app.py --server.port 8501
        ;;
        
    2)
        echo "🐳 Building and running Docker container..."
        
        # Build Docker image
        docker build -t resume-analyzer .
        
        # Run container
        docker run -d \
            --name resume-analyzer \
            -p 8501:8501 \
            -e PERPLEXITY_API_KEY="$PERPLEXITY_API_KEY" \
            -v $(pwd)/uploads:/app/uploads \
            -v $(pwd)/logs:/app/logs \
            resume-analyzer
        
        echo "✅ Container started! Access at http://localhost:8501"
        echo "📊 View logs: docker logs resume-analyzer"
        echo "🛑 Stop: docker stop resume-analyzer"
        ;;
        
    3)
        echo "🐳 Starting with Docker Compose..."
        
        # Create .env file if it doesn't exist
        if [ ! -f ".env" ]; then
            echo "PERPLEXITY_API_KEY=$PERPLEXITY_API_KEY" > .env
            echo "📝 Created .env file"
        fi
        
        # Start services
        docker-compose up -d
        
        echo "✅ Services started!"
        echo "🌐 Web app: http://localhost:8501"
        echo "📊 View logs: docker-compose logs -f"
        echo "🛑 Stop: docker-compose down"
        ;;
        
    4)
        echo "🏭 Production setup..."
        
        # Create production directories
        mkdir -p uploads logs ssl
        
        # Set proper permissions
        chmod 755 uploads logs
        
        # Create systemd service file
        cat > resume-analyzer.service << EOF
[Unit]
Description=Resume + JD Analyzer Web Application
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=$(pwd)
Environment=PERPLEXITY_API_KEY=$PERPLEXITY_API_KEY
Environment=STREAMLIT_SERVER_PORT=8501
Environment=STREAMLIT_SERVER_ADDRESS=0.0.0.0
ExecStart=$(which streamlit) run app.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
        
        echo "📝 Created systemd service file: resume-analyzer.service"
        echo ""
        echo "To complete production setup:"
        echo "1. sudo cp resume-analyzer.service /etc/systemd/system/"
        echo "2. sudo systemctl daemon-reload"
        echo "3. sudo systemctl enable resume-analyzer"
        echo "4. sudo systemctl start resume-analyzer"
        echo "5. Configure nginx reverse proxy (optional)"
        ;;
        
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "📚 Documentation:"
echo "   • README_WEB.md - Complete web app guide"
echo "   • README.md - Core functionality documentation"
echo "   • USAGE_EXAMPLES.md - Advanced usage examples"
echo ""
echo "🔧 Troubleshooting:"
echo "   • Check logs for any errors"
echo "   • Verify API key is correctly set"
echo "   • Ensure all dependencies are installed"
echo ""
echo "💡 Need help? Check the documentation or contact support!"