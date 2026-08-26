from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.session import get_db
from app.schemas.auth import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.services.auth_service import (
    authenticate_user,
    create_access_token,
    register_user,
)

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def register(
    request: UserRegisterRequest, db: Session = Depends(get_db)
) -> UserResponse:
    """Register a new user account."""
    user = register_user(db, request)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
def login(request: UserLoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Authenticate and receive a JWT access token."""
    user = authenticate_user(db, request.email, request.password)
    access_token = create_access_token(user.id, user.email, user.role)
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in_seconds=settings.access_token_expire_minutes * 60,
        user_id=user.id,
        email=user.email,
        role=user.role,
    )
