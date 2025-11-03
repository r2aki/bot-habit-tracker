from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from schemas.habit import HabitResponse


class UserBase(BaseModel):
    telegram_id: str
    username: Optional[str] = None
    email: Optional[EmailStr] = None


class UserCreate(UserBase):
    password: Optional[str] = None


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class UserInDB(UserResponse):
    hashed_password: Optional[str] = None


class UserWithHabits(UserResponse):
    habits: List[HabitResponse] = []

    class Config:
        orm_mode = True