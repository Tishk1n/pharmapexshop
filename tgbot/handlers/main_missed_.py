# - *- coding: utf- 8 - *-
import sqlite3
from tgbot.data.config import GROUP_ID, PATH_DATABASE

from contextlib import suppress

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.exceptions import MessageCantBeDeleted

from tgbot.data.loader import dp
from tgbot.keyboards.reply_all import menu_frep


# Колбэк с удалением сообщения
@dp.callback_query_handler(text="close_this", state="*")
async def main_missed_callback_close(call: CallbackQuery, state: FSMContext):
    with suppress(MessageCantBeDeleted):
        await call.message.delete()


# Колбэк с обработкой кнопки
@dp.callback_query_handler(text="...", state="*")
async def main_missed_callback_answer(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)


# Обработка всех колбэков которые потеряли стейты после перезапуска скрипта
@dp.callback_query_handler(state="*")
async def main_missed_callback(call: CallbackQuery, state: FSMContext):
    with suppress(MessageCantBeDeleted):
        await call.message.delete()

    await call.message.answer("❌ Данные не были найдены из-за перезапуска скрипта.\n"
                              "♻ Выполните действие заново.",
                              reply_markup=menu_frep(call.from_user.id))


# Обработка всех неизвестных команд
@dp.message_handler()
async def main_missed_message(message: Message, state: FSMContext):
    if '/start' in message.text:
        referer_id = None
        referer_name = None
        if message.text != "/start":
            info = message.text.split()
            if len(info) >= 2 and info[1].split('_')[0].isdigit():
                i = info[1].split('_')
                referer_id = int(i[0])
                referer_name = i[1]
        with sqlite3.connect(PATH_DATABASE) as con:
            con.execute(
                "INSERT OR IGNORE INTO referral_system VALUES(?, ?, ?)", (message.from_user.id, referer_id, referer_name)
            )
        await state.finish()

        await message.answer(f"🔸 Бот готов к использованию.\n🔸 Если не появились вспомогательные кнопки\n▶ Введите /start",reply_markup=menu_frep(message.from_user.id))
        return
        
    await message.answer(f"♦ Неизвестная команда.\n"
                         "▶ Введите /start")
