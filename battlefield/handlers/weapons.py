from aiogram.dispatcher import FSMContext
from aiogram import types
from ..commands import weapons
import re
from app import StatState, dp
from ..bftracker import bf1, bf5

@dp.message_handler(commands=['bf2weapongraph'])
async def bf2stats(message: types.Message):
    message.text = re.sub(r"^/[a-zA-Z0-9_.-@]*", "", message.text).lstrip()
    if message.text == "":
        await StatState.bf2weapongraph.set()
        await message.reply("Give me a playername (\"/cancel\" to cancel)")
    else:
        await weapons.bf2Graph(message)

@dp.message_handler(state=StatState.bf2weapongraph)
async def bf2stats_return(message: types.Message, state: FSMContext):
    message.text = re.sub(r"^/[a-zA-Z0-9_.-@]*", "", message.text).lstrip()
    await weapons.bf2Graph(message)
    await state.finish()


@dp.message_handler(commands=['bf3weapongraph'])
async def bf3stats(message: types.Message):
    message.text = re.sub(r"^/[a-zA-Z0-9_.-@]*", "", message.text).lstrip()
    if message.text == "":
        await StatState.bf3weapongraph.set()
        await message.reply("Give me a platform and playername (pc is default platform if none given, \"/cancel\" to cancel)")
    else:
        await weapons.battlelogGraph(message, "weaponsPopulateStats", "bf3")

@dp.message_handler(state=StatState.bf3weapongraph)
async def bf3stats_return(message: types.Message, state: FSMContext):
    message.text = re.sub(r"^/[a-zA-Z0-9_.-@]*", "", message.text).lstrip()
    await weapons.battlelogGraph(message, "weaponsPopulateStats", "bf3")
    await state.finish()


@dp.message_handler(commands=['bfhweapongraph'])
async def bfhstats(message: types.Message):
    message.text = re.sub(r"^/[a-zA-Z0-9_.-@]*", "", message.text).lstrip()
    if message.text == "":
        await StatState.bfhweapongraph.set()
        await message.reply("Give me a platform and playername (pc is default platform if none given, \"/cancel\" to cancel)")
    else:
        await weapons.battlelogGraph(message, "BFHWeaponsPopulateStats", "bfh")

@dp.message_handler(state=StatState.bfhweapongraph)
async def bfhstats_return(message: types.Message, state: FSMContext):
    message.text = re.sub(r"^/[a-zA-Z0-9_.-@]*", "", message.text).lstrip()
    await weapons.battlelogGraph(message, "BFHWeaponsPopulateStats", "bfh")
    await state.finish()


@dp.message_handler(commands=['bf4weapongraph'])
async def bf4stats(message: types.Message):
    message.text = re.sub(r"^/[a-zA-Z0-9_.-@]*", "", message.text).lstrip()
    if message.text == "":
        await StatState.bf4weapongraph.set()
        await message.reply("Give me a platform and playername (pc is default platform if none given, \"/cancel\" to cancel)")
    else:
        await weapons.battlelogGraph(message, "warsawWeaponsPopulateStats", "bf4")

@dp.message_handler(state=StatState.bf4weapongraph)
async def bf4stats_return(message: types.Message, state: FSMContext):
    message.text = re.sub(r"^/[a-zA-Z0-9_.-@]*", "", message.text).lstrip()
    await weapons.battlelogGraph(message, "warsawWeaponsPopulateStats", "bf4")
    await state.finish()


@dp.message_handler(commands=['bfweapongraph', 'bf1weapongraph'])
async def bf1stats(message: types.Message):
    message.text = re.sub(r"^/[a-zA-Z0-9_.-@]*", "", message.text).lstrip()
    if message.text == "":
        await StatState.bf1.set()
        await message.reply("Give me a platform and playername (pc is default platform if none given, \"/cancel\" to cancel)")
    else:
        result = await bf1.bf1TrackerPlatformSelect(message.text)
        if result["current"] == "pc":
            message.text = result["new_message"]
            await weapons.graph(message, "tunguska")
        else:
            await bf1.top10WeaponGraph(message, result)

@dp.message_handler(state=StatState.bf1weapongraph)
async def bf1stats_return(message: types.Message, state: FSMContext):
    message.text = re.sub(r"^/[a-zA-Z0-9_.-@]*", "", message.text).lstrip()
    result = await bf1.bf1TrackerPlatformSelect(message.text)
    if result["current"] == "pc":
        message.text = result["new_message"]
        await weapons.graph(message, "tunguska")
    else:
        await bf1.top10WeaponGraph(message, result)


@dp.message_handler(commands=['bf5weapongraph', 'bfvweapongraph'])
async def bf5stats(message: types.Message):
    message.text = re.sub(r"^/[a-zA-Z0-9_.-@]*", "", message.text).lstrip()
    if message.text == "":
        await StatState.bf5weapongraph.set()
        await message.reply("Give me a platform and playername (pc is default platform if none given, \"/cancel\" to cancel)")
    else:
        await bf5.bf5weapongraph(message)

@dp.message_handler(state=StatState.bf5weapongraph)
async def bf5stats_return(message: types.Message, state: FSMContext):
    message.text = re.sub(r"^/[a-zA-Z0-9_.-@]*", "", message.text).lstrip()
    await bf5.bf5weapongraph(message)
    await state.finish()
