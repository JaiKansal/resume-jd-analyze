#!/usr/bin/env python3
"""
Resume Matcher AI Setup Utility
Helps users configure the application environment and validate their setup.
"""

import os
import sys
from pathlib import Path
from resume_matcher_ai.utils import (
    setup_environment, 
    display_setup_instructions, 
    validate_api_key,
    get_usage_statistics
)

def main():
    """Main setup utility function"""
    print("=" * 70)
    print("🚀 RESUME MATCHER AI - SETUP UTILITY")
    print("=" * 70)
    print()
    
    print("This utility will help you configure Resume Matcher AI.")
    print("Choose an option:")
    print()
    print("1. 🔧 Run complete setup and validation")
    print("2. 📋 Display setup instructions")
    print("3. ✅ Validate current configuration")
    print("4. 📊 Show usage statistics")
    print("5. 🔑 Test API key")
    print("6. 📁 Create .env file from template")
    print("7. ❌ Exit")
    print()
    
    while True:
        try:
            choice = input("Enter your choice (1-7): ").strip()
            
            if choice == '1':
                run_complete_setup()
            elif choice == '2':
                display_setup_instructions()
            elif choice == '3':
                validate_current_configuration()
            elif choice == '4':
                show_usage_statistics()
            elif choice == '5':
                test_api_key()
            elif choice == '6':
                create_env_file()
            elif choice == '7':
                print("\nExiting setup utility. Good luck with Resume Matcher AI!")
                break
            else:
                print("❌ Invalid choice. Please enter a number between 1-7.")
                continue
            
            print("\n" + "-" * 50)
            print("Choose another option or press 7 to exit:")
            
        except KeyboardInterrupt:
            print("\n\nSetup cancelled by user. Goodbye!")
            break
        except EOFError:
            print("\n\nSetup terminated. Goodbye!")
            break

def run_complete_setup():
    """Run complete setup and validation"""
    print("\n🔧 RUNNING COMPLETE SETUP...")
    print()
    
    setup_result = setup_environment()
    
    if setup_result['success']:
        print("✅ SETUP COMPLETED SUCCESSFULLY!")
        print()
        
        # Display setup steps
        for step in setup_result['setup_steps']:
            print(step)
        
        # Display warnings if any
        if setup_result['warnings']:
            print("\n⚠️  WARNINGS:")
            for warning in setup_result['warnings']:
                print(f"   • {warning}")
        
        print("\n🎉 Your Resume Matcher AI is ready to use!")
        print("   You can now run the main application.")
        
    else:
        print("❌ SETUP FAILED")
        print()
        
        for error in setup_result['errors']:
            print(f"❌ {error}")
        
        print("\n💡 NEXT STEPS:")
        print("   1. Follow the setup instructions below")
        print("   2. Run this setup utility again to validate")
        print()
        
        display_setup_instructions()

def validate_current_configuration():
    """Validate the current configuration without full setup"""
    print("\n✅ VALIDATING CURRENT CONFIGURATION...")
    print()
    
    # Check for API key
    api_key = os.getenv('PERPLEXITY_API_KEY')
    if not api_key:
        print("❌ PERPLEXITY_API_KEY environment variable not found")
        print("   Set your API key using: export PERPLEXITY_API_KEY='your-key-here'")
        print("   Or create a .env file with your API key")
        return
    
    print("✅ API key found in environment")
    
    # Validate API key format
    if not api_key.startswith('pplx-'):
        print("⚠️  WARNING: API key doesn't start with 'pplx-'")
        print("   Make sure you're using a valid Perplexity API key")
    else:
        print("✅ API key format looks correct")
    
    # Test API key connectivity
    print("\n🔑 Testing API key connectivity...")
    try:
        if validate_api_key(api_key):
            print("✅ API key validation successful!")
            print("   Your key is valid and can connect to Perplexity API")
        else:
            print("❌ API key validation failed")
            print("   Check your key and internet connection")
    except Exception as e:
        print(f"⚠️  Could not validate API key: {str(e)}")
        print("   This might be due to network issues")
    
    # Check .env file
    env_file = Path('.env')
    if env_file.exists():
        print("\n✅ .env file found")
        try:
            with open(env_file, 'r') as f:
                content = f.read()
                if 'PERPLEXITY_API_KEY' in content:
                    print("✅ .env file contains API key configuration")
                else:
                    print("⚠️  .env file exists but doesn't contain API key")
        except Exception:
            print("⚠️  Could not read .env file")
    else:
        print("ℹ️  No .env file found (using environment variables)")
    
    print("\n🎯 CONFIGURATION SUMMARY:")
    print("   • API Key: ✅ Present" if api_key else "   • API Key: ❌ Missing")
    print("   • Format: ✅ Valid" if api_key and api_key.startswith('pplx-') else "   • Format: ⚠️  Check required")
    print("   • .env File: ✅ Present" if env_file.exists() else "   • .env File: ℹ️  Not used")

def show_usage_statistics():
    """Display usage statistics"""
    print("\n📊 USAGE STATISTICS...")
    print()
    
    try:
        # Show stats for different periods
        periods = [7, 30]
        
        for days in periods:
            stats = get_usage_statistics(days)
            
            print(f"📈 LAST {days} DAYS:")
            print(f"   • Total API Calls: {stats['total_calls']}")
            print(f"   • Successful Calls: {stats['successful_calls']}")
            print(f"   • Failed Calls: {stats['failed_calls']}")
            print(f"   • Total Tokens Used: {stats['total_tokens']:,}")
            print(f"   • Estimated Cost: ${stats['total_cost']:.3f}")
            
            if stats['average_processing_time'] > 0:
                print(f"   • Avg Processing Time: {stats['average_processing_time']:.1f}s")
            
            print()
        
        if all(get_usage_statistics(7)['total_calls'] == 0 for _ in [7, 30]):
            print("ℹ️  No usage data found. Statistics will appear after you use the application.")
    
    except Exception as e:
        print(f"❌ Could not load usage statistics: {str(e)}")
        print("   This is normal if you haven't used the application yet.")

def test_api_key():
    """Test API key functionality"""
    print("\n🔑 TESTING API KEY...")
    print()
    
    api_key = os.getenv('PERPLEXITY_API_KEY')
    if not api_key:
        print("❌ No API key found in environment variables")
        print("   Set your API key first: export PERPLEXITY_API_KEY='your-key-here'")
        return
    
    print(f"🔍 Testing API key: {api_key[:12]}...")
    
    try:
        print("   • Checking format...", end=" ")
        if api_key.startswith('pplx-') and len(api_key) > 20:
            print("✅")
        else:
            print("⚠️  Format may be incorrect")
        
        print("   • Testing connectivity...", end=" ")
        if validate_api_key(api_key):
            print("✅")
            print("\n🎉 API key test successful!")
            print("   Your key is working correctly.")
        else:
            print("❌")
            print("\n❌ API key test failed")
            print("   Check your key and try again.")
    
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")

def create_env_file():
    """Create .env file from template"""
    print("\n📁 CREATING .ENV FILE...")
    print()
    
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if env_file.exists():
        response = input("⚠️  .env file already exists. Overwrite? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("   Cancelled. Existing .env file preserved.")
            return
    
    if not env_example.exists():
        print("❌ .env.example template not found")
        print("   Creating a basic .env file...")
        
        # Create basic .env content
        env_content = """# Resume Matcher AI Configuration
# Copy this file to .env and fill in your actual values

# Perplexity API Configuration
PERPLEXITY_API_KEY=your-perplexity-api-key-here
PERPLEXITY_API_URL=https://api.perplexity.ai
MAX_TOKENS=4000
API_TIMEOUT=30

# Usage Tracking Configuration (Optional)
ENABLE_USAGE_TRACKING=true
USAGE_LOG_FILE=usage_log.json
COST_ALERT_THRESHOLD=10.00

# Application Configuration (Optional)
DEBUG_MODE=false
LOG_LEVEL=INFO
"""
    else:
        # Copy from template
        with open(env_example, 'r') as f:
            env_content = f.read()
    
    # Write .env file
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print("✅ .env file created successfully!")
        print()
        print("📝 NEXT STEPS:")
        print("   1. Edit the .env file with your actual API key")
        print("   2. Replace 'your-perplexity-api-key-here' with your real key")
        print("   3. Save the file")
        print("   4. Run this setup utility again to validate")
        print()
        print(f"   File location: {env_file.absolute()}")
        
    except Exception as e:
        print(f"❌ Failed to create .env file: {str(e)}")

if __name__ == "__main__":
    main()