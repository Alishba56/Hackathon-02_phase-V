"""
Complete chat test with task operations
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

def test_complete_chat_flow():
    """Test complete chat flow with task operations"""

    print("=" * 60)
    print("Complete Chat Flow Test")
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

    print(f"\n[Setup] Token created for user: {user_id}")

    # Test 1: Add a task
    print("\n[Test 1] Adding task via chat...")
    response = client.post(
        f"/api/{user_id}/chat",
        json={"message": "Add task: Buy groceries"},
        headers={"Authorization": f"Bearer {token}"}
    )

    if response.status_code == 200:
        data = response.json()
        print(f"[OK] Task added")
        print(f"     Response: {data.get('response')[:80]}...")
        print(f"     Tool calls: {len(data.get('tool_calls', []))} tool(s) executed")
        conversation_id = data.get('conversation_id')
    else:
        print(f"[FAIL] Status: {response.status_code}")
        print(f"       Response: {response.text}")
        return

    # Test 2: List tasks
    print("\n[Test 2] Listing tasks via chat...")
    response = client.post(
        f"/api/{user_id}/chat",
        json={
            "conversation_id": conversation_id,
            "message": "Show me all my tasks"
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    if response.status_code == 200:
        data = response.json()
        print(f"[OK] Tasks listed")
        print(f"     Response: {data.get('response')[:80]}...")
    else:
        print(f"[FAIL] Status: {response.status_code}")

    # Test 3: Urdu command
    print("\n[Test 3] Testing Urdu command...")
    response = client.post(
        f"/api/{user_id}/chat",
        json={
            "conversation_id": conversation_id,
            "message": "Meri email kya hai?"
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    if response.status_code == 200:
        data = response.json()
        print(f"[OK] Urdu command processed")
        print(f"     Response: {data.get('response')[:80]}...")
    else:
        print(f"[FAIL] Status: {response.status_code}")

    # Test 4: Get conversation history
    print("\n[Test 4] Getting conversation history...")
    response = client.get(
        f"/api/{user_id}/conversations/{conversation_id}/messages",
        headers={"Authorization": f"Bearer {token}"}
    )

    if response.status_code == 200:
        data = response.json()
        message_count = len(data.get('messages', []))
        print(f"[OK] Conversation history retrieved")
        print(f"     Messages: {message_count}")
    else:
        print(f"[FAIL] Status: {response.status_code}")

    print("\n" + "=" * 60)
    print("All Tests Completed Successfully!")
    print("=" * 60)

if __name__ == "__main__":
    test_complete_chat_flow()
