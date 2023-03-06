import asyncio
from medods import Medods


async def update_token_coroutine():
    # in seconds
    wait_for = 5
    while True:
        medods = Medods()
        token = medods.gen_token()
        medods.update_token(token)
        await asyncio.sleep(wait_for)


async def update_users_coroutine():
    # in seconds
    wait_for = 43200
    while True:
        Medods().update_users()
        await asyncio.sleep(wait_for)


async def update_schedule_coroutine():
    # in seconds
    wait_for = 600
    while True:
        medods = Medods()
        medods.update_schedule()
        medods.filter_users_by_schedule()
        await asyncio.sleep(wait_for)
