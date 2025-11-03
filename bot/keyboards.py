from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Get main menu keyboard"""
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(
        KeyboardButton("➕ Добавить привычку"),
        KeyboardButton("📋 Мои привычки"),
        KeyboardButton("✅ Отметить выполнение"),
        KeyboardButton("⚙️ Настройки")
    )
    return keyboard

def get_habit_actions_keyboard(habit_id: int) -> InlineKeyboardMarkup:
    """Get keyboard for habit actions"""
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("✏️ Редактировать", callback_data=f"edit_habit:{habit_id}"),
        InlineKeyboardButton("🗑️ Удалить", callback_data=f"delete_habit:{habit_id}")
    )
    return keyboard

def get_completion_keyboard(habit_id: int) -> InlineKeyboardMarkup:
    """Get keyboard for marking habit"""
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("✅ Выполнено", callback_data=f"complete_yes:{habit_id}"),
        InlineKeyboardButton("❌ Не выполнено", callback_data=f"complete_no:{habit_id}")
    )
    return keyboard

def get_confirmation_keyboard(action: str, item_id: int) -> InlineKeyboardMarkup:
    """Get confirmation keyboard"""
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("✅ Да", callback_data=f"confirm_{action}:{item_id}"),
        InlineKeyboardButton("❌ Нет", callback_data=f"cancel_{action}:{item_id}")
    )
    return keyboard