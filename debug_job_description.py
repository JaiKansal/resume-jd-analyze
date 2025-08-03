#!/usr/bin/env python3
"""
Debug script to check job description content
"""

def check_job_description():
    file_path = input("Enter path to job description file: ").strip().strip('"\'')
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"\n📊 FILE ANALYSIS:")
        print(f"File size: {len(content)} characters")
        print(f"Word count: {len(content.split())} words")
        print(f"Line count: {len(content.splitlines())} lines")
        
        # Check for problematic characters
        problematic_chars = ['�', '\x00', '\ufffd']
        has_problems = any(char in content for char in problematic_chars)
        
        if has_problems:
            print("⚠️  Found problematic characters in file")
        else:
            print("✅ No problematic characters found")
        
        # Show first few lines
        print(f"\n📝 FIRST 200 CHARACTERS:")
        print(repr(content[:200]))
        
        # Check if it looks like a job description
        job_indicators = ['job', 'position', 'role', 'responsibilities', 'requirements', 'qualifications', 'experience', 'skills']
        found_indicators = [word for word in job_indicators if word.lower() in content.lower()]
        
        print(f"\n🔍 JOB DESCRIPTION INDICATORS FOUND:")
        print(f"Found: {', '.join(found_indicators)}")
        
        if len(found_indicators) < 3:
            print("⚠️  This might not be a proper job description")
        else:
            print("✅ Looks like a valid job description")
        
        # Check length
        if len(content) > 50000:
            print("⚠️  File is very long (>50k chars) - this might cause API issues")
        elif len(content) < 50:
            print("⚠️  File is very short (<50 chars) - might not be enough content")
        else:
            print("✅ File length looks good")
            
    except Exception as e:
        print(f"❌ Error reading file: {e}")

if __name__ == "__main__":
    check_job_description()