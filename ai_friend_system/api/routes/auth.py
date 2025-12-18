from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional
from datetime import timedelta
from auth.jwt_handler import create_access_token, verify_token, get_password_hash, verify_password, Token
from utils.logger import Logger

router = APIRouter()
logger = Logger("AuthRoute")
security = HTTPBearer()

users_db: dict[str, dict[str, Optional[str]]] = {}

class RegisterRequest(BaseModel):
    username: str
    password: str = Field(min_length=6, max_length=64)
    email: Optional[str] = None
    name: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/register", response_model=Token)
async def register(request: RegisterRequest):
    if request.username in users_db:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = get_password_hash(request.password)
    users_db[request.username] = {
        'password': hashed_password,
        'email': request.email,
        'name': request.name,
        'user_id': request.username
    }

    access_token = create_access_token(
        data={"sub": request.username},
        expires_delta=timedelta(minutes=30)
    )

    logger.info(f"New user registered: {request.username}")
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(request: LoginRequest):
    user = users_db.get(request.username)
    if not user or not verify_password(request.password, user['password']):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(
        data={"sub": request.username},
        expires_delta=timedelta(minutes=30)
    )

    logger.info(f"User logged in: {request.username}")
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    logger.info("User logged out")
    return {"message": "Logged out successfully"}

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    token = credentials.credentials
    user_id = verify_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return users_db.get(user_id)
