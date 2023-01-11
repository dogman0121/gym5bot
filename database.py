import sqlite3
from user import User
from exceptions import UserNotFoundError

class Database:
    def __init__(self):
        self.connection = sqlite3.connect("database.db")
        self.cursor = self.connection.cursor()

    def add_user(self, user):
        try:
            self.cursor.execute(
                """INSERT INTO students (telegram_id, surname, name, grade, symbol, built, role) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (user.telegram_id, user.surname, user.name, user.grade, user.symbol, user.built, user.role)
            )
        except sqlite3.IntegrityError:
            self.cursor.execute(
                """UPDATE students SET surname = ?, name = ?, grade = ?, symbol = ?, built = ?, role = ? WHERE telegram_id = ?""",
                (user.surname, user.name, user.grade, user.symbol, user.built, user.role, user.telegram_id)
            )

        self.connection.commit()

    def get_user_data(self, telegram_id):
        try:
            data = self.cursor.execute(" SELECT * FROM students WHERE telegram_id = ? ", (telegram_id,)).fetchall()[0]
            return User(*data)
        except IndexError:
            raise UserNotFoundError
