from aiogram import types
from ..api.api_requests import getBf2DataFromEa, getDataFromBattlelog, getMultipleFromEa
import datetime
import urllib.parse
from ..imageStats.main import imageStats
from aiogram import types

async def bf2(message: types.Message):
    try:
        stats = (await getBf2DataFromEa(message))
        gameUrl = f"https://www.bf2hub.com/stats/{str(stats['pid'])}"
        kits = {int(stats['kkl-0']): "Anti-Tank", int(stats['kkl-1']): "Assault", int(stats['kkl-2']): "Engineer", int(stats['kkl-3']): "Medic", int(stats['kkl-4']): "Spec-Ops", int(stats['kkl-5']): "Support", int(stats['kkl-6']): "Sniper"}
        sort = {}
        [sort.update({key: value}) for (key, value) in sorted(kits.items(), reverse=True)]
        stats = {
            "name": stats['nick'],
            "rank": stats['rank'],
            "rankImg": f"https://www.bf2hub.com/home/images/ranks/rank_{stats['rank']}.png",
            "0.0": round(int(stats["kill"])/(int(stats['time'])/60),2),
            "0.1": int(int(stats['scor'])/(int(stats['time'])/60)),
            "0.2": round(int(stats["kill"])/int(stats["deth"]),2),

            "0.3": stats["kill"],
            "0.4": stats["deth"],

            "1.0": str(round(float(stats['osaa']),2)) + "%",
            "1.1": list(sort.values())[0],
            "1.2": str(int(int(stats["wins"])/(int(stats["wins"])+int(stats["loss"]))*100)) + "%",

            "1.3": stats["wins"],
            "1.4": stats["loss"],

            "2.0": str(datetime.timedelta(seconds=int(stats['time'])))
        }
        await imageStats.oldBfImageRender(message, stats, gameUrl, "bf2")
    except:
        await message.reply("player not found")

async def bf3(message: types.Message):
    try:
        stats = (await getDataFromBattlelog("overviewPopulateStats", message.text, "bf3"))
        if stats['platformName'] == "cem_ea_id":
            platformName = "pc"
        else: 
            platformName = stats['platformName']
        gameUrl = f"https://gametools.network/stats/{platformName}/name/{urllib.parse.quote(stats['personaName'])}?game=bf3"

        platform = stats["platformName"]
        #get Best Class:
        items = []
        kits = {}
        sort = {}
        [items.append(item) for item in stats["data"]["overviewStats"]["kitScores"]]
        [kits.update({stats["data"]["overviewStats"]["kitScores"][i]: i}) for i in items]
        [sort.update({key: value}) for (key, value) in sorted(kits.items(), reverse=True)]
        try:
            kpm = round(stats["data"]["overviewStats"]["kills"]/(stats["data"]["overviewStats"]["timePlayed"]/60),2)
        except:
            kpm = 0
        try:
            killDeath = round(stats["data"]["overviewStats"]["kills"]/stats["data"]["overviewStats"]["deaths"],2)
        except:
            killDeath = 0
        try:
            winPercent = str(int(stats["data"]["overviewStats"]["numWins"]/(stats["data"]["overviewStats"]["numWins"]+stats["data"]["overviewStats"]["numLosses"])*100)) + "%"
        except:
            winPercent = "0%"
        stats = {
            "onlyName": stats['personaName'],
            "name": stats['personaName'],
            "avatar": stats["avatar"],
            "rank": stats["data"]["overviewStats"]["rank"],
            "rankImg": f'https://cdn.gametools.network/bf3/{stats["data"]["currentRankNeeded"]["texture"].replace("UI/Art/Persistence/Ranks/Rank", "").replace("UI/art/Persistence/Ranks/Rank", "").replace("UI/Art/Persistence/Ranks/rank", "").replace("S0100", "S100")}.png',
            "0.0": kpm,
            "0.1": stats["data"]["overviewStats"]["scorePerMinute"],
            "0.2": stats["data"]["overviewStats"]["elo"],
            "0.3": killDeath,
            "0.4": stats["data"]["overviewStats"]["longestHeadshot"],
            "1.0": winPercent,
            "1.1": stats["data"]["overviewStats"]["headshots"],
            "1.2": str(round(stats["data"]["overviewStats"]["accuracy"],2))+"%",
            "1.3": stats["data"]["kitMap"][list(sort.values())[0]]["name"].capitalize(),
            "1.4": stats["data"]["overviewStats"]["killStreakBonus"],
            "2.0": stats["data"]["overviewStats"]["revives"],
            "2.1": stats["data"]["overviewStats"]["repairs"],
            "2.2": stats["data"]["overviewStats"]["resupplies"],
            "2.3": str(datetime.timedelta(seconds=stats["data"]["overviewStats"]["timePlayed"]))
        }
        await imageStats.imageRender(message, stats, gameUrl, "bf3", platform)
    except:
        await message.reply("player not found")

async def bfh(message: types.Message):
    try:
        stats = (await getDataFromBattlelog("bfhoverviewpopulate", message.text, "bfh"))
        if stats['platformName'] == "cem_ea_id":
            platformName = "pc"
        else: 
            platformName = stats['platformName']
        gameUrl = f"https://gametools.network/stats/{platformName}/name/{urllib.parse.quote(stats['personaName'])}?game=bfh"
        platform = stats["platformName"]
        #get Best Class:
        classes = {"2048": "commander", "4096": "enforcer", "8192": "mechanic", "16384": "operator", "32768": "professional"}
        items = []
        kits = {}
        sort = {}
        [items.append(item) for item in stats["data"]["overviewStats"]["kitScores"]]
        [kits.update({int(stats["data"]["overviewStats"]["kitScores"][i]): i}) for i in items]
        [sort.update({key: value}) for (key, value) in sorted(kits.items(), reverse=True)]
        try:
            kpm = round(stats["data"]["overviewStats"]["kills"]/(stats["data"]["overviewStats"]["timePlayed"]/60),2)
        except:
            kpm = 0
        try:
            winPercent = str(int(stats["data"]["overviewStats"]["numWins"]/(stats["data"]["overviewStats"]["numWins"]+stats["data"]["overviewStats"]["numLosses"])*100)) + "%"
        except:
            winPercent = "0%"
        stats = {
            "onlyName": stats['personaName'],
            "name": stats['personaName'],
            "avatar": stats["avatar"],
            "rank": stats["data"]["overviewStats"]["rank"],
            "rankImg": f'https://cdn.gametools.network/bfh/{stats["data"]["overviewStats"]["rank"]}.png',
            "0.0": kpm,
            "0.1": stats["data"]["overviewStats"]["scorePerMinute"],
            "0.2": winPercent,
            "0.3": stats["data"]["overviewStats"]["kdRatio"],
            "0.4": str(round(stats["data"]["overviewStats"]["accuracy"],2))+"%",
            "1.0": stats["data"]["overviewStats"]["sc_enforcer"],
            "1.1": stats["data"]["overviewStats"]["sc_mechanic"],
            "1.2": stats["data"]["overviewStats"]["sc_operator"],
            "1.3": stats["data"]["overviewStats"]["sc_professional"],
            "1.4": stats["data"]["overviewStats"]["sc_hacker"],
            "2.0": classes[list(sort.values())[0]][0:4].capitalize(),
            "2.1": stats["data"]["overviewStats"]["cashPerMinute"],
            "2.2": stats["data"]["overviewStats"]["killAssists"],
            "2.3": str(datetime.timedelta(seconds=stats["data"]["overviewStats"]["timePlayed"]))
        }
        await imageStats.imageRender(message, stats, gameUrl, "bfh", platform)
    except:
        await message.reply("player not found")


async def bf4(message: types.Message):
    try:
        stats = (await getDataFromBattlelog("warsawdetailedstatspopulate", message.text, "bf4"))
        if stats['platformName'] == "cem_ea_id":
            platformName = "pc"
        else: 
            platformName = stats['platformName']
        gameUrl = f"https://gametools.network/stats/{platformName}/name/{urllib.parse.quote(stats['personaName'])}?game=bf4"
        platform = stats["platformName"]
        #get Best Class:
        classes = {"1":"Assault","2":"engineer","32":"support","8":"recon","2048":"commander"}
        items = []
        kits = {}
        sort = {}
        [items.append(item) for item in stats["data"]["generalStats"]["kitScores"]]
        [kits.update({int(stats["data"]["generalStats"]["kitScores"][i]): i}) for i in items]
        [sort.update({key: value}) for (key, value) in sorted(kits.items(), reverse=True)]
        try:
            winPercent = str(int(int(stats["data"]["generalStats"]["numWins"])/(int(stats["data"]["generalStats"]["numWins"])+int(stats["data"]["generalStats"]["numLosses"]))*100)) + "%"
        except:
            winPercent = "0%"
        stats = {
            "onlyName": stats['personaName'],
            "name": stats['personaName'],
            "avatar": stats["avatar"],
            "rank": stats["data"]["generalStats"]["rank"],
            "rankImg": f'https://cdn.gametools.network/bf4/{stats["data"]["generalStats"]["rank"]}.png',
            "0.0": stats["data"]["generalStats"]["killsPerMinute"],
            "0.1": stats["data"]["generalStats"]["scorePerMinute"],
            "0.2": stats["data"]["generalStats"]["skill"],
            "0.3": stats["data"]["generalStats"]["kdRatio"],
            "0.4": stats["data"]["generalStats"]["longestHeadshot"],
            "1.0": winPercent,
            "1.1": stats["data"]["generalStats"]["headshots"],
            "1.2": str(round(stats["data"]["generalStats"]["accuracy"],2))+"%",
            "1.3": classes[list(sort.values())[0]].capitalize(),
            "1.4": stats["data"]["generalStats"]["killStreakBonus"],
            "2.0": stats["data"]["generalStats"]["revives"],
            "2.1": stats["data"]["generalStats"]["repairs"],
            "2.2": stats["data"]["generalStats"]["resupplies"],
            "2.3": str(datetime.timedelta(seconds=int(stats["data"]["generalStats"]["timePlayed"])))
        }
        await imageStats.imageRender(message, stats, gameUrl, "bf4", platform)
    except:
        await message.reply("player not found")

async def bf1(message: types.Message, name, game, rGameName):
    """returns stats for bf4 and bf1"""
    try:
        stats = (await getMultipleFromEa(name, "Stats.detailedStatsByPersonaId", game))
        if game == "tunguska":
            gameUrl = f"https://gametools.network/stats/pc/name/{urllib.parse.quote(stats['personaName'])}?game=bf1"
        else: #bf4
            gameUrl = f"https://gametools.network/stats/pc/name/{urllib.parse.quote(stats['personaName'])}?game=bf4"
        vehicleKills = 0
        vehicleKills = 0
        try:
            for vehicle in stats["result"]["vehicleStats"]:
                vehicleKills += vehicle["killsAs"]
        except:
            pass
        try:
            winLoseProcent = str(int(float(stats["result"]["basicStats"]["wins"])/(float(stats["result"]["basicStats"]["wins"])+float(stats["result"]["basicStats"]["losses"]))*100)) + "%"
        except:
            winLoseProcent = "0%"
        try:
            headshotProcent = str(round((stats["result"]["headShots"]/stats["result"]["basicStats"]["kills"])*100,2))+"%"
        except:
            headshotProcent = "0%"
        try:
            kd = round(float(stats["result"]["basicStats"]["kills"])/float(stats["result"]["basicStats"]["deaths"]),2)
            infantryKD = round((float(stats["result"]["basicStats"]["kills"])-float(vehicleKills))/float(stats["result"]["basicStats"]["deaths"]),2)
            infantryKPM = round((float(stats["result"]["basicStats"]["kills"])-float(vehicleKills))/float((stats["result"]["basicStats"]["timePlayed"])/60),2)
        except:
            kd = 0
            infantryKD = 0
            infantryKPM = 0
        try:
            bestClass = stats["result"]["favoriteClass"].capitalize()
        except:
            bestClass = ""
        try:
            accuracy = str(round(stats["result"]["accuracyRatio"]*100,2))+"%"
        except:
            accuracy = "0%"
        if stats['activePlatoon']["result"] == None:
            name = stats['personaName']
        else:
            name = f"[{stats['activePlatoon']['result']['tag']}]{stats['personaName']}"
        stats = {
            "onlyName": stats['personaName'],
            "name": name,
            "avatar": stats["avatar"],
            "rank": "",
            "rankImg": "",
            "0.0": stats["result"]["basicStats"]["kpm"],
            "0.1": stats["result"]["basicStats"]["spm"],
            "0.2": stats["result"]["basicStats"]["skill"],
            "0.3": kd,
            "0.4": stats["result"]["longestHeadShot"],
            "1.0": winLoseProcent,
            "1.1": headshotProcent,
            "1.2": accuracy,
            "1.3": bestClass,
            "1.4": stats["result"]["highestKillStreak"],
            "2.0": stats["result"]["revives"],
            "2.1": infantryKD,
            "2.2": infantryKPM,
            "2.3": datetime.timedelta(seconds=stats["result"]["basicStats"]["timePlayed"])
        }
        await imageStats.imageRender(message, stats, gameUrl, rGameName, "pc")
    except:
        await message.reply("player not found")