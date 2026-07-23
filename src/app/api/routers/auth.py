from datetime import timedelta
import requests
import secrets
from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from jose import jwt

from app.core import security
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, User as UserSchema, GoogleToken
from app.schemas.token import Token, TokenPayload
from app.api import deps

router = APIRouter()

@router.post("/register", response_model=UserSchema)
async def register(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: UserCreate,
) -> User:
    result = await db.execute(select(User).filter(User.email == user_in.email))
    user = result.scalars().first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user_data = user_in.model_dump(exclude={"password"})
    hashed_password = security.get_password_hash(user_in.password)
    db_user = User(**user_data, password_hash=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.post("/login", response_model=Token)
async def login(
    db: AsyncSession = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Token:
    result = await db.execute(select(User).filter(User.email == form_data.username))
    user = result.scalars().first()
    if not user or not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        refresh_token=security.create_refresh_token(user.id),
        token_type="bearer",
    )

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str = Body(..., embed=True), db: AsyncSession = Depends(get_db)
) -> Token:
    try:
        payload = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        if token_data.type != "refresh":
            raise HTTPException(status_code=400, detail="Invalid token type")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )

    result = await db.execute(select(User).filter(User.id == int(token_data.sub)))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        refresh_token=security.create_refresh_token(user.id),
        token_type="bearer",
    )

@router.post("/google", response_model=Token)
async def google_login(
    token_in: GoogleToken,
    db: AsyncSession = Depends(get_db)
) -> Token:
    try:
        response = requests.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={token_in.id_token}", timeout=5)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Invalid Google token")
        
        token_info = response.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to verify Google token: {str(e)}")
        
    email = token_info.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email not provided by Google")
    
    name = token_info.get("name")
    
    result = await db.execute(select(User).filter(User.email == email))
    user = result.scalars().first()
    
    if not user:
        random_password = secrets.token_urlsafe(16)
        hashed_password = security.get_password_hash(random_password)
        user_data = {"email": email, "name": name, "is_verified": True, "role": "user"}
        db_user = User(**user_data, password_hash=hashed_password)
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        user = db_user

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        refresh_token=security.create_refresh_token(user.id),
        token_type="bearer",
    )
