# https://docs.aiogram.dev/en/latest/
import re
import os
import asyncio
from battlefield.api.api_requests import onReadyCheck
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

API_TOKEN = os.environ["token"]

# Configure logging
logging.basicConfig(level=logging.INFO)


class StatState(StatesGroup):
    bf2 = State()
    bf3 = State()
    bfh = State()
    bf4 = State()
    bf1 = State()
    bf5 = State()

    bf2weapongraph = State()
    bf3weapongraph = State()
    bfhweapongraph = State()
    bf4weapongraph = State()
    bf1weapongraph = State()
    bf5weapongraph = State()

    bf2vehiclegraph = State()
    bf3vehiclegraph = State()
    bfhvehiclegraph = State()
    bf4vehiclegraph = State()
    bf1vehiclegraph = State()
    bf5vehiclegraph = State()


# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=["start", "help"])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply(
        "This is the first initial version of the gamestats bot for telegram\nWe will start by adding the main commands:\n/bf1stats, /bf5stats, /bf4stats etc..."
    )


from battlefield.handlers import *

if __name__ == "__main__":
    asyncio.ensure_future(onReadyCheck())
    executor.start_polling(dp, skip_updates=True)
