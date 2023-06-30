import asyncio
from medods import Medods


async def update_token_coroutine():
    print(f"Start updating token....")
    medods = Medods()
    token = medods.gen_token()
    medods.update_token(token)
    print(f'Token updated successfully')


# async def update_token_coroutine():
#     # in seconds
#     wait_for = 60
#     while True:
#         medods = Medods()
#         token = medods.gen_token()
#         medods.update_token(token)
#         await asyncio.sleep(wait_for)


async def update_users_coroutine():
    print(f"Start updating users....")
    Medods().update_users()
    print(f'Users updated successfully')


# async def update_users_coroutine():
#     # in seconds
#     wait_for = 21600
#     while True:
#         Medods().update_users()
#         await asyncio.sleep(wait_for)


async def update_schedule_coroutine():
    print(f"Start update schedule....")
    medods = Medods()
    medods.update_schedule()
    medods.filter_users_by_schedule()
    print(f'Schedule updated successfully')


# async def update_schedule_coroutine():
#     # in seconds
#     wait_for = 600
#     while True:
#         medods = Medods()
#         medods.update_schedule()
#         medods.filter_users_by_schedule()
#         await asyncio.sleep(wait_for)
