"""
Test task list formatting with new instructions
"""
import sys
sys.path.insert(0, '.')

from fastapi.testclient import TestClient
from main import app
from datetime import datetime, timedelta
import jwt
import os
from dotenv import load_dotenv

load_dotenv()
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")

client = TestClient(app)

def test_task_list_format():
    """Test that task list shows only ID, Title, Status"""

    print("=" * 60)
    print("Testing Task List Format")
    print("=" * 60)

    # Create token
    user_id = "test-user-123"
    expiration = datetime.now() + timedelta(days=7)
    token_payload = {
        "sub": user_id,
        "email": "test@example.com",
        "exp": expiration
    }
    token = jwt.encode(token_payload, BETTER_AUTH_SECRET, algorithm="HS256")

    print(f"\n[Test] Asking AI to list tasks...")

    response = client.post(
        f"/api/{user_id}/chat",
        json={"message": "Show all my tasks"},
        headers={"Authorization": f"Bearer {token}"}
    )

    if response.status_code == 200:
        data = response.json()
        print(f"\n[Response]")
        print(data.get('response'))
        print("\n[Expected Format]")
        print("ID: abc12345 | Task Title | Completed/Pending")
        print("\n[Check]: Should NOT show timestamps or created_at/updated_at")
    else:
        print(f"[FAIL] Status: {response.status_code}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_task_list_format()
