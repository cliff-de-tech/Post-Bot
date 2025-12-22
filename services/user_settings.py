"""
User Settings Storage Service - Preferences Only

Stores per-user preferences, onboarding state, and connection status.

IMPORTANT - NO SECRETS STORED HERE:
    This module does NOT store any sensitive credentials.
    All tokens and secrets are stored in token_store.py with encryption.
    
    The following are stored in ENV ONLY (never in DB):
    - GROQ_API_KEY
    - LINKEDIN_CLIENT_SECRET  
    - UNSPLASH_ACCESS_KEY
    - GITHUB_TOKEN

WHAT IS STORED HERE:
    - user_id: Clerk user ID (tenant isolation key)
    - github_username: Public GitHub username
    - preferences: JSON blob for UI preferences
    - onboarding_complete: Boolean flag
    - subscription_tier: 'free' | 'pro' | 'enterprise'
    - subscription_status: 'active' | 'cancelled' | 'expired'
    - created_at / updated_at: Timestamps

MULTI-TENANT ISOLATION:
    - All queries filter by user_id (Clerk ID)
    - No cross-tenant data access is possible
    - Uses parameterized queries to prevent SQL injection
"""

import sqlite3
import os
import json
import time

DB_PATH = os.getenv('USER_SETTINGS_DB_PATH', os.path.join(os.path.dirname(__file__), '..', 'user_settings.db'))


def get_conn():
    """Get database connection, creating directory if needed."""
    dirpath = os.path.dirname(DB_PATH)
    if dirpath and not os.path.exists(dirpath):
        try:
            os.makedirs(dirpath, exist_ok=True)
        except Exception:
            pass
    conn = sqlite3.connect(DB_PATH)
    return conn


def init_db():
    """
    Initialize the database schema.
    
    Creates a clean preferences-only schema.
    Handles migration from old secrets-based schema.
    """
    conn = get_conn()
    cur = conn.cursor()
    
    # Check if table exists
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_settings'")
    table_exists = cur.fetchone() is not None
    
    if not table_exists:
        # Create new clean schema (no secrets)
        cur.execute('''
        CREATE TABLE user_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE,
            github_username TEXT,
            preferences TEXT DEFAULT '{}',
            onboarding_complete INTEGER DEFAULT 0,
            subscription_tier TEXT DEFAULT 'free',
            subscription_status TEXT DEFAULT 'active',
            subscription_expires_at INTEGER,
            created_at INTEGER,
            updated_at INTEGER
        )
        ''')
    else:
        # Migration: Add new columns if needed
        cur.execute("PRAGMA table_info(user_settings)")
        columns = [info[1] for info in cur.fetchall()]
        
        if 'preferences' not in columns:
            cur.execute("ALTER TABLE user_settings ADD COLUMN preferences TEXT DEFAULT '{}'")
        if 'onboarding_complete' not in columns:
            cur.execute("ALTER TABLE user_settings ADD COLUMN onboarding_complete INTEGER DEFAULT 0")
        if 'subscription_tier' not in columns:
            cur.execute("ALTER TABLE user_settings ADD COLUMN subscription_tier TEXT DEFAULT 'free'")
        if 'subscription_status' not in columns:
            cur.execute("ALTER TABLE user_settings ADD COLUMN subscription_status TEXT DEFAULT 'active'")
        if 'subscription_expires_at' not in columns:
            cur.execute("ALTER TABLE user_settings ADD COLUMN subscription_expires_at INTEGER")

    conn.commit()
    conn.close()


def save_user_settings(user_id: str, settings: dict):
    """
    Save or update user preferences.
    
    Args:
        user_id: Clerk user ID
        settings: Dict containing preferences to save
        
    Accepted fields:
        - github_username: Public GitHub username
        - preferences: Dict of UI preferences
        - onboarding_complete: Boolean
        - subscription_tier: 'free' | 'pro' | 'enterprise'
        - subscription_status: 'active' | 'cancelled' | 'expired'
        
    SECURITY: No secrets should be passed to this function.
    
    TENANT ISOLATION:
        - Settings are saved scoped to user_id
        - Each user can only modify their own settings
    """
    init_db()
    conn = get_conn()
    cur = conn.cursor()
    
    timestamp = int(time.time())
    
    # Get existing settings to merge
    existing = get_user_settings(user_id) or {}
    
    # Merge fields (only update if provided)
    def merge_field(key, default=None):
        new_val = settings.get(key)
        if new_val is not None:
            return new_val
        return existing.get(key, default)
    
    merged = {
        'github_username': merge_field('github_username', ''),
        'preferences': settings.get('preferences') or existing.get('preferences') or {},
        'onboarding_complete': merge_field('onboarding_complete', 0),
        'subscription_tier': merge_field('subscription_tier', 'free'),
        'subscription_status': merge_field('subscription_status', 'active'),
    }
    
    # Convert preferences dict to JSON
    preferences_json = json.dumps(merged['preferences']) if isinstance(merged['preferences'], dict) else merged['preferences']
    
    cur.execute('''
    INSERT INTO user_settings 
    (user_id, github_username, preferences, onboarding_complete, 
     subscription_tier, subscription_status, updated_at, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(user_id) DO UPDATE SET
        github_username=excluded.github_username,
        preferences=excluded.preferences,
        onboarding_complete=excluded.onboarding_complete,
        subscription_tier=excluded.subscription_tier,
        subscription_status=excluded.subscription_status,
        updated_at=excluded.updated_at
    ''', (
        user_id,
        merged['github_username'],
        preferences_json,
        1 if merged['onboarding_complete'] else 0,
        merged['subscription_tier'],
        merged['subscription_status'],
        timestamp,
        existing.get('created_at', timestamp)
    ))
    
    conn.commit()
    conn.close()


def get_user_settings(user_id: str) -> dict | None:
    """
    Get user preferences by Clerk user ID.
    
    Args:
        user_id: Clerk user ID
        
    Returns:
        Dict with user preferences, or None if not found
        
    TENANT ISOLATION:
        - Query explicitly filters by user_id
        - User can only retrieve their own settings
    """
    init_db()
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # TENANT ISOLATION: Query filters by user_id
    cur.execute('SELECT * FROM user_settings WHERE user_id=?', (user_id,))
    row = cur.fetchone()
    conn.close()
    
    if not row:
        return None
    
    def get_col(name, default=None):
        try:
            return row[name]
        except (IndexError, KeyError):
            return default
    
    # Parse preferences JSON
    preferences_raw = get_col('preferences', '{}')
    try:
        preferences = json.loads(preferences_raw) if preferences_raw else {}
    except json.JSONDecodeError:
        preferences = {}
    
    return {
        'user_id': get_col('user_id'),
        'github_username': get_col('github_username', ''),
        'preferences': preferences,
        'onboarding_complete': bool(get_col('onboarding_complete', 0)),
        'subscription_tier': get_col('subscription_tier', 'free'),
        'subscription_status': get_col('subscription_status', 'active'),
        'subscription_expires_at': get_col('subscription_expires_at'),
        'created_at': get_col('created_at'),
        'updated_at': get_col('updated_at')
    }


def mark_onboarding_complete(user_id: str):
    """Mark user's onboarding as complete."""
    save_user_settings(user_id, {'onboarding_complete': True})


def get_subscription_info(user_id: str) -> dict:
    """
    Get subscription info for a user (safe for frontend).
    
    Returns:
        Dict with subscription tier and status
    """
    settings = get_user_settings(user_id)
    if not settings:
        return {
            'tier': 'free',
            'status': 'active',
            'expires_at': None
        }
    
    return {
        'tier': settings.get('subscription_tier', 'free'),
        'status': settings.get('subscription_status', 'active'),
        'expires_at': settings.get('subscription_expires_at')
    }


# =============================================================================
# DEPRECATED - MIGRATION HELPERS
# =============================================================================
# The following functions help migrate from the old secrets-in-settings schema

def get_legacy_secrets(user_id: str) -> dict | None:
    """
    Get any legacy secrets that may still be in the old schema.
    
    Used during migration to move secrets to token_store.
    
    DEPRECATED: Will be removed in future version.
    """
    init_db()
    conn = get_conn()
    cur = conn.cursor()
    
    # Check if old secret columns exist
    cur.execute("PRAGMA table_info(user_settings)")
    columns = [info[1] for info in cur.fetchall()]
    
    legacy_fields = []
    for field in ['linkedin_client_id', 'linkedin_client_secret', 'groq_api_key', 'unsplash_access_key']:
        if field in columns:
            legacy_fields.append(field)
    
    if not legacy_fields:
        conn.close()
        return None
    
    # Fetch legacy secrets
    query = f"SELECT {', '.join(legacy_fields)} FROM user_settings WHERE user_id=?"
    cur.execute(query, (user_id,))
    row = cur.fetchone()
    conn.close()
    
    if not row:
        return None
    
    return dict(zip(legacy_fields, row))
