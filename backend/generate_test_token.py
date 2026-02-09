import jwt
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Get the secret from .env
secret = os.getenv("BETTER_AUTH_SECRET")

# Create a test JWT token with a fake user_id
payload = {
    "sub": "test-user-123",  # user_id
    "email": "test@example.com",
    "iat": datetime.utcnow(),
    "exp": datetime.utcnow() + timedelta(hours=24)
}

token = jwt.encode(payload, secret, algorithm="HS256")
print(token)
