from aiogram.dispatcher.filters.state import State, StatesGroup


class Zakaz(StatesGroup):
    why = State()
    what = State()
    nexts = State()
    phone = State()

class Helping(StatesGroup):
    why = State()