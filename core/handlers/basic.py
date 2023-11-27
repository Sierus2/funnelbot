import asyncio
from datetime import datetime, timedelta
import datetime as dt
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from validate_email import validate_email

from core.keyboards.inline import keyboard_channel
from core.keyboards.reply import keyboard_telephone
from core.others.db_connect import Request
from core.others.states import Steps
from core.settings import settings


async def start_check_subscribe(message: Message, bot: Bot, state: FSMContext, request: Request):
    await request.add_data(user_id=message.from_user.id, first_name=message.from_user.first_name)
    user_channel_status = await bot.get_chat_member(chat_id=settings.bots.post_channel, user_id=message.from_user.id)

    if user_channel_status.status == 'left':
        await message.answer(
            f"😢😢 Siz kanalga a'zo bo'lmagansiz. Kanalga a'zo bo'lmaguningizcha ushbu botdan foydalana olmaysiz. Avval a'zo bo'ling, qayta /start qiling ",
            reply_markup=keyboard_channel)
        if not await wait_subs_channel(bot, message.from_user.id, 60):
            await bot.send_message(message.chat.id,
                                   f"❗️ Nahotki a'zo bo'lishni xoxlamasangiz? Balki keyinroq harakat qilib ko'rarsiz. \r\n \r\n ▶️ /start tugmasini bosish orqali")
            await state.clear()
            return

    await message.answer(
        f"😍😊👍 Ajoyib, ulangansiz! Endi kontagingiz ushbu tugma orqali jo'nating ⏬", reply_markup=keyboard_telephone)
    await state.set_state(Steps.get_telephone)


async def get_telephone_fake(message: Message):
    await message.answer("Bu sizning shaxsiy telegram kontagingiz emas! Iltimos o'zingizni raqamingizni jo'nating! ")


async def get_telephone(message: Message, state: FSMContext, request: Request):
    await message.answer("Ajoyib, endi elektron pochtangizni jo'nating....", reply_markup=ReplyKeyboardRemove())
    await request.add_data(message.from_user.id, tel=message.contact.phone_number)
    await state.set_state(Steps.get_email)


async def wait_subs_channel(bot: Bot, user_id: int, seconds: int):
    for second in range(seconds):
        user_channel_status = await bot.get_chat_member(chat_id=settings.bots.post_channel, user_id=user_id)

        if user_channel_status.status == 'member':
            return True
        await asyncio.sleep(1)
    return False


async def get_email(message: Message, state: FSMContext, request: Request):
    if validate_email(message.text):
        await request.add_data(message.from_user.id, email=message.text)
        await message.answer(
            "Siz nega bizning materiallarimizni yuklab olmoqchisiz? To'liq javob berishga harakat qiling")
        await state.set_state(Steps.get_answer)
        await asyncio.sleep(60)

        data = await state.get_data()
        if data.get('answer') is None:
            await message.answer(
                f"{message.from_user.first_name} afsuski sizdan 1 daqiqa davomida hech qanday xabar kelmadi. Endi siz /start buyrug'i orqali barchasini boshidan boshlashingiz talab etiladi.")
            await state.clear()

    else:
        await message.answer("Bu emailga o'xshamayapti. Iltimos boshqattan harakat qilib ko'ring")


async def get_answer(message: Message, state: FSMContext, request: Request, scheduler: AsyncIOScheduler()):
    scheduler = AsyncIOScheduler()
    print(75)
    await state.update_data(answer=message.text)
    if len(message.text) > 20:
        await request.add_data(message.from_user.id, question=message.text)
        msg = await message.answer(
            " Ajoyib, mana bu sizga ajoyib maxfiy ma'lumot! Ushbu ma'lumotni yuklab olish uchun sizga atigi 50 sekund vaqt bor. Keyin manzil o'chiriladi. Vaqt ketdi..")
        await state.set_state(Steps.get_age)
        await asyncio.sleep(5)

        await message.answer(
            "Demak materialni olish uchun bir-ikkita savolmga javob berishingiz talab etiladi. \r\n\r\n Yoshingiz nechada?")

        scheduler.add_job(func=delete_message, trigger='date',
                          run_date=datetime.now() + timedelta(seconds=25),
                          kwargs={'chat_id': msg.chat.id, 'message_id': msg.message_id}, jobstore='default')

    else:
        await message.answer(
            " Men sizdan javob kutyapman. Yoki maxfiy material siz uchun qiziq emasmi? Iltimos boshqattan urinib ko'ring")


async def delete_message(chat_id: int, message_id: int, bot: Bot):
    await bot.delete_message(chat_id, message_id)
