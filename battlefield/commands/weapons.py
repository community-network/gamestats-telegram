from aiogram import types
from ..api.api_requests import getBf2DataFromEa, getDataFromBattlelog, getDataFromEa, getMultipleFromEa
from . import grapher

async def graph(message: types.Message, game):
    """returns top weapons for bf1 in a graph"""
    try:
        stats = (await getDataFromEa(message.text, "Progression.getWeaponsByPersonaId", game))
        weapons = []
        for weaponGroup in stats["result"]:
            for weapon in weaponGroup["weapons"]:
                try:
                    weapons.append({"name": weapon["name"], "kills": int(weapon["stats"]["values"]["kills"])})
                except:
                    pass
        graphing = sorted(weapons, key=lambda k: k['kills'], reverse=True) 
        await grapher.main(message, graphing, stats, game, "weapons")
    except:
        await message.reply("player not found")

async def battlelogGraph(message: types.Message, type, game):
    """returns top weapons for bfh, bf3 and bf4 as graph"""
    try:    
        stats = (await getDataFromBattlelog(type, message.text, game))
        weapons = []
        naming = "name"
        if game in ["bfh", "bf4"]:
            naming = "slug"
        for weapon in stats["data"]["mainWeaponStats"]:
            try:
                weapons.append({"name": weapon[naming], "kills": int(weapon["kills"])})
            except:
                pass
        graphing = sorted(weapons, key=lambda k: k['kills'], reverse=True) 
        await grapher.main(message, graphing, stats, game, "weapons")
    except:
        await message.reply("player not found")

async def bf2Graph(message: types.Message):
    try:
        stats = (await getBf2DataFromEa(message.text))
        weaponNames = ["Assault-Rifle", "Grenade-Launcher", "Carbine", "Light Machine Gun", "Sniper Rifle", "Pistol", "Anti-Tank", "Sub-Machine Gun", "Shotgun", "Knife", "Defibrillator", "Explosives", "Grenade"]
        weapons = []
        for i in range(len(weaponNames)):
            try:
                weapons.append({"name": weaponNames[i], "kills": int(stats["wkl-"+str(i)])})
            except:
                pass
        graphing = sorted(weapons, key=lambda k: k['kills'], reverse=True) 
        await grapher.main(message, graphing, stats, "bf2", "weapons")
    except:
        await message.reply("player not found")
