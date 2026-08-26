from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128, description="Password must be at least 8 characters")
    full_name: str = Field(min_length=2, max_length=120)


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int
    user_id: int
    email: str
    role: str


class TokenPayload(BaseModel):
    sub: str  # user_id as string
    email: str
    role: str
    exp: int
    iat: int


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserPreferenceDTO(BaseModel):
    hotel_preference: Optional[str] = None
    food_preference: Optional[str] = None
    transport_preference: Optional[str] = None
    travel_style: Optional[str] = None
    special_requirements: Optional[str] = None
    activities: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class UserProfileResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    created_at: datetime
    preferences: Optional[UserPreferenceDTO] = None

    model_config = ConfigDict(from_attributes=True)
