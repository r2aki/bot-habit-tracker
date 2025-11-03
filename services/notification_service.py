from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from core.config import settings
from bot.bot_instance import get_bot
from services.habit_service import HabitService
import logging

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()
habit_service = HabitService()
bot = get_bot()


class NotificationService:
    def __init__(self):
        self.scheduler = scheduler

    def start(self):
        """Start scheduler"""
        if not self.scheduler.running:
            # Schedule daily notification
            notification_time = settings.NOTIFICATION_TIME.split(":")
            hour = int(notification_time[0])
            minute = int(notification_time[1])

            self.scheduler.add_job(
                self.send_daily_notifications,
                CronTrigger(hour=hour, minute=minute),
                id="daily_notifications",
                replace_existing=True
            )

            # Schedule daily habits processing at midnight
            self.scheduler.add_job(
                self.process_daily_habits,
                CronTrigger(hour=0, minute=0),
                id="daily_habits_processing",
                replace_existing=True
            )

            self.scheduler.start()
            logger.info("Notification scheduler started")

    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Notification scheduler stopped")

    async def send_daily_notifications(self):
        """Send daily notifications to all users"""
        try:
            users = self.db.query(User).all()

            for user in users:
                habits = await habit_service.get_user_habits(user.id)

                if habits:
                    message = self._format_daily_notification(habits)
                    await bot.send_message(user.telegram_id, message)

            logger.info(f"Daily notifications sent to {len(users)} users")

        except Exception as e:
            logger.error(f"Error sending daily notifications: {e}")

    async def process_daily_habits(self):
        """Process daily habits"""
        try:
            await habit_service.process_daily_habits()
            logger.info("Daily habits processing completed")
        except Exception as e:
            logger.error(f"Error processing daily habits: {e}")

    def _format_daily_notification(self, habits: list) -> str:
        """Daily notification message"""
        message = "🌅 Доброе утро! Время для ваших привычек:\n\n"

        for i, habit in enumerate(habits, 1):
            progress = f"{habit.completion_count}/{settings.HABIT_COMPLETION_DAYS}"
            message += f"{i}. {habit.title}\n   📊 Прогресс: {progress}\n"

            if habit.description:
                message += f"   💡 {habit.description}\n"
            message += "\n"

        message += (
            "✅ Отметьте выполнение привычек в боте!\n"
            "💪 Постоянство - ключ к успеху!"
        )

        return message


# Singleton
notification_service = NotificationService()