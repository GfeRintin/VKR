from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import db

reference_materials = {
    "Регламент": """
    Технический регламент описывает основные процессы и требования к работе на газоконденсатном промысле...
    """,
    # Добавьте больше материалов
}

async def reference_section(callback_query: types.CallbackQuery):
    markup = InlineKeyboardMarkup()
    for doc in reference_materials.keys():
        short_doc = doc[:30]  # Ограничим длину
        markup.add(InlineKeyboardButton(doc, callback_data=f"ref_{short_doc}"))
    await callback_query.message.edit_text("Выберите документ:", reply_markup=markup)

async def send_reference_material(callback_query: types.CallbackQuery):
    short_doc = callback_query.data[len('ref_'):]
    doc = next((d for d in reference_materials if d.startswith(short_doc)), None)
    material = reference_materials.get(doc, "Документ не найден.")
    await callback_query.message.edit_text(material)

def register_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(reference_section, lambda c: c.data == 'reference')
    dp.register_callback_query_handler(send_reference_material, lambda c: c.data.startswith('ref_'))
