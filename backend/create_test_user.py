from sqlmodel import Session, create_engine
from models import User
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL
DATABASE_URL = os.getenv("NEON_DB_URL")

# Create engine
engine = create_engine(DATABASE_URL)

# Create test user
with Session(engine) as session:
    # Check if user already exists
    existing_user = session.get(User, "test-user-123")

    if existing_user:
        print("Test user already exists")
    else:
        # Create new test user
        test_user = User(
            id="test-user-123",
            email="test@example.com",
            name="Test User",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(test_user)
        session.commit()
        print("Test user created successfully!")
        print(f"User ID: {test_user.id}")
        print(f"Email: {test_user.email}")
        print(f"Name: {test_user.name}")
