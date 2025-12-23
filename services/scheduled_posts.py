"""
Scheduled Posts Service (PostgreSQL Async)

Handles queuing posts for scheduled publishing.
"""

import time
import logging
from typing import Optional, List
from services.db import get_database

logger = logging.getLogger(__name__)


async def schedule_post(
    user_id: str, 
    post_content: str, 
    scheduled_time: int,
    image_url: Optional[str] = None
) -> dict:
    """Schedule a post for later publishing."""
    db = get_database()
    
    try:
        await db.execute("""
            INSERT INTO scheduled_posts (user_id, post_content, image_url, scheduled_time, created_at)
            VALUES ($1, $2, $3, $4, $5)
        """, [user_id, post_content, image_url, scheduled_time, int(time.time())])
        
        # Get the ID of the inserted post
        row = await db.fetch_one(
            "SELECT id FROM scheduled_posts WHERE user_id = $1 AND scheduled_time = $2",
            [user_id, scheduled_time]
        )
        post_id = row['id'] if row else None
        
        return {
            "success": True,
            "post_id": post_id,
            "scheduled_time": scheduled_time
        }
    except Exception as e:
        if "unique" in str(e).lower() or "duplicate" in str(e).lower():
            return {"success": False, "error": "A post is already scheduled for this time"}
        logger.error(f"Error scheduling post: {e}")
        return {"success": False, "error": str(e)}


async def get_scheduled_posts(user_id: str, include_past: bool = False) -> List[dict]:
    """Get all scheduled posts for a user."""
    db = get_database()
    
    if include_past:
        rows = await db.fetch_all("""
            SELECT id, post_content, image_url, scheduled_time, status, error_message, created_at, published_at
            FROM scheduled_posts
            WHERE user_id = $1
            ORDER BY scheduled_time ASC
        """, [user_id])
    else:
        now = int(time.time())
        rows = await db.fetch_all("""
            SELECT id, post_content, image_url, scheduled_time, status, error_message, created_at, published_at
            FROM scheduled_posts
            WHERE user_id = $1 AND (status = 'pending' OR scheduled_time > $2)
            ORDER BY scheduled_time ASC
        """, [user_id, now - 86400])
    
    return [{
        "id": row['id'],
        "post_content": row['post_content'],
        "image_url": row['image_url'],
        "scheduled_time": row['scheduled_time'],
        "status": row['status'],
        "error_message": row['error_message'],
        "created_at": row['created_at'],
        "published_at": row['published_at']
    } for row in rows]


async def get_due_posts() -> List[dict]:
    """Get all posts that are due to be published."""
    db = get_database()
    
    now = int(time.time())
    rows = await db.fetch_all("""
        SELECT id, user_id, post_content, image_url, scheduled_time
        FROM scheduled_posts
        WHERE status = 'pending' AND scheduled_time <= $1
        ORDER BY scheduled_time ASC
    """, [now])
    
    return [{
        "id": row['id'],
        "user_id": row['user_id'],
        "post_content": row['post_content'],
        "image_url": row['image_url'],
        "scheduled_time": row['scheduled_time']
    } for row in rows]


async def update_post_status(post_id: int, status: str, error_message: Optional[str] = None) -> None:
    """Update the status of a scheduled post."""
    db = get_database()
    
    published_at = int(time.time()) if status == 'published' else None
    
    await db.execute("""
        UPDATE scheduled_posts
        SET status = $1, error_message = $2, published_at = $3
        WHERE id = $4
    """, [status, error_message, published_at, post_id])


async def cancel_scheduled_post(post_id: int, user_id: str) -> bool:
    """Cancel a scheduled post."""
    db = get_database()
    
    result = await db.execute("""
        DELETE FROM scheduled_posts
        WHERE id = $1 AND user_id = $2 AND status = 'pending'
    """, [post_id, user_id])
    
    return result > 0 if isinstance(result, int) else True


async def reschedule_post(post_id: int, user_id: str, new_time: int) -> bool:
    """Reschedule a pending post."""
    db = get_database()
    
    try:
        result = await db.execute("""
            UPDATE scheduled_posts
            SET scheduled_time = $1
            WHERE id = $2 AND user_id = $3 AND status = 'pending'
        """, [new_time, post_id, user_id])
        
        return result > 0 if isinstance(result, int) else True
    except Exception as e:
        if "unique" in str(e).lower() or "duplicate" in str(e).lower():
            return False
        raise
