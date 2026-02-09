from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get authentication secret from environment
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")

if not BETTER_AUTH_SECRET:
    raise ValueError("BETTER_AUTH_SECRET environment variable is not set")

# Security scheme for Bearer token
security = HTTPBearer()


def verify_jwt_token(token: str) -> dict:
    """
    Verify and decode JWT token using PyJWT

    Args:
        token: JWT token string

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        # Decode and verify the JWT token
        payload = jwt.decode(
            token,
            BETTER_AUTH_SECRET,
            algorithms=["HS256"]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> str:
    """
    Dependency function to extract and verify JWT token from Authorization header

    Args:
        credentials: HTTP Bearer credentials from Authorization header

    Returns:
        user_id extracted from the token

    Raises:
        HTTPException: If token is missing, invalid, or expired
    """
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Missing authentication token"
        )

    token = credentials.credentials
    payload = verify_jwt_token(token)

    # Extract user_id from token payload
    user_id = payload.get("sub") or payload.get("user_id") or payload.get("id")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid token: user_id not found"
        )

    return user_id
