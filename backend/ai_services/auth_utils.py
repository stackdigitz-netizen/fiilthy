"""JWT and password utilities for user authentication."""

import os
import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from pydantic import BaseModel

# Configuration
SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days


class TokenPayload(BaseModel):
    """JWT token payload."""
    sub: str  # user_id
    exp: datetime
    iat: datetime
    email: str


class UserBase(BaseModel):
    """Base user model."""
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(UserBase):
    """User creation model."""
    password: str


class UserResponse(UserBase):
    """User response model (no password)."""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str
    user: UserResponse


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    if not password:
        raise ValueError("Password cannot be empty")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token(user_id: str, email: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        'sub': user_id,
        'email': email,
        'exp': expire,
        'iat': datetime.now(timezone.utc),
    }

    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_user_id_from_token(token: str) -> Optional[str]:
    """Extract user_id from token."""
    payload = decode_token(token)
    if payload:
        return payload.get('sub')
    return None
