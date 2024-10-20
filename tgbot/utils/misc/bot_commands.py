# - *- coding: utf- 8 - *-
from aiogram import Dispatcher
from aiogram.types import BotCommand, BotCommandScopeChat, BotCommandScopeDefault

from tgbot.data.config import get_admins

# Команды для юзеров
user_commands = [
    BotCommand("start", "♻ Перезапустить бота"),
]

# Команды для админов
admin_commands = [
    BotCommand("start", "♻ Перезапустить бота"),
    BotCommand("db", "📦 Получить Базу Данных"),
]


# Установка команд
async def set_commands(dp: Dispatcher):
    await dp.bot.set_my_commands(user_commands, scope=BotCommandScopeDefault())

    for admin in get_admins():
        try:
            await dp.bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=admin))
        except:
            pass
