"""
Migration script to add password_hash column to users table
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("NEON_DB_URL")

def add_password_hash_column():
    """Add password_hash column to users table"""
    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        # Check if column already exists
        result = conn.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='users' AND column_name='password_hash'
        """))

        if result.fetchone():
            print("✓ password_hash column already exists")
            return

        # Add the column
        conn.execute(text("""
            ALTER TABLE users
            ADD COLUMN password_hash VARCHAR NOT NULL DEFAULT ''
        """))
        conn.commit()

        print("✓ Successfully added password_hash column to users table")
        print("⚠ Note: Existing users will have empty password_hash and won't be able to login")
        print("  They will need to be recreated or have their passwords set manually")

if __name__ == "__main__":
    add_password_hash_column()
