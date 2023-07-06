from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import *
from database import Database


bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot)
db = Database()
scheduler = AsyncIOScheduler()
