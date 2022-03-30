import sqlite3


class Database:

    def __init__(self):
        self.connection = sqlite3.connect("students.db")
        self.cursor = self.connection.cursor()

    def add_student(self, user_id, data):
        try:
            self.cursor.execute(
                " INSERT INTO students (user_id, name, surname, grade, symbol, built) VALUES (?, ?, ?, ?, ?, ?) ",
                (user_id,) + data)
            self.connection.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def check_user(self, user_id):
        result = self.cursor.execute(" SELECT * FROM students WHERE user_id = ? ", (user_id,)).fetchall()
        if len(result) > 0:
            return True
        else:
            return False

    def get_user_data(self, user_id):
        return self.cursor.execute(" SELECT * FROM students WHERE user_id = ? ", (user_id,)).fetchall()

    def get_users(self):
        self.cursor.execute(" SELECT user_id FROM students ")
        return self.cursor.fetchall()

    def update_user(self, user_id, data):
        self.cursor.execute(
            " UPDATE students SET name= ?, surname = ?, grade = ?, symbol = ?, built = ? WHERE user_id = ? ",
            data + (user_id,))
        self.connection.commit()

    def get_user_from_class(self, settings):
        if settings[0][1] == "":
            self.cursor.execute(" SELECT user_id FROM students WHERE grade = ? AND built = ? ",
                                (settings[0][0], settings[0][2],))
            return self.cursor.fetchall()
        else:
            self.cursor.execute(" SELECT user_id FROM students WHERE grade = ? AND symbol = ? AND built = ? ",
                                settings[0])
            return self.cursor.fetchall()

    def get_class_from_user(self, user):
        self.cursor.execute(" SELECT grade, symbol, built FROM students WHERE user_id = ? ", (user,))
        return self.cursor.fetchall()

    def get_user_from_built(self, built):
        self.cursor.execute(" SELECT user_id FROM students WHERE built = ?", (built,))
        return self.cursor.fetchall()

    def user_data_by_params(self, grade=None, symbol=None, built=None):
        example = " SELECT user_id, name, surname, grade, symbol FROM students WHERE"
        tp = ()
        if not (grade is None):
            if len(tp) == 0:
                example += " grade = ?"
            else:
                example += " AND grade = ?"
            tp += (grade,)
        if not (symbol is None):
            if len(tp) == 0:
                example += " symbol = ?"
            else:
                example += " AND symbol = ?"
            tp += (symbol,)
        if not (built is None):
            if len(tp) == 0:
                example += " built = ?"
            else:
                example += " AND built = ?"
            tp += (built,)
        self.cursor.execute(example, tp)
        return self.cursor.fetchall()
