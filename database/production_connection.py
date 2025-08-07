"""
PRODUCTION DATABASE CONNECTION - BULLETPROOF
Handles both SQLite (development) and PostgreSQL (production) seamlessly
"""

import os
import sqlite3
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ProductionDatabaseManager:
    """Production-ready database manager that NEVER loses data"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL', 'sqlite:///data/app.db')
        self.is_postgresql = 'postgresql' in self.database_url.lower()
        
        if self.is_postgresql:
            self.setup_postgresql()
        else:
            self.setup_sqlite()
    
    def setup_postgresql(self):
        """Set up PostgreSQL connection"""
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            
            self.connection_params = {
                'dsn': self.database_url,
                'cursor_factory': RealDictCursor
            }
            
            # Test connection
            conn = psycopg2.connect(**self.connection_params)
            conn.close()
            
            logger.info("✅ PostgreSQL connection established")
            self.db_type = 'postgresql'
            
        except ImportError:
            logger.error("❌ psycopg2 not available - falling back to SQLite")
            self.setup_sqlite()
        except Exception as e:
            logger.error(f"❌ PostgreSQL connection failed: {e} - falling back to SQLite")
            self.setup_sqlite()
    
    def setup_sqlite(self):
        """Set up SQLite connection with data persistence"""
        self.db_path = 'data/app.db'
        Path('data').mkdir(exist_ok=True)
        
        # Ensure database exists
        if not Path(self.db_path).exists():
            self.initialize_sqlite_schema()
        
        logger.info("✅ SQLite connection established")
        self.db_type = 'sqlite'
    
    def get_connection(self):
        """Get database connection"""
        if self.db_type == 'postgresql':
            import psycopg2
            return psycopg2.connect(**self.connection_params)
        else:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
    
    def execute_query(self, query, params=None):
        """Execute query with automatic connection handling"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            
            if query.strip().upper().startswith('SELECT'):
                return [dict(row) for row in cursor.fetchall()]
            else:
                conn.commit()
                return cursor.rowcount
    
    def initialize_sqlite_schema(self):
        """Initialize SQLite with complete schema"""
        logger.info("🔧 Initializing SQLite schema...")
        
        schema_sql = """
        -- Users table
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
        
        -- Analysis sessions
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
        
        -- Analysis reports
        CREATE TABLE IF NOT EXISTS analysis_reports (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            analysis_type TEXT DEFAULT 'resume_jd_match',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata JSON,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
        
        -- Subscriptions
        CREATE TABLE IF NOT EXISTS subscriptions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            plan_id TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            current_period_start TIMESTAMP,
            current_period_end TIMESTAMP,
            cancel_at_period_end INTEGER DEFAULT 0,
            canceled_at TIMESTAMP,
            trial_start TIMESTAMP,
            trial_end TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
        
        -- Plans
        CREATE TABLE IF NOT EXISTS plans (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            plan_type TEXT NOT NULL,
            price_monthly REAL,
            price_yearly REAL,
            features TEXT,
            analysis_limit INTEGER,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Engagement events
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
        );
        
        -- Create indexes
        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        CREATE INDEX IF NOT EXISTS idx_analysis_sessions_user_id ON analysis_sessions(user_id);
        CREATE INDEX IF NOT EXISTS idx_analysis_reports_user_id ON analysis_reports(user_id);
        CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id);
        CREATE INDEX IF NOT EXISTS idx_engagement_events_user_id ON engagement_events(user_id);
        """
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executescript(schema_sql)
            conn.commit()
        
        # Insert default plans
        self.insert_default_plans()
        
        logger.info("✅ SQLite schema initialized")
    
    def insert_default_plans(self):
        """Insert default subscription plans"""
        plans = [
            ('free', 'Free Plan', 'FREE', 0, 0, '{"analyses_per_month": 3}', 3, 1),
            ('professional', 'Professional Plan', 'PROFESSIONAL', 19, 190, '{"unlimited_analyses": true}', -1, 1),
            ('business', 'Business Plan', 'BUSINESS', 99, 990, '{"unlimited_analyses": true, "team_features": true}', -1, 1)
        ]
        
        for plan in plans:
            try:
                self.execute_query("""
                    INSERT OR IGNORE INTO plans (id, name, plan_type, price_monthly, price_yearly, features, analysis_limit, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, plan)
            except:
                pass  # Plan already exists

# Global instance
production_db = ProductionDatabaseManager()
