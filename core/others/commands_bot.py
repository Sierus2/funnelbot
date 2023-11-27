from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot):
    command = [
        BotCommand(
            command='start',
            description='Ишни бошлаш'
        ),
        BotCommand(
            command='help',
            description='Ёрдам ҳизмати'
        ),
        BotCommand(
            command='cancel',
            description='Тозалаш'
        ),
    ]

    await bot.set_my_commands(command, BotCommandScopeDefault())
