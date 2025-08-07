#!/usr/bin/env python3
"""
Fix the startup import error in app.py
"""

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_startup_import():
    """Fix the startup import error by making it optional"""
    logger.info("🔧 Fixing startup import error...")
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Replace the problematic startup import with error handling
        old_import = '''# Startup initialization (must be first)
import startup'''
        
        new_import = '''# Startup initialization (must be first)
try:
    import startup
except ImportError as e:
    # Startup module not available, continue without it
    import os
    import sys
    from pathlib import Path
    
    # Basic path setup
    project_root = Path(__file__).parent.absolute()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    print(f"Warning: startup module not available: {e}")'''
        
        if old_import in content:
            content = content.replace(old_import, new_import)
            
            with open('app.py', 'w') as f:
                f.write(content)
            
            logger.info("✅ Fixed startup import with error handling")
        else:
            logger.info("✅ Startup import already handled or not found")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to fix startup import: {e}")
        return False

def create_simple_startup():
    """Create a simpler startup.py that won't cause import issues"""
    logger.info("🔧 Creating simplified startup.py...")
    
    simple_startup = '''"""
Simple startup initialization for Streamlit Cloud
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
try:
    project_root = Path(__file__).parent.absolute()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # Basic environment setup
    os.environ.setdefault('PYTHONPATH', str(project_root))
    
    print(f"✅ Startup initialized - Project root: {project_root}")
    
except Exception as e:
    print(f"⚠️ Startup initialization warning: {e}")
'''
    
    try:
        with open('startup.py', 'w') as f:
            f.write(simple_startup)
        
        logger.info("✅ Created simplified startup.py")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create startup.py: {e}")
        return False

def remove_startup_dependency():
    """Remove startup dependency entirely and inline the initialization"""
    logger.info("🔧 Removing startup dependency entirely...")
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Replace startup import with inline initialization
        startup_replacement = '''# Inline startup initialization
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Set environment variables
os.environ.setdefault('PYTHONPATH', str(project_root))'''
        
        # Find and replace the startup import section
        lines = content.split('\n')
        new_lines = []
        skip_startup = False
        
        for line in lines:
            if '# Startup initialization (must be first)' in line:
                new_lines.append(startup_replacement)
                skip_startup = True
            elif skip_startup and ('import startup' in line or 'except ImportError' in line or 'print(f"Warning:' in line):
                continue  # Skip startup-related lines
            elif skip_startup and line.strip() == '':
                skip_startup = False
                new_lines.append(line)
            elif not skip_startup:
                new_lines.append(line)
        
        new_content = '\n'.join(new_lines)
        
        with open('app.py', 'w') as f:
            f.write(new_content)
        
        logger.info("✅ Removed startup dependency and inlined initialization")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to remove startup dependency: {e}")
        return False

def main():
    """Run startup import fixes"""
    logger.info("🚀 Fixing startup import error...")
    
    # Try the simplest fix first - remove dependency entirely
    if remove_startup_dependency():
        logger.info("🎉 Startup import issue resolved!")
        logger.info("🔄 Push changes to fix the KeyError: 'startup' issue")
        return True
    
    # Fallback fixes
    fixes = [
        ("Startup import error handling", fix_startup_import),
        ("Simple startup.py", create_simple_startup)
    ]
    
    success_count = 0
    for fix_name, fix_func in fixes:
        logger.info(f"\n--- {fix_name} ---")
        if fix_func():
            success_count += 1
    
    logger.info(f"\n✅ Applied {success_count}/{len(fixes)} fallback fixes")
    return success_count > 0

if __name__ == "__main__":
    main()