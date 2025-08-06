#!/usr/bin/env python3
"""
COMPREHENSIVE DIAGNOSTIC SCAN FOR STREAMLIT APP
Checks every single component that could cause issues
"""

import os
import sys
import sqlite3
import json
import logging
import subprocess
from pathlib import Path
import importlib.util

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class StreamlitDiagnostic:
    def __init__(self):
        self.issues = []
        self.fixes_applied = []
        self.critical_errors = []
        
    def log_issue(self, severity, component, issue, fix=None):
        """Log an issue found during diagnostic"""
        self.issues.append({
            'severity': severity,
            'component': component,
            'issue': issue,
            'fix': fix
        })
        
        if severity == 'CRITICAL':
            self.critical_errors.append(f"{component}: {issue}")
        
        logger.error(f"[{severity}] {component}: {issue}")
        if fix:
            logger.info(f"[FIX] {fix}")
    
    def check_python_environment(self):
        """Check Python environment and dependencies"""
        logger.info("🐍 Checking Python Environment...")
        
        # Check Python version
        python_version = sys.version_info
        if python_version < (3, 8):
            self.log_issue('CRITICAL', 'Python Version', 
                          f"Python {python_version.major}.{python_version.minor} is too old",
                          "Upgrade to Python 3.8+")
        else:
            logger.info(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Check requirements.txt
        if not Path('requirements.txt').exists():
            self.log_issue('CRITICAL', 'Requirements', 
                          "requirements.txt missing",
                          "Create requirements.txt with all dependencies")
        else:
            with open('requirements.txt', 'r') as f:
                requirements = f.read()
            
            critical_packages = ['streamlit', 'pandas', 'sqlite3']
            missing_packages = []
            
            for package in critical_packages:
                if package not in requirements.lower():
                    missing_packages.append(package)
            
            if missing_packages:
                self.log_issue('HIGH', 'Requirements', 
                              f"Missing packages: {missing_packages}",
                              "Add missing packages to requirements.txt")
            else:
                logger.info("✅ Requirements.txt looks good")
    
    def check_streamlit_config(self):
        """Check Streamlit configuration"""
        logger.info("⚙️ Checking Streamlit Configuration...")
        
        # Check .streamlit directory
        streamlit_dir = Path('.streamlit')
        if not streamlit_dir.exists():
            self.log_issue('MEDIUM', 'Streamlit Config', 
                          ".streamlit directory missing",
                          "Create .streamlit/config.toml")
        
        # Check config.toml
        config_file = streamlit_dir / 'config.toml'
        if not config_file.exists():
            self.log_issue('MEDIUM', 'Streamlit Config', 
                          "config.toml missing",
                          "Create .streamlit/config.toml with proper settings")
        else:
            logger.info("✅ Streamlit config exists")
        
        # Check secrets.toml
        secrets_file = streamlit_dir / 'secrets.toml'
        if not secrets_file.exists():
            self.log_issue('HIGH', 'Streamlit Secrets', 
                          "secrets.toml missing",
                          "Create .streamlit/secrets.toml with API keys")
        else:
            logger.info("✅ Streamlit secrets exist")
    
    def check_database_integrity(self):
        """Check database integrity and structure"""
        logger.info("🗄️ Checking Database Integrity...")
        
        db_path = 'data/app.db'
        
        # Check if database exists
        if not Path(db_path).exists():
            self.log_issue('HIGH', 'Database', 
                          "Database file missing",
                          "Initialize database with proper schema")
            return
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check critical tables
            critical_tables = ['users', 'analysis_sessions', 'subscriptions', 'engagement_events']
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            missing_tables = [table for table in critical_tables if table not in existing_tables]
            
            if missing_tables:
                self.log_issue('CRITICAL', 'Database Schema', 
                              f"Missing tables: {missing_tables}",
                              "Run database initialization script")
            else:
                logger.info("✅ All critical tables exist")
            
            # Check table structures
            for table in existing_tables:
                if table in critical_tables:
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = cursor.fetchall()
                    
                    if not columns:
                        self.log_issue('HIGH', 'Database Schema', 
                                      f"Table {table} has no columns",
                                      f"Recreate {table} table with proper schema")
                    else:
                        logger.info(f"✅ Table {table} has {len(columns)} columns")
            
            # Check data integrity
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM analysis_sessions")
            session_count = cursor.fetchone()[0]
            
            logger.info(f"📊 Database contains: {user_count} users, {session_count} sessions")
            
            conn.close()
            
        except Exception as e:
            self.log_issue('CRITICAL', 'Database Connection', 
                          f"Cannot connect to database: {e}",
                          "Recreate database with proper permissions")
    
    def check_app_structure(self):
        """Check application file structure"""
        logger.info("📁 Checking Application Structure...")
        
        critical_files = [
            'app.py',
            'startup.py',
            'requirements.txt'
        ]
        
        critical_directories = [
            'auth',
            'database',
            'billing',
            'analytics',
            'resume_matcher_ai'
        ]
        
        # Check critical files
        for file in critical_files:
            if not Path(file).exists():
                self.log_issue('CRITICAL', 'File Structure', 
                              f"Missing critical file: {file}",
                              f"Create {file} with proper content")
            else:
                logger.info(f"✅ {file} exists")
        
        # Check critical directories
        for directory in critical_directories:
            if not Path(directory).exists():
                self.log_issue('HIGH', 'Directory Structure', 
                              f"Missing directory: {directory}",
                              f"Create {directory} directory with required modules")
            else:
                logger.info(f"✅ {directory}/ exists")
    
    def check_imports_and_dependencies(self):
        """Check if all imports work correctly"""
        logger.info("📦 Checking Imports and Dependencies...")
        
        critical_imports = [
            ('streamlit', 'st'),
            ('pandas', 'pd'),
            ('sqlite3', None),
            ('json', None),
            ('os', None),
            ('pathlib', 'Path'),
            ('datetime', 'datetime')
        ]
        
        for module_name, alias in critical_imports:
            try:
                if alias:
                    exec(f"import {module_name} as {alias}")
                else:
                    exec(f"import {module_name}")
                logger.info(f"✅ {module_name} imports successfully")
            except ImportError as e:
                self.log_issue('CRITICAL', 'Import Error', 
                              f"Cannot import {module_name}: {e}",
                              f"Install {module_name}: pip install {module_name}")
        
        # Check custom modules
        custom_modules = [
            'auth.services',
            'database.connection',
            'billing.watermark_service',
            'resume_matcher_ai.matcher'
        ]
        
        for module in custom_modules:
            try:
                spec = importlib.util.find_spec(module)
                if spec is None:
                    self.log_issue('HIGH', 'Custom Module', 
                                  f"Module {module} not found",
                                  f"Check {module.replace('.', '/')} file exists")
                else:
                    logger.info(f"✅ {module} found")
            except Exception as e:
                self.log_issue('HIGH', 'Custom Module', 
                              f"Error checking {module}: {e}",
                              f"Fix {module} module structure")
    
    def check_environment_variables(self):
        """Check environment variables and secrets"""
        logger.info("🔐 Checking Environment Variables...")
        
        critical_env_vars = [
            'PERPLEXITY_API_KEY',
            'RAZORPAY_KEY_ID',
            'RAZORPAY_KEY_SECRET'
        ]
        
        # Check .env file
        env_file = Path('.env')
        if not env_file.exists():
            self.log_issue('HIGH', 'Environment', 
                          ".env file missing",
                          "Create .env file with required variables")
        else:
            with open('.env', 'r') as f:
                env_content = f.read()
            
            for var in critical_env_vars:
                if var not in env_content:
                    self.log_issue('HIGH', 'Environment Variables', 
                                  f"Missing {var} in .env",
                                  f"Add {var} to .env file")
                else:
                    logger.info(f"✅ {var} found in .env")
    
    def check_git_repository(self):
        """Check Git repository status"""
        logger.info("🔧 Checking Git Repository...")
        
        if not Path('.git').exists():
            self.log_issue('MEDIUM', 'Git Repository', 
                          "Not a git repository",
                          "Initialize git repository")
            return
        
        try:
            # Check git status
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                self.log_issue('MEDIUM', 'Git Status', 
                              "Cannot check git status",
                              "Fix git repository issues")
            else:
                uncommitted_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
                if uncommitted_files and uncommitted_files != ['']:
                    logger.info(f"⚠️ {len(uncommitted_files)} uncommitted files")
                else:
                    logger.info("✅ Git repository is clean")
            
            # Check remote
            result = subprocess.run(['git', 'remote', '-v'], 
                                  capture_output=True, text=True)
            
            if 'github.com' not in result.stdout:
                self.log_issue('HIGH', 'Git Remote', 
                              "No GitHub remote found",
                              "Add GitHub remote for Streamlit Cloud deployment")
            else:
                logger.info("✅ GitHub remote configured")
                
        except Exception as e:
            self.log_issue('MEDIUM', 'Git Commands', 
                          f"Git command failed: {e}",
                          "Check git installation and repository")
    
    def check_streamlit_cloud_compatibility(self):
        """Check Streamlit Cloud deployment compatibility"""
        logger.info("☁️ Checking Streamlit Cloud Compatibility...")
        
        # Check for Streamlit Cloud specific files
        cloud_files = {
            'packages.txt': 'System packages for Streamlit Cloud',
            '.streamlit/config.toml': 'Streamlit configuration',
            'requirements.txt': 'Python dependencies'
        }
        
        for file, description in cloud_files.items():
            if not Path(file).exists():
                self.log_issue('MEDIUM', 'Streamlit Cloud', 
                              f"Missing {file}",
                              f"Create {file} for {description}")
            else:
                logger.info(f"✅ {file} exists")
        
        # Check app.py structure
        if Path('app.py').exists():
            with open('app.py', 'r') as f:
                app_content = f.read()
            
            # Check for common Streamlit Cloud issues
            if 'st.set_page_config' not in app_content:
                self.log_issue('MEDIUM', 'Streamlit App', 
                              "Missing st.set_page_config",
                              "Add page configuration at the top of app.py")
            
            if '__name__ == "__main__"' in app_content:
                self.log_issue('MEDIUM', 'Streamlit App', 
                              "Contains main block (not needed for Streamlit Cloud)",
                              "Remove or modify main block for cloud deployment")
    
    def generate_fixes(self):
        """Generate comprehensive fixes for all issues"""
        logger.info("🔧 Generating Comprehensive Fixes...")
        
        fixes = {
            'requirements_txt': self._generate_requirements_fix(),
            'streamlit_config': self._generate_streamlit_config_fix(),
            'database_init': self._generate_database_fix(),
            'app_structure': self._generate_app_structure_fix(),
            'environment': self._generate_environment_fix()
        }
        
        return fixes
    
    def _generate_requirements_fix(self):
        """Generate requirements.txt fix"""
        return """streamlit>=1.28.0
pandas>=1.5.0
sqlite3
python-dotenv>=1.0.0
bcrypt>=4.0.0
psycopg2-binary>=2.9.0
reportlab>=4.0.0
PyPDF2>=3.0.0
requests>=2.28.0
python-multipart>=0.0.6
pydantic>=2.0.0
email-validator>=2.0.0
"""
    
    def _generate_streamlit_config_fix(self):
        """Generate Streamlit config fix"""
        return """[global]
developmentMode = false
showWarningOnDirectExecution = false

[server]
headless = true
enableCORS = false
enableXsrfProtection = false
maxUploadSize = 200

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#FF6B35"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
"""
    
    def _generate_database_fix(self):
        """Generate database initialization fix"""
        return """-- Complete database schema
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    first_name TEXT,
    last_name TEXT,
    company_name TEXT,
    role TEXT DEFAULT 'individual',
    phone TEXT,
    country TEXT,
    timezone TEXT DEFAULT 'UTC',
    email_verified INTEGER DEFAULT 0,
    email_verification_token TEXT,
    password_reset_token TEXT,
    password_reset_expires TIMESTAMP,
    last_login TIMESTAMP,
    login_count INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS analysis_sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    resume_filename TEXT,
    score INTEGER,
    match_category TEXT,
    analysis_result TEXT,
    processing_time_seconds REAL,
    status TEXT DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS engagement_events (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    event_data TEXT,
    page_path TEXT,
    session_id TEXT,
    parameters TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_analysis_sessions_user_id ON analysis_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_engagement_events_user_id ON engagement_events(user_id);
"""
    
    def _generate_app_structure_fix(self):
        """Generate app structure fixes"""
        return {
            'startup.py': '''"""Startup initialization for Streamlit app"""
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Set environment variables
os.environ.setdefault('PYTHONPATH', str(project_root))
''',
            'packages.txt': '''sqlite3
libsqlite3-dev
''',
            '.streamlit/secrets.toml': '''# Streamlit Cloud Secrets
PERPLEXITY_API_KEY = "your_api_key_here"
RAZORPAY_KEY_ID = "your_razorpay_key_id"
RAZORPAY_KEY_SECRET = "your_razorpay_secret"
DATABASE_URL = "sqlite:///data/app.db"
ENVIRONMENT = "production"
SECRET_KEY = "your-secret-key"
'''
        }
    
    def _generate_environment_fix(self):
        """Generate environment fix"""
        return """.env file template:
PERPLEXITY_API_KEY=your_perplexity_api_key_here
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_secret
DATABASE_URL=sqlite:///data/app.db
ENVIRONMENT=development
SECRET_KEY=dev-secret-key-change-in-production
"""
    
    def run_full_diagnostic(self):
        """Run complete diagnostic scan"""
        logger.info("🚀 STARTING COMPREHENSIVE DIAGNOSTIC SCAN")
        logger.info("=" * 60)
        
        # Run all diagnostic checks
        self.check_python_environment()
        self.check_streamlit_config()
        self.check_database_integrity()
        self.check_app_structure()
        self.check_imports_and_dependencies()
        self.check_environment_variables()
        self.check_git_repository()
        self.check_streamlit_cloud_compatibility()
        
        # Generate report
        logger.info("\n" + "=" * 60)
        logger.info("📊 DIAGNOSTIC REPORT")
        logger.info("=" * 60)
        
        if self.critical_errors:
            logger.error(f"🚨 CRITICAL ERRORS FOUND: {len(self.critical_errors)}")
            for error in self.critical_errors:
                logger.error(f"   ❌ {error}")
        
        logger.info(f"\n📋 TOTAL ISSUES FOUND: {len(self.issues)}")
        
        severity_counts = {}
        for issue in self.issues:
            severity = issue['severity']
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        for severity, count in severity_counts.items():
            logger.info(f"   {severity}: {count}")
        
        # Generate fixes
        fixes = self.generate_fixes()
        
        return {
            'issues': self.issues,
            'critical_errors': self.critical_errors,
            'fixes': fixes,
            'total_issues': len(self.issues)
        }

def main():
    """Run comprehensive diagnostic"""
    diagnostic = StreamlitDiagnostic()
    results = diagnostic.run_full_diagnostic()
    
    # Save results
    with open('diagnostic_report.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"\n💾 Full diagnostic report saved to: diagnostic_report.json")
    
    if results['critical_errors']:
        logger.error("🚨 CRITICAL ISSUES MUST BE FIXED BEFORE DEPLOYMENT")
        return False
    else:
        logger.info("✅ No critical errors found")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)