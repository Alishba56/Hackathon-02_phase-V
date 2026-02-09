from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import datetime, timedelta
import uuid
import jwt
import os
from dotenv import load_dotenv
from passlib.context import CryptContext

from db import get_session
from models import User
from pydantic import BaseModel, EmailStr
from auth import get_current_user

load_dotenv()
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(prefix="/api/auth", tags=["authentication"])


class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    token: str
    user: dict


@router.post("/signup", response_model=AuthResponse, status_code=201)
async def signup(
    signup_data: SignupRequest,
    session: Session = Depends(get_session)
):
    """
    Register a new user with secure password hashing.

    - **email**: User's email address (must be unique)
    - **password**: User's password (will be hashed with bcrypt)
    - **name**: User's display name (optional)

    Returns JWT token valid for 7 days and user data (without password).
    """
    # Check if user already exists
    existing_user = session.exec(
        select(User).where(User.email == signup_data.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    # Hash the password
    password_hash = pwd_context.hash(signup_data.password)

    # Create new user
    user = User(
        id=str(uuid.uuid4()),
        email=signup_data.email,
        name=signup_data.name,
        password_hash=password_hash,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    # Generate JWT token with 7-day expiration
    expiration = datetime.utcnow() + timedelta(days=7)
    token_payload = {
        "sub": user.id,
        "email": user.email,
        "exp": expiration
    }
    token = jwt.encode(token_payload, BETTER_AUTH_SECRET, algorithm="HS256")

    return {
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name
        }
    }


@router.post("/login", response_model=AuthResponse)
async def login(
    login_data: LoginRequest,
    session: Session = Depends(get_session)
):
    """
    Login existing user with password verification.

    - **email**: User's email address
    - **password**: User's password

    Returns JWT token valid for 7 days and user data (without password).
    Raises 401 if credentials are invalid.
    """
    # Find user by email
    user = session.exec(
        select(User).where(User.email == login_data.email)
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Verify password hash
    if not pwd_context.verify(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Generate JWT token with 7-day expiration
    expiration = datetime.utcnow() + timedelta(days=7)
    token_payload = {
        "sub": user.id,
        "email": user.email,
        "exp": expiration
    }
    token = jwt.encode(token_payload, BETTER_AUTH_SECRET, algorithm="HS256")

    return {
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name
        }
    }


@router.get("/me")
async def get_current_user_info(
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user)
):
    """
    Get current user information from JWT token.

    Requires valid JWT token in Authorization header.
    Returns user data (without password).
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "email": user.email,
        "name": user.name
    }
