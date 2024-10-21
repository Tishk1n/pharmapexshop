# - *- coding: utf- 8 - *-
import asyncio
from contextlib import suppress

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.exceptions import MessageCantBeDeleted

from tgbot.data.config import BOT_DESCRIPTION, GROUP_ID
from tgbot.data.loader import dp
from tgbot.keyboards.inline_all import profile_open_inl
from tgbot.keyboards.inline_page import *
from tgbot.keyboards.inline_user import user_support_finl, products_open_finl, products_confirm_finl
from tgbot.keyboards.reply_all import menu_frep, worker_frep
from tgbot.services.api_sqlite import *
from tgbot.utils.const_functions import get_date, split_messages, get_unix, ded
from tgbot.utils.misc_functions import open_profile_user, upload_text, get_faq
from tgbot.keyboards.inline_user import refill_bill_finl, refill_choice_finl
from tgbot.keyboards.inline_all import profile_popoln_inl, reviews_channel_inl2, worker_menu
from tgbot.data.config import WORKER_WORD


@dp.message_handler(text="Получить реферральную ссылку")
async def my_referral_url(message: Message) -> None:
    bot_me = await message.bot.get_me()
    await message.answer(f"<code>https://t.me/{bot_me.username}?start={message.from_user.id}_{message.from_user.username}</code>", parse_mode="HTML")
# Открытие товаров

@dp.message_handler(text="🛒 Заказать", state="*")
async def user_shop(message: Message, state: FSMContext):
    await state.finish()

    if len(get_all_categoriesx()) >= 1:
        await message.answer("<b>🎁 Выберите нужную вам категорию:</b>",
                             reply_markup=products_item_category_swipe_fp(0))
    else:
        await message.answer("<b>🎁 Увы, товары в данное время отсутствуют.</b>")


# Открытие профиля
@dp.message_handler(text="💾 Профиль", state="*")
async def user_profile(message: Message, state: FSMContext):
    await state.finish()

    await message.answer(open_profile_user(message.from_user.id), reply_markup=profile_open_inl)




# Открытие FAQ
@dp.message_handler(text=["ℹ️ Информация и правила", "/faq"], state="*")
async def user_faq(message: Message, state: FSMContext):
    await state.finish()

    send_message = get_settingsx()['misc_faq']
    if send_message == "None":
        send_message = f"ℹ Информация. Измените её в настройках бота.\\n{BOT_DESCRIPTION}"

    await message.answer(get_faq(message.from_user.id, send_message), disable_web_page_preview=True)




################################################################################################
# Просмотр истории покупок
@dp.callback_query_handler(text="user_history", state="*")
async def user_history(call: CallbackQuery, state: FSMContext):
    last_purchases = last_purchasesx(call.from_user.id, 5)

    if len(last_purchases) >= 1:
        await call.answer("🎁 Последние 5 покупок")
        with suppress(MessageCantBeDeleted):
            await call.message.delete()

        for purchases in last_purchases:
            link_items = await upload_text(call, purchases['purchase_item'])

            await call.message.answer(ded(f"""
                                      <b>🧾 Чек: <code>#{purchases['purchase_receipt']}</code></b>
                                      🎁 Товар: <code>{purchases['purchase_position_name']} | {purchases['purchase_count']}шт | {purchases['purchase_price']}₽</code>
                                      🕰 Дата покупки: <code>{purchases['purchase_date']}</code>
                                      🔗 Товары: <a href='{link_items}'>кликабельно</a>
                                      """))

        await call.message.answer(open_profile_user(call.from_user.id), reply_markup=profile_open_inl)
    else:
        await call.answer("❗ У вас отсутствуют покупки", True)


# Возвращение к профилю
@dp.callback_query_handler(text="user_profile", state="*")
async def user_profile_return(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(open_profile_user(call.from_user.id), reply_markup=profile_open_inl)


################################################################################################
######################################### ПОКУПКА ТОВАРА #######################################
# Переключение страниц категорий для покупки
@dp.callback_query_handler(text_startswith="buy_category_swipe:", state="*")
async def user_purchase_category_next_page(call: CallbackQuery, state: FSMContext):
    remover = int(call.data.split(":")[1])

    await call.message.edit_text("<b>🎁 Выберите нужную вам категорию:</b>",
                                 reply_markup=products_item_category_swipe_fp(remover))


# Открытие категории для покупки
@dp.callback_query_handler(text_startswith="buy_category_open:", state="*")
async def user_purchase_category_open(call: CallbackQuery, state: FSMContext):
    category_id = call.data.split(":")[1]
    remover = int(call.data.split(":")[2])

    get_category = get_categoryx(category_id=category_id)
    get_positions = get_positionsx(category_id=category_id)

    if len(get_positions) >= 1:
        with suppress(MessageCantBeDeleted):
            await call.message.delete()

        await call.message.answer(f"<b>🎁 Текущая категория: <code>{get_category['category_name']}</code></b>",
                                  reply_markup=products_item_position_swipe_fp(remover, category_id))
    else:
        if remover == "0":
            await call.message.edit_text("<b>🎁 Увы, товары в данное время отсутствуют.</b>")
            await call.answer("❗ Позиции были изменены или удалены")
        else:
            await call.answer(f"❕ Товары в категории {get_category['category_name']} отсутствуют")


# Открытие позиции для покупки
@dp.callback_query_handler(text_startswith="buy_position_open:", state="*")
async def user_purchase_position_open(call: CallbackQuery, state: FSMContext):
    position_id = call.data.split(":")[1]
    category_id = call.data.split(":")[2]
    remover = int(call.data.split(":")[3])

    get_position = get_positionx(position_id=position_id)
    get_category = get_categoryx(category_id=category_id)
    get_items = get_itemsx(position_id=position_id)

    if get_position['position_description'] == "0":
        text_description = ""
    else:
        text_description = f"\n📜 Описание:\n{get_position['position_description']}"

    send_msg = ded(f"""
               <b>🎁 Покупка товара:</b>
               ➖➖➖➖➖➖➖➖➖➖
               🏷 Название: <code>{get_position['position_name']}</code>
               🗃 Категория: <code>{get_category['category_name']}</code>
               💰 Стоимость: <code>{get_position['position_price']}₽</code>
               📦 Количество: <code>{len(get_items)}шт</code>
               {text_description}
               """)

    if len(get_position['position_photo']) >= 5:
        with suppress(MessageCantBeDeleted):
            await call.message.delete()
        await call.message.answer_photo(get_position['position_photo'],
                                        send_msg, reply_markup=products_open_finl(position_id, category_id, remover))
    else:
        await call.message.edit_text(send_msg,
                                     reply_markup=products_open_finl(position_id, category_id, remover))


# Переключение страницы позиций для покупки
@dp.callback_query_handler(text_startswith="buy_position_swipe:", state="*")
async def user_purchase_position_next_page(call: CallbackQuery, state: FSMContext):
    category_id = call.data.split(":")[1]
    remover = int(call.data.split(":")[2])

    get_category = get_categoryx(category_id=category_id)

    await call.message.edit_text(f"<b>🎁 Текущая категория: <code>{get_category['category_name']}</code></b>",
                                 reply_markup=products_item_position_swipe_fp(remover, category_id))


########################################### ПОКУПКА ##########################################
# Выбор количества товаров для покупки
@dp.callback_query_handler(text_startswith="buy_item_open:", state="*")
async def user_purchase_select(call: CallbackQuery, state: FSMContext):
    position_id = call.data.split(":")[1]
    remover = int(call.data.split(":")[2])

    get_position = get_positionx(position_id=position_id)
    get_items = get_itemsx(position_id=position_id)
    get_user = get_userx(user_id=call.from_user.id)

    if get_position['position_price'] != 0:
        get_count = int(get_user['user_balance'] / get_position['position_price'])
        if get_count > len(get_items): get_count = len(get_items)
    else:
        get_count = len(get_items)

    if int(get_user['user_balance']) >= int(get_position['position_price']):
        if get_count == 1:
            await state.update_data(here_cache_position_id=position_id)
            await state.finish()

            with suppress(MessageCantBeDeleted):
                await call.message.delete()
            await call.message.answer(ded(f"""
                                      <b>🎁 Вы действительно хотите купить товар(ы)?</b>
                                      ➖➖➖➖➖➖➖➖➖➖
                                      🎁 Товар: <code>{get_position['position_name']}</code>
                                      📦 Количество: <code>1шт</code>
                                      💰 Сумма к покупке: <code>{get_position['position_price']}₽</code>"""),
                                      reply_markup=products_confirm_finl(position_id, 1))
        elif get_count >= 1:
            await state.update_data(here_cache_position_id=position_id)
            await state.set_state("here_item_count")

            with suppress(MessageCantBeDeleted):
                await call.message.delete()
            await call.message.answer(ded(f"""
                                      <b>🎁 Введите количество товаров для покупки</b>
                                      ▶ От <code>1</code> до <code>{get_count}</code>
                                      ➖➖➖➖➖➖➖➖➖➖
                                      🎁 Товар: <code>{get_position['position_name']}</code> - <code>{get_position['position_price']}₽</code>
                                      💰 Ваш баланс: <code>{get_user['user_balance']}₽</code>
                                      """))
        else:
            await call.answer("🎁 Товаров нет в наличии")
    else:
        await call.answer("❗ У вас недостаточно средств. Пополните баланс", True)
        await call.message.reply("Пополнить баланс", reply_markup=profile_popoln_inl)

@dp.callback_query_handler(text="user_refill1", state="*")
async def refill_way(call: CallbackQuery, state: FSMContext):
    get_kb = refill_choice_finl()

    if get_kb is not None:
        await call.message.edit_text("💰 Выберите способ пополнения\n<b>Оплата картой</b>", reply_markup=get_kb)
    else:
        await call.answer("⛔ Пополнение временно недоступно", True)


# Принятие количества товаров для покупки
@dp.message_handler(state="here_item_count")
async def user_purchase_select_count(message: Message, state: FSMContext):
    position_id = (await state.get_data())['here_cache_position_id']

    get_position = get_positionx(position_id=position_id)
    get_user = get_userx(user_id=message.from_user.id)
    get_items = get_itemsx(position_id=position_id)

    if get_position['position_price'] != 0:
        get_count = int(get_user['user_balance'] / get_position['position_price'])
        if get_count > len(get_items): get_count = len(get_items)
    else:
        get_count = len(get_items)

    send_message = ded(f"""
                   ➖➖➖➖➖➖➖➖➖➖
                   🎁 Введите количество товаров для покупки
                   ▶ От <code>1</code> до <code>{get_count}</code>
                   ➖➖➖➖➖➖➖➖➖➖
                   🎁 Товар: <code>{get_position['position_name']}</code> - <code>{get_position['position_price']}₽</code>
                   💰 Ваш баланс: <code>{get_user['user_balance']}₽</code>
                   """)

    if message.text.isdigit():
        get_count = int(message.text)
        amount_pay = int(get_position['position_price']) * get_count

        if len(get_items) >= 1:
            if 1 <= get_count <= len(get_items):
                if int(get_user['user_balance']) >= amount_pay:
                    await state.finish()
                    await message.answer(ded(f"""
                                         <b>🎁 Вы действительно хотите купить товар(ы)?</b>
                                         ➖➖➖➖➖➖➖➖➖➖
                                         🎁 Товар: <code>{get_position['position_name']}</code>
                                         📦 Количество: <code>{get_count}шт</code>
                                         💰 Сумма к покупке: <code>{amount_pay}₽</code>
                                         """),
                                         reply_markup=products_confirm_finl(position_id, get_count))
                else:
                    await message.answer(f"<b>❌ Недостаточно средств на счете.</b>\n" + send_message)
            else:
                await message.answer(f"<b>❌ Неверное количество товаров.</b>\n" + send_message)
        else:
            await state.finish()
            await message.answer("<b>🎁 Товар который вы хотели купить, закончился</b>")
    else:
        await message.answer(f"<b>❌ Данные были введены неверно.</b>\n" + send_message)


# Подтверждение покупки товара
@dp.callback_query_handler(text_startswith="buy_item_confirm:", state="*")
async def user_purchase_confirm(call: CallbackQuery, state: FSMContext):
    get_action = call.data.split(":")[1]
    position_id = int(call.data.split(":")[2])
    get_count = int(call.data.split(":")[3])

    if get_action == "yes":
        await call.message.edit_text("<b>🔄 Ждите, товары подготавливаются</b>")
        with sqlite3.connect(PATH_DATABASE) as con:
            referer_info = con.execute(f"SELECT * FROM referral_system WHERE user_id=?", (call.from_user.id, )).fetchone()
            full = referer_info[2]
        get_position = get_positionx(position_id=position_id)
        get_items = get_itemsx(position_id=position_id)
        get_user = get_userx(user_id=call.from_user.id)

        amount_pay = int(get_position['position_price'] * get_count)

        if 1 <= int(get_count) <= len(get_items):
            if int(get_user['user_balance']) >= amount_pay:
                save_items, send_count, split_len = buy_itemx(get_items, get_count)

                if get_count != send_count:
                    amount_pay = int(get_position['position_price'] * send_count)
                    get_count = send_count

                receipt = get_unix()
                buy_time = get_date()

                with suppress(MessageCantBeDeleted):
                    await call.message.delete()
                if split_len == 0:
                    await call.message.answer("\n\n".join(save_items), parse_mode="None")
                else:
                    for item in split_messages(save_items, split_len):
                        await call.message.answer("\n\n".join(item), parse_mode="None")
                        await asyncio.sleep(0.3)

                update_userx(get_user['user_id'], user_balance=get_user['user_balance'] - amount_pay)
                add_purchasex(get_user['user_id'], get_user['user_login'], get_user['user_name'], receipt, get_count,
                              amount_pay, get_position['position_price'], get_position['position_id'],
                              get_position['position_name'], "\n".join(save_items), buy_time, receipt,
                              get_user['user_balance'], int(get_user['user_balance'] - amount_pay))

                await call.message.answer(ded(f"""
                                          <b>✅ Вы успешно купили товар(ы)</b>
                                          ➖➖➖➖➖➖➖➖➖➖
                                          🧾 Чек: <code>#{receipt}</code>
                                          🎁 Товар: <code>{get_position['position_name']} | {get_count}шт | {amount_pay}₽</code>
                                          🕰 Дата покупки: <code>{buy_time}</code>
                                          """),
                                          reply_markup=menu_frep(call.from_user.id)) and await call.bot.send_message(text=f"<b>✅ Клиент успешно купил товар(ы)</b>\n🧑‍💻 Пользователь: @{get_user['user_login']}\n🔗 Рефер: @{full} (<a href=\"tg://user?id={referer_info[1]}\">{referer_info[1]}</a>)\n🧾 Чек: <code>#{receipt}</code>\n🎁 Товар: <code>{get_position['position_name']} | {get_count}шт | {amount_pay}₽</code>\n🕰 Дата покупки: <code>{buy_time}</code>", chat_id=GROUP_ID)
            else:
                await call.message.answer("<b>❗ На вашем счёте недостаточно средств</b>")
        else:
            await call.message.answer("<b>🎁 Товар который вы хотели купить закончился или изменился.</b>",
                                      reply_markup=menu_frep(call.from_user.id))
    else:
        if len(get_all_categoriesx()) >= 1:
            await call.message.edit_text("<b>🎁 Выберите нужную вам категорию:</b>",
                                         reply_markup=products_item_category_swipe_fp(0))
        else:
            await call.message.edit_text("<b>✅ Вы отменили покупку товаров.</b>")


# Кнопка оператор
@dp.message_handler(text= "❔ОПЕРАТОР❔")
async def chat(message: Message):
    await message.reply('<b>Служба поддержки </b>\n\n\n🥷🏻 Оператор нашего магазина:: @\n\n❗️ Для того, чтобы открыть диспут, пишите сразу с полной информацией о заказе.')


# Кнопка отзывы
@dp.message_handler(text= "✅ Отзывы")
async def chat(message: Message):
    await message.reply('<b>Отзывы</b>', reply_markup=reviews_channel_inl2)

@dp.message_handler(text="🖥 Работа")
async def work(message: Message):
    await message.reply("<b>Работа в </b>\n\n\nНаш магазин ведет постоянный набор по всей РФ.\n\n\nОткрыты вакансии на следующие должности:\n\n    1. Кладмен (от 400 руб/клад)\n    2. Трафаретчик (от 80 руб/рисунок)\n    3. Перевозчик (только с залогом)\n    4. Склад (только с залогом)\n\nТак же приглашаем к сотрудничеству химиков и гроверов с качественным товаром. Достойную оплату гарантируем. Найдете магазин в который продадите дороже - мы перебьем цену.\n\n\n\nДля связи писать:  с пометкой 'Работа'")

@dp.message_handler(text=WORKER_WORD)
async def worker_panel(message: Message):
    await message.reply('<b>Панель менеджера</b>', reply_markup=worker_frep(message.from_user.id))

@dp.message_handler(text='🔸 Отзывы')
async def reviews(message: Message):
    await message.reply('Канал с отзывами', reply_markup=reviews_channel_inl2)
