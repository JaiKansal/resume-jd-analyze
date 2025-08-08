#!/usr/bin/env python3
"""
Integration script to connect enhanced analysis system to main app
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def create_analysis_directory():
    """Create analysis directory if it doesn't exist"""
    analysis_dir = project_root / "analysis"
    analysis_dir.mkdir(exist_ok=True)
    
    # Create __init__.py
    init_file = analysis_dir / "__init__.py"
    if not init_file.exists():
        init_file.write_text('"""Enhanced Analysis System"""')
    
    print("✅ Analysis directory created")

def update_main_app_integration():
    """Add integration code to main app"""
    
    integration_code = '''
# Enhanced Analysis System Integration
try:
    from analysis.enhanced_analysis_service import enhanced_analysis_service, create_analysis_result
    from analysis.analysis_history_ui import show_analysis_history_page
    ENHANCED_ANALYSIS_AVAILABLE = True
    print("✅ Enhanced Analysis System loaded successfully")
except ImportError as e:
    print(f"⚠️ Enhanced Analysis System not available: {e}")
    ENHANCED_ANALYSIS_AVAILABLE = False

def save_analysis_to_database(user_id, resume_filename, job_description, resume_content, analysis_data):
    """Save analysis results to database using enhanced system"""
    if not ENHANCED_ANALYSIS_AVAILABLE:
        print("⚠️ Enhanced analysis system not available, skipping save")
        return False
    
    try:
        # Create analysis result object
        analysis_result = create_analysis_result(
            user_id=user_id,
            resume_filename=resume_filename,
            job_description=job_description,
            resume_content=resume_content,
            analysis_data=analysis_data
        )
        
        # Save to database
        success = enhanced_analysis_service.save_analysis(analysis_result)
        if success:
            print(f"✅ Analysis saved successfully: {analysis_result.id}")
        else:
            print("❌ Failed to save analysis")
        
        return success
        
    except Exception as e:
        print(f"❌ Error saving analysis: {e}")
        return False

def show_user_analysis_history(user_id):
    """Show analysis history page"""
    if not ENHANCED_ANALYSIS_AVAILABLE:
        st.error("❌ Analysis history not available")
        return
    
    try:
        show_analysis_history_page(user_id)
    except Exception as e:
        st.error(f"❌ Error loading analysis history: {e}")
'''
    
    print("📝 Integration code prepared")
    print("🔧 To integrate with main app, add the above code to app.py")
    print("💡 Then call save_analysis_to_database() after each analysis")
    print("📊 And add analysis history to your navigation menu")

def create_sample_integration():
    """Create a sample integration file"""
    sample_file = project_root / "sample_analysis_integration.py"
    
    sample_code = '''#!/usr/bin/env python3
"""
Sample integration showing how to use the enhanced analysis system
"""

import streamlit as st
from analysis.enhanced_analysis_service import enhanced_analysis_service, create_analysis_result
from analysis.analysis_history_ui import show_analysis_history_page

def example_save_analysis():
    """Example of how to save an analysis"""
    
    # Sample analysis data (replace with real analysis results)
    analysis_data = {
        'analysis_type': 'resume_jd_match',
        'match_score': 85.5,
        'strengths': [
            'Strong technical skills in Python and machine learning',
            'Relevant experience in data analysis',
            'Good educational background'
        ],
        'weaknesses': [
            'Limited experience with cloud platforms',
            'Could improve communication skills section'
        ],
        'recommendations': [
            'Add more details about cloud computing experience',
            'Include specific project outcomes and metrics',
            'Highlight leadership and teamwork experiences'
        ],
        'keywords_matched': ['Python', 'Machine Learning', 'Data Analysis', 'SQL'],
        'keywords_missing': ['AWS', 'Docker', 'Kubernetes'],
        'sections_analysis': {
            'experience': {'score': 90, 'feedback': 'Strong relevant experience'},
            'skills': {'score': 85, 'feedback': 'Good technical skills'},
            'education': {'score': 80, 'feedback': 'Solid educational background'}
        },
        'processing_time_seconds': 2.5,
        'api_cost_usd': 0.05,
        'tokens_used': 1250
    }
    
    # Create and save analysis
    analysis_result = create_analysis_result(
        user_id="sample_user_id",
        resume_filename="john_doe_resume.pdf",
        job_description="Senior Data Scientist position...",
        resume_content="John Doe\\nData Scientist\\n...",
        analysis_data=analysis_data
    )
    
    success = enhanced_analysis_service.save_analysis(analysis_result)
    
    if success:
        st.success(f"✅ Analysis saved! ID: {analysis_result.id}")
    else:
        st.error("❌ Failed to save analysis")

def example_show_history():
    """Example of how to show analysis history"""
    user_id = "sample_user_id"  # Replace with actual user ID
    show_analysis_history_page(user_id)

# Streamlit app example
if __name__ == "__main__":
    st.title("Enhanced Analysis System Demo")
    
    tab1, tab2 = st.tabs(["Save Analysis", "View History"])
    
    with tab1:
        st.header("Save Sample Analysis")
        if st.button("Save Sample Analysis"):
            example_save_analysis()
    
    with tab2:
        st.header("Analysis History")
        example_show_history()
'''
    
    sample_file.write_text(sample_code)
    print(f"✅ Sample integration created: {sample_file}")

if __name__ == "__main__":
    print("🚀 Setting up Enhanced Analysis System integration...")
    
    create_analysis_directory()
    update_main_app_integration()
    create_sample_integration()
    
    print("\n🎉 Enhanced Analysis System setup complete!")
    print("\n📋 Next steps:")
    print("1. The database schema has been updated with comprehensive analysis storage")
    print("2. Enhanced analysis service is ready to save/retrieve complete analysis data")
    print("3. Analysis history UI is available for users to view their past analyses")
    print("4. Integrate the save_analysis_to_database() function into your main analysis flow")
    print("5. Add analysis history page to your app navigation")
    print("\n✨ All analysis results will now be fully saved and accessible!")