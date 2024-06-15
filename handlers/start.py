from aiogram import types, Dispatcher
from utils.keyboards import get_main_menu_inline
from database import db

async def send_welcome(message: types.Message):
    print("Бот ВКР")
    db.add_user(message.from_user.id, message.from_user.first_name, message.from_user.last_name, message.from_user.username)
    await message.answer("Выберите раздел:", reply_markup=get_main_menu_inline(message.from_user.id))

async def send_welcome_callback(callback_query: types.CallbackQuery):
    db.add_user(callback_query.message.from_user.id, callback_query.message.from_user.first_name, callback_query.message.from_user.last_name, callback_query.message.from_user.username)
    await callback_query.message.edit_text("Выберите раздел:", reply_markup=get_main_menu_inline(callback_query.from_user.id))

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(send_welcome, commands=['start', 'menu'])
    dp.register_callback_query_handler(send_welcome_callback, lambda c: c.data == 'menu')
