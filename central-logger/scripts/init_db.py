"""
Database initialization script
Run this to create tables in your database
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import init_db

if __name__ == "__main__":
    print("Initializing database tables...")
    try:
        init_db()
        print("✅ Database initialized successfully!")
        print("Tables created: workflow_logs")
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        sys.exit(1)
