from sqlalchemy.orm import Session
from models.habit import Habit
from schemas.habit import HabitCreate, HabitUpdate
from typing import List, Optional
from sqlalchemy import and_


class CRUDHabit:
    def get(self, db: Session, habit_id: int) -> Optional[Habit]:
        """Get habit by ID"""
        return db.query(Habit).filter(Habit.id == habit_id).first()

    def get_by_user(self, db: Session, user_id: int) -> List[Habit]:
        """Get habits by user ID"""
        return db.query(Habit).filter(Habit.owner_id == user_id).all()

    def get_active_by_user(self, db: Session, user_id: int) -> List[Habit]:
        """Get active habits by user ID"""
        return db.query(Habit).filter(
            and_(
                Habit.owner_id == user_id,
                Habit.is_active == True
            )
        ).all()

    def create(self, db: Session, *, obj_in: HabitCreate, owner_id: int) -> Habit:
        """Create new habit"""
        db_obj = Habit(
            title=obj_in.title,
            description=obj_in.description,
            is_active=obj_in.is_active,
            owner_id=owner_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
            self, db: Session, *, db_obj: Habit, obj_in: HabitUpdate
    ) -> Habit:
        """Update habit"""
        update_data = obj_in.dict(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, habit_id: int) -> Habit:
        """Remove habit"""
        obj = db.query(Habit).get(habit_id)
        db.delete(obj)
        db.commit()
        return obj

    def mark_completed(self, db: Session, *, habit_id: int, completed: bool) -> Habit:
        """Mark habit as completed or not completed"""
        habit = self.get(db, habit_id)
        if not habit:
            return None

        if completed:
            habit.completion_count += 1
            habit.last_completed = func.now()
        else:
            pass

        db.commit()
        db.refresh(habit)
        return habit

    def get_habits_to_continue(self, db: Session, user_id: int, completion_days: int = 21) -> List[Habit]:
        """Get habits that need to continue"""
        return db.query(Habit).filter(
            and_(
                Habit.owner_id == user_id,
                Habit.is_active == True,
                Habit.completion_count < completion_days
            )
        ).all()


habit_crud = CRUDHabit()