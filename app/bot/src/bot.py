import messages
import utils_bot
from masks import *
from keyboards import *
from callback import Callback
from private_message import PrivateMessage
from aiogram import types
from update_cache import *
from redis_storage import RedisStorage
from bot_instanse import *
import utils


if not db.connected:
    print('Database not connected')
    exit(1)
if not RedisStorage().connected():
    print('Redis not connected')
    exit(1)


async def main():
    await update_token_coroutine()
    await asyncio.sleep(10)
    await update_users_coroutine()
    await update_schedule_coroutine()

    scheduler.start()
    await bot.delete_webhook(drop_pending_updates=True)
    scheduler.add_job(update_token_coroutine, 'interval', minutes=1)
    await asyncio.sleep(20)
    scheduler.add_job(update_users_coroutine, 'interval', hours=6)
    scheduler.add_job(update_schedule_coroutine, 'interval', minutes=5)
    await dp.start_polling(bot)


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    if not message['from']['username']:
        await message.answer(f"Привет!" + messages.username_info)
    else:
        name = message['from']['first_name']
        await message.answer(f'Привет, {name}!' + messages.start_message, reply_markup=main_menu_markup)


@dp.message_handler(commands=['menu'])
async def cmd_menu(message: types.Message):
    await message.answer('Вы вернулись в главное меню', reply_markup=main_menu_markup)


@dp.message_handler(content_types=['text'])
async def message_handler(message: types.Message):
    username = message.from_user.username
    if not username:
        await message.answer(messages.username_info, reply_markup=main_menu_markup)
        return
    if message.chat.type == 'private':
        private_message = PrivateMessage(message, db, bot, scheduler)
        lite_messages = (
            'В главное меню ◀️',
            'Информация',
            'График',
            'Контакты',
            'Записаться на прием'
        )

        result_set = db.get_state(username)
        if result_set == 1:
            return await message.answer(messages.just_error, reply_markup=main_menu_markup)

        if message.text in lite_messages:
            await private_message.handle_lite_message()
        elif is_phone_number(message.text) and result_set[0][0] == 'send phone':
            await private_message.handle_phone_number()
        elif is_full_name(message.text) and result_set[0][0] == 'enter name':
            await private_message.handle_enter_name()
        elif message.text == '✅ПОДТВЕРДИТЬ✅':
            await private_message.handle_confirm()
        elif result_set[0][0] == 'feedback':
            await private_message.handle_feedback()
        else:
            await message.answer('Я вас не понимаю', reply_markup=main_menu_markup)


@dp.callback_query_handler(lambda c: c.data)
async def query_handler(call: types.CallbackQuery):
    if call.data == 'main_menu':
        await bot.send_message(call.from_user.id, messages.return_menu, reply_markup=main_menu_markup)
        return

    result = db.get_state(call.from_user.username)
    if result == 1 or not result or len(result[0]) == 0:
        return await bot.send_message(call.from_user.id, messages.just_error, reply_markup=main_menu_markup)

    username = call.from_user.username
    if not username:
        return await bot.send_message(call.from_user.id, messages.username_info, reply_markup=main_menu_markup)

    callback = Callback(username, call, db, bot)
    state = db.get_state(username)[0][0]

    if call.data in ('yes_feedback', 'no_feedback'):
        return await callback.handle_feedback()
    elif state == 'choice doctor' and call.data.isdigit():
        return await callback.handle_choice_doctor()
    elif state == 'choice date' and is_date(call.data):
        return await callback.handle_choice_date()
    elif state == 'choice time' and is_time(call.data):
        return await callback.handle_choice_time()
    elif state == 'enter name':
        return await callback.handle_enter_name()


@dp.message_handler(content_types=types.ContentType.CONTACT)
async def read_contact_phone(message: types.Message):
    username = message.from_user.username
    if not username:
        return await message.answer(messages.username_info, reply_markup=main_menu_markup)
    result = db.get_state(username)
    if result == 1 or result[0][0] != 'send phone':
        return await message.answer(messages.just_error, reply_markup=main_menu_markup)
    phone = utils.phone_to_crm_format(message.contact.phone_number)
    if db.update_row(username, 'phone_number', phone):
        return await message.answer(
            'Произошла ошибка, при отправке телефона',
            reply_markup=main_menu_markup
        )
    if db.update_row(username, 'state', 'check data'):
        return await message.answer('Произошла ошибка, при проверке данных', reply_markup=main_menu_markup)
    if db.update_row(username, 'state', 'enter name'):
        return await message.answer(messages.just_error, reply_markup=main_menu_markup)
    await utils_bot.ask_name(phone, message, db)


if __name__ == '__main__':
    asyncio.run(main())
