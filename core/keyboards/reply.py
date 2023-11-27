from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

keyboard_telephone = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(
            text="Контактни улашиш",
            request_contact=True
        )
    ],
], one_time_keyboard=True, resize_keyboard=True)
