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
    
    # Total posts (all time)
    cur.execute('SELECT COUNT(*) FROM post_history WHERE user_id=?', (user_id,))
    total_posts = cur.fetchone()[0]
    
    # Published posts (all time)
    cur.execute('SELECT COUNT(*) FROM post_history WHERE user_id=? AND status=?', (user_id, 'published'))
    published_posts = cur.fetchone()[0]
    
    # This month (30 days)
    current_month_start = int(time.time()) - (30 * 24 * 60 * 60)
    cur.execute('SELECT COUNT(*) FROM post_history WHERE user_id=? AND created_at > ?', (user_id, current_month_start))
    posts_this_month = cur.fetchone()[0]
    
    # Week-over-week growth calculation
    one_week_ago = int(time.time()) - (7 * 24 * 60 * 60)
    two_weeks_ago = int(time.time()) - (14 * 24 * 60 * 60)
    
    # Posts this week (last 7 days)
    cur.execute('SELECT COUNT(*) FROM post_history WHERE user_id=? AND created_at > ?', 
                (user_id, one_week_ago))
    posts_this_week = cur.fetchone()[0]
    
    # Posts last week (7-14 days ago)
    cur.execute('SELECT COUNT(*) FROM post_history WHERE user_id=? AND created_at > ? AND created_at <= ?', 
                (user_id, two_weeks_ago, one_week_ago))
    posts_last_week = cur.fetchone()[0]
    
    # Calculate growth percentage
    if posts_last_week > 0:
        growth_percentage = round(((posts_this_week - posts_last_week) / posts_last_week) * 100)
    elif posts_this_week > 0:
        growth_percentage = 100  # All new this week (100% growth from 0)
    else:
        growth_percentage = 0  # No posts at all
    
    conn.close()
    
    return {
        'posts_generated': total_posts,
        'posts_published': published_posts,
        'posts_this_month': posts_this_month,
        'posts_this_week': posts_this_week,
        'posts_last_week': posts_last_week,
        'growth_percentage': growth_percentage,
        'draft_posts': total_posts - published_posts
    }


# =============================================================================
# FREE TIER USAGE TRACKING
# =============================================================================

# Free tier limits
FREE_TIER_DAILY_POSTS = 10
FREE_TIER_SCHEDULED_POSTS = 10


def get_daily_post_count(user_id: str, user_timezone: str = "UTC") -> int:
    """
    Count PUBLISHED posts by user today (in user's local timezone).
    Used for enforcing daily post limit (10 published posts/day for free tier).
    
    Args:
        user_id: The user's ID
        user_timezone: User's timezone string (e.g., 'America/New_York', 'Europe/London')
                      Defaults to UTC if not provided or invalid.
    """
    init_db()
    conn = get_conn()
    cur = conn.cursor()
    
    # Get start of today in user's timezone
    import datetime
    try:
        from zoneinfo import ZoneInfo
        user_tz = ZoneInfo(user_timezone)
    except Exception:
        # Fallback to UTC if timezone invalid
        from zoneinfo import ZoneInfo
        user_tz = ZoneInfo("UTC")
    
    # Get current time in user's timezone
    now_local = datetime.datetime.now(user_tz)
    # Get start of today (midnight) in user's timezone
    today_start_local = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
    # Convert to UTC timestamp for database query
    today_start_utc = int(today_start_local.timestamp())
    
    # Only count PUBLISHED posts (not drafts or generated)
    cur.execute('''
    SELECT COUNT(*) FROM post_history 
    WHERE user_id=? AND status='published' AND published_at >= ?
    ''', (user_id, today_start_utc))
    
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


def get_user_usage(user_id: str, tier: str = "free", user_timezone: str = "UTC") -> dict:
    """
    Get comprehensive usage data for a user.
    Returns current usage counts, limits, and reset time (in user's timezone).
    
    Args:
        user_id: The user's ID
        tier: Subscription tier ("free", "pro", "team")
        user_timezone: User's timezone string (e.g., 'America/New_York')
    """
    import datetime
    
    # Get post count with timezone support
    posts_today = get_daily_post_count(user_id, user_timezone)
    scheduled_count = get_scheduled_post_count(user_id)
    
    # Calculate time until reset (next midnight in user's timezone)
    try:
        from zoneinfo import ZoneInfo
        user_tz = ZoneInfo(user_timezone)
    except Exception:
        from zoneinfo import ZoneInfo
        user_tz = ZoneInfo("UTC")
    
    now_local = datetime.datetime.now(user_tz)
    # Next midnight in user's timezone
    tomorrow_midnight = (now_local + datetime.timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    seconds_until_reset = int((tomorrow_midnight - now_local).total_seconds())
    
    # Format reset time as ISO string
    reset_time_iso = tomorrow_midnight.isoformat()
    
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
            "resets_at": reset_time_iso,
            "timezone": user_timezone
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
