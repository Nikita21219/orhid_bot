import datetime
from babel.dates import format_datetime

from medods import Medods
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton


def get_main_menu_markup():
    button_appointment = KeyboardButton('Записаться на прием')
    button_info = KeyboardButton('Информация')
    button_schedule = KeyboardButton('График')
    button_contacts = KeyboardButton('Контакты')
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(button_info, button_schedule, button_contacts).add(button_appointment)
    return markup


def get_yes_or_no_markup():
    keyboard = InlineKeyboardMarkup()
    yes_button = InlineKeyboardButton('Да', callback_data='yes')
    no_button = InlineKeyboardButton('Нет', callback_data='no')
    main_menu_button = InlineKeyboardButton('В главное меню ◀️', callback_data='main_menu')
    keyboard.add(yes_button, no_button)
    keyboard.add(main_menu_button)
    return keyboard


def get_schedule_for_4_weeks_markup(user_id):
    # Если есть рабочие дни отпраляю их
    medods = Medods()
    available_days = medods.get_available_days_from_cache(str(user_id))
    if available_days:
        markup = InlineKeyboardMarkup()
        for day in available_days:
            date = datetime.datetime.strptime(day, '%Y-%m-%d')
            date_ru = str(format_datetime(date, 'd MMMM', locale='ru_RU'))
            date_button = InlineKeyboardButton(date_ru, callback_data=day)
            markup.add(date_button)
        main_menu_button = InlineKeyboardButton('В главное меню ◀️', callback_data='main_menu')
        markup.add(main_menu_button)
        return markup
    return None


def get_confirming_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton('✅ПОДТВЕРДИТЬ✅'))
    markup.add(KeyboardButton('В главное меню ◀️'))
    return markup


def get_social_networks_markup():
    markup = InlineKeyboardMarkup()
    vk_button = InlineKeyboardButton('VK 🌐', url='https://vk.com/orchid_74')
    ok_button = InlineKeyboardButton('OK 🌐', url='https://ok.ru/meditsinsi')
    inst_button = InlineKeyboardButton('Instagram 🌐', url='https://www.instagram.com/orhidtrk_74/')
    site_button = InlineKeyboardButton('Наш сайт 🌐', url='https://xn---74-mddfq5bq9bzg.xn--p1ai/')
    markup.add(vk_button, ok_button, inst_button)
    markup.add(site_button)
    main_menu_button = InlineKeyboardButton('В главное меню ◀️', callback_data='main_menu')
    markup.add(main_menu_button)
    return markup


def get_times_markup(user_id, date):
    medods = Medods()
    free_times = medods.get_times(str(user_id), date)
    keyboard = InlineKeyboardMarkup()
    if free_times:
        # Добавляю время в клавиатуру
        for time in free_times:
            time_button = InlineKeyboardButton(time, callback_data=time)
            keyboard.add(time_button)
        main_menu_button = InlineKeyboardButton('В главное меню ◀️', callback_data='main_menu')
        keyboard.add(main_menu_button)
        return keyboard
    return 0


def get_users_markup():
    keyboard = InlineKeyboardMarkup()
    # Добавляю каждого врача в клавиатуру
    medods = Medods()
    users = medods.users_result
    if users:
        for user in users:
            name = f"{user.get('surname')} {user.get('name')[0]}.{user.get('secondName')[0]}."
            specialty = f"{user['specialties'][0]['title']}"
            text_button = f"{name} - {specialty}"
            doctor_button = InlineKeyboardButton(text_button, callback_data=user['id'])
            keyboard.add(doctor_button)
    main_menu_button = InlineKeyboardButton('В главное меню ◀️', callback_data='main_menu')
    keyboard.add(main_menu_button)
    return keyboard


def get_leave_feedback_markup():
    keyboard = InlineKeyboardMarkup()

    buttons_text = ('Да', 'Нет', 'В главное меню ◀️')
    buttons_callback = ('yes_feedback', 'no_feedback', 'main_menu')
    for btn_text, btn_callback in zip(buttons_text, buttons_callback):
        btn = InlineKeyboardButton(btn_text, callback_data=btn_callback)
        keyboard.add(btn)

    return keyboard


leave_feedback_markup = get_leave_feedback_markup()
main_menu_markup = get_main_menu_markup()
social_networks_markup = get_social_networks_markup()
