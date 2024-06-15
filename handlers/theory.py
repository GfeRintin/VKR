from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data.theory_materials import PMLA, TECHREGULATION

# Объединение всех материалов в одну структуру
theory_materials = {
    "ПМЛА": PMLA,
    "ТЕХРЕГЛАМЕНТ": TECHREGULATION
}

# Обработчики для теоретического обучения
async def theory_section(callback_query: types.CallbackQuery):
    markup = InlineKeyboardMarkup()
    for doc in theory_materials.keys():
        markup.add(InlineKeyboardButton(doc, callback_data=f"theory_{doc[:3]}"))
    markup.add(InlineKeyboardButton("🏠 Главное меню", callback_data='menu'))
    await callback_query.message.edit_text("Выберите документ:", reply_markup=markup)

async def show_theory_topics(callback_query: types.CallbackQuery):
    doc_short = callback_query.data[len('theory_'):]
    doc_full = next((d for d in theory_materials if d.startswith(doc_short)), None)
    if doc_full is None:
        await callback_query.message.edit_text("Документ не найден.")
        return
    markup = InlineKeyboardMarkup()
    for index, topic in enumerate(theory_materials[doc_full].keys()):
        topic_id = f"{index:02d}"
        markup.add(InlineKeyboardButton(topic, callback_data=f"theory_{doc_short}_{topic_id}"))
    markup.add(InlineKeyboardButton("🏠 В меню", callback_data='theory'))
    markup.add(InlineKeyboardButton("🏠 Главное меню", callback_data='menu'))
    await callback_query.message.edit_text(f"Выберите тему из {doc_full}:", reply_markup=markup)

async def send_theory_material(callback_query: types.CallbackQuery):
    data_parts = callback_query.data.split('_')
    if len(data_parts) != 3:
        await callback_query.message.edit_text("Ошибка данных.")
        return
    
    doc_short, topic_id = data_parts[1], int(data_parts[2])
    doc_full = next((d for d in theory_materials if d.startswith(doc_short)), None)
    if doc_full is None:
        await callback_query.message.edit_text("Документ не найден.")
        return
    
    topics = list(theory_materials[doc_full].keys())
    topic_full = topics[topic_id]
    if topic_full is None:
        await callback_query.message.edit_text("Тема не найдена.")
        return

    material = theory_materials[doc_full][topic_full]
    
    # Формируем текст сообщения
    text = material['text']


    # Добавляем кнопки "Назад" и "Далее"
    markup = InlineKeyboardMarkup()
    if topic_id > 0:
        prev_topic_id = f"{topic_id - 1:02d}"
        markup.add(InlineKeyboardButton("⬅️ Предыдущая тема", callback_data=f"theory_{doc_short}_{prev_topic_id}"))
    if topic_id < len(topics) - 1:
        next_topic_id = f"{topic_id + 1:02d}"
        markup.add(InlineKeyboardButton("➡️ Следующая тема", callback_data=f"theory_{doc_short}_{next_topic_id}"))
    markup.add(InlineKeyboardButton("↩️ Назад", callback_data=f"theory_{doc_short}"))
    markup.add(InlineKeyboardButton("🏠 Главное меню", callback_data='menu'))

    # Проверка на изменение текста сообщения и разметки кнопок
    if callback_query.message.text != text:
        await callback_query.message.edit_text(text, reply_markup=markup)
    else:
        await callback_query.message.edit_reply_markup(reply_markup=markup)

def register_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(theory_section, lambda c: c.data == 'theory')
    dp.register_callback_query_handler(show_theory_topics, lambda c: c.data.startswith('theory_') and len(c.data.split('_')) == 2)
    dp.register_callback_query_handler(send_theory_material, lambda c: c.data.startswith('theory_') and len(c.data.split('_')) == 3)
