from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.models import user
from app.utils.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.authentication.password import hash_password, verify_password
from app.authentication.jwt import create_access_token, create_refresh_token
from app.authentication.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(400, "Username already taken")
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(400, "Email already registered")
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == credentials.username).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    token_data = {"user_id": user.id, "username": user.username, "role": user.role}
    return {
        "access_token": create_access_token(token_data),
        "refresh_token": create_refresh_token(token_data),
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
