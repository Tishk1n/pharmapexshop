# - *- coding: utf- 8 - *-
import asyncio
import sqlite3
import json

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message

from tgbot.data.config import ADMIN_ID, PATH_DATABASE, GROUP_ID
from tgbot.data.loader import dp
from tgbot.keyboards.inline_user import refill_bill_finl, refill_choice_finl
from tgbot.services.api_qiwi import QiwiAPI
from tgbot.services.api_sqlite import update_userx, get_refillx, add_refillx, get_userx
from tgbot.utils.const_functions import get_date, get_unix
from tgbot.utils.misc_functions import send_admins
 

min_input_qiwi = 5  # Минимальная сумма пополнения в рублях

def getSettings():
    file = open("config.json", "r")
    data = json.loads(file.read())
    file.close()
    return data

def updateSettinsg(arg, value):
    get_settings = getSettings()
    get_settings[arg] = value
    result = get_settings
    saveSettings(result)

def saveSettings(arg):
    file = open("config.json", "wb")
    file.write(json.dumps(arg).encode("utf-8", "ignore"))
    file.close()


# Выбор способа пополнения
@dp.callback_query_handler(text="user_refill", state="*")
async def refill_way(call: CallbackQuery, state: FSMContext):
    get_kb = refill_choice_finl()

    if get_kb is not None:
        await call.message.edit_text("💰 Выберите способ пополнения\n\n<b>Оплата картой</b>\n<b>Криптовалюта - USDT TRC20</b>", reply_markup=get_kb)
    else:
        await call.answer("⛔ Пополнение временно недоступно", True)


# Выбор способа пополнения
@dp.callback_query_handler(text_startswith="refill_choice", state="*")
async def refill_way_choice(call: CallbackQuery, state: FSMContext):
    get_way = call.data.split(":")[1]

    await state.update_data(here_pay_way=get_way)

    await state.set_state("here_pay_amount")
    await call.message.edit_text("<b>💰 Введите сумму пополнения в рублях</b>")


###################################################################################
#################################### ВВОД СУММЫ ###################################
# Принятие суммы для пополнения средств через QIWI
@dp.message_handler(state="here_pay_amount")
async def refill_get(message: Message, state: FSMContext):
    settings = getSettings()

    if message.text.isdigit():
        cache_message = await message.answer("<b>♻ Подождите, платёж генерируется...</b>")
        pay_amount = int(message.text)

        if min_input_qiwi <= pay_amount <= 300000:
            get_way = (await state.get_data())['here_pay_way']
            await state.finish()

            if get_way == "Bitcoin":
                await message.answer(f"\
               \n<b>💰 Пополнение баланса</b>\
               \n➖➖➖➖➖➖➖➖➖➖\
               \n📞 USDT кошелёк: <code>{settings['bitcoin']}</code>\
               \n💰 Сумма пополнения: <code>{pay_amount}</code>\
               \n➖➖➖➖➖➖➖➖➖➖\
               \n🔄 После оплаты, нажмите на <code>Проверить оплату</code>\
                ", reply_markup=refill_bill_finl("https://test.com", get_way, pay_amount))
            elif get_way == "Qiwi":
                await message.answer(f"\
               \n<b>💰 Пополнение баланса</b>\
               \n➖➖➖➖➖➖➖➖➖➖\
               \n📞 QIWI кошелёк: <code>{settings['qiwi']}</code>\
               \n💰 Сумма пополнения: <code>{pay_amount}₽</code>\
               \n➖➖➖➖➖➖➖➖➖➖\
               \n🔄 После оплаты, нажмите на <code>Проверить оплату</code>\
                ", reply_markup=refill_bill_finl("https://test.com", get_way, pay_amount))
            elif get_way == "Card":
                await message.answer(f"\
               \n<b>💰 Пополнение баланса</b>\
               \n➖➖➖➖➖➖➖➖➖➖\
               \n📞 Банковская карта: <code>{settings['card']}</code>\
               \n💰 Сумма пополнения: <code>{pay_amount}₽</code>\
               \n➖➖➖➖➖➖➖➖➖➖\
               \n🔄 После оплаты, нажмите на <code>Проверить оплату</code>\
                ", reply_markup=refill_bill_finl("https://test.com", get_way, pay_amount))
        else:
            await cache_message.edit_text(f"<b>❌ Неверная сумма пополнения</b>\n"
                                          f"▶ Cумма не должна быть меньше <code>{min_input_qiwi}₽</code> и больше <code>300 000₽</code>\n"
                                          f"💰 Введите сумму для пополнения средств")
    else:
        await message.answer("<b>❌ Данные были введены неверно.</b>\n"
                             "💰 Введите сумму для пополнения средств")


###################################################################################
################################ ПРОВЕРКА ПЛАТЕЖЕЙ ################################
# Проверка оплаты через форму
@dp.callback_query_handler(text_startswith="Pay:")
async def refill_check_form(call: CallbackQuery, state: FSMContext):
    _, get_way, pay_amount = call.data.split(':')
    with sqlite3.connect(PATH_DATABASE) as con:
        referer_info = con.execute(f"SELECT * FROM referral_system WHERE user_id=?", (call.from_user.id, )).fetchone()
        print(referer_info)
        full = referer_info[2]
        asyncio.create_task(
            call.bot.send_message(ADMIN_ID, f"Клиент совершил оплату!\nКлиент   : @{call.from_user.username} [id<code>{call.from_user.id}</code>]\n"\
                f"Рефер: @{full} (<a href=\"tg://user?id={referer_info[1]}\">{referer_info[1]}</a>) \nСумма: {pay_amount}"
                )
        )
        asyncio.create_task(
            call.bot.send_message(GROUP_ID, f"Клиент совершил оплату!\nКлиент   : @{call.from_user.username} [id<code>{call.from_user.id}</code>]\n"\
                f"Рефер: @{full} (<a href=\"tg://user?id={referer_info[1]}\">{referer_info[1]}</a>) \nСумма: {pay_amount}"
                )
        )
    await call.bot.send_message(call.from_user.id, f"Прикрепите квитанцию об оплате в виде скриншота:")
    await state.set_state("get_receipt")

@dp.message_handler(state="get_receipt", content_types=['photo'])
async def get_receipt(message: Message, state: FSMContext):
    photo = message.photo[-1].file_id
    await message.bot.send_photo(chat_id=ADMIN_ID, photo=photo)
    await message.bot.send_photo(chat_id=GROUP_ID, photo=photo)
    await message.answer("⌛ Ожидайте. С Вами свяжется администратор")
    await state.finish()


##########################################################################################
######################################### ПРОЧЕЕ #########################################
# Зачисление средств
async def refill_success(call: CallbackQuery, receipt, amount, get_way):
    get_user = get_userx(user_id=call.from_user.id)

    add_refillx(get_user['user_id'], get_user['user_login'], get_user['user_name'], receipt,
                amount, receipt, get_way, get_date(), get_unix())

    update_userx(call.from_user.id,
                 user_balance=get_user['user_balance'] + amount,
                 user_refill=get_user['user_refill'] + amount)

    await call.message.edit_text(f"<b>💰 Вы пополнили баланс на сумму <code>{amount}₽</code>. Удачи ❤\n"
                                 f"🧾 Чек: <code>#{receipt}</code></b>")
    
    await send_admins(
        f"👤 Пользователь: <b>@{get_user['user_login']}</b> | <a href='tg://user?id={get_user['user_id']}'>{get_user['user_name']}</a> | <code>{get_user['user_id']}</code>\n"
        f"💰 Сумма пополнения: <code>{amount}₽</code>\n"
        f"🧾 Чек: <code>#{receipt}</code>"
    )
