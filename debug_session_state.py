#!/usr/bin/env python3
"""
Debug script to check session state handling in the app
"""

import re

def analyze_session_state_usage():
    """Analyze how session state is used in the app"""
    print("🔍 DEBUGGING SESSION STATE USAGE")
    print("=" * 50)
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ app.py not found")
        return
    
    # Check session state initialization
    print("🧪 Checking session state initialization...")
    init_calls = re.findall(r'st\.session_state\.[a-zA-Z_]+ = \[\]', content)
    print(f"Found {len(init_calls)} session state initializations:")
    for call in init_calls:
        print(f"  - {call}")
    
    # Check session state access patterns
    print("\n🧪 Checking session state access patterns...")
    access_patterns = re.findall(r'st\.session_state\.[a-zA-Z_]+', content)
    unique_patterns = list(set(access_patterns))
    print(f"Found {len(unique_patterns)} unique session state variables:")
    for pattern in sorted(unique_patterns):
        count = content.count(pattern)
        print(f"  - {pattern}: {count} occurrences")
    
    # Check for potential session state clearing
    print("\n🧪 Checking for session state clearing...")
    clearing_patterns = [
        r'st\.session_state\.clear\(\)',
        r'del st\.session_state\.',
        r'st\.session_state\.[a-zA-Z_]+ = \[\]',
        r'st\.session_state\.[a-zA-Z_]+ = None'
    ]
    
    for pattern in clearing_patterns:
        matches = re.findall(pattern, content)
        if matches:
            print(f"  Found clearing pattern: {pattern}")
            for match in matches:
                print(f"    - {match}")
    
    # Check for problematic rerun patterns
    print("\n🧪 Checking for problematic rerun patterns...")
    
    # Find all st.rerun() calls with context
    rerun_matches = []
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'st.rerun()' in line:
            # Get context (3 lines before and after)
            start = max(0, i-3)
            end = min(len(lines), i+4)
            context = '\n'.join(f"{j+1:4d}: {lines[j]}" for j in range(start, end))
            rerun_matches.append((i+1, context))
    
    if rerun_matches:
        print(f"Found {len(rerun_matches)} st.rerun() calls:")
        for line_num, context in rerun_matches:
            print(f"\n  At line {line_num}:")
            print(f"    {context}")
    else:
        print("  No st.rerun() calls found")
    
    # Check for form submissions that might cause issues
    print("\n🧪 Checking for form submissions...")
    form_patterns = [
        r'with st\.form\(',
        r'st\.form_submit_button\(',
        r'st\.button\([^)]*type=["\']primary["\']'
    ]
    
    for pattern in form_patterns:
        matches = re.findall(pattern, content)
        if matches:
            print(f"  Found form pattern: {pattern} - {len(matches)} occurrences")
    
    # Check for file upload handling
    print("\n🧪 Checking file upload handling...")
    upload_patterns = [
        r'st\.file_uploader\(',
        r'resume_file\.read\(\)',
        r'resume_file\.getvalue\(\)'
    ]
    
    for pattern in upload_patterns:
        matches = re.findall(pattern, content)
        if matches:
            print(f"  Found upload pattern: {pattern} - {len(matches)} occurrences")
    
    print("\n" + "=" * 50)
    print("🎯 RECOMMENDATIONS:")
    print("1. Check if session state is being cleared unexpectedly")
    print("2. Verify that file uploads don't trigger unwanted reruns")
    print("3. Ensure analysis results are stored immediately after generation")
    print("4. Check for any widgets that might cause state loss")

if __name__ == "__main__":
    analyze_session_state_usage()