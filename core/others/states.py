from aiogram.fsm.state import StatesGroup, State


class Steps(StatesGroup):
    get_telephone = State()
    get_email = State()
    get_answer = State()
    get_age = State()
    q1 = State()
    q2 = State()
    buy_product = State()
    review = State()
