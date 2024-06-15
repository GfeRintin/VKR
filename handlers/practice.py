from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data.practical_materials import PRACTICAL_TRAINING
from database import db

async def practical_section(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    progress = db.get_progress(user_id)
    progress_dict = {section_id: completed for section_id, completed in progress}

    markup = InlineKeyboardMarkup()
    for section_id, section in PRACTICAL_TRAINING.items():
        completed = progress_dict.get(section_id, False)
        status = "✅" if completed else "❌"
        markup.add(InlineKeyboardButton(f"{section['title']} {status}", callback_data=f"practical_{section_id}"))
    markup.add(InlineKeyboardButton("🏠 Главное меню", callback_data='menu'))
    await callback_query.message.edit_text("Выберите раздел практического обучения:", reply_markup=markup)

async def show_practical_content(callback_query: types.CallbackQuery):
    section_id = callback_query.data[len('practical_'):]
    section = PRACTICAL_TRAINING.get(section_id)
    if section is None:
        await callback_query.message.edit_text("Раздел не найден.")
        return

    content = section['content']
    question_data = section['question']
    
    await callback_query.message.edit_text(content)

    question_text = question_data['text']
    options = question_data['options']
    
    markup = InlineKeyboardMarkup()
    for i, option in enumerate(options):
        callback_data = f"ans_{section_id}_{i}_{callback_query.message.message_id}"
        markup.add(InlineKeyboardButton(option, callback_data=callback_data))

    await callback_query.message.answer(question_text, reply_markup=markup)

async def check_practical_answer(callback_query: types.CallbackQuery):
    data = callback_query.data.split('_')
    section_id = data[1]
    selected_option = int(data[2])
    message_id = int(data[3])
    section = PRACTICAL_TRAINING.get(section_id)
    correct_option = section['question']['correct_option']

    user_id = callback_query.from_user.id

    if selected_option == correct_option:
        db.update_progress(user_id, section_id, True)
        markup = InlineKeyboardMarkup()
        if section.get("prev"):
            prev_section = section["prev"]
            markup.add(InlineKeyboardButton("⬅️ Предыдущая тема", callback_data=f"practical_{prev_section}"))
        if section.get("next"):
            next_section = section["next"]
            markup.add(InlineKeyboardButton("➡️ Следующая тема", callback_data=f"practical_{next_section}"))
        markup.add(InlineKeyboardButton("↩️ Назад", callback_data='practical'))
        markup.add(InlineKeyboardButton("🏠 Главное меню", callback_data='menu'))

        await callback_query.message.edit_text("Правильный ответ! ✅\n\nВыберите дальнейшее действие:", reply_markup=markup)
    else:
        await callback_query.answer("Неправильный ответ. ❌", show_alert=True)

def register_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(practical_section, lambda c: c.data == 'practical')
    dp.register_callback_query_handler(show_practical_content, lambda c: c.data.startswith('practical_'))
    dp.register_callback_query_handler(check_practical_answer, lambda c: c.data.startswith('ans_'))
