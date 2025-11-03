from crud.crud_user import user_crud
from crud.crud_habit import habit_crud
from schemas.user import UserCreate
from schemas.habit import HabitCreate, HabitUpdate
from db.session import SessionLocal
from typing import List, Optional
from models.user import User
from models.habit import Habit
import logging

logger = logging.getLogger(__name__)


class HabitService:
    def __init__(self):
        self.db = SessionLocal()

    async def get_or_create_user(
            self,
            telegram_id: str,
            username: Optional[str] = None,
            full_name: Optional[str] = None,
            email: Optional[str] = None
    ) -> User:
        """Get or create user by telegram ID"""
        try:
            user = user_crud.get_by_telegram_id(self.db, telegram_id=telegram_id)

            if not user:
                user_in = UserCreate(
                    telegram_id=telegram_id,
                    username=username or full_name,
                    email=email
                )
                user = user_crud.create(self.db, obj_in=user_in)
                logger.info(f"Created new user with telegram_id: {telegram_id}")

            return user

        except Exception as e:
            logger.error(f"Error getting or creating user: {e}")
            raise

    async def get_user_habits(self, user_id: int) -> List[Habit]:
        """Get active habits for user"""
        try:
            return habit_crud.get_active_by_user(self.db, user_id=user_id)
        except Exception as e:
            logger.error(f"Error getting user habits: {e}")
            raise

    async def create_habit(
            self,
            user_id: int,
            title: str,
            description: str = ""
    ) -> Habit:
        """Create new habit for user"""
        try:
            habit_in = HabitCreate(
                title=title,
                description=description,
                is_active=True
            )
            return habit_crud.create(self.db, obj_in=habit_in, owner_id=user_id)
        except Exception as e:
            logger.error(f"Error creating habit: {e}")
            raise

    async def mark_habit_completed(
            self,
            habit_id: int,
            user_id: int,
            completed: bool
    ) -> Habit:
        """Mark habit"""
        try:
            habit = habit_crud.get(self.db, habit_id=habit_id)
            if not habit:
                raise ValueError("Habit not found")

            if habit.owner_id != user_id:
                raise ValueError("Not enough permissions")

            return habit_crud.mark_completed(self.db, habit_id=habit_id, completed=completed)

        except Exception as e:
            logger.error(f"Error marking habit completed: {e}")
            raise

    async def delete_habit(self, habit_id: int, user_id: int) -> None:
        """Delete habit"""
        try:
            habit = habit_crud.get(self.db, habit_id=habit_id)
            if not habit:
                raise ValueError("Habit not found")

            if habit.owner_id != user_id:
                raise ValueError("Not enough permissions")

            habit_crud.remove(self.db, habit_id=habit_id)

        except Exception as e:
            logger.error(f"Error deleting habit: {e}")
            raise

    async def get_active_habits_count(self, telegram_id: str) -> int:
        """Get count of active habits for user"""
        try:
            user = user_crud.get_by_telegram_id(self.db, telegram_id=telegram_id)
            if not user:
                return 0

            habits = habit_crud.get_active_by_user(self.db, user_id=user.id)
            return len(habits)

        except Exception as e:
            logger.error(f"Error getting active habits count: {e}")
            return 0

    async def process_daily_habits(self) -> None:
        """Process daily habits"""
        try:
            users = self.db.query(User).all()
            completion_days = int(settings.HABIT_COMPLETION_DAYS)

            for user in users:
                habits_to_continue = habit_crud.get_habits_to_continue(
                    self.db, user_id=user.id, completion_days=completion_days
                )

                for habit in habits_to_continue:
                    pass

            logger.info("Daily habits processing completed")

        except Exception as e:
            logger.error(f"Error processing daily habits: {e}")
            raise