# - *- coding: utf- 8 - *-
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from tgbot.data.config import CHANNEL_LINK

# Рассылка
mail_confirm_inl = InlineKeyboardMarkup(
).add(
    InlineKeyboardButton("✅ Отправить", callback_data="confirm_mail:yes"),
    InlineKeyboardButton("❌ Отменить", callback_data="confirm_mail:not")
)

reviews_channel_inl = InlineKeyboardMarkup(
).add(
    InlineKeyboardButton("Наш канал", url=CHANNEL_LINK),
)

reviews_channel_inl2 = InlineKeyboardMarkup(
).add(
    InlineKeyboardButton("Канал с отзывами", url=CHANNEL_LINK),
)

# Кнопки при поиске профиля через админ-меню
profile_open_inl = InlineKeyboardMarkup(
).add(
    InlineKeyboardButton("💰 Пополнить", callback_data="user_refill"),
    InlineKeyboardButton("🎁 Мои покупки", callback_data="user_history")
)

# Отдельная кнопка пополнения
profile_popoln_inl = InlineKeyboardMarkup(
).add(
    InlineKeyboardButton("💰 Пополнить", callback_data="user_refill1"),
)

# Удаление сообщения
close_inl = InlineKeyboardMarkup(
).add(
    InlineKeyboardButton("❌ Закрыть", callback_data="close_this"),
)

######################################## ТОВАРЫ ########################################
# Удаление категорий
category_remove_confirm_inl = InlineKeyboardMarkup(
).add(
    InlineKeyboardButton("❌ Да, удалить все", callback_data="confirm_remove_category:yes"),
    InlineKeyboardButton("✅ Нет, отменить", callback_data="confirm_remove_category:not")
)

# Удаление позиций
position_remove_confirm_inl = InlineKeyboardMarkup(
).add(
    InlineKeyboardButton("❌ Да, удалить все", callback_data="confirm_remove_position:yes"),
    InlineKeyboardButton("✅ Нет, отменить", callback_data="confirm_remove_position:not")
)

# Удаление товаров
item_remove_confirm_inl = InlineKeyboardMarkup(
).add(
    InlineKeyboardButton("❌ Да, удалить все", callback_data="confirm_remove_item:yes"),
    InlineKeyboardButton("✅ Нет, отменить", callback_data="confirm_remove_item:not")
)

worker_menu = InlineKeyboardMarkup(
).add(
    InlineKeyboardButton("Да✅", callback_data="admin_user_balance_add")
)