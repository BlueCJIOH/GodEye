from aiogram.dispatcher.filters.state import StatesGroup, State


class EmployeeStatesGroup(StatesGroup):
    img = State()
    delete = State()
    list = State()
