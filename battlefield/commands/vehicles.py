from aiogram import types
from ..api.api_requests import getBf2DataFromEa, getDataFromBattlelog, getDataFromEa, getMultipleFromEa
from . import grapher

async def bf2Graph(message: types.Message):
    try:
        stats = (await getBf2DataFromEa(message.text))
        vehicleNames = ["Armor", "Jet", "Helicopter", "Transport", "Anti-Air", "Ground-Def."]
        graphing = []
        for i in range(len(vehicleNames)):
            try:
                graphing.append({"name": vehicleNames[i], "kills": int(stats["vkl-"+str(i)])})
            except:
                pass
        await grapher.main(message, graphing, stats, "bf2", "vehicles")
    except:
        await message.reply("player not found")

async def graph(message: types.Message, game):
    """returns top vehicles for bf1 in a graph"""
    try:
        stats = (await getDataFromEa(message.text, "Progression.getVehiclesByPersonaId", game))
        vehicles = []
        for weapon in stats["result"]:
            try:
                vehicles.append({"name": weapon["name"].capitalize(), "kills": int(weapon["stats"]["values"]["kills"])})
            except:
                pass
        graphing = sorted(vehicles, key=lambda k: k['kills'], reverse=True) 
        await grapher.main(message, graphing, stats, game, "vehicles")
    except:
        await message.reply("player not found")

async def battlelogGraph(message: types.Message, type, game):
    """returns top vehicles for bfh, bf3 and bf4 as graph"""
    try:
        stats = (await getDataFromBattlelog(type, message.text, game))
        naming = "name"
        if game in ["bfh", "bf4"]:
            naming = "slug"
        vehicles = []
        for weapon in stats["data"]["mainVehicleStats"]:
            try:
                vehicles.append({"name": weapon[naming], "kills": int(weapon["kills"])})
            except:
                pass
        graphing = sorted(vehicles, key=lambda k: k['kills'], reverse=True) 
        await grapher.main(message, graphing, stats, game, "vehicles")
    except:
        await message.reply("player not found")