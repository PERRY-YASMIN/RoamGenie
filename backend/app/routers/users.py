from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.db.session import get_db
from app.schemas.auth import (
    UserPreferenceDTO,
    UserProfileResponse,
    UserResponse,
)
from app.services.auth_service import (
    get_current_user,
    get_user_preferences_dto,
    update_user_preferences,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserProfileResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserProfileResponse:
    """Retrieve the profile and preferences of the authenticated user."""
    prefs = get_user_preferences_dto(db, current_user.id)
    return UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        created_at=current_user.created_at,
        preferences=prefs,
    )


@router.get("/me/preferences", response_model=UserPreferenceDTO)
def get_my_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserPreferenceDTO:
    """Retrieve the current user's travel preferences."""
    return get_user_preferences_dto(db, current_user.id)


@router.put("/me/preferences", response_model=UserPreferenceDTO)
def update_my_preferences(
    prefs: UserPreferenceDTO,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserPreferenceDTO:
    """Update or create travel preferences for the authenticated user."""
    return update_user_preferences(db, current_user.id, prefs)
