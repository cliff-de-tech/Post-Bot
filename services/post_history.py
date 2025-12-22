import sqlite3
import os
import json
import time

DB_PATH = os.getenv('POST_HISTORY_DB_PATH', os.path.join(os.path.dirname(__file__), '..', 'post_history.db'))


def get_conn():
    dirpath = os.path.dirname(DB_PATH)
    if dirpath and not os.path.exists(dirpath):
        try:
            os.makedirs(dirpath, exist_ok=True)
        except Exception:
            pass
    conn = sqlite3.connect(DB_PATH)
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS post_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        post_content TEXT,
        post_type TEXT,
        context TEXT,
        status TEXT,
        linkedin_post_id TEXT,
        engagement TEXT,
        created_at INTEGER,
        published_at INTEGER
    )
    ''')
    conn.commit()
    conn.close()


def save_post(user_id: str, post_content: str, post_type: str, context: dict, status: str = 'draft', linkedin_post_id: str = None):
    init_db()
    conn = get_conn()
    cur = conn.cursor()
    
    timestamp = int(time.time())
    published_at = timestamp if status == 'published' else None
    
    cur.execute('''
    INSERT INTO post_history 
    (user_id, post_content, post_type, context, status, linkedin_post_id, engagement, created_at, published_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        post_content,
        post_type,
        json.dumps(context),
        status,
        linkedin_post_id,
        json.dumps({}),
        timestamp,
        published_at
    ))
    post_id = cur.lastrowid
    conn.commit()
    conn.close()
    return post_id


def get_user_posts(user_id: str, limit: int = 50, status: str = None):
    init_db()
    conn = get_conn()
    cur = conn.cursor()
    
    if status:
        cur.execute('''
        SELECT id, post_content, post_type, context, status, linkedin_post_id, engagement, created_at, published_at
        FROM post_history 
        WHERE user_id=? AND status=?
        ORDER BY created_at DESC
        LIMIT ?
        ''', (user_id, status, limit))
    else:
        cur.execute('''
        SELECT id, post_content, post_type, context, status, linkedin_post_id, engagement, created_at, published_at
        FROM post_history 
        WHERE user_id=?
        ORDER BY created_at DESC
        LIMIT ?
        ''', (user_id, limit))
    
    rows = cur.fetchall()
    conn.close()
    
    posts = []
    for row in rows:
        posts.append({
            'id': row[0],
            'post_content': row[1],
            'post_type': row[2],
            'context': json.loads(row[3]) if row[3] else {},
            'status': row[4],
            'linkedin_post_id': row[5],
            'engagement': json.loads(row[6]) if row[6] else {},
            'created_at': row[7],
            'published_at': row[8]
        })
    
    return posts


def update_post_status(post_id: int, status: str, linkedin_post_id: str = None):
    conn = get_conn()
    cur = conn.cursor()
    
    published_at = int(time.time()) if status == 'published' else None
    
    if linkedin_post_id:
        cur.execute('''
        UPDATE post_history 
        SET status=?, linkedin_post_id=?, published_at=?
        WHERE id=?
        ''', (status, linkedin_post_id, published_at, post_id))
    else:
        cur.execute('''
        UPDATE post_history 
        SET status=?, published_at=?
        WHERE id=?
        ''', (status, published_at, post_id))
    
    conn.commit()
    conn.close()


def delete_post(post_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('DELETE FROM post_history WHERE id=?', (post_id,))
    conn.commit()
    conn.close()


def get_user_stats(user_id: str):
    init_db()
    conn = get_conn()
    cur = conn.cursor()
    
    # Total posts
    cur.execute('SELECT COUNT(*) FROM post_history WHERE user_id=?', (user_id,))
    total_posts = cur.fetchone()[0]
    
    # Published posts
    cur.execute('SELECT COUNT(*) FROM post_history WHERE user_id=? AND status=?', (user_id, 'published'))
    published_posts = cur.fetchone()[0]
    
    # This month
    current_month_start = int(time.time()) - (30 * 24 * 60 * 60)
    cur.execute('SELECT COUNT(*) FROM post_history WHERE user_id=? AND created_at > ?', (user_id, current_month_start))
    posts_this_month = cur.fetchone()[0]
    
    conn.close()
    
    return {
        'total_posts': total_posts,
        'published_posts': published_posts,
        'posts_this_month': posts_this_month,
        'draft_posts': total_posts - published_posts
    }


# =============================================================================
# FREE TIER USAGE TRACKING
# =============================================================================

# Free tier limits
FREE_TIER_DAILY_POSTS = 10
FREE_TIER_SCHEDULED_POSTS = 10


def get_daily_post_count(user_id: str) -> int:
    """
    Count posts created by user today (UTC).
    Used for enforcing daily post generation limit.
    """
    init_db()
    conn = get_conn()
    cur = conn.cursor()
    
    # Get start of today (UTC midnight)
    import datetime
    today_start = int(datetime.datetime.utcnow().replace(
        hour=0, minute=0, second=0, microsecond=0
    ).timestamp())
    
    cur.execute('''
    SELECT COUNT(*) FROM post_history 
    WHERE user_id=? AND created_at >= ?
    ''', (user_id, today_start))
    
    count = cur.fetchone()[0]
    conn.close()
    return count


def get_scheduled_post_count(user_id: str) -> int:
    """
    Count pending scheduled posts for user.
    Free tier is limited to 10 scheduled posts.
    """
    # Note: This queries the scheduled_posts table, not post_history
    # Scheduled posts are managed separately
    try:
        scheduled_db_path = os.getenv('SCHEDULED_POSTS_DB_PATH', 
                                       os.path.join(os.path.dirname(__file__), '..', 'scheduled_posts.db'))
        conn = sqlite3.connect(scheduled_db_path)
        cur = conn.cursor()
        
        cur.execute('''
        SELECT COUNT(*) FROM scheduled_posts 
        WHERE user_id=? AND status='pending'
        ''', (user_id,))
        
        count = cur.fetchone()[0]
        conn.close()
        return count
    except Exception:
        # If scheduled_posts table doesn't exist yet, return 0
        return 0


def get_user_usage(user_id: str, tier: str = "free") -> dict:
    """
    Get comprehensive usage data for a user.
    Returns current usage counts, limits, and reset time.
    """
    import datetime
    
    posts_today = get_daily_post_count(user_id)
    scheduled_count = get_scheduled_post_count(user_id)
    
    # Calculate time until reset (next UTC midnight)
    now = datetime.datetime.utcnow()
    tomorrow = (now + datetime.timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    seconds_until_reset = int((tomorrow - now).total_seconds())
    
    if tier == "free":
        return {
            "tier": "free",
            "posts_today": posts_today,
            "posts_limit": FREE_TIER_DAILY_POSTS,
            "posts_remaining": max(0, FREE_TIER_DAILY_POSTS - posts_today),
            "scheduled_count": scheduled_count,
            "scheduled_limit": FREE_TIER_SCHEDULED_POSTS,
            "scheduled_remaining": max(0, FREE_TIER_SCHEDULED_POSTS - scheduled_count),
            "resets_in_seconds": seconds_until_reset,
            "resets_at": tomorrow.isoformat() + "Z"
        }
    else:
        # Pro/Team tiers have unlimited usage
        return {
            "tier": tier,
            "posts_today": posts_today,
            "posts_limit": -1,  # -1 = unlimited
            "posts_remaining": -1,
            "scheduled_count": scheduled_count,
            "scheduled_limit": -1,
            "scheduled_remaining": -1,
            "resets_in_seconds": 0,
            "resets_at": None
        }


def can_user_generate_posts(user_id: str, count: int = 1, tier: str = "free") -> dict:
    """
    Check if user can generate more posts.
    Returns { allowed: bool, reason: str, remaining: int }
    """
    if tier != "free":
        return {"allowed": True, "reason": None, "remaining": -1}
    
    posts_today = get_daily_post_count(user_id)
    remaining = FREE_TIER_DAILY_POSTS - posts_today
    
    if remaining <= 0:
        return {
            "allowed": False,
            "reason": f"Daily limit reached. You've used all {FREE_TIER_DAILY_POSTS} posts today.",
            "remaining": 0
        }
    
    if count > remaining:
        return {
            "allowed": False,
            "reason": f"You can only generate {remaining} more post(s) today.",
            "remaining": remaining
        }
    
    return {"allowed": True, "reason": None, "remaining": remaining}


def can_user_schedule_post(user_id: str, tier: str = "free") -> dict:
    """
    Check if user can schedule another post.
    Free tier limited to 10 scheduled posts.
    """
    if tier != "free":
        return {"allowed": True, "reason": None, "remaining": -1}
    
    scheduled_count = get_scheduled_post_count(user_id)
    remaining = FREE_TIER_SCHEDULED_POSTS - scheduled_count
    
    if remaining <= 0:
        return {
            "allowed": False,
            "reason": f"Scheduled posts limit reached. Free tier allows {FREE_TIER_SCHEDULED_POSTS} scheduled posts.",
            "remaining": 0
        }
    
    return {"allowed": True, "reason": None, "remaining": remaining}
