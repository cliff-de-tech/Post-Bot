"""
Feedback Service (PostgreSQL Async)

Collects user feedback and stores in PostgreSQL.
Optionally sends feedback to admin email.
"""

import time
import logging
from typing import Optional
from services.db import get_database

logger = logging.getLogger(__name__)


async def save_feedback(
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
    db = get_database()
    
    try:
        await db.execute("""
            INSERT INTO feedback (user_id, rating, liked, improvements, suggestions, created_at)
            VALUES ($1, $2, $3, $4, $5, $6)
        """, [
            user_id,
            rating,
            liked or '',
            improvements or '',
            suggestions or '',
            int(time.time())
        ])
        
        # Get the ID of the inserted feedback
        row = await db.fetch_one(
            "SELECT id FROM feedback WHERE user_id = $1 ORDER BY id DESC LIMIT 1",
            [user_id]
        )
        feedback_id = row['id'] if row else None
        
        return {
            'success': True,
            'feedback_id': feedback_id,
            'message': 'Thank you for your feedback!'
        }
    except Exception as e:
        logger.error(f"Error saving feedback: {e}")
        return {
            'success': False,
            'error': str(e)
        }


async def get_all_feedback(limit: int = 100) -> list:
    """Get all feedback entries (for admin use)."""
    db = get_database()
    
    rows = await db.fetch_all("""
        SELECT id, user_id, rating, liked, improvements, suggestions, created_at
        FROM feedback
        ORDER BY created_at DESC
        LIMIT $1
    """, [limit])
    
    return [
        {
            'id': row['id'],
            'user_id': row['user_id'],
            'rating': row['rating'],
            'liked': row['liked'],
            'improvements': row['improvements'],
            'suggestions': row['suggestions'],
            'created_at': row['created_at']
        }
        for row in rows
    ]


async def get_user_feedback_count(user_id: str) -> int:
    """Check how many times a user has submitted feedback."""
    db = get_database()
    
    row = await db.fetch_one(
        "SELECT COUNT(*) as count FROM feedback WHERE user_id = $1",
        [user_id]
    )
    
    return row['count'] if row else 0


async def has_user_submitted_feedback(user_id: str) -> bool:
    """Check if user has ever submitted feedback."""
    count = await get_user_feedback_count(user_id)
    return count > 0
