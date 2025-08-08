"""
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
        self.is_postgresql = self.database_url and 'postgresql' in self.database_url.lower()
        
        if not self.is_postgresql:
            # Fallback to SQLite mode - don't raise exception
            logger.warning("PostgreSQL DATABASE_URL not configured, service will be disabled")
            self.database_url = None
    
    def get_connection(self):
        """Get PostgreSQL connection"""
        import psycopg2
        from psycopg2.extras import RealDictCursor
        return psycopg2.connect(self.database_url, cursor_factory=RealDictCursor)
    
    def get_user_by_email(self, email: str):
        """Get user by email using PostgreSQL syntax"""
        if not self.is_postgresql:
            logger.warning("PostgreSQL not configured, falling back to regular auth service")
            return None
            
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
        if not self.is_postgresql:
            logger.warning("PostgreSQL not configured, falling back to regular auth service")
            return None
            
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
    
    def create_user(self, email: str, password: str, first_name: str = "", last_name: str = "", 
                   company_name: str = "", role=None, phone: str = "", country: str = ""):
        """Create new user with PostgreSQL"""
        if not self.is_postgresql:
            logger.warning("PostgreSQL not configured, falling back to regular auth service")
            return None
            
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if user exists
                cursor.execute("SELECT id FROM users WHERE email = %s", (email.lower().strip(),))
                if cursor.fetchone():
                    logger.warning(f"User already exists: {email}")
                    return None
                
                # Create user
                import uuid
                user_id = str(uuid.uuid4())
                password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                
                # Handle role parameter
                role_str = 'individual'
                if role:
                    if hasattr(role, 'value'):
                        role_str = role.value
                    else:
                        role_str = str(role)
                
                cursor.execute("""
                    INSERT INTO users (
                        id, email, password_hash, first_name, last_name, company_name,
                        role, phone, country, email_verified, login_count, is_active, 
                        created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    user_id, email.lower().strip(), password_hash, first_name, last_name, company_name,
                    role_str, phone, country, False, 0, True, datetime.utcnow(), datetime.utcnow()
                ))
                
                conn.commit()
                logger.info(f"✅ User created successfully: {email}")
                
                # Return created user
                user_data = self.get_user_by_email(email)
                if user_data:
                    # Convert to User object-like structure
                    class User:
                        def __init__(self, data):
                            self.id = data['id']
                            self.email = data['email']
                            self.first_name = data['first_name']
                            self.last_name = data['last_name']
                            self.company_name = data.get('company_name', '')
                            self.role = data['role']
                            self.phone = data.get('phone', '')
                            self.country = data.get('country', '')
                    
                    return User(user_data)
                return None
                
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            import traceback
            traceback.print_exc()
            return None

# Global instance
postgresql_auth_service = PostgreSQLAuthService()
