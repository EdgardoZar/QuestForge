# Agent Task: Authentication System

## Task ID: CHUNK-1.4
## Priority: CRITICAL
## Estimated Time: 3-4 hours
## Dependencies: CHUNK-1.3 (Database Models)

---

## Objective

Implement JWT-based authentication with registration, login, token refresh, and protected route dependencies.

---

## Deliverables

### 1. Security Module

Create `backend/app/core/security.py`:

```python
from datetime import datetime, timedelta
from typing import Optional, Any
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(
    subject: str | Any,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT access token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    subject: str | Any,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT refresh token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
```

### 2. Auth Schemas

Create `backend/app/schemas/auth.py`:

```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID


class UserRegister(BaseModel):
    """Schema for user registration."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema for token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Schema for token refresh request."""
    refresh_token: str


class UserResponse(BaseModel):
    """Schema for user response."""
    id: UUID
    username: str
    email: str
    is_active: bool
    is_verified: bool
    timezone: str
    has_character: bool = False

    class Config:
        from_attributes = True


class TokenPayload(BaseModel):
    """Schema for decoded token payload."""
    sub: str
    exp: int
    type: str
```

### 3. Auth Service

Create `backend/app/services/auth_service.py`:

```python
from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import User, Character
from app.schemas.auth import UserRegister, UserResponse
from app.core.security import get_password_hash, verify_password


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_user(self, user_data: UserRegister) -> User:
        """Create a new user."""
        user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=get_password_hash(user_data.password),
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user by email and password."""
        user = await self.get_user_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    async def user_has_character(self, user_id: UUID) -> bool:
        """Check if user has a character."""
        result = await self.db.execute(
            select(Character).where(Character.user_id == user_id)
        )
        return result.scalar_one_or_none() is not None

    async def get_user_response(self, user: User) -> UserResponse:
        """Convert user to response schema."""
        has_character = await self.user_has_character(user.id)
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            is_active=user.is_active,
            is_verified=user.is_verified,
            timezone=user.timezone,
            has_character=has_character,
        )
```

### 4. Auth Dependencies

Update `backend/app/api/deps.py`:

```python
from typing import Annotated, AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.db.session import async_session_maker
from app.db.models import User
from app.core.security import decode_token
from app.services.auth_service import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


DBSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    db: DBSession,
    token: str = Depends(oauth2_scheme)
) -> User:
    """Get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    if payload.get("type") != "access":
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise credentials_exception

    auth_service = AuthService(db)
    user = await auth_service.get_user_by_id(user_uuid)

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    return user


async def get_current_user_optional(
    db: DBSession,
    token: Optional[str] = Depends(oauth2_scheme)
) -> Optional[User]:
    """Get current user if authenticated, None otherwise."""
    if not token:
        return None
    try:
        return await get_current_user(db, token)
    except HTTPException:
        return None


CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalUser = Annotated[Optional[User], Depends(get_current_user_optional)]
```

### 5. Auth Router

Create `backend/app/api/v1/auth.py`:

```python
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import DBSession, CurrentUser
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    Token,
    TokenRefresh,
    UserResponse,
)
from app.services.auth_service import AuthService
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: DBSession):
    """Register a new user."""
    auth_service = AuthService(db)

    # Check if email exists
    if await auth_service.get_user_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if username exists
    if await auth_service.get_user_by_username(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    user = await auth_service.create_user(user_data)
    return await auth_service.get_user_response(user)


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: DBSession = Depends()):
    """Login and get access token."""
    auth_service = AuthService(db)
    user = await auth_service.authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()

    return Token(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.post("/login/json", response_model=Token)
async def login_json(user_data: UserLogin, db: DBSession):
    """Login with JSON body and get access token."""
    auth_service = AuthService(db)
    user = await auth_service.authenticate_user(user_data.email, user_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()

    return Token(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(token_data: TokenRefresh, db: DBSession):
    """Refresh access token using refresh token."""
    payload = decode_token(token_data.refresh_token)

    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user_id = payload.get("sub")
    auth_service = AuthService(db)
    user = await auth_service.get_user_by_id(user_id)

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return Token(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: CurrentUser, db: DBSession):
    """Get current authenticated user info."""
    auth_service = AuthService(db)
    return await auth_service.get_user_response(current_user)
```

### 6. Update Main App

Update `backend/app/main.py` to include auth router:

```python
# Add import
from app.api.v1.auth import router as auth_router

# Add after CORS middleware
app.include_router(auth_router, prefix="/api/v1")
```

---

## Success Criteria

- [ ] User registration creates new user with hashed password
- [ ] Login returns valid JWT tokens
- [ ] Access token works for protected endpoints
- [ ] Refresh token generates new access token
- [ ] Invalid credentials return 401 error
- [ ] Duplicate email/username returns 400 error
- [ ] `/api/v1/auth/me` returns user info when authenticated

---

## Test Instructions

1. Register user:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "password123"}'
```

2. Login:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/json \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

3. Get current user:
```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"
```

4. Refresh token:
```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<refresh_token>"}'
```
