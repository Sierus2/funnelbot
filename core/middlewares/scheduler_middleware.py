from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from apscheduler_di import ContextSchedulerDecorator


class SchedulerMiddleware(BaseMiddleware):
    def __init__(self, scheduler: ContextSchedulerDecorator):
        super().__init__()
        self.scheduler = scheduler

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        data['scheduler'] = self.scheduler
        return await handler(event, data)
