# 🗄️ Setup Persistent Database for User Data

## Problem
Your current SQLite database (`data/app.db`) will be wiped every time Streamlit Cloud redeploys your app. All users and analysis history will be lost.

## Solution Options

### Option 1: PostgreSQL (Recommended) 🌟

#### Free PostgreSQL Providers:
1. **Neon** (https://neon.tech) - Free tier: 512MB storage
2. **Supabase** (https://supabase.com) - Free tier: 500MB storage  
3. **Railway** (https://railway.app) - Free tier with PostgreSQL
4. **ElephantSQL** (https://www.elephantsql.com) - Free tier: 20MB

#### Setup Steps:
1. **Create PostgreSQL database** on one of the providers above
2. **Get connection URL** (format: `postgresql://user:password@host:port/database`)
3. **Update Streamlit secrets** with the new DATABASE_URL
4. **Migrate existing data** (optional)

#### Example Streamlit Secrets:
```toml
DATABASE_URL = "postgresql://username:password@hostname:5432/database_name"
```

### Option 2: Streamlit Cloud + External SQLite (Workaround)
- Use a service like **Turso** (https://turso.tech) for hosted SQLite
- More complex setup but keeps SQLite compatibility

### Option 3: Export/Import Users (Temporary)
- Export current users before deployment
- Import them back after deployment
- Not ideal for production use

## Migration Script

If you choose PostgreSQL, here's a migration script:

```python
# migrate_to_postgresql.py
import sqlite3
import psycopg2
import os

def migrate_sqlite_to_postgresql():
    # Connect to SQLite
    sqlite_conn = sqlite3.connect('data/app.db')
    sqlite_conn.row_factory = sqlite3.Row
    
    # Connect to PostgreSQL
    pg_conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    
    # Migrate users table
    sqlite_cursor = sqlite_conn.cursor()
    sqlite_cursor.execute("SELECT * FROM users")
    users = sqlite_cursor.fetchall()
    
    pg_cursor = pg_conn.cursor()
    for user in users:
        pg_cursor.execute("""
            INSERT INTO users (id, email, password_hash, full_name, created_at, is_active)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, (user['id'], user['email'], user['password_hash'], 
              user['full_name'], user['created_at'], user['is_active']))
    
    # Migrate analysis_sessions
    sqlite_cursor.execute("SELECT * FROM analysis_sessions")
    sessions = sqlite_cursor.fetchall()
    
    for session in sessions:
        pg_cursor.execute("""
            INSERT INTO analysis_sessions (id, user_id, resume_filename, score, match_category, created_at, analysis_result)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, (session['id'], session['user_id'], session['resume_filename'],
              session['score'], session['match_category'], session['created_at'], session['analysis_result']))
    
    pg_conn.commit()
    pg_conn.close()
    sqlite_conn.close()
    
    print("✅ Migration completed!")

if __name__ == "__main__":
    migrate_sqlite_to_postgresql()
```

## Immediate Action Required

1. **Choose a PostgreSQL provider** (Neon recommended for free tier)
2. **Create database** and get connection URL
3. **Update Streamlit Cloud secrets** with new DATABASE_URL
4. **Test the connection** before going live
5. **Optionally migrate existing users** using the script above

## Timeline
- **Setup time:** 15-30 minutes
- **Migration time:** 5 minutes
- **Testing time:** 10 minutes

Without this change, every deployment will wipe all user data!