from config import TZ_SERVER, TZ_YEKT
from bot_instanse import scheduler, bot
from aiogram.types import Message
from datetime import datetime, timedelta
import pytz
import aiogram


NOTIFY_HOURS = 3


class Notifier:
    def __init__(self):
        pass

    @staticmethod
    async def send_message(message: Message, msg: str):
        try:
            await bot.send_message(chat_id=message.chat.id, text=msg)
        except aiogram.utils.exceptions.BotBlocked:
            print(f"User {message.chat.username} blocked bot")
            return

    @staticmethod
    async def notify_appointment(message: Message, date_appointment: datetime, doctor_name: str):
        ekb_tz = pytz.timezone(TZ_YEKT)
        server_tz = pytz.timezone(TZ_SERVER)
        ekb_time = ekb_tz.localize(date_appointment - timedelta(hours=NOTIFY_HOURS))
        server_time = ekb_time.astimezone(server_tz)

        print(f"server_time: {server_time}")
        time = ekb_time.strftime("%H:%M")
        msg = f'Добрый день! Врач {doctor_name} будет ждать вас сегодня в {time}'
        scheduler.add_job(
            Notifier.send_message,
            trigger="date",
            run_date=server_time,
            kwargs={"message": message, "msg": msg},
        )
