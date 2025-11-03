from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.session import get_db
from schemas.habit import HabitCreate, HabitUpdate, HabitResponse, HabitCompletion
from crud.crud_habit import habit_crud
from api.deps import get_current_active_user
from models.user import User
from typing import List

router = APIRouter()


@router.post("/", response_model=HabitResponse, status_code=status.HTTP_201_CREATED)
def create_habit(
        *,
        db: Session = Depends(get_db),
        habit_in: HabitCreate,
        current_user: User = Depends(get_current_active_user)
):
    """
    Create new habit
    """
    habit = habit_crud.create(db, obj_in=habit_in, owner_id=current_user.id)
    return habit


@router.get("/", response_model=List[HabitResponse])
def read_habits(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve habits for current user
    """
    habits = habit_crud.get_active_by_user(db, user_id=current_user.id)
    return habits


@router.get("/{habit_id}", response_model=HabitResponse)
def read_habit(
        *,
        db: Session = Depends(get_db),
        habit_id: int,
        current_user: User = Depends(get_current_active_user)
):
    """
    Get habit by ID
    """
    habit = habit_crud.get(db, habit_id=habit_id)
    if not habit:
        raise HTTPException(
            status_code=404,
            detail="Habit not found",
        )
    if habit.owner_id != current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Not enough permissions",
        )
    return habit


@router.put("/{habit_id}", response_model=HabitResponse)
def update_habit(
        *,
        db: Session = Depends(get_db),
        habit_id: int,
        habit_in: HabitUpdate,
        current_user: User = Depends(get_current_active_user)
):
    """
    Update a habit
    """
    habit = habit_crud.get(db, habit_id=habit_id)
    if not habit:
        raise HTTPException(
            status_code=404,
            detail="Habit not found",
        )
    if habit.owner_id != current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Not enough permissions",
        )
    habit = habit_crud.update(db, db_obj=habit, obj_in=habit_in)
    return habit


@router.delete("/{habit_id}", response_model=HabitResponse)
def delete_habit(
        *,
        db: Session = Depends(get_db),
        habit_id: int,
        current_user: User = Depends(get_current_active_user)
):
    """
    Delete a habit
    """
    habit = habit_crud.get(db, habit_id=habit_id)
    if not habit:
        raise HTTPException(
            status_code=404,
            detail="Habit not found",
        )
    if habit.owner_id != current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Not enough permissions",
        )
    habit = habit_crud.remove(db, habit_id=habit_id)
    return habit


@router.post("/{habit_id}/complete", response_model=HabitResponse)
def complete_habit(
        *,
        db: Session = Depends(get_db),
        habit_id: int,
        completion: HabitCompletion,
        current_user: User = Depends(get_current_active_user)
):
    """
    Mark habit as completed or not completed
    """
    habit = habit_crud.get(db, habit_id=habit_id)
    if not habit:
        raise HTTPException(
            status_code=404,
            detail="Habit not found",
        )
    if habit.owner_id != current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Not enough permissions",
        )

    habit = habit_crud.mark_completed(db, habit_id=habit_id, completed=completion.completed)
    return habit