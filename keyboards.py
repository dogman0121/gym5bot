from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

buttonSchedule = KeyboardButton("🕑 Расписание")
buttonChanges = KeyboardButton("❌ Замены")
buttonLibrary = KeyboardButton("📚 Книги")
basedKeyboard = ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
basedKeyboard.add(buttonSchedule)
basedKeyboard.add(buttonChanges, buttonLibrary)