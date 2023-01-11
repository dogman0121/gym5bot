import re


def user_data_from_text(text):
    user_data = re.findall(r"(\w+) (\w+) (\d+) *(\w) (\w)", text)
    try:
        return self.__init__(user_data[0])
    except IndexError:
        return user_data
