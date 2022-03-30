import asyncio
import json
import os
import re
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils import exceptions

from TOKEN import TOKEN
from browser import WebFunction
from database import Database

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
browser = WebFunction()
database = Database()

loop = asyncio.get_event_loop()

with open("books_data.json", "r", encoding="utf-8") as f:
    books = json.load(f)


# функция по парсингу и обработке замен
async def timeprocess():
    while True:
        for built in ["А", "Т"]:
            dateTomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            changesResult = browser.get_changes(dateTomorrow, built)
            if not os.path.exists(f"zameny\\{dateTomorrow}_{built}.json"):
                if not (changesResult == "Для этого дня замен нет."):
                    with open(f"zameny\\{dateTomorrow}_{built}.json", "w", encoding="utf-8") as file:
                        json.dump(changesResult, file, indent=2, ensure_ascii=False)
                    for classNumber in changesResult.keys():
                        changesString = classNumber + "\n"
                        for lessonNumber in changesResult[classNumber].keys():
                            changesString += lessonNumber + ": " + changesResult[classNumber][lessonNumber] + "\n"
                        cs = re.findall(r"(\d{1,2})(\w{0,1}?)( )?/(\w)", classNumber)
                        if cs[0][1] == "":
                            spisokStudents = database.user_data_by_params(grade=cs[0][0], built=cs[0][3])
                        else:
                            spisokStudents = database.user_data_by_params(grade=cs[0][0], symbol=cs[0][1],
                                                                          built=cs[0][3])
                        for student in spisokStudents:
                            try:
                                await bot.send_message(student[0],
                                                       f"Расписание на следующий день доступно: \n{changesString}")
                            except exceptions.ChatNotFound:
                                pass
        await asyncio.sleep(3600)


# кнопка старт
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await bot.send_message(message.from_user.id,
                           "Привет! Чтобы было проще пользоваться функциями бота авторизируйся. "
                           "Напиши информацию о себе. <Имя> <Фамилия> <Класс> <Корпус>."
                           "\nНапример: Иван Иванов 7А А")


# отправление расписания по запросу
@dp.message_handler(commands=["schedule"])
async def message(message: types.Message):
    user_inf = re.findall(r"(/schedule) (\w+) (\w+) (\d+) (\w) (\w)", message.text)
    if len(user_inf) > 0:
        timetable = browser.get_schedule(user_inf[0][1:])
    else:
        if database.check_user(message.from_user.id):
            timetable = browser.get_schedule(database.get_user_data(message.from_user.id)[0][1:])
        else:
            timetable = 0
    if timetable != 0:
        await bot.send_photo(message.from_user.id, timetable, caption="Вот ваше расписание")
    else:
        await bot.send_message(message.from_user.id,
                               "Похоже вы неправильно указали ваши данные для просмотра расписания")


# изменение данный пользователя в дб
@dp.message_handler(commands=["changename"])
async def change_name(message: types.Message):
    if not (re.search(r"\w+ \w+ \d+\w \w", message.text) is None):
        info_student = re.findall(r"(\w+) (\w+) (\d+)(\w) (\w)", message.text)[0]
        database.update_user(message.from_user.id, info_student)
        await bot.send_message(message.from_user.id, "Ваши данные успешно изменены.")
    else:
        await bot.send_message(message.from_user.id,
                               "Проверьте правильность написания ваших данных. Образец: Иванов Иван 7А А")


# поиск книги в базе данных
@dp.message_handler(commands="library")
async def searchbook(message: types.Message):
    if message.text == "/library":
        await bot.send_message(message.from_user.id,
                               "Мы не можем определить ваш запрос. Пожалуйста, напишите подробнее.")
    else:
        s = ""
        for id in books.keys():
            print(id)
            if any(not (re.search(i, books[id]["name"], flags=re.IGNORECASE) is None) for i in
                   message.text[8:].split()):
                s += f"*{books[id]['name']}*\nСкачать: /download{id}\n\n"
        if s == "":
            await bot.send_message(message.from_user.id, f"По запросу \"{message.text[8:]}\" ничего не нашлось.")
        else:
            await bot.send_message(message.from_user.id, "Вот что мне удалось найти:\n\n" + s, parse_mode="Markdown")


# добавляем документ в базу данных
@dp.message_handler(content_types=["document"])
async def get_book(message: types.Message):
    """Если надо будет больше аргументов, используем regex"""
    file_id = message.document.file_id
    caption = message.caption
    books[str(len(books) + 1)] = {"name": caption, "file_id": file_id}
    with open("books_data.json", "w", encoding="utf-8") as file:
        json.dump(books, file, indent=2, ensure_ascii=False)
    await bot.send_message(message.from_user.id, "Книга добавлена")


@dp.message_handler(content_types=["text"])
async def only_text(message: types.Message):
    if not (re.search(r"\w+ \w+ \d+\w \w", message.text) is None):
        info_student = re.findall(r"(\w+) (\w+) (\d+)(\w) (\w)", message.text)[0]
        result = database.add_student(message.from_user.id, info_student)
        if not result:
            await bot.send_message(message.from_user.id, "Похоже вы уже авторизированы")
        else:
            await bot.send_message(message.from_user.id, "Авторизация прошла успешно")
    if message.text.startswith("/download"):
        try:
            print(books[message.text[9:]]["file_id"])
            await bot.send_document(message.from_user.id, books[message.text[9:]]["file_id"])
        except KeyError:
            await bot.send_message(message.from_user.id, "Данный учебник не был найден")


if __name__ == '__main__':
    loop.create_task(timeprocess())
    executor.start_polling(dp, skip_updates=True)
