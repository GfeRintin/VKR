import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import API_TOKEN
from handlers import start, theory, practice, reference, test, admin
from database import db

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# Initialize database

db.create_tables()

# Register handlers with database instance
start.register_handlers(dp)
theory.register_handlers(dp)
practice.register_handlers(dp)
reference.register_handlers(dp)
test.register_handlers(dp)
admin.register_handlers_admin(dp)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
