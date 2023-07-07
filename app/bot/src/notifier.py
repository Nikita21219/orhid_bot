from config import TZ_SERVER, TZ_YEKT
from bot_instanse import scheduler, bot
from aiogram.types import Message
from datetime import datetime, timedelta
import pytz
import aiogram
from keyboards import leave_feedback_markup


NOTIFY_HOURS = 3


class Notifier:
    def __init__(self):
        pass

    @staticmethod
    async def send_message(message: Message, msg: str, markup=None):
        print(f"notified appointment to user {message.chat.username}")
        try:
            await bot.send_message(chat_id=message.chat.id, text=msg, reply_markup=markup)
        except aiogram.utils.exceptions.BotBlocked:
            print(f"User {message.chat.username} blocked bot")
            return

    @staticmethod
    async def notify_appointment(message: Message, date_appointment: datetime, doctor_name: str):
        ekb_tz = pytz.timezone(TZ_YEKT)
        server_tz = pytz.timezone(TZ_SERVER)
        ekb_time = ekb_tz.localize(date_appointment - timedelta(hours=NOTIFY_HOURS))
        server_time = ekb_time.astimezone(server_tz)

        time = ekb_time.strftime("%H:%M")
        msg = f'Добрый день! Врач {doctor_name} будет ждать вас сегодня в {time}'
        scheduler.add_job(
            Notifier.send_message,
            trigger="date",
            run_date=server_time,
            kwargs={"message": message, "msg": msg},
        )

    @staticmethod
    async def notify_leave_feedback(message: Message, date_appointment: datetime):
        ekb_tz = pytz.timezone(TZ_YEKT)
        server_tz = pytz.timezone(TZ_SERVER)
        ekb_time = ekb_tz.localize(date_appointment + timedelta(days=1))
        server_time = ekb_time.astimezone(server_tz)

        msg = f'Добрый день! Вам понравилось песещение нашей клиники?'
        scheduler.add_job(
            Notifier.send_message,
            trigger="date",
            run_date=server_time,
            kwargs={"message": message, "msg": msg, "markup": leave_feedback_markup},
        )
