"""
JWT-based authentication system (Argon2 password hashing)
"""

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# -------------------------------------------------------------------
# JWT CONFIG
# -------------------------------------------------------------------

SECRET_KEY = "your-secret-key-change-in-production"  # 🔴 move to env in prod
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# -------------------------------------------------------------------
# PASSWORD HASHING (ARGON2 - RECOMMENDED)
# -------------------------------------------------------------------

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

# -------------------------------------------------------------------
# MODELS
# -------------------------------------------------------------------

class TokenData(BaseModel):
    user_id: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str


# -------------------------------------------------------------------
# PASSWORD HELPERS
# -------------------------------------------------------------------

def get_password_hash(password: str) -> str:
    """
    Hash a password using Argon2
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    """
    return pwd_context.verify(plain_password, hashed_password)


# -------------------------------------------------------------------
# JWT HELPERS
# -------------------------------------------------------------------

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token
    """
    to_encode = data.copy()

    expire = datetime.utcnow() + (
        expires_delta
        if expires_delta
        else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """
    Verify JWT token and return user_id (sub)
    """
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        user_id: str | None = payload.get("sub")
        return user_id
    except JWTError:
        return None
