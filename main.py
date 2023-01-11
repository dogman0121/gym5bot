import logging

from aiogram import Bot, Dispatcher, executor, types, utils
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from web_func import *
from utils import *
from config import API_TOKEN
from user import User
from database import Database
from exceptions import *
import datetime
import json
from keyboards import basedKeyboard
import re

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

db = Database()

books = json.load(open("books_data.json", "r", encoding="utf-8"))


""" Регистрация пользователя """


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    await message.answer(
        "Привет, на связи гимназический бот!\n\n"
        "Он создан для того, чтобы собрать такие функции как просмотр расписания, замен и т.д. в одном месте.\n\n"
        "Чтобы зарегистрироваться, отправьте команду /register и следуйте указаниям."
    )


@dp.message_handler(state=RegistrationUser.waiting_to_register)
async def get_user_data(message: types.Message, state: FSMContext):
    try:
        user = User.get_data_from_text(message.from_user.id, message.text)
        db.add_user(user)
        await message.answer("Регистрация прошла успешно", reply_markup=basedKeyboard)
        await state.finish()
    except UserCreationError:
        await message.answer("Ошибка регистрации! Проверьте правильность написания данный. Пример: Иванов Иван 11А А")


async def start_registration(message: types.Message, state: FSMContext):
    await message.answer(
        "Как тебя зовут?\n"
        "Напиши о себе в формате <фамилия> <имя> <класс> <литера класса> <корпус>\n"
        "Например: Иванов Иван 11А А"
    )
    await state.set_state(RegistrationUser.waiting_to_register.state)


@dp.callback_query_handler(lambda call: call.data == "register_yes")
async def confirm_registration(callback: types.CallbackQuery, state: FSMContext):
    await start_registration(callback.message, state)


@dp.callback_query_handler(lambda call: call.data == "register_no")
async def confirm_registration(callback: types.CallbackQuery, state: FSMContext):
    await bot.edit_message_text(
        chat_id=callback.from_user.id,
        text="Вы уже зарегестрированы, хотите перерегестрироваться заново?\n\n *_Отменено_*",
        parse_mode="MarkdownV2",
        message_id=callback.message.message_id
    )


@dp.message_handler(commands=["register"])
async def register_command(message: types.Message, state: FSMContext):
    try:
        db.get_user_data(message.from_user.id)

        button_yes = types.InlineKeyboardButton("Да", callback_data="register_yes")
        button_no = types.InlineKeyboardButton("Нет", callback_data="register_no")
        buttons = types.InlineKeyboardMarkup()
        buttons.add(button_yes, button_no)

        await message.answer("Вы уже зарегестрированы, хотите перерегестрироваться заново?", reply_markup=buttons)
    except UserNotFoundError:
        await start_registration(message, state)


""" Функции связанные с расписанием """


async def send_schedule(user, msg_id):
    schedule = get_schedule(user)

    await bot.edit_message_text(chat_id=user.telegram_id, text="Ваше расписание готово", message_id=msg_id)
    await bot.send_document(user.telegram_id, ("schedule.png", schedule))


@dp.message_handler(lambda message: message.text == "🕑 Расписание")
async def schedule_from_keyboard(message: types.Message):
    try:
        user = db.get_user_data(message.from_user.id)
        msg = await message.answer("Ждите...")
        await send_schedule(user, msg.message_id)
    except UserNotFoundError:
        await message.answer("Зарегистрируйтесь, чтобы воспользоваться данной функцией. Чтобы зарегестрироваться: /register")


@dp.message_handler(commands=["schedule"])
async def schedule_command(message: types.Message):
    try:
        try:
            user = User.get_data_from_text(message.from_user.id, message.get_args())
        except UserCreationError:
            user = db.get_user_data(message.from_user.id)

        msg = await message.answer("Ждите...")
        await send_schedule(user, msg.message_id)
    except UserNotFoundError:
        await message.answer("Зарегистрируйтесь, чтобы воспользоваться данной функцией. Чтобы зарегестрироваться: /register")

""" Функции, связанные с заменами """


async def send_changes(user, msg_id, date):
    changes = user.get_user_changes(date.strftime("%Y-%m-%d"))

    button_prev = types.InlineKeyboardButton("◀◀", callback_data=(date-datetime.timedelta(days=1)).strftime("%Y-%m-%d"))
    button_now = types.InlineKeyboardButton(date.strftime("%d.%m.%Y"), callback_data=date.strftime("%Y-%m-%d"))
    button_next = types.InlineKeyboardButton("▶▶", callback_data=(date+datetime.timedelta(days=1)).strftime("%Y-%m-%d"))

    buttons = types.InlineKeyboardMarkup()
    buttons.add(button_prev, button_now, button_next)

    try:
        await bot.edit_message_text(chat_id=user.telegram_id, text=changes, reply_markup=buttons, message_id=msg_id)
    except utils.exceptions.MessageNotModified:
        pass


@dp.message_handler(lambda message: message.text == "❌ Замены")
async def changes_from_keyboard(message: types.Message):
    try:
        user = db.get_user_data(message.from_user.id)
        msg = await message.answer("Ждите...")

        today_date = datetime.datetime.now() + datetime.timedelta(days=datetime.datetime.now().hour >= 16)

        await send_changes(user, msg.message_id, today_date)
    except UserNotFoundError:
        await message.answer("Зарегистрируйтесь, чтобы воспользоваться данной функцией. Чтобы зарегестрироваться: /register")

@dp.message_handler(commands=["changes"])
async def changes_command(message: types.Message):
    try:
        try:
            user = User.get_data_from_text(message.from_user.id, message.get_args())
        except UserCreationError:
            user = db.get_user_data(message.from_user.id)

        today_date = datetime.datetime.now() + datetime.timedelta(days=datetime.datetime.now().hour >= 16)
        msg = await message.answer("Ждите...")
        await send_changes(user, msg.message_id, today_date)
    except UserNotFoundError:
        await message.answer("Зарегистрируйтесь, чтобы воспользоваться данной функцией. Чтобы зарегестрироваться: /register")


@dp.callback_query_handler(lambda callback: callback.data.startswith("2023"))
async def changes_call(callback: types.CallbackQuery):
    user = db.get_user_data(callback.from_user.id)

    date = datetime.datetime.strptime(callback.data, "%Y-%m-%d")
    await send_changes(user, callback.message.message_id, date)

""" Функции для библиотеки """


@dp.message_handler(commands=["library"])
async def book_command(message: types.Message, state: FSMContext):
    await message.answer("Привет! Чтобы найти книгу напиши ее название здесь.")
    await state.set_state(SearchingBook.waiting_to_search.state)

@dp.message_handler(lambda message: message.text == "📚 Книги")
async def library_from_keyboard(message: types.Message, state: FSMContext):
    await book_command(message, state)

@dp.message_handler(state=SearchingBook.waiting_to_search)
async def search_book(message: types.Message, state: FSMContext):
    answer = ""
    for book_id in books.keys():
        if any(not (re.search(i, books[book_id]["name"], flags=re.IGNORECASE) is None) for i in message.text.split()):
            answer += f"*{books[book_id]['name']}*\nСкачать: /download{book_id}\n\n"
    if answer == "":
        await bot.send_message(message.from_user.id, f"По запросу \"{message.text}\" ничего не нашлось.")
    else:
        await bot.send_message(message.from_user.id, "Вот что мне удалось найти:\n\n" + answer, parse_mode="Markdown")
    await state.finish()


@dp.message_handler(content_types=["document"])
async def get_book(message: types.Message):
    """Если надо будет больше аргументов, используем regex"""
    file_id = message.document.file_id
    caption = message.caption
    books[str(len(books) + 1)] = {"name": caption, "file_id": file_id}
    with open("books_data.json", "w", encoding="utf-8") as file:
        json.dump(books, file, indent=2, ensure_ascii=False)
    await bot.send_message(message.from_user.id, "Книга добавлена")


@dp.message_handler(lambda message: message.text.startswith("/download"))
async def send_book(message: types.Message):
    try:
        await message.answer_document(books[message.text[9:]]["file_id"])
    except KeyError:
        await message.answer_document("Данный учебник не был найден")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
