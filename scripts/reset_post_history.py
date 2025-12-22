"""
Database Reset Script
Clears post_history table for a fresh start during development.
Run this to reset stats to 0.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'post_history.db')

def reset_post_history():
    """Clear all post history - for development only."""
    if not os.path.exists(DB_PATH):
        print(f"Database not found: {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Count existing entries
    cur.execute("SELECT COUNT(*) FROM post_history")
    count = cur.fetchone()[0]
    print(f"Found {count} posts in database")
    
    if count > 0:
        # Delete all entries
        cur.execute("DELETE FROM post_history")
        conn.commit()
        print(f"✅ Deleted {count} posts. Stats are now reset to 0!")
    else:
        print("No posts to delete.")
    
    conn.close()

if __name__ == "__main__":
    print("⚠️  Resetting post history...")
    reset_post_history()
