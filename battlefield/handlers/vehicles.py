from aiogram.dispatcher import FSMContext
from aiogram import types
from ..commands import vehicles
import re
from app import StatState, dp
from ..bftracker import bf1, bf5

@dp.message_handler(commands=['bf2vehiclegraph'])
async def bf2stats(message: types.Message):
    message.text = re.sub(r"^/[a-zA-Z0-9_.-@]*", "", message.text).lstrip()
    if message.text == "":
        await StatState.bf2vehiclegraph.set()
        await message.reply("Give me a playername (\"/cancel\" to cancel)")
    else:
        await vehicles.bf2Graph(message)

@dp.message_handler(state=StatState.bf2vehiclegraph)
async def bf2stats_return(message: types.Message, state: FSMContext):
    message.text = re.sub(r"^/[a-zA-Z0-9_.-@]*", "", message.text).lstrip()
    await vehicles.bf2Graph(message)
    await state.finish()


@dp.message_handler(commands=['bf3vehiclegraph'])
async def bf3stats(message: types.Message):
    message.text = re.sub(r"^/[a-zA-Z0-9_.-@]*", "", message.text).lstrip()
    if message.text == "":
        await StatState.bf3vehiclegraph.set()
        await message.reply("Give me a platform and playername (pc is default platform if none given, \"/cancel\" to cancel)")
    else:
        await vehicles.battlelogGraph(message, "vehiclesPopulateStats", "bf3")

@dp.message_handler(state=StatState.bf3vehiclegraph)
async def bf3stats_return(message: types.Message, state: FSMContext):
    message.text = re.sub(r"^/[a-zA-Z0-9_.-@]*", "", message.text).lstrip()
    await vehicles.battlelogGraph(message, "vehiclesPopulateStats", "bf3")
    await state.finish()


@dp.message_handler(commands=['bfhvehiclegraph'])
async def bfhstats(message: types.Message):
    message.text = re.sub(r"^/[a-zA-Z0-9_.-@]*", "", message.text).lstrip()
    if message.text == "":
        await StatState.bfhvehiclegraph.set()
        await message.reply("Give me a platform and playername (pc is default platform if none given, \"/cancel\" to cancel)")
    else:
        await vehicles.battlelogGraph(message, "bfhvehiclesPopulateStats", "bfh")

@dp.message_handler(state=StatState.bfhvehiclegraph)
async def bfhstats_return(message: types.Message, state: FSMContext):
    message.text = re.sub(r"^/[a-zA-Z0-9_.-@]*", "", message.text).lstrip()
    await vehicles.battlelogGraph(message, "bfhvehiclesPopulateStats", "bfh")
    await state.finish()


@dp.message_handler(commands=['bf4vehiclegraph'])
async def bf4stats(message: types.Message):
    message.text = re.sub(r"^/[a-zA-Z0-9_.-@]*", "", message.text).lstrip()
    if message.text == "":
        await StatState.bf4vehiclegraph.set()
        await message.reply("Give me a platform and playername (pc is default platform if none given, \"/cancel\" to cancel)")
    else:
        await vehicles.battlelogGraph(message, "warsawvehiclesPopulateStats", "bf4")

@dp.message_handler(state=StatState.bf4vehiclegraph)
async def bf4stats_return(message: types.Message, state: FSMContext):
    message.text = re.sub(r"^/[a-zA-Z0-9_.-@]*", "", message.text).lstrip()
    await vehicles.battlelogGraph(message, "warsawvehiclesPopulateStats", "bf4")
    await state.finish()


@dp.message_handler(commands=['bfvehiclegraph', 'bf1vehiclegraph'])
async def bf1stats(message: types.Message):
    message.text = re.sub(r"^/[a-zA-Z0-9_.-@]*", "", message.text).lstrip()
    if message.text == "":
        await StatState.bf1.set()
        await message.reply("Give me a platform and playername (pc is default platform if none given, \"/cancel\" to cancel)")
    else:
        result = await bf1.bf1TrackerPlatformSelect(message.text)
        if result["current"] == "pc":
            message.text = result["new_message"]
            await vehicles.graph(message, "tunguska")
        else:
            await bf1.top10VehicleGraph(message, result)

@dp.message_handler(state=StatState.bf1vehiclegraph)
async def bf1stats_return(message: types.Message, state: FSMContext):
    message.text = re.sub(r"^/[a-zA-Z0-9_.-@]*", "", message.text).lstrip()
    result = await bf1.bf1TrackerPlatformSelect(message.text)
    if result["current"] == "pc":
        message.text = result["new_message"]
        await vehicles.graph(message, "tunguska")
    else:
        await bf1.top10VehicleGraph(message, result)


@dp.message_handler(commands=['bf5vehiclegraph', 'bfvvehiclegraph'])
async def bf5stats(message: types.Message):
    message.text = re.sub(r"^/[a-zA-Z0-9_.-@]*", "", message.text).lstrip()
    if message.text == "":
        await StatState.bf5vehiclegraph.set()
        await message.reply("Give me a platform and playername (pc is default platform if none given, \"/cancel\" to cancel)")
    else:
        await bf5.bf5vehiclegraph(message)

@dp.message_handler(state=StatState.bf5vehiclegraph)
async def bf5stats_return(message: types.Message, state: FSMContext):
    message.text = re.sub(r"^/[a-zA-Z0-9_.-@]*", "", message.text).lstrip()
    await bf5.bf5vehiclegraph(message)
    await state.finish()
