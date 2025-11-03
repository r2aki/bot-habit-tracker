from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.session import get_db
from schemas.user import UserCreate, UserResponse, UserWithHabits
from crud.crud_user import user_crud
from api.deps import get_current_active_user
from models.user import User

router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
        *,
        db: Session = Depends(get_db),
        user_in: UserCreate
):
    """
    Create new user
    """
    user = user_crud.get_by_telegram_id(db, telegram_id=user_in.telegram_id)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this telegram ID already exists in the system.",
        )

    if user_in.email:
        existing_email = user_crud.get_by_email(db, email=user_in.email)
        if existing_email:
            raise HTTPException(
                status_code=400,
                detail="The user with this email already exists in the system.",
            )

    user = user_crud.create(db, obj_in=user_in)
    return user


@router.get("/me", response_model=UserWithHabits)
def read_user_me(
        current_user: User = Depends(get_current_active_user)
):
    """
    Get current user
    """
    return current_user


@router.put("/me", response_model=UserResponse)
def update_user_me(
        *,
        db: Session = Depends(get_db),
        user_in: UserUpdate,
        current_user: User = Depends(get_current_active_user)
):
    """
    Update own user
    """
    if user_in.email and user_in.email != current_user.email:
        existing_user = user_crud.get_by_email(db, email=user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="User with this email already exists",
            )

    user = user_crud.update(db, db_obj=current_user, obj_in=user_in)
    return user


@router.get("/{telegram_id}", response_model=UserWithHabits)
def read_user_by_telegram_id(
        telegram_id: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific user by telegram ID
    """
    user = user_crud.get_by_telegram_id(db, telegram_id=telegram_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this telegram ID does not exist in the system",
        )
    return user