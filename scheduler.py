"""
LinkedIn Post Bot Scheduler - Runs daily for 60 days
Posts automatically at a specified time each day
"""

import schedule
import time
import subprocess
import datetime
import sys

# Configuration
POST_TIME = "09:00"  # Time to post (24-hour format, e.g., "09:00" = 9 AM)
DURATION_DAYS = 60
START_DATE = datetime.datetime.now().date()
END_DATE = START_DATE + datetime.timedelta(days=DURATION_DAYS)

def run_bot():
    """Execute bot.py to generate and post content"""
    print(f"\n{'='*60}")
    print(f"🤖 Running LinkedIn Post Bot at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([sys.executable, 'bot.py'], capture_output=False)
        if result.returncode == 0:
            print(f"✅ Post completed successfully!")
        else:
            print(f"❌ Bot exited with code {result.returncode}")
    except Exception as e:
        print(f"❌ Error running bot: {e}")
    
    print(f"{'='*60}\n")

def is_within_campaign():
    """Check if we're still within the 60-day campaign window"""
    today = datetime.datetime.now().date()
    if today > END_DATE:
        print(f"\n⏰ 60-day campaign ended on {END_DATE}")
        print("To continue posting, update END_DATE in scheduler.py")
        return False
    return True

if __name__ == "__main__":
    print(f"\n🚀 LinkedIn Post Bot Scheduler")
    print(f"📅 Campaign: {START_DATE} to {END_DATE} ({DURATION_DAYS} days)")
    print(f"⏰ Daily post time: {POST_TIME}")
    print(f"\n💡 Make sure TEST_MODE = False in bot.py before starting!\n")
    
    # Schedule the job
    schedule.every().day.at(POST_TIME).do(run_bot)
    
    print(f"✅ Scheduler active. Posts scheduled daily at {POST_TIME}")
    print(f"   Press Ctrl+C to stop\n")
    
    # Keep scheduler running
    try:
        while True:
            if is_within_campaign():
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            else:
                print("\n🛑 Campaign ended. Stopping scheduler.")
                break
    except KeyboardInterrupt:
        print("\n\n🛑 Scheduler stopped by user")
        sys.exit(0)
