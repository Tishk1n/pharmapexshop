# - *- coding: utf- 8 - *-
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.services.api_sqlite import get_paymentx


# Выбор способов пополнения
def refill_choice_finl():
    keyboard = InlineKeyboardMarkup()

    get_payments = get_paymentx()
    active_kb = []

    if get_payments['way_form'] == "True":
        active_kb.append(InlineKeyboardButton("📋 QIWI форма", callback_data="refill_choice:Form"))
    if get_payments['way_number'] == "True":
        active_kb.append(InlineKeyboardButton("📞 QIWI номер", callback_data="refill_choice:Number"))
    if get_payments['way_nickname'] == "True":
        active_kb.append(InlineKeyboardButton("Ⓜ QIWI", callback_data="refill_choice:Qiwi"))
        
    active_kb.append(InlineKeyboardButton("💰 USDT TRC20", callback_data="refill_choice:Bitcoin"))
    active_kb.append(InlineKeyboardButton("💳 Оплата картой", callback_data="refill_choice:Card"))

    if len(active_kb) == 3:
        keyboard.add(active_kb[0], active_kb[1])
        keyboard.add(active_kb[2])
    elif len(active_kb) == 2:
        keyboard.add(active_kb[0], active_kb[1])
    elif len(active_kb) == 1:
        keyboard.add(active_kb[0])
    else:
        keyboard = None

    if len(active_kb) >= 1:
        keyboard.add(InlineKeyboardButton("⬅ Вернуться ↩", callback_data="user_profile"))

    return keyboard


# Проверка киви платежа
def refill_bill_finl(send_requests, get_way, amount):
    keyboard = InlineKeyboardMarkup(
    ).add(
        InlineKeyboardButton("🔄 Проверить оплату", callback_data=f"Pay:{get_way}:{amount}")
    )

    return keyboard


# Кнопки при открытии самого товара
def products_open_finl(position_id, category_id, remover):
    keyboard = InlineKeyboardMarkup(
    ).add(
        InlineKeyboardButton("💰 Купить товар", callback_data=f"buy_item_open:{position_id}:{remover}")
    ).add(
        InlineKeyboardButton("⬅ Вернуться ↩", callback_data=f"buy_category_open:{category_id}:{remover}")
    )

    return keyboard


# Подтверждение покупки товара
def products_confirm_finl(position_id, get_count):
    keyboard = InlineKeyboardMarkup(
    ).add(
        InlineKeyboardButton("✅ Подтвердить", callback_data=f"buy_item_confirm:yes:{position_id}:{get_count}"),
        InlineKeyboardButton("❌ Отменить", callback_data=f"buy_item_confirm:not:{position_id}:{get_count}")
    )

    return keyboard


# Ссылка на поддержку
def user_support_finl(user_name):
    keyboard = InlineKeyboardMarkup(
    ).add(
        InlineKeyboardButton("💌 Написать в поддержку", url=f"https://t.me/{user_name}"),
    )

    return keyboard
