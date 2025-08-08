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
    
    def create_user(self, email: str, password: str, first_name: str = "", last_name: str = ""):
        """Create new user with PostgreSQL"""
        if not self.is_postgresql:
            logger.warning("PostgreSQL not configured, falling back to regular auth service")
            return None, "PostgreSQL not configured"
            
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
