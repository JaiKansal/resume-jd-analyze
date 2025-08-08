#!/usr/bin/env python3
"""
Fix PostgreSQL syntax issues - convert ? to %s for PostgreSQL compatibility
"""

import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_database_connection_for_postgresql():
    """Fix database connection to handle both SQLite and PostgreSQL syntax"""
    logger.info("🔧 Fixing database connection for PostgreSQL compatibility...")
    
    try:
        with open('database/connection.py', 'r') as f:
            content = f.read()
        
        # Add parameter conversion method
        parameter_conversion = '''
    def _convert_query_params(self, query, params):
        """Convert query parameters based on database type"""
        if self.config.db_type == 'postgresql':
            # Convert ? to %s for PostgreSQL
            converted_query = query.replace('?', '%s')
            return converted_query, params
        else:
            # Keep ? for SQLite
            return query, params
'''
        
        # Add the method before the execute_query method
        if '_convert_query_params' not in content:
            # Find the execute_query method and add the conversion method before it
            execute_query_pos = content.find('def execute_query(self, query: str')
            if execute_query_pos != -1:
                content = content[:execute_query_pos] + parameter_conversion + '\n    ' + content[execute_query_pos:]
        
        # Update execute_query method to use parameter conversion
        old_execute = '''def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params or ())'''
        
        new_execute = '''def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results"""
        try:
            # Convert query parameters for database compatibility
            converted_query, converted_params = self._convert_query_params(query, params or ())
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(converted_query, converted_params)'''
        
        if old_execute in content:
            content = content.replace(old_execute, new_execute)
        
        # Update execute_command method similarly
        old_command = '''def execute_command(self, command: str, params: Optional[tuple] = None) -> int:
        """Execute an INSERT, UPDATE, or DELETE command"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(command, params or ())'''
        
        new_command = '''def execute_command(self, command: str, params: Optional[tuple] = None) -> int:
        """Execute an INSERT, UPDATE, or DELETE command"""
        try:
            # Convert query parameters for database compatibility
            converted_command, converted_params = self._convert_query_params(command, params or ())
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(converted_command, converted_params)'''
        
        if old_command in content:
            content = content.replace(old_command, new_command)
        
        # Update get_single_result method
        old_single = '''def get_single_result(self, query: str, params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
        """Execute query and return single result or None"""
        results = self.execute_query(query, params)'''
        
        new_single = '''def get_single_result(self, query: str, params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
        """Execute query and return single result or None"""
        results = self.execute_query(query, params)'''
        
        # get_single_result doesn't need changes as it uses execute_query
        
        with open('database/connection.py', 'w') as f:
            f.write(content)
        
        logger.info("✅ Fixed database connection for PostgreSQL compatibility")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to fix database connection: {e}")
        return False

def create_postgresql_user_table():
    """Create PostgreSQL-compatible user table"""
    logger.info("🔧 Creating PostgreSQL user table...")
    
    create_table_script = '''#!/usr/bin/env python3
"""
Create PostgreSQL tables with proper schema
"""

import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_postgresql_tables():
    """Create all required tables in PostgreSQL"""
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url or 'postgresql' not in database_url:
        logger.error("PostgreSQL DATABASE_URL not configured")
        return False
    
    try:
        import psycopg2
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute("""
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
                email_verified BOOLEAN DEFAULT FALSE,
                email_verification_token TEXT,
                password_reset_token TEXT,
                password_reset_expires TIMESTAMP,
                last_login TIMESTAMP,
                login_count INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create analysis_sessions table
        cursor.execute("""
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
            )
        """)
        
        # Create other required tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                plan_id TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                current_period_start TIMESTAMP,
                current_period_end TIMESTAMP,
                cancel_at_period_end BOOLEAN DEFAULT FALSE,
                canceled_at TIMESTAMP,
                trial_start TIMESTAMP,
                trial_end TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS plans (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                plan_type TEXT NOT NULL,
                price_monthly DECIMAL(10,2),
                price_yearly DECIMAL(10,2),
                features JSONB,
                analysis_limit INTEGER,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS engagement_events (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_data TEXT,
                page_path TEXT,
                session_id TEXT,
                parameters TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Insert default plans
        cursor.execute("""
            INSERT INTO plans (id, name, plan_type, price_monthly, price_yearly, features, analysis_limit, is_active)
            VALUES 
                ('free', 'Free Plan', 'FREE', 0, 0, '{"analyses_per_month": 3}', 3, TRUE),
                ('professional', 'Professional Plan', 'PROFESSIONAL', 19, 190, '{"unlimited_analyses": true}', -1, TRUE),
                ('business', 'Business Plan', 'BUSINESS', 99, 990, '{"unlimited_analyses": true, "team_features": true}', -1, TRUE)
            ON CONFLICT (id) DO NOTHING
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_analysis_sessions_user_id ON analysis_sessions(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_engagement_events_user_id ON engagement_events(user_id)")
        
        conn.commit()
        conn.close()
        
        logger.info("✅ PostgreSQL tables created successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create PostgreSQL tables: {e}")
        return False

if __name__ == "__main__":
    create_postgresql_tables()
'''
    
    with open('create_postgresql_tables.py', 'w') as f:
        f.write(create_table_script)
    
    logger.info("✅ Created PostgreSQL table creation script")
    return True

def main():
    """Fix PostgreSQL compatibility issues"""
    logger.info("🚀 Fixing PostgreSQL compatibility issues...")
    
    fixes = [
        ("Database Connection PostgreSQL Fix", fix_database_connection_for_postgresql),
        ("PostgreSQL Table Creation Script", create_postgresql_user_table)
    ]
    
    success_count = 0
    for fix_name, fix_func in fixes:
        logger.info(f"\n--- {fix_name} ---")
        if fix_func():
            success_count += 1
    
    logger.info(f"\n✅ Applied {success_count}/{len(fixes)} PostgreSQL fixes")
    
    if success_count == len(fixes):
        logger.info("🎉 PostgreSQL compatibility fixed!")
        logger.info("🔄 Push changes and run create_postgresql_tables.py")
        logger.info("✅ Your login should work after this!")
    
    return success_count == len(fixes)

if __name__ == "__main__":
    main()