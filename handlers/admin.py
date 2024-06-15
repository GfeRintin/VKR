from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

from database import db

class AdminStates(StatesGroup):
    add_admin = State()
    remove_admin = State()

async def admin_panel(callback_query: types.CallbackQuery):
    if not db.is_admin(callback_query.from_user.id):
        await callback_query.message.answer("У вас нет доступа к этой команде.")
        return

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Просмотр результатов всех пользователей", callback_data='view_all_users'))
    markup.add(InlineKeyboardButton("Просмотр администраторов", callback_data='view_admins'))
    markup.add(InlineKeyboardButton("Добавить администратора", callback_data='add_admin'))
    markup.add(InlineKeyboardButton("Удалить администратора", callback_data='remove_admin'))
    markup.add(InlineKeyboardButton("🏠 Главное меню", callback_data='menu'))
    await callback_query.message.edit_text("Административная панель", reply_markup=markup)

async def view_all_users(callback_query: types.CallbackQuery):
    if not db.is_admin(callback_query.from_user.id):
        await callback_query.message.answer("У вас нет доступа к этой команде.")
        return

    users = db.get_all_users()
    if not users:
        await callback_query.message.edit_text("Нет пользователей, проходивших тесты.")
        return

    text = "Выберите пользователя для просмотра результатов тестирования:"
    markup = InlineKeyboardMarkup()
    for user in users:
        username = user[1] if user[1] else f"ID: {user[0]}"
        markup.add(InlineKeyboardButton(username, callback_data=f'view_user_{user[0]}'))
    markup.add(InlineKeyboardButton("↩️ Назад", callback_data='admin'))
    await callback_query.message.edit_text(text, reply_markup=markup)

async def view_user_results(callback_query: types.CallbackQuery):
    if not db.is_admin(callback_query.from_user.id):
        await callback_query.message.answer("У вас нет доступа к этой команде.")
        return

    user_id = int(callback_query.data.split('_')[-1])
    results = db.get_test_results_for_user(user_id)
    if not results:
        await callback_query.message.edit_text("Нет результатов тестирования для данного пользователя.")
        return

    text = f"Результаты тестирования для пользователя {user_id}:\n\n"
    for result in results:
        text += f"Документ: {result[0]}, Правильных ответов: {result[1]}, Всего вопросов: {result[2]}, Дата: {result[3]}\n"
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("↩️ Назад", callback_data='view_all_users'))
    await callback_query.message.edit_text(text, reply_markup=markup)
    
async def add_admin_start(callback_query: types.CallbackQuery, state: FSMContext):
    if not db.is_admin(callback_query.from_user.id):
        await callback_query.message.answer("У вас нет доступа к этой команде.")
        return

    await AdminStates.add_admin.set()
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("↩️ Назад", callback_data='cancel_add_admin'))
    await callback_query.message.edit_text("Отправьте user_id пользователя, которого хотите сделать администратором.", reply_markup=markup)


async def add_admin_finish(message: types.Message, state: FSMContext):
    if not db.is_admin(message.from_user.id):
        await message.answer("У вас нет доступа к этой команде.")
        return

    try:
        user_id = int(message.text)
        db.add_admin(user_id)
        await message.answer(f"Пользователь с user_id {user_id} добавлен как администратор.")
        await state.finish()
    except ValueError:
        await message.answer("Некорректный user_id. Пожалуйста, отправьте корректный user_id.")

async def cancel_add_admin(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await admin_panel(callback_query)  # Возвращаем пользователя в административную панель


async def remove_admin_start(callback_query: types.CallbackQuery, state: FSMContext):
    if not db.is_admin(callback_query.from_user.id):
        await callback_query.message.answer("У вас нет доступа к этой команде.")
        return

    admins = db.get_all_admins()
    if not admins:
        await callback_query.message.edit_text("Нет администраторов для удаления.")
        return

    text = "Выберите администратора для удаления:"
    markup = InlineKeyboardMarkup()
    for admin in admins:
        markup.add(InlineKeyboardButton(str(admin[0]), callback_data=f'remove_admin_{admin[0]}'))
    markup.add(InlineKeyboardButton("↩️ Назад", callback_data='admin'))
    await callback_query.message.edit_text(text, reply_markup=markup)

async def remove_admin_finish(callback_query: types.CallbackQuery):
    if not db.is_admin(callback_query.from_user.id):
        await callback_query.message.answer("У вас нет доступа к этой команде.")
        return

    user_id = int(callback_query.data.split('_')[-1])
    db.remove_admin(user_id)
    await callback_query.message.edit_text(f"Пользователь с user_id {user_id} удален из администраторов.")

async def view_admins(callback_query: types.CallbackQuery):
    if not db.is_admin(callback_query.from_user.id):
        await callback_query.message.answer("У вас нет доступа к этой команде.")
        return

    admins = db.get_all_admins_views()
    if not admins:
        await callback_query.message.edit_text("Нет администраторов.")
        return

    text = "Список администраторов:\n\n"
    for admin in admins:
        username = admin[1] if admin[1] else f"ID: {admin[0]}"
        text += f"{username}\n"
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("↩️ Назад", callback_data='admin'))
    await callback_query.message.edit_text(text, reply_markup=markup)


def register_handlers_admin(dp: Dispatcher):
    dp.register_callback_query_handler(admin_panel, lambda c: c.data == 'admin')
    dp.register_callback_query_handler(view_all_users, lambda c: c.data == 'view_all_users')
    dp.register_callback_query_handler(view_user_results, lambda c: c.data.startswith('view_user_'))
    dp.register_callback_query_handler(add_admin_start, lambda c: c.data == 'add_admin', state='*')
    dp.register_callback_query_handler(remove_admin_start, lambda c: c.data == 'remove_admin', state='*')
    dp.register_callback_query_handler(remove_admin_finish, lambda c: c.data.startswith('remove_admin_'), state='*')
    dp.register_callback_query_handler(cancel_add_admin, lambda c: c.data == 'cancel_add_admin', state='*')
    dp.register_message_handler(add_admin_finish, state=AdminStates.add_admin)
    dp.register_callback_query_handler(view_admins, lambda c: c.data == 'view_admins')
