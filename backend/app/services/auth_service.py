from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.models.user import ActivityPreference, User, UserPreference
from app.db.session import get_db
from app.schemas.auth import TokenPayload, UserPreferenceDTO, UserRegisterRequest

settings = get_settings()
password_hasher = PasswordHash.recommended()
http_bearer = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    """Hash a plaintext password with Argon2id."""
    return password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against its hash."""
    return password_hasher.verify(plain_password, hashed_password)


def create_access_token(
    user_id: int, email: str, role: str, expires_delta: Optional[timedelta] = None
) -> str:
    """Generate a signed, expiring JWT token."""
    now = datetime.now(timezone.utc)
    expire = now + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "exp": int(expire.timestamp()),
        "iat": int(now.timestamp()),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> TokenPayload:
    """Decode and validate a JWT token payload."""
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.jwt_algorithm]
        )
        return TokenPayload(**payload)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (jwt.InvalidTokenError, Exception):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )


def register_user(db: Session, request: UserRegisterRequest) -> User:
    """Register a new user in the database."""
    # Check for existing email
    stmt = select(User).where(User.email == request.email.lower())
    existing = db.execute(stmt).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email address already exists.",
        )

    user = User(
        email=request.email.lower(),
        password_hash=hash_password(request.password),
        full_name=request.full_name,
        role="traveller",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User:
    """Authenticate a user by email and password."""
    stmt = select(User).where(User.email == email.lower())
    user = db.execute(stmt).scalar_one_or_none()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
    db: Session = Depends(get_db),
) -> User:
    """FastAPI dependency to extract and verify the current authenticated user."""
    if not credentials or not credentials.credentials or not credentials.credentials.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token_payload = decode_access_token(credentials.credentials.strip())
    user_id = int(token_payload.sub)
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with token no longer exists.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """FastAPI dependency to extract the current user if token is present, else None."""
    if not credentials or not credentials.credentials or not credentials.credentials.strip():
        return None
    try:
        token_payload = decode_access_token(credentials.credentials.strip())
        user_id = int(token_payload.sub)
        return db.get(User, user_id)
    except Exception:
        return None


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """FastAPI dependency to verify admin privileges."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required for this action.",
        )
    return current_user


def update_user_preferences(
    db: Session, user_id: int, prefs: UserPreferenceDTO
) -> UserPreferenceDTO:
    """Update or create user preferences and activity tags."""
    # 1. Update UserPreference (1:1)
    user_pref = db.get(UserPreference, user_id)
    if not user_pref:
        user_pref = UserPreference(user_id=user_id)
        db.add(user_pref)

    user_pref.hotel_preference = prefs.hotel_preference
    user_pref.food_preference = prefs.food_preference
    user_pref.transport_preference = prefs.transport_preference
    user_pref.travel_style = prefs.travel_style
    user_pref.special_requirements = prefs.special_requirements

    # 2. Update ActivityPreferences (1:N)
    # Delete existing
    stmt = select(ActivityPreference).where(ActivityPreference.user_id == user_id)
    existing_activities = db.execute(stmt).scalars().all()
    for act in existing_activities:
        db.delete(act)

    # Insert new
    for activity_name in set(prefs.activities):
        if activity_name.strip():
            db.add(ActivityPreference(user_id=user_id, activity=activity_name.strip()))

    db.commit()
    db.refresh(user_pref)

    # Return refreshed DTO
    act_stmt = select(ActivityPreference.activity).where(
        ActivityPreference.user_id == user_id
    )
    activities = list(db.execute(act_stmt).scalars().all())

    return UserPreferenceDTO(
        hotel_preference=user_pref.hotel_preference,
        food_preference=user_pref.food_preference,
        transport_preference=user_pref.transport_preference,
        travel_style=user_pref.travel_style,
        special_requirements=user_pref.special_requirements,
        activities=activities,
    )


def get_user_preferences_dto(db: Session, user_id: int) -> UserPreferenceDTO:
    """Retrieve full user preference DTO including activity tags."""
    user_pref = db.get(UserPreference, user_id)
    act_stmt = select(ActivityPreference.activity).where(
        ActivityPreference.user_id == user_id
    )
    activities = list(db.execute(act_stmt).scalars().all())

    if not user_pref:
        return UserPreferenceDTO(activities=activities)

    return UserPreferenceDTO(
        hotel_preference=user_pref.hotel_preference,
        food_preference=user_pref.food_preference,
        transport_preference=user_pref.transport_preference,
        travel_style=user_pref.travel_style,
        special_requirements=user_pref.special_requirements,
        activities=activities,
    )
