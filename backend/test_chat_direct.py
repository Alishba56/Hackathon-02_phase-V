"""
Direct test of chat endpoint with detailed error logging
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

# Create test client
client = TestClient(app)

def test_chat_endpoint():
    """Test chat endpoint with proper authentication"""

    print("=" * 60)
    print("Direct Chat Endpoint Test")
    print("=" * 60)

    # Create a valid JWT token for test user
    user_id = "test-user-123"
    expiration = datetime.utcnow() + timedelta(days=7)
    token_payload = {
        "sub": user_id,
        "email": "test@example.com",
        "exp": expiration
    }
    token = jwt.encode(token_payload, BETTER_AUTH_SECRET, algorithm="HS256")

    print(f"\n1. Generated token for user: {user_id}")
    print(f"   Token: {token[:30]}...")

    # Test chat endpoint
    print("\n2. Sending chat request...")

    chat_data = {
        "message": "Hello, can you help me?"
    }

    try:
        response = client.post(
            f"/api/{user_id}/chat",
            json=chat_data,
            headers={
                "Authorization": f"Bearer {token}"
            }
        )

        print(f"\n3. Response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("[OK] Chat request successful!")
            print(f"   Conversation ID: {data.get('conversation_id')}")
            print(f"   Response: {data.get('response')[:100]}...")
        else:
            print(f"[FAIL] Chat request failed")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")

    except Exception as e:
        print(f"[FAIL] Exception occurred: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_chat_endpoint()
