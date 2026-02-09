"""
Database migration script to add advanced fields to tasks table.

This migration adds:
- priority (VARCHAR with default 'medium')
- tags (JSONB array with default [])
- due_date (TIMESTAMP WITH TIME ZONE, nullable)
- remind_at (TIMESTAMP WITH TIME ZONE, nullable)
- recurrence_rule (JSONB, nullable)
- reminded (BOOLEAN with default FALSE)

Also creates indexes for performance:
- idx_tasks_priority on priority
- idx_tasks_due_date on due_date
- idx_tasks_tags_gin on tags (GIN index for JSONB)
"""

from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("NEON_DB_URL")

if not DATABASE_URL:
    raise ValueError("NEON_DB_URL environment variable not set")

engine = create_engine(DATABASE_URL)

migration_sql = """
-- Handle existing priority column (convert from ENUM to VARCHAR if needed)
DO $$
BEGIN
    -- Check if priority column exists and is an ENUM
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'tasks' AND column_name = 'priority'
    ) THEN
        -- Drop existing enum type constraint if it exists
        ALTER TABLE tasks ALTER COLUMN priority TYPE VARCHAR(20);
    ELSE
        -- Add priority column if it doesn't exist
        ALTER TABLE tasks ADD COLUMN priority VARCHAR(20) NOT NULL DEFAULT 'medium';
    END IF;
END $$;

-- Add other new columns if they don't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'tasks' AND column_name = 'tags') THEN
        ALTER TABLE tasks ADD COLUMN tags JSONB NOT NULL DEFAULT '[]'::jsonb;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'tasks' AND column_name = 'due_date') THEN
        ALTER TABLE tasks ADD COLUMN due_date TIMESTAMP WITH TIME ZONE;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'tasks' AND column_name = 'remind_at') THEN
        ALTER TABLE tasks ADD COLUMN remind_at TIMESTAMP WITH TIME ZONE;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'tasks' AND column_name = 'recurrence_rule') THEN
        ALTER TABLE tasks ADD COLUMN recurrence_rule JSONB;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'tasks' AND column_name = 'reminded') THEN
        ALTER TABLE tasks ADD COLUMN reminded BOOLEAN NOT NULL DEFAULT FALSE;
    END IF;
END $$;

-- Add check constraint for priority values
ALTER TABLE tasks DROP CONSTRAINT IF EXISTS chk_priority_values;
ALTER TABLE tasks ADD CONSTRAINT chk_priority_values
  CHECK (priority IN ('low', 'medium', 'high', 'urgent'));

-- Add check constraint for recurrence validation
ALTER TABLE tasks DROP CONSTRAINT IF EXISTS chk_recurrence_requires_due_date;
ALTER TABLE tasks ADD CONSTRAINT chk_recurrence_requires_due_date
  CHECK (recurrence_rule IS NULL OR due_date IS NOT NULL);

-- Create indexes for performance (IF NOT EXISTS)
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
CREATE INDEX IF NOT EXISTS idx_tasks_tags_gin ON tasks USING GIN(tags);

-- Update existing tasks to have default priority if NULL or empty
UPDATE tasks SET priority = 'medium' WHERE priority IS NULL OR priority = '';
"""

def run_migration():
    """Execute the migration script"""
    print("Starting database migration...")

    try:
        with engine.connect() as conn:
            # Execute migration in a transaction
            with conn.begin():
                conn.execute(text(migration_sql))
            print("Migration completed successfully!")
            print("   - Added/updated priority, tags, due_date, remind_at, recurrence_rule, reminded columns")
            print("   - Created indexes: idx_tasks_priority, idx_tasks_due_date, idx_tasks_tags_gin")
            print("   - Added validation constraints")
    except Exception as e:
        print(f"Migration failed: {e}")
        raise

if __name__ == "__main__":
    run_migration()
