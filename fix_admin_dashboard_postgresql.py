#!/usr/bin/env python3
"""
Fix admin dashboard PostgreSQL compatibility
"""

def fix_admin_dashboard():
    """Fix admin dashboard to use PostgreSQL syntax"""
    
    with open('analytics/admin_dashboard.py', 'r') as f:
        content = f.read()
    
    # Replace all SQLite parameter placeholders with PostgreSQL ones
    content = content.replace(' = ?', ' = %s')
    content = content.replace(' >= ?', ' >= %s')
    content = content.replace(' <= ?', ' <= %s')
    content = content.replace(' < ?', ' < %s')
    content = content.replace(' > ?', ' > %s')
    content = content.replace('(?, ', '(%s, ')
    content = content.replace(', ?)', ', %s)')
    content = content.replace('(?)', '(%s)')
    
    # Fix any remaining standalone ? parameters
    content = content.replace('?', '%s')
    
    with open('analytics/admin_dashboard.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed admin dashboard PostgreSQL compatibility")

if __name__ == "__main__":
    print("🚀 Fixing admin dashboard PostgreSQL compatibility...")
    fix_admin_dashboard()
    print("🎉 Admin dashboard PostgreSQL fixes completed!")