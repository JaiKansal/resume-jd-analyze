#!/usr/bin/env python3
"""
Comprehensive audit for Streamlit Cloud deployment issues
"""

import os
import re
import ast
from pathlib import Path

def check_file_paths_and_permissions():
    """Check for file path and permission issues"""
    print("🔍 Checking File Paths and Permissions")
    print("=" * 45)
    
    issues = []
    
    # Check for hardcoded paths
    files_to_check = ['app.py', 'startup.py', 'database/connection.py']
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check for absolute paths
            absolute_paths = re.findall(r'["\']\/[^"\']*["\']', content)
            if absolute_paths:
                issues.append(f"❌ {file_path}: Absolute paths found: {absolute_paths}")
            
            # Check for Windows-specific paths
            windows_paths = re.findall(r'["\'][A-Z]:\\[^"\']*["\']', content)
            if windows_paths:
                issues.append(f"❌ {file_path}: Windows paths found: {windows_paths}")
            
            # Check for home directory references
            home_refs = re.findall(r'["\']~[^"\']*["\']', content)
            if home_refs:
                issues.append(f"⚠️  {file_path}: Home directory references: {home_refs}")
    
    # Check data directory structure
    data_dir = Path('data')
    if not data_dir.exists():
        issues.append("❌ Data directory doesn't exist - will cause issues on Streamlit Cloud")
    else:
        print("✅ Data directory exists")
    
    # Check for write permissions issues
    temp_dirs = ['temp', 'tmp', '/tmp']
    for temp_dir in temp_dirs:
        if temp_dir in str(Path.cwd()):
            issues.append(f"⚠️  Using temp directory {temp_dir} - may not be writable on Streamlit Cloud")
    
    if not issues:
        print("✅ No file path issues found")
    else:
        for issue in issues:
            print(issue)
    
    return len(issues) == 0

def check_environment_variables():
    """Check environment variable usage"""
    print("\n🔍 Checking Environment Variables")
    print("=" * 35)
    
    issues = []
    required_vars = []
    optional_vars = []
    
    # Check .env file
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            env_content = f.read()
        
        # Extract all environment variables
        env_vars = re.findall(r'^([A-Z_]+)=', env_content, re.MULTILINE)
        print(f"📋 Found {len(env_vars)} environment variables in .env")
        
        # Categorize variables
        for var in env_vars:
            if any(keyword in var for keyword in ['API_KEY', 'SECRET', 'PASSWORD', 'TOKEN']):
                required_vars.append(var)
            else:
                optional_vars.append(var)
    
    # Check for missing environment variables in code
    files_to_check = ['app.py', 'startup.py', 'config.py']
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Find os.getenv() calls
            getenv_calls = re.findall(r'os\.getenv\(["\']([^"\']+)["\']', content)
            for var in getenv_calls:
                if var not in required_vars and var not in optional_vars:
                    if any(keyword in var for keyword in ['API_KEY', 'SECRET', 'PASSWORD', 'TOKEN']):
                        required_vars.append(var)
                    else:
                        optional_vars.append(var)
    
    print(f"🔑 Required variables: {required_vars}")
    print(f"⚙️  Optional variables: {optional_vars}")
    
    # Check for hardcoded secrets
    for file_path in ['app.py', 'config.py']:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Look for potential hardcoded secrets
            secret_patterns = [
                r'api_key\s*=\s*["\'][^"\']{20,}["\']',
                r'secret\s*=\s*["\'][^"\']{20,}["\']',
                r'password\s*=\s*["\'][^"\']{8,}["\']',
                r'token\s*=\s*["\'][^"\']{20,}["\']'
            ]
            
            for pattern in secret_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    issues.append(f"❌ {file_path}: Potential hardcoded secret found")
    
    if not issues:
        print("✅ No environment variable issues found")
    else:
        for issue in issues:
            print(issue)
    
    return len(issues) == 0, required_vars, optional_vars

def check_dependencies():
    """Check requirements.txt and package dependencies"""
    print("\n🔍 Checking Dependencies")
    print("=" * 25)
    
    issues = []
    
    # Check requirements.txt exists
    if not os.path.exists('requirements.txt'):
        issues.append("❌ requirements.txt not found")
        return False
    
    with open('requirements.txt', 'r') as f:
        requirements = f.read().strip().split('\n')
    
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith('#')]
    
    print(f"📦 Found {len(requirements)} dependencies")
    
    # Check for problematic packages
    problematic_packages = [
        'tensorflow',  # Large package
        'torch',       # Large package
        'opencv-python',  # Can cause issues
        'pyqt5',       # GUI package not needed
        'tkinter',     # GUI package not needed
    ]
    
    for req in requirements:
        package_name = req.split('==')[0].split('>=')[0].split('<=')[0].split('>')[0].split('<')[0]
        if package_name.lower() in problematic_packages:
            issues.append(f"⚠️  Potentially problematic package: {package_name}")
    
    # Check for missing essential packages
    essential_packages = ['streamlit', 'pandas', 'numpy']
    for essential in essential_packages:
        if not any(essential in req for req in requirements):
            issues.append(f"❌ Missing essential package: {essential}")
    
    # Check for version conflicts
    streamlit_reqs = [req for req in requirements if 'streamlit' in req.lower()]
    if len(streamlit_reqs) > 1:
        issues.append(f"⚠️  Multiple Streamlit requirements: {streamlit_reqs}")
    
    # Check packages.txt if it exists
    if os.path.exists('packages.txt'):
        with open('packages.txt', 'r') as f:
            system_packages = f.read().strip().split('\n')
        
        system_packages = [pkg.strip() for pkg in system_packages if pkg.strip()]
        print(f"🔧 Found {len(system_packages)} system packages")
        
        # Check for problematic system packages
        problematic_system = ['mysql-server', 'postgresql', 'redis-server']
        for pkg in system_packages:
            if pkg in problematic_system:
                issues.append(f"❌ Problematic system package: {pkg}")
    
    if not issues:
        print("✅ No dependency issues found")
    else:
        for issue in issues:
            print(issue)
    
    return len(issues) == 0

def check_streamlit_config():
    """Check Streamlit configuration"""
    print("\n🔍 Checking Streamlit Configuration")
    print("=" * 35)
    
    issues = []
    
    # Check .streamlit/config.toml
    streamlit_config_path = '.streamlit/config.toml'
    if os.path.exists(streamlit_config_path):
        with open(streamlit_config_path, 'r') as f:
            config_content = f.read()
        
        print("✅ Streamlit config found")
        
        # Check for problematic configurations
        if 'enableCORS = false' in config_content:
            issues.append("⚠️  CORS disabled - may cause issues on Streamlit Cloud")
        
        if 'headless = true' not in config_content:
            issues.append("⚠️  Consider adding 'headless = true' for cloud deployment")
    
    # Check for st.set_page_config usage
    if os.path.exists('app.py'):
        with open('app.py', 'r') as f:
            app_content = f.read()
        
        if 'st.set_page_config' in app_content:
            print("✅ Page config found")
        else:
            issues.append("⚠️  No st.set_page_config found - consider adding for better UX")
    
    if not issues:
        print("✅ No Streamlit config issues found")
    else:
        for issue in issues:
            print(issue)
    
    return len(issues) == 0

def check_database_issues():
    """Check for database-related issues"""
    print("\n🔍 Checking Database Configuration")
    print("=" * 35)
    
    issues = []
    
    # Check database connection
    if os.path.exists('database/connection.py'):
        with open('database/connection.py', 'r') as f:
            db_content = f.read()
        
        # Check for SQLite usage (good for Streamlit Cloud)
        if 'sqlite3' in db_content:
            print("✅ SQLite database detected (good for Streamlit Cloud)")
        
        # Check for PostgreSQL (needs proper configuration)
        if 'psycopg2' in db_content or 'postgresql' in db_content:
            print("⚠️  PostgreSQL detected - ensure DATABASE_URL is configured")
        
        # Check for hardcoded database paths
        db_paths = re.findall(r'["\'][^"\']*\.db["\']', db_content)
        for path in db_paths:
            if path.startswith('"/') or path.startswith("'/"):
                issues.append(f"❌ Absolute database path: {path}")
    
    # Check if database initialization is handled
    init_files = ['startup.py', 'database/simple_init.py', 'database/emergency_init.py']
    init_found = False
    
    for init_file in init_files:
        if os.path.exists(init_file):
            init_found = True
            print(f"✅ Database initialization found: {init_file}")
            break
    
    if not init_found:
        issues.append("❌ No database initialization found")
    
    if not issues:
        print("✅ No database issues found")
    else:
        for issue in issues:
            print(issue)
    
    return len(issues) == 0

def check_memory_and_performance():
    """Check for memory and performance issues"""
    print("\n🔍 Checking Memory and Performance")
    print("=" * 35)
    
    issues = []
    
    # Check for large file operations
    if os.path.exists('app.py'):
        with open('app.py', 'r') as f:
            app_content = f.read()
        
        # Check for file upload size limits
        if 'file_uploader' in app_content:
            if 'max_upload_size' not in app_content:
                issues.append("⚠️  No file upload size limit set")
        
        # Check for caching usage
        if '@st.cache' in app_content or '@st.cache_data' in app_content:
            print("✅ Caching found")
        else:
            issues.append("⚠️  No caching found - consider adding for performance")
        
        # Check for large data operations
        large_ops = ['pd.read_csv', 'pd.read_excel', 'json.load']
        for op in large_ops:
            if op in app_content:
                print(f"⚠️  Large data operation found: {op}")
    
    # Check for session state usage
    if os.path.exists('app.py'):
        with open('app.py', 'r') as f:
            content = f.read()
        
        session_state_vars = re.findall(r'st\.session_state\.([a-zA-Z_]+)', content)
        unique_vars = set(session_state_vars)
        
        if len(unique_vars) > 20:
            issues.append(f"⚠️  Many session state variables ({len(unique_vars)}) - may impact memory")
        else:
            print(f"✅ Session state usage reasonable ({len(unique_vars)} variables)")
    
    if not issues:
        print("✅ No memory/performance issues found")
    else:
        for issue in issues:
            print(issue)
    
    return len(issues) == 0

def check_security_issues():
    """Check for security issues"""
    print("\n🔍 Checking Security Issues")
    print("=" * 25)
    
    issues = []
    
    # Check for unsafe operations
    files_to_check = ['app.py', 'auth/registration.py', 'auth/services.py']
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check for eval/exec usage
            if 'eval(' in content or 'exec(' in content:
                issues.append(f"❌ {file_path}: Unsafe eval/exec usage found")
            
            # Check for SQL injection risks
            if re.search(r'f["\'].*SELECT.*{.*}.*["\']', content):
                issues.append(f"❌ {file_path}: Potential SQL injection risk")
            
            # Check for unsafe HTML
            if 'unsafe_allow_html=True' in content:
                print(f"⚠️  {file_path}: unsafe_allow_html used - ensure content is sanitized")
    
    # Check for proper password hashing
    if os.path.exists('auth/models.py'):
        with open('auth/models.py', 'r') as f:
            content = f.read()
        
        if 'bcrypt' in content or 'hashlib' in content:
            print("✅ Password hashing found")
        else:
            issues.append("❌ No password hashing found")
    
    if not issues:
        print("✅ No security issues found")
    else:
        for issue in issues:
            print(issue)
    
    return len(issues) == 0

def check_error_handling():
    """Check error handling"""
    print("\n🔍 Checking Error Handling")
    print("=" * 25)
    
    issues = []
    
    # Check for proper exception handling
    files_to_check = ['app.py', 'auth/services.py', 'database/connection.py']
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Count try/except blocks
            try_count = content.count('try:')
            except_count = content.count('except')
            
            if try_count > 0 and except_count >= try_count:
                print(f"✅ {file_path}: Good exception handling ({try_count} try blocks)")
            elif try_count > 0:
                issues.append(f"⚠️  {file_path}: Some try blocks without proper except")
            
            # Check for bare except clauses
            if 'except:' in content:
                issues.append(f"⚠️  {file_path}: Bare except clause found - should specify exception type")
    
    if not issues:
        print("✅ No error handling issues found")
    else:
        for issue in issues:
            print(issue)
    
    return len(issues) == 0

def main():
    """Run comprehensive Streamlit Cloud audit"""
    print("🚀 STREAMLIT CLOUD DEPLOYMENT AUDIT")
    print("=" * 50)
    
    checks = [
        ("File Paths & Permissions", check_file_paths_and_permissions),
        ("Environment Variables", lambda: check_environment_variables()[0]),
        ("Dependencies", check_dependencies),
        ("Streamlit Configuration", check_streamlit_config),
        ("Database Configuration", check_database_issues),
        ("Memory & Performance", check_memory_and_performance),
        ("Security", check_security_issues),
        ("Error Handling", check_error_handling)
    ]
    
    results = []
    
    for check_name, check_func in checks:
        print(f"\n{'='*15} {check_name} {'='*15}")
        try:
            success = check_func()
            results.append((check_name, success))
        except Exception as e:
            print(f"❌ Check failed: {e}")
            results.append((check_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 STREAMLIT CLOUD AUDIT SUMMARY")
    print("=" * 50)
    
    passed = 0
    for check_name, success in results:
        status = "✅ PASS" if success else "❌ ISSUES"
        print(f"{check_name:.<30} {status}")
        if success:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} checks passed")
    
    if passed == len(results):
        print("\n🎉 ALL CHECKS PASSED!")
        print("✅ App should deploy successfully to Streamlit Cloud")
    else:
        print(f"\n⚠️  {len(results) - passed} checks found issues")
        print("🔧 Review and fix issues before deploying to Streamlit Cloud")
    
    # Get environment variables for secrets configuration
    if os.path.exists('.env'):
        _, required_vars, optional_vars = check_environment_variables()
        
        if required_vars:
            print(f"\n🔑 REQUIRED SECRETS FOR STREAMLIT CLOUD:")
            for var in required_vars:
                print(f"   - {var}")
            print("\n💡 Add these to your Streamlit Cloud app secrets")

if __name__ == "__main__":
    main()