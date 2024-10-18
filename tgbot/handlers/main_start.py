# - *- coding: utf- 8 - *-
import sqlite3

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.types import ChatMemberMember, ChatMemberAdministrator, ChatMemberOwner

from tgbot.data.config import GROUP_ID, PATH_DATABASE
from tgbot.data.loader import dp
from tgbot.keyboards.inline_user import user_support_finl
from tgbot.keyboards.reply_all import menu_frep, admin_kb
from tgbot.services.api_sqlite import get_settingsx, get_userx
from tgbot.utils.misc.bot_filters import IsBuy, IsRefill, IsWork
from tgbot.keyboards.inline_all import reviews_channel_inl
from tgbot.data.loader import bot

# Игнор-колбэки покупок
prohibit_buy = ['buy_category_open', 'buy_category_swipe', 'buy_position_open', 'buy_position_swipe',
                'buy_item_open', 'buy_item_confirm']

# Игнор-колбэки пополнений
prohibit_refill = ['user_refill', 'refill_choice', 'Pay:', 'Pay:Form', 'Pay:Number', 'Pay:Nickname']


####################################################################################################
######################################## ТЕХНИЧЕСКИЕ РАБОТЫ ########################################
# Фильтр на технические работы - сообщение
@dp.message_handler(IsWork(), state="*")
async def filter_work_message(message: Message, state: FSMContext):
    await state.finish()

    user_support = get_settingsx()['misc_support']
    if str(user_support).isdigit():
        get_user = get_userx(user_id=user_support)

        if len(get_user['user_login']) >= 1:
            await message.answer("<b>⛔ Бот находится на технических работах.</b>",
                                 reply_markup=user_support_finl(get_user['user_login']))
            return

    await message.answer("<b>⛔ Бот находится на технических работах.</b>")


# Фильтр на технические работы - колбэк
@dp.callback_query_handler(IsWork(), state="*")
async def filter_work_callback(call: CallbackQuery, state: FSMContext):
    await state.finish()

    await call.answer("⛔ Бот находится на технических работах.", True)


####################################################################################################
########################################### СТАТУС ПОКУПОК #########################################
# Фильтр на доступность покупок - сообщение
@dp.message_handler(IsBuy(), text="🛒 Купить", state="*")
@dp.message_handler(IsBuy(), state="here_item_count")
async def filter_buy_message(message: Message, state: FSMContext):
    await state.finish()

    await message.answer("<b>⛔ Покупки временно отключены.</b>")


# Фильтр на доступность покупок - колбэк
@dp.callback_query_handler(IsBuy(), text_startswith=prohibit_buy, state="*")
async def filter_buy_callback(call: CallbackQuery, state: FSMContext):
    await state.finish()

    await call.answer("⛔ Покупки временно отключены.", True)


####################################################################################################
######################################### СТАТУС ПОПОЛНЕНИЙ ########################################
# Фильтр на доступность пополнения - сообщение
@dp.message_handler(IsRefill(), state="here_pay_amount")
async def filter_refill_message(message: Message, state: FSMContext):
    await state.finish()

    await message.answer("<b>⛔ Пополнение временно отключено.</b>")


# Фильтр на доступность пополнения - колбэк
@dp.callback_query_handler(IsRefill(), text_startswith=prohibit_refill, state="*")
async def filter_refill_callback(call: CallbackQuery, state: FSMContext):
    await state.finish()

    await call.answer("⛔ Пополнение временно отключено.", True)


####################################################################################################
############################################## ПРОЧЕЕ ##############################################
# Открытие главного меню
@dp.message_handler(text=['⬅ Главное меню', '/start'], state="*")
async def main_start(message: Message, state: FSMContext):
    user_status = await bot.get_chat_member(chat_id='-1001437156916', user_id=message.from_user.id)
    referer_id = None
    referer_name = None
    if isinstance(user_status, ChatMemberMember):
        if "/start" in message.text:
            await message.answer(f"🔸 Бот готов к использованию.\n🔸 Если не появились вспомогательные кнопки\n▶ Введите /start",reply_markup=menu_frep(message.from_user.id))
        if message.text != "/start":
            info = message.text.split()
            if len(info) >= 3 and info[1].isdigit():
                referer_id = int(info[1])
                referer_name = info[2]
        with sqlite3.connect(PATH_DATABASE) as con:
            con.execute(
                "INSERT OR IGNORE INTO referral_system VALUES(?, ?, ?)", (message.from_user.id, referer_id, referer_name)
            )
        await state.finish()

    else:
           await bot.send_message(message.from_user.id, 'Чтобы пользоваться ботом, подпишись на канал', reply_markup=reviews_channel_inl)
        
@dp.message_handler(text='⬅️ Главное меню')
async def back_in_main_menu(message: Message):
    await message.answer(f"🔸 Бот готов к использованию.\n🔸 Если не появились вспомогательные кнопки\n▶ Введите /start",reply_markup=menu_frep(message.from_user.id))

@dp.message_handler(text='/admin')
async def admin_panel(message: Message):
    await message.answer("Админ панель", reply_markup=admin_kb(message.from_user.id))
