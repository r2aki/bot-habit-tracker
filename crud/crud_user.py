from sqlalchemy.orm import Session
from models.user import User
from schemas.user import UserCreate, UserUpdate
from core.security import get_password_hash, verify_password
from typing import Optional


class CRUDUser:
    def get_by_telegram_id(self, db: Session, telegram_id: str) -> Optional[User]:
        """Get user by telegram ID"""
        return db.query(User).filter(User.telegram_id == telegram_id).first()

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """Create new user"""
        db_obj = User(
            telegram_id=obj_in.telegram_id,
            username=obj_in.username,
            email=obj_in.email,
            is_active=True
        )

        if obj_in.password:
            db_obj.hashed_password = get_password_hash(obj_in.password)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: User, obj_in: UserUpdate) -> User:
        """Update user"""
        update_data = obj_in.dict(exclude_unset=True)

        if "password" in update_data and update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            update_data["hashed_password"] = hashed_password
            del update_data["password"]

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self, db: Session, telegram_id: str) -> Optional[User]:
        """Authenticate user by telegram ID"""
        user = self.get_by_telegram_id(db, telegram_id)
        if not user:
            return None
        return user

    def is_active(self, user: User) -> bool:
        """Check if user is active"""
        return user.is_active


user_crud = CRUDUser()