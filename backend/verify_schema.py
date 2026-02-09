"""
Verification script to check database schema after migration.
Verifies that all new columns, indexes, and constraints were created.
"""

from sqlalchemy import create_engine, text, inspect
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("NEON_DB_URL")

if not DATABASE_URL:
    raise ValueError("NEON_DB_URL environment variable not set")

engine = create_engine(DATABASE_URL)

def verify_schema():
    """Verify the tasks table schema"""
    print("Verifying database schema...")

    with engine.connect() as conn:
        # Check columns
        print("\n1. Checking columns in tasks table:")
        result = conn.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'tasks'
            ORDER BY ordinal_position;
        """))

        expected_columns = {
            'priority': 'character varying',
            'tags': 'jsonb',
            'due_date': 'timestamp with time zone',
            'remind_at': 'timestamp with time zone',
            'recurrence_rule': 'jsonb',
            'reminded': 'boolean'
        }

        found_columns = {}
        for row in result:
            col_name, data_type, nullable, default = row
            print(f"   - {col_name}: {data_type} (nullable: {nullable}, default: {default})")
            if col_name in expected_columns:
                found_columns[col_name] = data_type

        # Verify expected columns exist
        print("\n2. Verifying new columns:")
        for col, expected_type in expected_columns.items():
            if col in found_columns:
                if expected_type in found_columns[col]:
                    print(f"   [PASS] {col} exists with correct type")
                else:
                    print(f"   [WARN] {col} exists but type mismatch: {found_columns[col]} vs {expected_type}")
            else:
                print(f"   [FAIL] {col} is missing")

        # Check indexes
        print("\n3. Checking indexes:")
        result = conn.execute(text("""
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE tablename = 'tasks'
            AND indexname IN ('idx_tasks_priority', 'idx_tasks_due_date', 'idx_tasks_tags_gin');
        """))

        expected_indexes = ['idx_tasks_priority', 'idx_tasks_due_date', 'idx_tasks_tags_gin']
        found_indexes = []

        for row in result:
            idx_name, idx_def = row
            print(f"   - {idx_name}: {idx_def}")
            found_indexes.append(idx_name)

        print("\n4. Verifying indexes:")
        for idx in expected_indexes:
            if idx in found_indexes:
                print(f"   [PASS] {idx} exists")
            else:
                print(f"   [FAIL] {idx} is missing")

        # Check constraints
        print("\n5. Checking constraints:")
        result = conn.execute(text("""
            SELECT constraint_name, check_clause
            FROM information_schema.check_constraints
            WHERE constraint_name IN ('chk_priority_values', 'chk_recurrence_requires_due_date');
        """))

        expected_constraints = ['chk_priority_values', 'chk_recurrence_requires_due_date']
        found_constraints = []

        for row in result:
            constraint_name, check_clause = row
            print(f"   - {constraint_name}: {check_clause}")
            found_constraints.append(constraint_name)

        print("\n6. Verifying constraints:")
        for constraint in expected_constraints:
            if constraint in found_constraints:
                print(f"   [PASS] {constraint} exists")
            else:
                print(f"   [FAIL] {constraint} is missing")

        # Test data integrity
        print("\n7. Testing data integrity:")
        result = conn.execute(text("""
            SELECT COUNT(*) as total,
                   COUNT(CASE WHEN priority IS NULL THEN 1 END) as null_priority,
                   COUNT(CASE WHEN tags IS NULL THEN 1 END) as null_tags
            FROM tasks;
        """))

        row = result.fetchone()
        total, null_priority, null_tags = row
        print(f"   - Total tasks: {total}")
        print(f"   - Tasks with NULL priority: {null_priority}")
        print(f"   - Tasks with NULL tags: {null_tags}")

        if null_priority == 0 and null_tags == 0:
            print("   [PASS] All existing tasks have default values")
        else:
            print("   [WARN] Some tasks have NULL values")

        print("\nSchema verification complete!")

if __name__ == "__main__":
    verify_schema()
