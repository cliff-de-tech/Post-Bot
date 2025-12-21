# Database Migration Guide: SQLite → PostgreSQL

This guide provides instructions for migrating from SQLite to PostgreSQL for production deployment.

## Why PostgreSQL?

| Feature | SQLite | PostgreSQL |
|---------|--------|------------|
| Concurrent writes | ❌ Single writer | ✅ Many writers |
| Scale | Single machine | Distributed |
| Connection pooling | ❌ | ✅ |
| Production ready | Development only | ✅ Enterprise |
| Backups | Manual file copy | Built-in tools |

## Migration Steps

### 1. Install PostgreSQL Dependencies

```bash
pip install psycopg2-binary sqlalchemy
```

### 2. Create PostgreSQL Database

```sql
CREATE DATABASE linkedin_post_bot;
CREATE USER botuser WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE linkedin_post_bot TO botuser;
```

### 3. Update Environment Variables

Add to your `.env`:

```env
# PostgreSQL Connection
DATABASE_URL=postgresql://botuser:your_secure_password@localhost:5432/linkedin_post_bot

# Or for cloud services like Supabase/Neon:
DATABASE_URL=postgresql://user:pass@host:5432/dbname?sslmode=require
```

### 4. Update Database Connection Code

Replace SQLite connections in these files:
- `services/token_store.py`
- `services/user_settings.py`
- `services/post_history.py`

**Before (SQLite):**
```python
import sqlite3
conn = sqlite3.connect('database.db')
```

**After (PostgreSQL with SQLAlchemy):**
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
```

### 5. Create Tables

Run the migration script (create a new file `migrate_to_postgres.py`):

```python
import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # User settings table
    conn.execute(text('''
        CREATE TABLE IF NOT EXISTS user_settings (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(255) UNIQUE NOT NULL,
            linkedin_client_id TEXT,
            linkedin_client_secret TEXT,
            linkedin_user_urn TEXT,
            groq_api_key TEXT,
            github_username TEXT,
            unsplash_access_key TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    '''))
    
    # Accounts/tokens table
    conn.execute(text('''
        CREATE TABLE IF NOT EXISTS accounts (
            id SERIAL PRIMARY KEY,
            linkedin_user_urn VARCHAR(255) UNIQUE,
            access_token TEXT,
            refresh_token TEXT,
            expires_at BIGINT,
            user_id VARCHAR(255)
        )
    '''))
    
    # Post history table
    conn.execute(text('''
        CREATE TABLE IF NOT EXISTS post_history (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(255) NOT NULL,
            post_content TEXT,
            post_type VARCHAR(50),
            context JSONB,
            status VARCHAR(50) DEFAULT 'draft',
            linkedin_post_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    '''))
    
    conn.commit()
    print("✅ Tables created successfully!")
```

### 6. Migrate Existing Data (Optional)

If you have existing SQLite data to migrate:

```python
import sqlite3
from sqlalchemy import create_engine, text
import os

# Source SQLite
sqlite_conn = sqlite3.connect('user_settings.db')
sqlite_cursor = sqlite_conn.cursor()

# Destination PostgreSQL
DATABASE_URL = os.getenv('DATABASE_URL')
pg_engine = create_engine(DATABASE_URL)

# Migrate user_settings
sqlite_cursor.execute('SELECT * FROM user_settings')
rows = sqlite_cursor.fetchall()

with pg_engine.connect() as conn:
    for row in rows:
        conn.execute(text('''
            INSERT INTO user_settings (user_id, linkedin_client_id, linkedin_client_secret, 
                                       linkedin_user_urn, groq_api_key, github_username, unsplash_access_key)
            VALUES (:user_id, :client_id, :client_secret, :urn, :groq, :github, :unsplash)
            ON CONFLICT (user_id) DO NOTHING
        '''), {
            'user_id': row[1],
            'client_id': row[2],
            'client_secret': row[3],
            'urn': row[4],
            'groq': row[5],
            'github': row[6],
            'unsplash': row[7]
        })
    conn.commit()

print("✅ Data migrated successfully!")
```

### 7. Cloud Database Options

For production, consider these managed PostgreSQL services:

| Service | Free Tier | Notes |
|---------|-----------|-------|
| **Supabase** | 500MB | Best DX, easy setup |
| **Neon** | 512MB | Serverless, auto-scaling |
| **Railway** | $5/mo credit | Great for full-stack |
| **PlanetScale** | N/A (MySQL) | If you prefer MySQL |
| **Render** | 90 day free | Easy deployment |

## Security Notes

- Never commit `DATABASE_URL` to git
- Use SSL connections in production (`?sslmode=require`)
- Regularly backup your database
- Use connection pooling for high traffic

## Next Steps After Migration

1. Update all database helper files to use PostgreSQL
2. Test all database operations
3. Set up automated backups
4. Configure connection pooling (e.g., PgBouncer)
