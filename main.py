from aiogram import Bot, Dispatcher, executor, types

import asyncio
import os
import re
from TOKEN import TOKEN

from browser import WebFunction

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
browser = WebFunction()


@dp.message_handler(commands=["schedule"])
async def message(message: types.Message):
    inf = re.findall(r"(/schedule) (\w+) (\w+) (\d+) (\w) (\w)", message.text)[0]
    result = browser.get_schedule(inf[1], inf[2], inf[3], inf[4], inf[5])
    with open(f"temp_picture//{result}.png", "rb") as file:
        await bot.send_photo(message.from_user.id, file, caption="Вот ваше расписание")
    os.remove(f"temp_picture//{result}.png")

    #await bot.send_message(message.from_user.id, message.text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)