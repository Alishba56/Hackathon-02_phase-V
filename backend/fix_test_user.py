"""
Fix test user password hash
"""
from models import User
from db import get_session
from sqlmodel import select
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def fix_test_user():
    session = next(get_session())

    try:
        # Find test user
        user = session.exec(select(User).where(User.email == 'test@example.com')).first()

        if not user:
            print("Test user not found")
            return

        print(f"Found user: {user.email}")
        print(f"Current password_hash: {user.password_hash}")

        # Update password hash
        new_password = "Test123456"
        user.password_hash = pwd_context.hash(new_password)

        session.add(user)
        session.commit()
        session.refresh(user)

        print(f"\n[OK] Password updated successfully!")
        print(f"Email: {user.email}")
        print(f"Password: {new_password}")
        print(f"New hash: {user.password_hash[:30]}...")

    except Exception as e:
        print(f"[FAIL] Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    fix_test_user()
