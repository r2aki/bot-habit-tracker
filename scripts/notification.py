import asyncio
import logging
from services.notification_service import notification_service
from bot.bot_instance import start_bot_polling, stop_bot

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main function for notification"""
    logger.info("Starting notification daemon...")

    try:
        # Start bot for sending notifications
        await start_bot_polling()

        # Start scheduler
        notification_service.start()

        while True:
            await asyncio.sleep(3600)

    except KeyboardInterrupt:
        logger.info("Shutting down notification daemon...")
    except Exception as e:
        logger.error(f"Error in notification daemon: {e}")
    finally:
        notification_service.stop()
        await stop_bot()
        logger.info("Notification daemon stopped")


if __name__ == "__main__":
    asyncio.run(main())