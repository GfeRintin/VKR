from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data.tests import TESTS
from database import db

user_answers = {}

async def select_test(callback_query: types.CallbackQuery):
    markup = InlineKeyboardMarkup()
    for doc in TESTS.keys():
        markup.add(InlineKeyboardButton(doc, callback_data=f"test_{doc[:3]}"))
    markup.add(InlineKeyboardButton("📈 Просмотр результатов", callback_data='view_results'))
    markup.add(InlineKeyboardButton("🏠 Главное меню", callback_data='menu'))
    await callback_query.message.edit_text("Выберите тест:", reply_markup=markup)

async def start_test(callback_query: types.CallbackQuery):
    doc_short = callback_query.data[len('test_'):]
    doc_full = next((d for d in TESTS if d.startswith(doc_short)), None)
    if doc_full is None:
        await callback_query.message.edit_text("Тест не найден.")
        return
    
    user_id = callback_query.from_user.id
    user_answers[user_id] = {
        "doc": doc_full,
        "answers": [],
        "current_question": 0
    }

    await send_question(callback_query.message, user_id)

async def send_question(message: types.Message, user_id: int):
    doc = user_answers[user_id]["doc"]
    question_index = user_answers[user_id]["current_question"]
    question_data = TESTS[doc][question_index]

    text = f"Вопрос {question_index + 1}: {question_data['question']}\n\n"
    markup = InlineKeyboardMarkup()
    for i, option in enumerate(question_data["options"]):
        text += f"{i + 1}. {option}\n"
        markup.add(InlineKeyboardButton(option, callback_data=f"answer_{i}"))

    await message.edit_text(text, reply_markup=markup)

async def answer_question(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    answer = int(callback_query.data.split('_')[1])
    user_answers[user_id]["answers"].append(answer)

    user_answers[user_id]["current_question"] += 1
    if user_answers[user_id]["current_question"] < len(TESTS[user_answers[user_id]["doc"]]):
        await send_question(callback_query.message, user_id)
    else:
        await show_results(callback_query.message, user_id)

async def show_results(message: types.Message, user_id: int):
    doc = user_answers[user_id]["doc"]
    answers = user_answers[user_id]["answers"]
    correct_answers = 0
    total_questions = len(TESTS[doc])

    for i, question in enumerate(TESTS[doc]):
        if answers[i] == question["correct_answer"]:
            correct_answers += 1

    db.save_test_result(user_id, doc, correct_answers, total_questions)

    text = f"Тест завершен!\n\nПравильных ответов: {correct_answers} из {total_questions}."
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("↩️ Назад", callback_data='menu'))
    await message.edit_text(text, reply_markup=markup)

async def view_test_results(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    results = db.get_test_results(user_id)
    text = "Результаты тестирования:\n\n"
    for result in results:
        text += f"Документ: {result[0]}, Правильных ответов: {result[1]}, Всего вопросов: {result[2]}, Дата: {result[3]}\n"
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("↩️ Назад", callback_data='test'))
    await callback_query.message.edit_text(text, reply_markup=markup)

def register_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(select_test, lambda c: c.data == 'test')
    dp.register_callback_query_handler(start_test, lambda c: c.data.startswith('test_') and len(c.data.split('_')) == 2)
    dp.register_callback_query_handler(answer_question, lambda c: c.data.startswith('answer_'))
    dp.register_callback_query_handler(view_test_results, lambda c: c.data == 'view_results')
