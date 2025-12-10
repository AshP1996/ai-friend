# """
# Authentication routes with JWT
# """

# from fastapi import APIRouter, HTTPException, Depends
# from starlette.requests import HTTPAuthorizationCredentials 
# from fastapi.security import HTTPBearer, HTTPAuthCredentials
# from pydantic import BaseModel
# from typing import Optional
# from auth.jwt_handler import (
#     create_access_token, verify_token, 
#     get_password_hash, verify_password, Token
# )
# from datetime import timedelta
# from utils.logger import Logger

# router = APIRouter()
# logger = Logger("AuthRoute")
# security = HTTPBearer()

# # Simple in-memory user store (replace with database in production)
# users_db = {}

# class RegisterRequest(BaseModel):
#     username: str
#     password: str
#     email: Optional[str] = None
#     name: Optional[str] = None

# class LoginRequest(BaseModel):
#     username: str
#     password: str

# @router.post("/register", response_model=Token)
# async def register(request: RegisterRequest):
#     if request.username in users_db:
#         raise HTTPException(status_code=400, detail="Username already exists")
    
#     hashed_password = get_password_hash(request.password)
#     users_db[request.username] = {
#         'password': hashed_password,
#         'email': request.email,
#         'name': request.name,
#         'user_id': request.username
#     }
    
#     access_token = create_access_token(
#         data={"sub": request.username},
#         expires_delta=timedelta(minutes=30)
#     )
    
#     logger.info(f"New user registered: {request.username}")
#     return {"access_token": access_token, "token_type": "bearer"}

# @router.post("/login", response_model=Token)
# async def login(request: LoginRequest):
#     user = users_db.get(request.username)
#     if not user or not verify_password(request.password, user['password']):
#         raise HTTPException(status_code=401, detail="Invalid credentials")
    
#     access_token = create_access_token(
#         data={"sub": request.username},
#         expires_delta=timedelta(minutes=30)
#     )
    
#     logger.info(f"User logged in: {request.username}")
#     return {"access_token": access_token, "token_type": "bearer"}

# @router.post("/logout")
# async def logout(credentials: HTTPAuthCredentials = Depends(security)):
#     # In production, add token to blacklist
#     return {"message": "Logged out successfully"}

# async def get_current_user(credentials: HTTPAuthCredentials = Depends(security)) -> str:
#     token = credentials.credentials
#     user_id = verify_token(token)
#     if user_id is None:
#         raise HTTPException(status_code=401, detail="Invalid token")
#     return user_id

# api/routes/auth.py
"""
Authentication routes with JWT (login, register, protected endpoints)
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from datetime import timedelta

from auth.jwt_handler import (
    create_access_token,
    verify_token,
    get_password_hash,
    verify_password,
    Token  # Your Token model from jwt_handler.py
)
from utils.logger import Logger

router = APIRouter()
logger = Logger("AuthRoute")
security = HTTPBearer()

# In-memory user store (for demo / testing — replace with real DB in production)
users_db: dict[str, dict] = {}

class RegisterRequest(BaseModel):
    username: str
    password: str
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
    # In production, you may add the token to a blacklist or change its status
    logger.info("User logged out")
    return {"message": "Logged out successfully"}

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    token = credentials.credentials
    user_id = verify_token(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user_id
