import asyncio
import logging

import psycopg_pool
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ContentType
from aiogram.filters import Command
from aiogram.types import BotCommand, BotCommandScopeDefault

from core.middlewares.db_middlewares import DbSession

from core.settings import Bots, Settings, Db, settings
from apscheduler.schedulers.asyncio import AsyncIOScheduler


async def my_command(bot: Bot):
    command = [
        BotCommand(
            command='start',
            description='Бошлаш'
        )
    ]
    await bot.set_my_commands(command, BotCommandScopeDefault())


async def start_bot(bot: Bot):
    await my_command(bot)
    await bot.send_message(chat_id=settings.bots.admin_id, text='Bot is started!')


async def stop_bot(bot: Bot):
    await my_command(bot)
    await bot.send_message(chat_id=settings.bots.admin_id, text='Bot is stoped!')


def create_pool(user, host, password, db):
    return psycopg_pool.AsyncConnectionPool(
        f"host={host} port=5432 dbname={db} user={user} password={password} connect_timeout=10"
    )


async def run_bot():
    logging.basicConfig(
        level=logging.INFO
    )
    bot = Bot(settings.bots.bot_token, parse_mode="HTML")
    dp = Dispatcher()

    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)

    dp.message.middleware(
        DbSession(create_pool(settings.db.user, settings.db.host, settings.db.password, settings.db.db)))
    dp.callback_query.middleware(
        DbSession(create_pool(settings.db.user, settings.db.host, settings.db.password, settings.db.db)))

    # schedular = AsyncIOScheduler(timezone='Asia/Tashkent')
    # schedular.add_job(database_entry, 'cron', hour=11, minute=25, start_date='2023-11-23 09:00:00')
    # schedular.start()

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(run_bot())
    except(KeyboardInterrupt, SystemExit):
        print('Error')
