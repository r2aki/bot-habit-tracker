from telebot.async_telebot import AsyncTeleBot
from core.config import settings
import asyncio
from typing import Optional

bot = AsyncTeleBot(settings.TELEGRAM_BOT_TOKEN)
_bot_task: Optional[asyncio.Task] = None


async def start_bot_polling():
    """Start the bot polling"""
    global _bot_task
    from bot.handlers import register_handlers

    # Register handlers
    register_handlers()

    # Start polling
    _bot_task = asyncio.create_task(bot.polling(non_stop=True))
    print("Bot polling started")


async def stop_bot():
    """Stop the bot polling"""
    global _bot_task
    if _bot_task:
        bot.stop_polling()
        await _bot_task
        _bot_task = None
        print("Bot polling stopped")


def get_bot() -> AsyncTeleBot:
    """Get bot instance"""
    return bot