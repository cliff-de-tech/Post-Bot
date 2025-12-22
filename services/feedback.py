"""
Feedback Service
Collects user feedback and stores in SQLite database.
Optionally sends feedback to admin email.
"""

import sqlite3
import os
import time
from typing import Optional
import threading


# Database path
FEEDBACK_DB_PATH = os.getenv('FEEDBACK_DB_PATH', 
                              os.path.join(os.path.dirname(__file__), '..', 'feedback.db'))

_local = threading.local()


def get_conn():
    """Get thread-local database connection"""
    if not hasattr(_local, 'conn') or _local.conn is None:
        _local.conn = sqlite3.connect(FEEDBACK_DB_PATH, check_same_thread=False)
    return _local.conn


def init_db():
    """Initialize the feedback database"""
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute('''
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        rating INTEGER,
        liked TEXT,
        improvements TEXT,
        suggestions TEXT,
        created_at INTEGER NOT NULL,
        email_sent INTEGER DEFAULT 0
    )
    ''')
    
    # Create index for faster queries
    cur.execute('''
    CREATE INDEX IF NOT EXISTS idx_feedback_user 
    ON feedback (user_id, created_at DESC)
    ''')
    
    conn.commit()


def save_feedback(
    user_id: str,
    rating: int,
    liked: Optional[str] = None,
    improvements: Optional[str] = None,
    suggestions: Optional[str] = None
) -> dict:
    """
    Save user feedback to database.
    
    Args:
        user_id: User's unique identifier
        rating: Rating 1-5 stars
        liked: What user liked (optional)
        improvements: What could be improved (required for submission)
        suggestions: Additional suggestions (optional)
    
    Returns:
        dict with success status and feedback_id
    """
    init_db()
    conn = get_conn()
    cur = conn.cursor()
    
    try:
        cur.execute('''
        INSERT INTO feedback (user_id, rating, liked, improvements, suggestions, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            rating,
            liked or '',
            improvements or '',
            suggestions or '',
            int(time.time())
        ))
        
        conn.commit()
        feedback_id = cur.lastrowid
        
        return {
            'success': True,
            'feedback_id': feedback_id,
            'message': 'Thank you for your feedback!'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def get_all_feedback(limit: int = 100) -> list:
    """Get all feedback entries (for admin use)"""
    init_db()
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute('''
    SELECT id, user_id, rating, liked, improvements, suggestions, created_at
    FROM feedback
    ORDER BY created_at DESC
    LIMIT ?
    ''', (limit,))
    
    rows = cur.fetchall()
    
    return [
        {
            'id': row[0],
            'user_id': row[1],
            'rating': row[2],
            'liked': row[3],
            'improvements': row[4],
            'suggestions': row[5],
            'created_at': row[6]
        }
        for row in rows
    ]


def get_user_feedback_count(user_id: str) -> int:
    """Check how many times a user has submitted feedback"""
    init_db()
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute('''
    SELECT COUNT(*) FROM feedback WHERE user_id = ?
    ''', (user_id,))
    
    return cur.fetchone()[0]


def has_user_submitted_feedback(user_id: str) -> bool:
    """Check if user has ever submitted feedback"""
    return get_user_feedback_count(user_id) > 0
