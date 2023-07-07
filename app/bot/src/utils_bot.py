from medods import Medods
from keyboards import *
import messages


async def ask_name(phone, message, db):
    # Проверяю есть ли клиент в crm
    medods = Medods()
    client = medods.check_client(phone)
    if client:
        client = client[0]
        full_name = f"{client['surname']} {client['name']}"
        if db.update_row(message.from_user.username, 'full_name', full_name):
            return await message.answer(messages.just_error, reply_markup=main_menu_markup)
        if db.update_row(message.from_user.username, 'client_id', client['id']):
            return await message.answer(messages.just_error, reply_markup=main_menu_markup)
        return await message.answer(f'Ваше имя {full_name}?', reply_markup=get_yes_or_no_markup())
    # Запрашиваю ФИО
    else:
        return await message.answer(messages.enter_name, reply_markup=main_menu_markup)
