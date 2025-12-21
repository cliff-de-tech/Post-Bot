"""
Scheduled Posts Service
Handles queuing posts for scheduled publishing
"""
import sqlite3
import json
import time
from datetime import datetime
from typing import Optional, List

DB_PATH = "scheduled_posts.db"

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    """Initialize the scheduled posts database"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS scheduled_posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        post_content TEXT NOT NULL,
        image_url TEXT,
        scheduled_time INTEGER NOT NULL,
        status TEXT DEFAULT 'pending',
        error_message TEXT,
        created_at INTEGER NOT NULL,
        published_at INTEGER,
        UNIQUE(user_id, scheduled_time)
    )
    ''')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_scheduled_time ON scheduled_posts(scheduled_time)')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON scheduled_posts(user_id)')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_status ON scheduled_posts(status)')
    conn.commit()
    conn.close()

def schedule_post(
    user_id: str, 
    post_content: str, 
    scheduled_time: int,
    image_url: Optional[str] = None
) -> dict:
    """Schedule a post for later publishing"""
    init_db()
    conn = get_conn()
    cur = conn.cursor()
    
    try:
        cur.execute('''
        INSERT INTO scheduled_posts (user_id, post_content, image_url, scheduled_time, created_at)
        VALUES (?, ?, ?, ?, ?)
        ''', (user_id, post_content, image_url, scheduled_time, int(time.time())))
        
        post_id = cur.lastrowid
        conn.commit()
        
        return {
            "success": True,
            "post_id": post_id,
            "scheduled_time": scheduled_time
        }
    except sqlite3.IntegrityError:
        return {"success": False, "error": "A post is already scheduled for this time"}
    finally:
        conn.close()

def get_scheduled_posts(user_id: str, include_past: bool = False) -> List[dict]:
    """Get all scheduled posts for a user"""
    init_db()
    conn = get_conn()
    cur = conn.cursor()
    
    if include_past:
        cur.execute('''
        SELECT id, post_content, image_url, scheduled_time, status, error_message, created_at, published_at
        FROM scheduled_posts
        WHERE user_id = ?
        ORDER BY scheduled_time ASC
        ''', (user_id,))
    else:
        now = int(time.time())
        cur.execute('''
        SELECT id, post_content, image_url, scheduled_time, status, error_message, created_at, published_at
        FROM scheduled_posts
        WHERE user_id = ? AND (status = 'pending' OR scheduled_time > ?)
        ORDER BY scheduled_time ASC
        ''', (user_id, now - 86400))  # Include posts from last 24h
    
    rows = cur.fetchall()
    conn.close()
    
    return [{
        "id": row[0],
        "post_content": row[1],
        "image_url": row[2],
        "scheduled_time": row[3],
        "status": row[4],
        "error_message": row[5],
        "created_at": row[6],
        "published_at": row[7]
    } for row in rows]

def get_due_posts() -> List[dict]:
    """Get all posts that are due to be published"""
    init_db()
    conn = get_conn()
    cur = conn.cursor()
    
    now = int(time.time())
    cur.execute('''
    SELECT id, user_id, post_content, image_url, scheduled_time
    FROM scheduled_posts
    WHERE status = 'pending' AND scheduled_time <= ?
    ORDER BY scheduled_time ASC
    ''', (now,))
    
    rows = cur.fetchall()
    conn.close()
    
    return [{
        "id": row[0],
        "user_id": row[1],
        "post_content": row[2],
        "image_url": row[3],
        "scheduled_time": row[4]
    } for row in rows]

def update_post_status(post_id: int, status: str, error_message: Optional[str] = None):
    """Update the status of a scheduled post"""
    init_db()
    conn = get_conn()
    cur = conn.cursor()
    
    published_at = int(time.time()) if status == 'published' else None
    
    cur.execute('''
    UPDATE scheduled_posts
    SET status = ?, error_message = ?, published_at = ?
    WHERE id = ?
    ''', (status, error_message, published_at, post_id))
    
    conn.commit()
    conn.close()

def cancel_scheduled_post(post_id: int, user_id: str) -> bool:
    """Cancel a scheduled post"""
    init_db()
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute('''
    DELETE FROM scheduled_posts
    WHERE id = ? AND user_id = ? AND status = 'pending'
    ''', (post_id, user_id))
    
    deleted = cur.rowcount > 0
    conn.commit()
    conn.close()
    
    return deleted

def reschedule_post(post_id: int, user_id: str, new_time: int) -> bool:
    """Reschedule a pending post"""
    init_db()
    conn = get_conn()
    cur = conn.cursor()
    
    try:
        cur.execute('''
        UPDATE scheduled_posts
        SET scheduled_time = ?
        WHERE id = ? AND user_id = ? AND status = 'pending'
        ''', (new_time, post_id, user_id))
        
        updated = cur.rowcount > 0
        conn.commit()
        return updated
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()
