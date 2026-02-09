"""
Test script to verify chat authentication flow
"""
import requests
import json
import sys

# Configuration
API_BASE_URL = "http://localhost:8002"

def test_auth_flow():
    """Test the complete authentication and chat flow"""

    print("=" * 60)
    print("Testing Chat Authentication Flow")
    print("=" * 60)

    # Step 1: Test health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("[OK] Backend is running")
        else:
            print(f"[FAIL] Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"[FAIL] Cannot connect to backend: {e}")
        print("Make sure backend is running: uvicorn main:app --reload --host 0.0.0.0 --port 8002")
        return

    # Step 2: Login to get token
    print("\n2. Testing login...")
    login_data = {
        "email": "test@example.com",
        "password": "Test123456"
    }

    try:
        response = requests.post(
            f"{API_BASE_URL}/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            data = response.json()
            token = data.get("token")
            user_id = data.get("user", {}).get("id")
            print("[OK] Login successful")
            print(f"  User ID: {user_id}")
            print(f"  Token: {token[:20]}...")
        else:
            print(f"[FAIL] Login failed: {response.status_code}")
            print(f"  Response: {response.text}")
            print("\nTrying to create test user...")

            # Try signup instead
            signup_data = {
                "name": "Test User",
                "email": "test@example.com",
                "password": "Test123456"
            }
            response = requests.post(
                f"{API_BASE_URL}/api/auth/signup",
                json=signup_data,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 201:
                data = response.json()
                token = data.get("token")
                user_id = data.get("user", {}).get("id")
                print("[OK] Signup successful")
                print(f"  User ID: {user_id}")
                print(f"  Token: {token[:20]}...")
            else:
                print(f"[FAIL] Signup also failed: {response.status_code}")
                print(f"  Response: {response.text}")
                return
    except Exception as e:
        print(f"[FAIL] Auth request failed: {e}")
        return

    # Step 3: Test chat endpoint
    print("\n3. Testing chat endpoint...")
    chat_data = {
        "message": "Hello, can you help me?"
    }

    try:
        response = requests.post(
            f"{API_BASE_URL}/api/{user_id}/chat",
            json=chat_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
        )

        if response.status_code == 200:
            data = response.json()
            print("[OK] Chat request successful")
            print(f"  Conversation ID: {data.get('conversation_id')}")
            print(f"  Response: {data.get('response')[:100]}...")
        else:
            print(f"[FAIL] Chat request failed: {response.status_code}")
            print(f"  Response: {response.text}")

            # Debug: Check what the backend received
            print("\n  Debug Info:")
            print(f"  - URL: {API_BASE_URL}/api/{user_id}/chat")
            print(f"  - Token (first 20 chars): {token[:20]}...")
            print(f"  - User ID: {user_id}")
    except Exception as e:
        print(f"[FAIL] Chat request failed: {e}")
        return

    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_auth_flow()
