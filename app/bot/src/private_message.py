import messages
from keyboards import *
import utils
import utils_bot

from config import *

class PrivateMessage:
    def __init__(self, message, db, bot):
        self._message = message
        self._chat_id = message.chat.id
        self._username = message.from_user.username
        self._db = db
        self._bot = bot

    async def handle_phone_number(self):
        phone = utils.phone_to_crm_format(self._message.text)
        if self._db.update_row(self._username, 'phone_number', phone):
            return await self.send_error('Произошла ошибка, при отправке телефона')
        if self._db.update_row(self._username, 'state', 'enter name'):
            return await self.send_error(messages.just_error)
        await utils_bot.ask_name(phone, self._message, self._db)

    async def handle_enter_name(self):
        phone = self._db.get_column(self._username, 'phone_number')[0][0]
        full_name = self._message.text
        medods = Medods()
        client_id = medods.create_client(phone, full_name)
        if not client_id:
            return await self.send_error('Произошла ошибка при создании клиента')
        if self._db.update_row(self._username, 'client_id', client_id):
            return await self.send_error(messages.just_error)
        if self._db.update_row(self._username, 'full_name', full_name):
            return await self.send_error(messages.just_error)
        await self._bot.send_message(
            self._chat_id,
            f'Информация правильная?\nВаше ФИО: {self._message.text}\nВаш телефон: {phone}',
            reply_markup=get_yes_or_no_markup()
        )

    async def handle_confirm(self):
        result_set = self._db.get_column(self._username, 'state')
        if result_set == 1:
            return await self._bot.send_message(self._chat_id, messages.just_error)
        if result_set[0][0] == 'finish':
            expr = f"SELECT doctor_id, date, time, phone_number, full_name FROM Users WHERE tg_user_id=%s;"
            doctor_id, date, chosen_time, phone, full_name = self._db.read_exec(expr, (self._username,))[0]
            if self._db.update_row(self._username, 'state', 'finish'):
                return await self._bot.send_message(self._chat_id, messages.just_error)

            client_id = self._db.get_column(self._username, 'client_id')[0][0]
            if self.make_appointment(doctor_id, date, chosen_time, client_id):
                medods = Medods()
                doctor = medods.get_user_full_name(doctor_id)
                if not doctor:
                    print(f"Not doctor. name = {doctor}")
                    return await self._bot.send_message(self._chat_id, 'Что-то пошло не так, попробуйте снова')
                date_ru = utils.get_date_ru(date)
                message = f'Вы успешно записались на прием к врачу {doctor}'
                message += f' на {date_ru} в {chosen_time}.\n'
                message += 'В ближайшее время с вами свяжется администратор'
                await self._bot.send_message(self._chat_id, message)

                message = f'Пользователь @{self._message.from_user.username} записался на прием к врачу'
                message += f' {doctor} на {date_ru} в {chosen_time}'
                await self._bot.send_message(OWNER_CHAT_ID, message)
            else:
                return await self._bot.send_message(self._chat_id, 'Что-то пошло не так, попробуйте снова')
        else:
            return await self._bot.send_message(self._chat_id, 'Что-то пошло не так, попробуйте снова')

    async def handle_lite_message(self):
        if self._message.text == 'В главное меню ◀️':
            await self._message.answer('Вы вернулись в главное меню', reply_markup=get_main_menu_markup())
        elif self._message.text == 'Информация':
            await self._message.answer(messages.centr_info, reply_markup=get_social_networks_markup())
        elif self._message.text == 'График':
            await self._message.answer(messages.schedule, reply_markup=get_main_menu_markup())
        elif self._message.text == 'Контакты':
            await self._message.answer(messages.contacts, reply_markup=get_main_menu_markup())
        elif self._message.text == 'Записаться на прием':
            if self._db.add_user(self._message.chat.username):
                return await self._message.answer(
                    'Произошла ошибка добавления пользователя в базу данных',
                    reply_markup=get_main_menu_markup()
                )
            await self._message.answer('Загружаю актуальных врачей, подождите немного')
            await self._message.answer('Выберите врача', reply_markup=get_users_markup())
        else:
            await self._message.answer('Test', reply_markup=get_main_menu_markup())

    async def send_error(self, message):
        await self._bot.send_message(self._chat_id, message)

    def is_allow_to_make_appointment(self, doctor_id, date, time):
        medods = Medods()
        appointment = medods.get_appointments(doctor_id, date)
        return False if not appointment or appointment['time'] == time else True

    def make_appointment(self, user_id, chosen_date, chosen_time, client_id):
        if not self.is_allow_to_make_appointment(user_id, chosen_date, chosen_time):
            print('Not allow to make appointment')
            return 0

        # Конвертирую продолжительность приема врача в int и записываю в переменную mm
        hh, mm, ss = map(int, str(Medods().get_appointment_duration(user_id)).split(':'))

        data = {
            'duration': mm,
            'chosen_date': chosen_date,
            'chosen_time': chosen_time,
            'user_id': user_id,
            'client_id': client_id,
        }
        medods = Medods()
        return medods.make_appointment(data)
