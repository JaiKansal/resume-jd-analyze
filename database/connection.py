"""
Database connection management for Resume + JD Analyzer
Supports both PostgreSQL (production) and SQLite (development)
"""

import os
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from typing import Optional, Dict, Any, List
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Database configuration management"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL', 'sqlite:///data/app.db')
        
        # Determine database type from URL
        if self.database_url.startswith('postgresql://') or self.database_url.startswith('postgres://'):
            self.db_type = 'postgresql'
        else:
            self.db_type = 'sqlite'
        
        # SQLite configuration (Streamlit Cloud default)
        self.sqlite_path = 'data/app.db'
        
        # PostgreSQL configuration (if needed)
        self.pg_host = os.getenv('DB_HOST', 'localhost')
        self.pg_port = os.getenv('DB_PORT', '5432')
        self.pg_name = os.getenv('DB_NAME', 'resume_analyzer')
        self.pg_user = os.getenv('DB_USER', 'postgres')
        self.pg_password = os.getenv('DB_PASSWORD', '')
        
    def get_connection_params(self) -> Dict[str, Any]:
        """Get connection parameters based on configuration"""
        if self.database_url:
            return {'database_url': self.database_url}
        elif self.db_type == 'postgresql':
            return {
                'host': self.pg_host,
                'port': self.pg_port,
                'database': self.pg_name,
                'user': self.pg_user,
                'password': self.pg_password
            }
        else:
            return {'database': self.sqlite_path}

class DatabaseManager:
    """Database connection and query management"""
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        self.config = config or DatabaseConfig()
        self._connection = None
        
    @contextmanager
    def get_connection(self):
        """Get database connection with automatic cleanup"""
        conn = None
        try:
            if self.config.database_url or self.config.db_type == 'postgresql':
                conn = self._get_postgresql_connection()
            else:
                conn = self._get_sqlite_connection()
            
            yield conn
            
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def _get_postgresql_connection(self):
        """Create PostgreSQL connection"""
        try:
            if self.config.database_url:
                return psycopg2.connect(
                    self.config.database_url,
                    cursor_factory=RealDictCursor
                )
            else:
                params = self.config.get_connection_params()
                return psycopg2.connect(
                    host=params['host'],
                    port=params['port'],
                    database=params['database'],
                    user=params['user'],
                    password=params['password'],
                    cursor_factory=RealDictCursor
                )
        except Exception as e:
            logger.warning(f"PostgreSQL connection failed: {e}. Falling back to SQLite.")
            # Fallback to SQLite if PostgreSQL fails
            self.config.db_type = 'sqlite'
            return self._get_sqlite_connection()
    
    def _get_sqlite_connection(self):
        """Create SQLite connection"""
        # Ensure directory exists
        db_path = Path(self.config.sqlite_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database if needed
        self._ensure_database_initialized()
        
        conn = sqlite3.connect(self.config.sqlite_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        return conn
    
    def _ensure_database_initialized(self):
        """Ensure database is initialized with all required tables"""
        try:
            from database.simple_init import ensure_database_exists
            ensure_database_exists()
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
    
    def _force_database_initialization(self):
        """Force database initialization when tables are missing"""
        try:
            from database.simple_init import create_minimal_database
            success = create_minimal_database()
            if not success:
                raise Exception("Failed to create minimal database")
            logger.info("Database force-initialized successfully")
        except Exception as e:
            logger.error(f"Failed to force initialize database: {e}")
            raise
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params or ())
                
                if self.config.db_type == 'postgresql' or self.config.database_url:
                    return [dict(row) for row in cursor.fetchall()]
                else:
                    return [dict(row) for row in cursor.fetchall()]
        except sqlite3.OperationalError as e:
            if "no such table" in str(e).lower():
                # Force database initialization and retry
                logger.warning(f"Table missing, initializing database: {e}")
                self._force_database_initialization()
                # Retry the query
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(query, params or ())
                    return [dict(row) for row in cursor.fetchall()]
            else:
                raise
    
    def execute_command(self, command: str, params: Optional[tuple] = None) -> int:
        """Execute an INSERT, UPDATE, or DELETE command"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(command, params or ())
                conn.commit()
                return cursor.rowcount
        except sqlite3.OperationalError as e:
            if "no such table" in str(e).lower():
                # Force database initialization and retry
                logger.warning(f"Table missing, initializing database: {e}")
                self._force_database_initialization()
                # Retry the command
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(command, params or ())
                    conn.commit()
                    return cursor.rowcount
            else:
                raise
    
    def execute_many(self, command: str, params_list: List[tuple]) -> int:
        """Execute multiple commands with different parameters"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(command, params_list)
            conn.commit()
            return cursor.rowcount
    
    def get_single_result(self, query: str, params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
        """Execute query and return single result or None"""
        results = self.execute_query(query, params)
        return results[0] if results else None
    
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database"""
        if self.config.db_type == 'postgresql' or self.config.database_url:
            query = """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                );
            """
        else:
            query = """
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=?;
            """
        
        result = self.get_single_result(query, (table_name,))
        
        if self.config.db_type == 'postgresql' or self.config.database_url:
            return result['exists'] if result else False
        else:
            return result is not None
    
    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """Get table schema information"""
        if self.config.db_type == 'postgresql' or self.config.database_url:
            query = """
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = %s
                ORDER BY ordinal_position;
            """
        else:
            query = "PRAGMA table_info(?)"
        
        return self.execute_query(query, (table_name,))

class MigrationManager:
    """Database migration management"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.migrations_dir = Path(__file__).parent / 'migrations'
        self.migrations_dir.mkdir(exist_ok=True)
    
    def create_migrations_table(self):
        """Create migrations tracking table"""
        if self.db.config.db_type == 'postgresql' or self.db.config.database_url:
            query = """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    id SERIAL PRIMARY KEY,
                    version VARCHAR(255) UNIQUE NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """
        else:
            query = """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version TEXT UNIQUE NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """
        
        self.db.execute_command(query)
    
    def get_applied_migrations(self) -> List[str]:
        """Get list of applied migration versions"""
        if not self.db.table_exists('schema_migrations'):
            return []
        
        results = self.db.execute_query(
            "SELECT version FROM schema_migrations ORDER BY version"
        )
        return [row['version'] for row in results]
    
    def apply_migration(self, version: str, sql_content: str):
        """Apply a single migration"""
        try:
            # Execute migration SQL
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Split SQL content into individual statements
                statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
                
                for statement in statements:
                    if statement:
                        cursor.execute(statement)
                
                # Record migration as applied
                cursor.execute(
                    "INSERT INTO schema_migrations (version) VALUES (?)" 
                    if self.db.config.db_type == 'sqlite' 
                    else "INSERT INTO schema_migrations (version) VALUES (%s)",
                    (version,)
                )
                conn.commit()
                
            logger.info(f"Applied migration: {version}")
            
        except Exception as e:
            logger.error(f"Failed to apply migration {version}: {e}")
            raise
    
    def run_migrations(self):
        """Run all pending migrations"""
        self.create_migrations_table()
        applied = set(self.get_applied_migrations())
        
        # Get all migration files
        migration_files = sorted([
            f for f in self.migrations_dir.glob('*.sql')
            if f.stem not in applied
        ])
        
        for migration_file in migration_files:
            version = migration_file.stem
            sql_content = migration_file.read_text()
            
            logger.info(f"Applying migration: {version}")
            self.apply_migration(version, sql_content)
    
    def create_initial_migration(self):
        """Create initial migration from schema.sql"""
        schema_file = Path(__file__).parent / 'schema.sql'
        if not schema_file.exists():
            raise FileNotFoundError("schema.sql not found")
        
        migration_file = self.migrations_dir / '001_initial_schema.sql'
        if not migration_file.exists():
            # Convert PostgreSQL schema to SQLite if needed
            schema_content = schema_file.read_text()
            
            if self.db.config.db_type == 'sqlite':
                schema_content = self._convert_postgres_to_sqlite(schema_content)
            
            migration_file.write_text(schema_content)
            logger.info("Created initial migration file")
    
    def _convert_postgres_to_sqlite(self, postgres_sql: str) -> str:
        """Convert PostgreSQL schema to SQLite compatible SQL"""
        # Basic conversions for SQLite compatibility
        sqlite_sql = postgres_sql
        
        # Remove PostgreSQL-specific extensions
        sqlite_sql = sqlite_sql.replace('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";', '')
        
        # Convert UUID to TEXT
        sqlite_sql = sqlite_sql.replace('UUID', 'TEXT')
        sqlite_sql = sqlite_sql.replace('uuid_generate_v4()', "lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || substr(lower(hex(randomblob(2))),2) || '-' || substr('89ab',abs(random()) % 4 + 1, 1) || substr(lower(hex(randomblob(2))),2) || '-' || lower(hex(randomblob(6)))")
        
        # Convert JSONB to JSON
        sqlite_sql = sqlite_sql.replace('JSONB', 'JSON')
        
        # Convert INET to TEXT
        sqlite_sql = sqlite_sql.replace('INET', 'TEXT')
        
        # Convert CHECK constraints (SQLite supports them but syntax might differ)
        # Keep as is for now, SQLite will handle basic CHECK constraints
        
        # Convert DECIMAL to REAL
        sqlite_sql = sqlite_sql.replace('DECIMAL(10,2)', 'REAL')
        sqlite_sql = sqlite_sql.replace('DECIMAL(10,4)', 'REAL')
        sqlite_sql = sqlite_sql.replace('DECIMAL(8,2)', 'REAL')
        
        # Remove PostgreSQL-specific trigger functions
        lines = sqlite_sql.split('\n')
        filtered_lines = []
        skip_trigger = False
        
        for line in lines:
            if 'CREATE OR REPLACE FUNCTION' in line:
                skip_trigger = True
                continue
            elif 'CREATE TRIGGER' in line and 'update_updated_at' in line:
                skip_trigger = True
                continue
            elif skip_trigger and line.strip().endswith(';'):
                skip_trigger = False
                continue
            elif not skip_trigger:
                filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)

# Global database manager instance
db_manager = DatabaseManager()

def get_db() -> DatabaseManager:
    """Get the global database manager instance"""
    return db_manager

def init_database():
    """Initialize database with schema"""
    migration_manager = MigrationManager(db_manager)
    
    try:
        # Create initial migration if it doesn't exist
        migration_manager.create_initial_migration()
        
        # Run all migrations
        migration_manager.run_migrations()
        
        logger.info("Database initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

if __name__ == "__main__":
    # Test database connection
    logging.basicConfig(level=logging.INFO)
    
    print("Testing database connection...")
    
    try:
        db = get_db()
        
        # Test connection
        with db.get_connection() as conn:
            print(f"✅ Connected to {db.config.db_type} database")
        
        # Initialize database
        if init_database():
            print("✅ Database initialized successfully")
        else:
            print("❌ Database initialization failed")
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")