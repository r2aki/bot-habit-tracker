from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class HabitBase(BaseModel):
    title: str
    description: Optional[str] = None
    is_active: bool = True


class HabitCreate(HabitBase):
    pass


class HabitUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    completion_count: Optional[int] = None


class HabitResponse(HabitBase):
    id: int
    completion_count: int
    last_completed: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    owner_id: int

    class Config:
        orm_mode = True


class HabitCompletion(BaseModel):
    completed: bool