from aiogram.dispatcher.filters.state import State, StatesGroup


class RegistrationUser(StatesGroup):
    waiting_to_register = State()

class SearchingBook(StatesGroup):
    waiting_to_search = State()