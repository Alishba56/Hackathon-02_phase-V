"""
Create chat tables in Neon database
"""
from sqlmodel import SQLModel
from db import engine
from models import Conversation, Message

def create_chat_tables():
    """Create conversations and messages tables"""
    print("Creating chat tables in Neon database...")

    try:
        # Create all tables (will only create missing ones)
        SQLModel.metadata.create_all(engine)

        print("[OK] Chat tables created successfully!")
        print("  - conversations table")
        print("  - messages table")

    except Exception as e:
        print(f"[FAIL] Error creating tables: {e}")

if __name__ == "__main__":
    create_chat_tables()
