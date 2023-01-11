import re
from exceptions import UserCreationError
from changes import *
# from aiogram import types

class User:
    def __init__(self, telegram_id, name, surname, grade, symbol, built, role="student"):
        self.telegram_id = telegram_id
        self.name = name
        self.surname = surname
        self.grade = grade
        self.symbol = symbol
        self.built = built
        self.role = role

    @staticmethod
    def get_data_from_text(telegram_id, text):
        try:
            user_data = re.findall(r"(\w+) (\w+) (\d+) *(\w) (\w)", text)[0]
            return User(telegram_id, *user_data)
        except IndexError:
            raise UserCreationError

    def get_user_changes(self, date):
        changes = get_changes(date, self.built)
        try:
            string = ""
            for change in changes[f"{self.grade}{self.symbol}/{self.built}"]:
                string += change["period"] + " "
                string += change["info"] + "\n"
            return string
        except KeyError:
            return "К сожалению для данного дня замен нет"