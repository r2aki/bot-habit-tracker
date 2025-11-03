from telebot.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from bot.bot_instance import get_bot
from bot.keyboards import (
    get_main_menu_keyboard,
    get_completion_keyboard,
    get_confirmation_keyboard
)
from services.habit_service import HabitService
from services.notification_service import NotificationService
from core.config import settings
import logging
from typing import Optional

bot = get_bot()
logger = logging.getLogger(__name__)
habit_service = HabitService()
notification_service = NotificationService()

# User states
USER_STATES = {}
STATE_ADDING_HABIT = "adding_habit"
STATE_EDITING_HABIT = "editing_habit"
STATE_EDITING_HABIT_TITLE = "editing_habit_title"
STATE_EDITING_HABIT_DESCRIPTION = "editing_habit_description"


def register_handlers():
    """Register all handlers"""
    bot.register_message_handler(start_command, commands=['start'], pass_bot=True)
    bot.register_message_handler(help_command, commands=['help'], pass_bot=True)
    bot.register_message_handler(cancel_command, commands=['cancel'], pass_bot=True)
    bot.register_message_handler(main_menu_handler, content_types=['text'], pass_bot=True)
    bot.register_callback_query_handler(habit_callback_handler, func=lambda call: True, pass_bot=True)
    bot.register_message_handler(add_habit_handler,
                                 func=lambda message: get_user_state(message.chat.id) == STATE_ADDING_HABIT,
                                 pass_bot=True)
    bot.register_message_handler(edit_habit_title_handler,
                                 func=lambda message: get_user_state(message.chat.id) == STATE_EDITING_HABIT_TITLE,
                                 pass_bot=True)
    bot.register_message_handler(edit_habit_description_handler, func=lambda message: get_user_state(
        message.chat.id) == STATE_EDITING_HABIT_DESCRIPTION, pass_bot=True)


def get_user_state(chat_id: int) -> Optional[str]:
    """Get user state"""
    return USER_STATES.get(chat_id)


def set_user_state(chat_id: int, state: Optional[str]):
    """Set user state"""
    if state is None:
        USER_STATES.pop(chat_id, None)
    else:
        USER_STATES[chat_id] = state


async def start_command(message: Message):
    """Handle /start"""
    user = await habit_service.get_or_create_user(
        telegram_id=str(message.from_user.id),
        username=message.from_user.username,
        full_name=f"{message.from_user.first_name} {message.from_user.last_name}".strip()
    )

    welcome_text = (
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "Я - ваш личный помощник по формированию полезных привычек.\n\n"
        "🎯 Со мной вы сможете:\n"
        "• Добавлять и отслеживать привычки\n"
        "• Получать напоминания о выполнении\n"
        "• Отмечать прогресс и видеть результаты\n\n"
        "Начните с добавления первой привычки!"
    )

    await bot.send_message(
        message.chat.id,
        welcome_text,
        reply_markup=get_main_menu_keyboard()
    )


async def help_command(message: Message):
    """Handle /help"""
    help_text = (
        "ℹ️ Помощь по использованию бота\n\n"
        "Основные команды:\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать это меню помощи\n"
        "/cancel - Отменить текущее действие\n\n"
        "Как работать с привычками:\n"
        "1. Нажмите '➕ Добавить привычку' для создания новой\n"
        "2. Используйте '📋 Мои привычки' для просмотра списка\n"
        "3. '✅ Отметить выполнение' для фиксации прогресса\n"
        "4. Нажмите на привычку для редактирования или удаления\n\n"
        f"Время напоминаний: {settings.NOTIFICATION_TIME}\n"
        f"Дней для формирования привычки: {settings.HABIT_COMPLETION_DAYS}"
    )

    await bot.send_message(
        message.chat.id,
        help_text,
        reply_markup=get_main_menu_keyboard()
    )


async def cancel_command(message: Message):
    """Handle /cancel"""
    set_user_state(message.chat.id, None)

    await bot.send_message(
        message.chat.id,
        "⚠️ Действие отменено. Выберите команду из меню.",
        reply_markup=get_main_menu_keyboard()
    )


async def main_menu_handler(message: Message):
    """Handle main menu buttons"""
    text = message.text.strip()

    if text == "➕ Добавить привычку":
        set_user_state(message.chat.id, STATE_ADDING_HABIT)
        await bot.send_message(
            message.chat.id,
            "📝 Введите название новой привычки:",
            reply_markup=None
        )

    elif text == "📋 Мои привычки":
        await show_user_habits(message)

    elif text == "✅ Отметить выполнение":
        await show_habits_for_completion(message)

    elif text == "⚙️ Настройки":
        await show_settings(message)

    else:
        await bot.send_message(
            message.chat.id,
            "❓ Неизвестная команда. Пожалуйста, используйте кнопки меню.",
            reply_markup=get_main_menu_keyboard()
        )


async def show_user_habits(message: Message):
    """Show user's habits"""
    user = await habit_service.get_or_create_user(
        telegram_id=str(message.from_user.id),
        username=message.from_user.username
    )

    habits = await habit_service.get_user_habits(user.id)

    if not habits:
        await bot.send_message(
            message.chat.id,
            "📭 У вас пока нет привычек. Нажмите '➕ Добавить привычку', чтобы создать первую!",
            reply_markup=get_main_menu_keyboard()
        )
        return

    response = "📋 Ваши активные привычки:\n\n"

    for i, habit in enumerate(habits, 1):
        status = "✅" if habit.completion_count > 0 else "🔄"
        response += (
            f"{i}. {status} {habit.title}\n"
            f"   Прогресс: {habit.completion_count}/{settings.HABIT_COMPLETION_DAYS} дней\n"
        )
        if habit.description:
            response += f"   Описание: {habit.description}\n"
        response += "\n"

    await bot.send_message(
        message.chat.id,
        response,
        reply_markup=get_main_menu_keyboard()
    )


async def show_habits_for_completion(message: Message):
    """Show habits for marking"""
    user = await habit_service.get_or_create_user(
        telegram_id=str(message.from_user.id),
        username=message.from_user.username
    )

    habits = await habit_service.get_user_habits(user.id)

    if not habits:
        await bot.send_message(
            message.chat.id,
            "📭 У вас нет привычек для отметки. Сначала добавьте привычку!",
            reply_markup=get_main_menu_keyboard()
        )
        return

    keyboard = InlineKeyboardMarkup()

    for habit in habits:
        status = "✅" if habit.completion_count > 0 else "🔄"
        keyboard.add(
            InlineKeyboardButton(
                f"{status} {habit.title}",
                callback_data=f"complete_habit:{habit.id}"
            )
        )

    await bot.send_message(
        message.chat.id,
        "✅ Выберите привычку для отметки выполнения:",
        reply_markup=keyboard
    )


async def show_settings(message: Message):
    """Settings menu"""
    settings_text = (
        "⚙️ Настройки\n\n"
        f"⏰ Время напоминаний: {settings.NOTIFICATION_TIME}\n"
        f"🏆 Дней для формирования привычки: {settings.HABIT_COMPLETION_DAYS}\n"
        f"👤 Ваш Telegram ID: {message.from_user.id}\n"
        f"📝 Активных привычек: {await habit_service.get_active_habits_count(str(message.from_user.id))}\n\n"
        "Для изменения настроек обратитесь к администратору."
    )

    await bot.send_message(
        message.chat.id,
        settings_text,
        reply_markup=get_main_menu_keyboard()
    )


async def add_habit_handler(message: Message):
    """Handle adding new habit"""
    habit_title = message.text.strip()

    if len(habit_title) < 3:
        await bot.send_message(
            message.chat.id,
            "❌ Название привычки должно содержать минимум 3 символа. Попробуйте еще раз:",
            reply_markup=None
        )
        return

    user = await habit_service.get_or_create_user(
        telegram_id=str(message.from_user.id),
        username=message.from_user.username
    )

    habit = await habit_service.create_habit(
        user_id=user.id,
        title=habit_title,
        description=""
    )

    set_user_state(message.chat.id, None)

    await bot.send_message(
        message.chat.id,
        f"✅ Отлично! Привычка '{habit_title}' добавлена.\n\n"
        "Теперь вы будете получать ежедневные напоминания о выполнении этой привычки.",
        reply_markup=get_main_menu_keyboard()
    )


async def habit_callback_handler(call: CallbackQuery):
    """Handle callback queries for habits"""
    data = call.data.split(":")
    action = data[0]
    habit_id = int(data[1]) if len(data) > 1 else None

    try:
        if action == "complete_habit":
            await show_completion_options(call, habit_id)

        elif action.startswith("complete_yes"):
            await mark_habit_completed(call, habit_id, True)

        elif action.startswith("complete_no"):
            await mark_habit_completed(call, habit_id, False)

        elif action == "edit_habit":
            await start_editing_habit(call, habit_id)

        elif action == "delete_habit":
            await confirm_deletion(call, habit_id)

        elif action.startswith("confirm_delete"):
            await delete_habit_confirmed(call, habit_id)

        elif action.startswith("cancel_delete"):
            await cancel_deletion(call, habit_id)

    except Exception as e:
        logger.error(f"Error in callback handler: {e}")
        await bot.answer_callback_query(
            call.id,
            "❌ Произошла ошибка при обработке запроса.",
            show_alert=True
        )

    await bot.answer_callback_query(call.id)


async def show_completion_options(call: CallbackQuery, habit_id: int):
    """Show completion options"""
    await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="✅ Как вы выполнили привычку сегодня?",
        reply_markup=get_completion_keyboard(habit_id)
    )


async def mark_habit_completed(call: CallbackQuery, habit_id: int, completed: bool):
    """Mark habit"""
    try:
        user = await habit_service.get_or_create_user(
            telegram_id=str(call.from_user.id),
            username=call.from_user.username
        )

        habit = await habit_service.mark_habit_completed(
            habit_id=habit_id,
            user_id=user.id,
            completed=completed
        )

        status_text = "✅" if completed else "❌"
        status_message = "выполнена" if completed else "не выполнена"

        await bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"{status_text} Привычка '{habit.title}' успешно {status_message}!",
            reply_markup=get_main_menu_keyboard()
        )

    except Exception as e:
        logger.error(f"Error marking habit completed: {e}")
        await bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="❌ Ошибка при отметке выполнения привычки. Попробуйте позже.",
            reply_markup=get_main_menu_keyboard()
        )


async def confirm_deletion(call: CallbackQuery, habit_id: int):
    """Confirm deletion"""
    await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="❓ Вы уверены, что хотите удалить эту привычку? Это действие нельзя отменить.",
        reply_markup=get_confirmation_keyboard("delete", habit_id)
    )


async def delete_habit_confirmed(call: CallbackQuery, habit_id: int):
    """Delete habit after confirmation"""
    try:
        user = await habit_service.get_or_create_user(
            telegram_id=str(call.from_user.id),
            username=call.from_user.username
        )

        await habit_service.delete_habit(habit_id=habit_id, user_id=user.id)

        await bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="✅ Привычка успешно удалена!",
            reply_markup=get_main_menu_keyboard()
        )

    except Exception as e:
        logger.error(f"Error deleting habit: {e}")
        await bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="❌ Ошибка при удалении привычки. Попробуйте позже.",
            reply_markup=get_main_menu_keyboard()
        )


async def cancel_deletion(call: CallbackQuery, habit_id: int):
    """Cancel habit deletion"""
    await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="❌ Удаление отменено.",
        reply_markup=get_main_menu_keyboard()
    )


async def start_editing_habit(call: CallbackQuery, habit_id: int):
    """Start editing habit"""
    set_user_state(call.message.chat.id, STATE_EDITING_HABIT)

    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("✏️ Изменить название", callback_data=f"edit_title:{habit_id}"),
        InlineKeyboardButton("📝 Изменить описание", callback_data=f"edit_description:{habit_id}")
    )
    keyboard.add(InlineKeyboardButton("⬅️ Назад", callback_data=f"back_to_habit:{habit_id}"))

    await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="✏️ Что вы хотите изменить?",
        reply_markup=keyboard
    )