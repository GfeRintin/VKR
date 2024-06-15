from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import db

def get_main_menu_inline(user_id):
    main_menu = InlineKeyboardMarkup(row_width=1)
    button = [
        InlineKeyboardButton('📚 Теоретическое обучение', callback_data='theory'),
        InlineKeyboardButton('🛠 Практическое обучение', callback_data='practical'),
        InlineKeyboardButton('📄 Справка', callback_data='reference'),
        InlineKeyboardButton('📝 Тестирование', callback_data='test')
    ]
    main_menu.add(*button)
    if db.is_admin(user_id):
        main_menu.add(InlineKeyboardButton("Административная панель", callback_data='admin'))
    return main_menu
