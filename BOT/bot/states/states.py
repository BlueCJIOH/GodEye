from aiogram.dispatcher.filters.state import StatesGroup, State


class EmployeeStatesGroup(StatesGroup):
    img = State()


class MonitorStatesGroup(StatesGroup):
    monitor = State()
