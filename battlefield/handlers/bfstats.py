from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram import types
from ..bftracker import bf1, bf5
from ..commands import bfstats
import re
from app import StatState, dp

@dp.message_handler(commands=['bf2', 'bf2stat', 'bf2stats'])
async def bf2stats(message: types.Message):
    message.text = re.sub(r"^/[a-zA-Z0-9_.-@]*", "", message.text).lstrip()
    if message.text == "":
        await StatState.bf2.set()
        await message.reply("Give me a playername (\"/cancel\" to cancel)")
    else:
        await bfstats.bf2(message)

@dp.message_handler(state=StatState.bf2)
async def bf2stats_return(message: types.Message, state: FSMContext):
    message.text = re.sub(r"^/[a-zA-Z0-9_.-@]*", "", message.text).lstrip()
    await bfstats.bf2(message)
    await state.finish()


@dp.message_handler(commands=['bf3', 'bf3stat', 'bf3stats'])
async def bf3stats(message: types.Message):
    message.text = re.sub(r"^/[a-zA-Z0-9_.-@]*", "", message.text).lstrip()
    if message.text == "":
        await StatState.bf3.set()
        await message.reply("Give me a platform and playername (pc is default platform if none given, \"/cancel\" to cancel)")
    else:
        await bfstats.bf3(message)

@dp.message_handler(state=StatState.bf3)
async def bf3stats_return(message: types.Message, state: FSMContext):
    message.text = re.sub(r"^/[a-zA-Z0-9_.-@]*", "", message.text).lstrip()
    await bfstats.bf3(message)
    await state.finish()


@dp.message_handler(commands=['bfh', 'bfhstat', 'bfhstats'])
async def bfhstats(message: types.Message):
    message.text = re.sub(r"^/[a-zA-Z0-9_.-@]*", "", message.text).lstrip()
    if message.text == "":
        await StatState.bfh.set()
        await message.reply("Give me a platform and playername (pc is default platform if none given, \"/cancel\" to cancel)")
    else:
        await bfstats.bfh(message)

@dp.message_handler(state=StatState.bfh)
async def bfhstats_return(message: types.Message, state: FSMContext):
    message.text = re.sub(r"^/[a-zA-Z0-9_.-@]*", "", message.text).lstrip()
    await bfstats.bfh(message)
    await state.finish()


@dp.message_handler(commands=['bf4', 'bf4stat', 'bf4stats'])
async def bf4stats(message: types.Message):
    message.text = re.sub(r"^/[a-zA-Z0-9_.-@]*", "", message.text).lstrip()
    if message.text == "":
        await StatState.bf4.set()
        await message.reply("Give me a platform and playername (pc is default platform if none given, \"/cancel\" to cancel)")
    else:
        await bfstats.bf4(message)

@dp.message_handler(state=StatState.bf4)
async def bf4stats_return(message: types.Message, state: FSMContext):
    message.text = re.sub(r"^/[a-zA-Z0-9_.-@]*", "", message.text).lstrip()
    await bfstats.bf4(message)
    await state.finish()


@dp.message_handler(commands=['bf1', 'bf1stat', 'bf1stats'])
async def bf1stats(message: types.Message):
    message.text = re.sub(r"^/[a-zA-Z0-9_.-@]*", "", message.text).lstrip()
    if message.text == "":
        await StatState.bf1.set()
        await message.reply("Give me a platform and playername (pc is default platform if none given, \"/cancel\" to cancel)")
    else:
        result = await bf1.bf1TrackerPlatformSelect(message.text)
        if result["current"] == "pc":
            await bfstats.bf1(message, result["new_message"], "tunguska", "bf1")
        else:
            await bf1.bf1Tracker(message, result)

@dp.message_handler(state=StatState.bf1)
async def bf1stats_return(message: types.Message, state: FSMContext):
    message.text = re.sub(r"^/[a-zA-Z0-9_.-@]*", "", message.text).lstrip()
    result = await bf1.bf1TrackerPlatformSelect(message.text)
    if result["current"] == "pc":
        await bfstats.bf1(message, result["new_message"], "tunguska", "bf1")
    else:
        await bf1.bf1Tracker(message, result)
    await state.finish()


@dp.message_handler(commands=['bf5', 'bf5stat', 'bf5stats', 'bfv', 'bfvstat', 'bfvstats'])
async def bf5stats(message: types.Message):
    message.text = re.sub(r"^/[a-zA-Z0-9_.-@]*", "", message.text).lstrip()
    if message.text == "":
        await StatState.bf5.set()
        await message.reply("Give me a platform and playername (pc is default platform if none given, \"/cancel\" to cancel)")
    else:
        await bf5.bf5stat(message)

@dp.message_handler(state=StatState.bf5)
async def bf5stats_return(message: types.Message, state: FSMContext):
    message.text = re.sub(r"^/[a-zA-Z0-9_.-@]*", "", message.text).lstrip()
    await bf5.bf5stat(message)
    await state.finish()


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('Cancelled action.')
