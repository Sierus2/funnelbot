import asyncio
import logging

import asyncpg
import psycopg_pool
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ContentType
from aiogram.filters import Command, CommandStart
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import BotCommand, BotCommandScopeDefault
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler_di import ContextSchedulerDecorator

from core.filters.is_contact_true import IsContactTrue
from core.handlers.basic import *
from core.middlewares.db_middlewares import DbSession
from core.middlewares.scheduler_middleware import SchedulerMiddleware
from core.others.commands_bot import set_commands

from core.settings import Bots, Settings, Db, settings
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logger = logging.getLogger(__name__)


async def start_bot(bot: Bot):
    await set_commands(bot)
    await bot.send_message(chat_id=settings.bots.admin_id, text='Bot is started!')


async def stop_bot(bot: Bot):
    await bot.send_message(chat_id=settings.bots.admin_id, text='Bot is stoped!')


async def create_pool(user, host, password, db):
    return await asyncpg.create_pool(user=user, password=password, database=db, host=host, port=5432,
                                     command_timeout=60)


async def run_bot():
    logging.basicConfig(
        level=logging.INFO
    )
    bot = Bot(settings.bots.bot_token, parse_mode="HTML")
    storage = RedisStorage.from_url(settings.db.redis)

    dp = Dispatcher(storage=storage)

    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)
    pooling = await create_pool(settings.db.user, settings.db.host, settings.db.password, settings.db.db)
    job_stores = {
        'default': RedisJobStore(
            jobs_key='dispatched_trips_job',
            run_times_key='dispatched_trips_running',
            host='localhost',
            db=2,
            port=6379
        )
    }

    scheduler = ContextSchedulerDecorator(AsyncIOScheduler(timezone='Asia/Tashkent', job_stores=job_stores))
    scheduler.ctx.add_instance(bot, declared_class=Bot)
    dp.message.register(get_telephone, Steps.get_telephone, F.content_type == 'contact', IsContactTrue())
    dp.message.register(get_telephone_fake, Steps.get_telephone, F.content_type == 'contact')

    dp.callback_query.middleware(DbSession(pooling))
    dp.message.middleware(DbSession(pooling))
    dp.callback_query.middleware(SchedulerMiddleware(scheduler))
    dp.message.register(get_email, Steps.get_email)
    dp.message.register(get_answer, Steps.get_answer)

    dp.message.register(start_check_subscribe, CommandStart())

    scheduler.start()

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(run_bot())
    except(KeyboardInterrupt, SystemExit):
        print('Error')
