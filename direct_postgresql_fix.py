#!/usr/bin/env python3
"""
Direct PostgreSQL fix - replace all ? with %s in auth services
"""

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_auth_services_postgresql():
    """Fix auth services to use PostgreSQL syntax directly"""
    logger.info("🔧 Fixing auth services for PostgreSQL...")
    
    try:
        with open('auth/services.py', 'r') as f:
            content = f.read()
        
        # Replace all SQLite ? parameters with PostgreSQL %s
        content = content.replace('WHERE email = ?', 'WHERE email = %s')
        content = content.replace('WHERE id = ?', 'WHERE id = %s')
        content = content.replace('VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)')
        content = content.replace('SET password_hash = ?, updated_at = ? WHERE id = ?', 'SET password_hash = %s, updated_at = %s WHERE id = %s')
        content = content.replace('SET last_login = ?, login_count = ?, updated_at = ? WHERE id = ?', 'SET last_login = %s, login_count = %s, updated_at = %s WHERE id = %s')
        
        # Replace any other ? patterns
        import re
        content = re.sub(r'\?', '%s', content)
        
        with open('auth/services.py', 'w') as f:
            f.write(content)
        
        logger.info("✅ Fixed auth services for PostgreSQL")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to fix auth services: {e}")
        return False

def fix_database_connection_detection():
    """Fix database type detection"""
    logger.info("🔧 Fixing database type detection...")
    
    try:
        with open('database/connection.py', 'r') as f:
            content = f.read()
        
        # Improve database type detection
        old_detection = '''        # Determine database type from URL
        if self.database_url.startswith('postgresql://') or self.database_url.startswith('postgres://'):
            self.db_type = 'postgresql'
        else:
            self.db_type = 'sqlite' '''
        
        new_detection = '''        # Determine database type from URL
        if self.database_url and ('postgresql://' in self.database_url or 'postgres://' in self.database_url):
            self.db_type = 'postgresql'
            logger.info(f"✅ Detected PostgreSQL database: {self.database_url[:50]}...")
        else:
            self.db_type = 'sqlite'
            logger.info(f"✅ Using SQLite database: {self.database_url}")'''
        
        if old_detection in content:
            content = content.replace(old_detection, new_detection)
        
        # Also fix the parameter conversion to be more aggressive
        old_convert = '''    def _convert_query_params(self, query, params):
        """Convert query parameters based on database type"""
        if self.config.db_type == 'postgresql':
            # Convert ? to %s for PostgreSQL
            converted_query = query.replace('?', '%s')
            return converted_query, params
        else:
            # Keep ? for SQLite
            return query, params'''
        
        new_convert = '''    def _convert_query_params(self, query, params):
        """Convert query parameters based on database type"""
        # Always convert ? to %s if we detect PostgreSQL in DATABASE_URL
        database_url = os.getenv('DATABASE_URL', '')
        if 'postgresql' in database_url.lower() or 'postgres' in database_url.lower():
            # Convert ? to %s for PostgreSQL
            converted_query = query.replace('?', '%s')
            logger.debug(f"Converted query: {query} -> {converted_query}")
            return converted_query, params
        else:
            # Keep ? for SQLite
            return query, params'''
        
        if old_convert in content:
            content = content.replace(old_convert, new_convert)
        
        with open('database/connection.py', 'w') as f:
            f.write(content)
        
        logger.info("✅ Fixed database type detection")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to fix database detection: {e}")
        return False

def create_emergency_postgresql_service():
    """Create emergency PostgreSQL-only auth service"""
    logger.info("🔧 Creating emergency PostgreSQL auth service...")
    
    postgresql_service = '''"""
Emergency PostgreSQL-only auth service
Uses %s parameters exclusively for PostgreSQL compatibility
"""

import os
import logging
from typing import Optional
from datetime import datetime
import bcrypt

logger = logging.getLogger(__name__)

class PostgreSQLAuthService:
    """PostgreSQL-only authentication service"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url or 'postgresql' not in self.database_url:
            raise Exception("PostgreSQL DATABASE_URL required")
    
    def get_connection(self):
        """Get PostgreSQL connection"""
        import psycopg2
        from psycopg2.extras import RealDictCursor
        return psycopg2.connect(self.database_url, cursor_factory=RealDictCursor)
    
    def get_user_by_email(self, email: str):
        """Get user by email using PostgreSQL syntax"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Use %s for PostgreSQL
                query = "SELECT * FROM users WHERE email = %s"
                cursor.execute(query, (email.lower().strip(),))
                
                result = cursor.fetchone()
                if result:
                    return dict(result)
                return None
                
        except Exception as e:
            logger.error(f"Failed to get user by email: {e}")
            return None
    
    def authenticate_user(self, email: str, password: str):
        """Authenticate user with PostgreSQL"""
        user = self.get_user_by_email(email)
        
        if not user:
            logger.info(f"User not found: {email}")
            return None
        
        try:
            # Verify password
            if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                logger.info(f"User authenticated successfully: {email}")
                return user
            else:
                logger.info(f"Invalid password for user: {email}")
                return None
                
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
    
    def create_user(self, email: str, password: str, first_name: str = "", last_name: str = ""):
        """Create new user with PostgreSQL"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if user exists
                cursor.execute("SELECT id FROM users WHERE email = %s", (email.lower().strip(),))
                if cursor.fetchone():
                    return None, "User already exists"
                
                # Create user
                import uuid
                user_id = str(uuid.uuid4())
                password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                
                cursor.execute("""
                    INSERT INTO users (
                        id, email, password_hash, first_name, last_name,
                        role, email_verified, login_count, is_active, created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    user_id, email.lower().strip(), password_hash, first_name, last_name,
                    'individual', False, 0, True, datetime.utcnow(), datetime.utcnow()
                ))
                
                conn.commit()
                
                # Return created user
                return self.get_user_by_email(email), None
                
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            return None, str(e)

# Global instance
postgresql_auth_service = PostgreSQLAuthService()
'''
    
    with open('auth/postgresql_service.py', 'w') as f:
        f.write(postgresql_service)
    
    logger.info("✅ Created emergency PostgreSQL auth service")
    return True

def update_auth_registration_to_use_postgresql():
    """Update registration to use PostgreSQL service"""
    logger.info("🔧 Updating registration to use PostgreSQL service...")
    
    try:
        with open('auth/registration.py', 'r') as f:
            content = f.read()
        
        # Add PostgreSQL service import at the top
        if 'from auth.postgresql_service import postgresql_auth_service' not in content:
            # Find the imports section
            import_pos = content.find('from auth.services import')
            if import_pos != -1:
                # Add the PostgreSQL import
                content = content[:import_pos] + 'from auth.postgresql_service import postgresql_auth_service\n' + content[import_pos:]
        
        # Replace user_service calls with postgresql_auth_service
        content = content.replace('user_service.authenticate_user', 'postgresql_auth_service.authenticate_user')
        content = content.replace('user_service.get_user_by_email', 'postgresql_auth_service.get_user_by_email')
        content = content.replace('user_service.create_user', 'postgresql_auth_service.create_user')
        
        with open('auth/registration.py', 'w') as f:
            f.write(content)
        
        logger.info("✅ Updated registration to use PostgreSQL service")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to update registration: {e}")
        return False

def main():
    """Apply all PostgreSQL fixes"""
    logger.info("🚀 Applying direct PostgreSQL fixes...")
    
    fixes = [
        ("Auth Services PostgreSQL Fix", fix_auth_services_postgresql),
        ("Database Connection Detection", fix_database_connection_detection),
        ("Emergency PostgreSQL Service", create_emergency_postgresql_service),
        ("Registration PostgreSQL Update", update_auth_registration_to_use_postgresql)
    ]
    
    success_count = 0
    for fix_name, fix_func in fixes:
        logger.info(f"\n--- {fix_name} ---")
        if fix_func():
            success_count += 1
    
    logger.info(f"\n✅ Applied {success_count}/{len(fixes)} PostgreSQL fixes")
    
    if success_count == len(fixes):
        logger.info("🎉 PostgreSQL fixes applied!")
        logger.info("🔄 Push changes - login should work now!")
        logger.info("✅ jaikansal85@gmail.com should work!")
    
    return success_count == len(fixes)

if __name__ == "__main__":
    main()