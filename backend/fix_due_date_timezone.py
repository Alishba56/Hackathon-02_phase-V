"""
Fix migration to convert due_date column from timestamp without time zone
to timestamp with time zone for proper timezone handling.
"""

from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("NEON_DB_URL")

if not DATABASE_URL:
    raise ValueError("NEON_DB_URL environment variable not set")

engine = create_engine(DATABASE_URL)

fix_sql = """
-- Convert due_date from timestamp without time zone to timestamp with time zone
-- This preserves existing data by treating it as UTC
ALTER TABLE tasks
ALTER COLUMN due_date TYPE TIMESTAMP WITH TIME ZONE
USING due_date AT TIME ZONE 'UTC';
"""

def run_fix():
    """Execute the fix migration"""
    print("Fixing due_date column timezone...")

    try:
        with engine.connect() as conn:
            with conn.begin():
                conn.execute(text(fix_sql))
            print("Fix completed successfully!")
            print("   - Converted due_date to TIMESTAMP WITH TIME ZONE")
            print("   - Existing dates treated as UTC")
    except Exception as e:
        print(f"Fix failed: {e}")
        raise

if __name__ == "__main__":
    run_fix()
