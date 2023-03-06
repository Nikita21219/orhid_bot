import datetime

import messages
from keyboards import *


class Callback:
    def __init__(self, username, call, db, bot):
        self._user_data = call.data
        self._username = username
        self._db = db
        self._bot = bot
        self._call = call

    async def handle_choice_doctor(self):
        markup = get_schedule_for_4_weeks_markup(int(self._user_data))
        if markup:
            if self._db.update_row(self._username, 'doctor_id', self._user_data):
                return self.send_error('Произошла ошибка при выборе врача')
            if self._db.update_row(self._username, 'state', 'choice date'):
                return self.send_error('Произошла ошибка при выборе врача')
            await self._bot.send_message(self._call.from_user.id, 'Выберите дату', reply_markup=markup)
        else:
            await self._bot.send_message(
                self._call.from_user.id,
                messages.not_allowed_doctor,
                reply_markup=get_main_menu_markup()
            )

    async def handle_choice_date(self):
        result_set = self._db.get_column(self._username, 'doctor_id')
        if len(result_set) == 0:
            return self.send_error(messages.just_error)

        doctor_id = result_set[0][0]
        keyboard_times = get_times_markup(doctor_id, self._user_data)
        if keyboard_times:
            if self._db.update_row(self._username, 'date', self._user_data):
                return self.send_error('Произошла ошибка при выборе даты')
            await self._bot.send_message(self._call.from_user.id, 'Выберите время', reply_markup=keyboard_times)
            if self._db.update_row(self._username, 'state', 'choice time'):
                return self.send_error('Произошла ошибка, при выборе даты')
        else:
            await self._bot.send_message(
                self._call.from_user.id,
                messages.not_allowed_time,
                reply_markup=get_main_menu_markup()
            )

    async def handle_choice_time(self):
        if self._db.update_row(self._username, 'time', self._user_data):
            return self.send_error('Произошла ошибка при выборе времени')
        phone_markup = ReplyKeyboardMarkup(resize_keyboard=True)
        phone_markup.add(KeyboardButton('☎️Отправить свой номер телефона☎️', request_contact=True))
        phone_markup.add(KeyboardButton('В главное меню ◀️'))
        await self._bot.send_message(self._call.from_user.id, messages.need_phone, reply_markup=phone_markup)
        if self._db.update_row(self._username, 'state', 'send phone'):
            return self.send_error('Произошла ошибка, при отправке телефона')

    async def handle_enter_name(self):
        if self._user_data == 'yes':
            expression = f"SELECT doctor_id, date, time, client_id, phone_number FROM Users WHERE tg_user_id=%s;"
            db_result = self._db.read_exec(expression, (self._username, ))
            if db_result == 1:
                return await self._bot.send_message(
                    self._call.from_user.id,
                    messages.just_error,
                    reply_markup=get_main_menu_markup()
                )
            doctor_id, date, chosen_time, client_id, phone = db_result[0]
            if self._db.update_row(self._username, 'state', 'finish'):
                return self.send_error(messages.just_error)
            medods = Medods()
            doctor = medods.get_user_full_name(doctor_id)
            if not doctor:
                return await self._bot.send_message(
                    self._call.from_user.id,
                    'Что-то пошло не так, попробуйте снова',
                    reply_markup=get_confirming_markup()
                )
            message = f'Выбранный врач: {doctor}\n'
            message += f'Выбранная дата: {utils.get_date_ru(date)}\n'
            message += f'Выбранное время: {chosen_time}\n'
            await self._bot.send_message(self._call.from_user.id, message, reply_markup=get_confirming_markup())
            message = '‼️Если информация правильная, нажмите кнопку ПОДТВЕРДИТЬ‼️'
            await self._bot.send_message(self._call.from_user.id, message, reply_markup=get_confirming_markup())
        elif self._user_data == 'no':
            await self._bot.send_message(self._call.from_user.id, messages.enter_name, reply_markup=get_main_menu_markup())

    async def send_error(self, message):
        await self._bot.send_message(self._call.from_user.id, message, reply_markup=get_main_menu_markup())
