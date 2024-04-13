import pymongo

from ..mongo import SingletonClient
from . import constants
import json
import re
import uuid
from time import time
import urllib.parse
import sys
import os
import datetime

from tabulate import tabulate

"""be able to do api's"""
import aiohttp
from ..api import authSession
from ..api.loginProcess import requestCookie
from .searchPlayer import checkMe, searchName, originID, platformSelect, getAccessToken
from influxdb_client.client.write_api import SYNCHRONOUS

"""make the command sleep while others run"""
import asyncio

regions = {}

BLREGIONS = {1: "NAm", 2: "SAm", 4: "AU", 8: "Africa", 16: "EU", 32: "Asia", 64:"OC"}

async def ingame_request_headers(code):
    return {
        "X-GatewaySession": f"{code}",
        "X-ClientVersion": "release-bf1-lsu35_26385_ad7bf56a_tunguska_all_prod",
        "X-DbId": "Tunguska.Shipping2PC.Win32",
        "X-CodeCL": "3779779",
        "X-DataCL": "3779779",
        "X-SaveGameVersion": "26",
        "X-HostingGameId": "tunguska",
        "X-Sparta-Info": "tenancyRootEnv=unknown; tenancyBlazeEnv=unknown",
    }

async def onReadyCheck():
    """this script will run every 30 minutes"""
    constants.COOKIE["sid"], constants.COOKIE["remid"], access_code = await requestCookie("api3@gametools.network", "FY5d9uEsv4Js9pQjygyDpzvRFgQUaEHE")
    while True:
        try:
            await getAccessToken()
        except Exception as e:
            print(f"on_ready: {e}")
        await asyncio.sleep(1800)

async def otherNameApi(message):
    db = SingletonClient.get_data_base()
    playersInfo = await db.playerList.find_insensitive_more({"usedNames": message})
    results = ""
    
    if len(playersInfo) != 0:
        for player in playersInfo:
            otherNames = ""
            for name in player["usedNames"]:
                otherNames += f"{name}\n"
            results += f"{player['playerName']}'s names: \n {otherNames}"
            results += f"Last seen in server: \n{player['lastServer']}"
        return {"title": "Manager", "description": f"{results}"}
    else:
        return {"title": "Manager", "description": "player not found"} 

async def bfBanApi(message, strUserId):
    """used for checking if he's on bfban"""
    async with aiohttp.ClientSession() as session:
        if strUserId is None:
            return {"color":0xe74c3c, "title":"BFBan", "description":"Not a valid origin username\n[BFBan.com](https://bfban.com/#/)"} # user not found
        else: 
            try:
                url = f"https://bfban.gametools.network/api/cheaters/{strUserId}"
                async with session.get(url) as r:
                    userInfo = await r.json()
                    for i in range(len(userInfo["data"]["cheater"])):
                        if strUserId == userInfo["data"]["cheater"][i]["originUserId"]:
                            if userInfo["data"]["cheater"][i]["status"] == "1":
                                otherNames = ""
                                for i in range(len(userInfo["data"]["origins"])):
                                    otherNames += f'{userInfo["data"]["origins"][i]["cheaterGameName"]}\n'
                                if otherNames == "":
                                    otherNames = "[BFBan.com](https://bfban.com/#/)"
                                else:
                                    otherNames += f"[BFBan.com](https://bfban.com/#/cheaters/{strUserId})"
                                return {"color":0xFFA500, "title":f"BFBan", "description":f"{message} found in BFBan, all usernames he used according to bfban:\n {otherNames}"}
                            return {"color":0xe74c3c, "title":"BFBan", "description":f"{message} found in BFBan, but not labeled as cheater\n[BFBan.com](https://bfban.com/#/cheaters/{strUserId})"}
                    return {"color":0xe74c3c, "title":"BFBan", "description":f"{message} isn't in BFBan\n[BFBan.com](https://bfban.com/#/)"}
            except:
                return {"color":0xe74c3c, "title":"BFBan", "description":"BFBan is down\n[BFBan.com](https://bfban.com/#/)"} # api down


async def getEA(playerId, method, game, code, session):
    if game == "casablanca":
        url = "https://sparta-gw-bfv.battlelog.com/jsonrpc/pc/api"
    else:
        url = "https://sparta-gw.battlelog.com/jsonrpc/web/api"
    ids = uuid.uuid1()
    headers = {
            "content-type": "application/json",
            "X-GatewaySession": f"{code}",
            "X-ClientVersion": "companion-4569f32f"
        }
    payload = {
            "jsonrpc":"2.0",
            "method":f"{method}",
            "params":{"game":f"{game}", "personaId":f"{playerId}"},
            "id":f"{ids}"
    }
    async with session.post(url, data=json.dumps(payload), headers=headers) as r:
        return await r.json()

async def getBothWeVeFromEa(message, game):
    async with aiohttp.ClientSession() as session:
        strpersonaId = await searchName(None, message, session, game)
        tasks = getEA(strpersonaId['personaId'], "Progression.getWeaponsByPersonaId", game, authSession.code[f'{game}:pc'], session), \
            getEA(strpersonaId['personaId'], "Progression.getVehiclesByPersonaId", game, authSession.code[f'{game}:pc'], session)
        statsWeapon, statsVehicle = await asyncio.gather(*tasks)
    
    statsWeapon["pid"] = strpersonaId['personaId']
    statsWeapon["avatar"] = strpersonaId["avatar"]
    statsWeapon["personaName"] = strpersonaId["personaName"]

    return statsWeapon, statsVehicle



async def getMultipleFromEa(message, firstMethod, game):
    async with aiohttp.ClientSession() as session:
        strpersonaId = await searchName(None, message, session, game)
        tasks = getEA(strpersonaId['personaId'], firstMethod, game, authSession.code[f'{game}:pc'], session), \
            getEA(strpersonaId['personaId'], "Stats.detailedStatsByPersonaId", game, authSession.code[f'{game}:pc'], session), \
            getEA(strpersonaId['personaId'], "Platoons.getActivePlatoon", game, authSession.code[f'{game}:pc'], session)
        stats, detailed_stats, activePlatoon = await asyncio.gather(*tasks)

        stats["pid"] = strpersonaId['personaId']
        stats["avatar"] = strpersonaId["avatar"]
        stats["personaName"] = strpersonaId["personaName"]

        stats["detailed"] = detailed_stats
        stats["activePlatoon"] = activePlatoon
        return stats


async def getDataFromEa(message, method, game):
    """get requested method and detailed stats in ['detailed'], personaId == ['personaId']"""
    async with aiohttp.ClientSession() as session:
        if game == "casablanca":
            url = "https://sparta-gw-bfv.battlelog.com/jsonrpc/pc/api"
        elif game == "bf4":
            url = "https://sparta-gw.battlelog.com/jsonrpc/web/api"
        else:
            url = "https://sparta-gw.battlelog.com/jsonrpc/web/api"
        strpersonaId = await searchName(None, message, session, game)
        # request based on method
        ids = uuid.uuid1()
        headers = {
                "content-type": "application/json",
                "X-GatewaySession": f"{authSession.code[f'{game}:pc']}",
                "X-ClientVersion": "companion-4569f32f"
            }
        payload = {
                "jsonrpc":"2.0",
                "method":f"{method}",
                "params":{"game":f"{game}", "personaId":f"{strpersonaId['personaId']}"},
                "id":f"{ids}"
        }
        async with session.post(url, data=json.dumps(payload), headers=headers) as r:
            stats = await r.json()
            stats["pid"] = strpersonaId['personaId']
            if strpersonaId["battlelog"]:
                stats["platformid"] = strpersonaId['platformid']
                if strpersonaId["platformName"] == "cem_ea_id":
                    stats["platformName"] = "pc"
                else:
                    stats["platformName"] = strpersonaId["platformName"]
            else:
                stats["platformName"] = "pc"
            stats["personaId"] = strpersonaId['personaId']
            stats["avatar"] = strpersonaId["avatar"]
            stats["personaName"] = strpersonaId["personaName"]
            return stats

async def getServerDataFromEa(game, method, params, platform: str = "pc"):
    """get details about a server ingame based on given method"""
    async with aiohttp.ClientSession() as session:
        code = await authSession.checkGatewaySession(game, session, platform=platform)
        ids = uuid.uuid1()
        headers = await ingame_request_headers(code[f'{game}:{platform}'])
        payload = {
                "jsonrpc":"2.0",
                "method": method,
                "params": params,
                "id":f"{ids}"
        }
        url = f"https://sparta-gw.battlelog.com/jsonrpc/{platform}/api"
        if game == "casablanca":
            url = f"https://sparta-gw-bfv.battlelog.com/jsonrpc/{platform}/api"
        async with session.post(url, data=json.dumps(payload), headers=headers) as r:
            items = await r.json()
            return items

async def getServerPrefixes(serverName):
    """for some special servers, change prefix"""
    bobPrefix = serverName[0:9]
    if "AMG" in bobPrefix:
        serverDetails = serverName.split("-")
        prefix = f'[AMG]#{int(list(filter(str.isdigit, serverName))[0])}'
    elif "epiX" in bobPrefix:
        epixPrefix = serverName[0:8].replace(" ","")
        serverDetails = serverName.split("-")
        prefix = epixPrefix + " " + serverDetails[1].strip()
    elif "Community" in bobPrefix:
        serverNumber = re.search(r'\d+', serverName).group()
        prefix = f"Operations #{serverNumber}"
    else:
        prefix = serverName[0:30]
    return prefix

async def getBattlelogServersBasedOnName(message, game):
    """gets list of servers for bf3, bf4 and bfh"""
    async with aiohttp.ClientSession() as session:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0.2) Gecko/20100101 Firefox/6.0.2',
	        'Accept': '*/*',
	        'Accept-Language': 'en-us,en;q=0.5',
	        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
	        'X-Requested-With': 'XMLHttpRequest',
	        'X-AjaxNavigation': '1'
        }
        url = f"https://battlelog.battlefield.com/{game}/servers/pc/?q={urllib.parse.quote(message)}"
        async with session.get(url, headers=headers) as r:
            items = await r.json()
            return items

async def getBf2DataFromEa(message):
    """gets stats for bf2 players"""
    # if message.lower() in ["me"]:
    #     message = await checkMe(self, ctx)
    async with aiohttp.ClientSession() as session:
        newmessage = re.escape(message).replace("_","\_")
        url = f'http://bf2web.bf2hub.com/ASP/searchforplayers.aspx?nick={newmessage}'
        async with session.get(url) as r:
            webData = await r.text()
            statsData = str(webData).split("\n")
            cols = statsData[3].split("\t")
            data = statsData[4].split("\t")
            response = dict(zip(cols, data))
            pid = str(response["pid"])
            info = 'per*,cmb*,twsc,cpcp,cacp,dfcp,kila,heal,rviv,rsup,rpar,tgte,dkas,dsab,cdsc,rank,cmsc,kick,kill,deth,suic,ospm,klpm,klpr,dtpr,bksk,wdsk,bbrs,tcdr,ban,dtpm,lbtl,osaa,vrk,tsql,tsqm,tlwf,mvks,vmks,mvn*,vmr*,fkit,fmap,fveh,fwea,wtm-,wkl-,wdt-,wac-,wkd-,vtm-,vkl-,vdt-,vkd-,vkr-,atm-,awn-,alo-,abr-,ktm-,kkl-,kdt-,kkd-'
            headers = {'User-agent': 'GameSpyHTTP/1.0'}
            url = f'http://bf2web.bf2hub.com/ASP/getplayerinfo.aspx?pid={pid}&info={info}&nocache={round(time())}'
            async with session.get(url, headers=headers) as r:
                response = await r.text()
                statsData = str(response).split("\n")
                cols = statsData[3].split("\t")
                data = statsData[4].split("\t")
                stats = dict(zip(cols, data))
                return stats

async def getDataFromBattlelog(method, message, game):
    """get stats for bf3, bf4 and bfh players"""
    async with aiohttp.ClientSession() as session:
        platformData = await platformSelect(message)
        strpersonaId = await searchName(None, platformData["new_message"], session, game, platformData["current"])
        if method == "overviewPopulateStats":
            url = f"http://battlelog.battlefield.com/{game}/overviewPopulateStats/{strpersonaId['personaId']}/None/{strpersonaId['platformid']}/"
        else:
            url = f"http://battlelog.battlefield.com/{game}/{method}/{strpersonaId['personaId']}/{strpersonaId['platformid']}/"
        headers = {
	    		'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0.2) Gecko/20100101 Firefox/6.0.2',
	    		'Accept': '*/*',
	    		'Accept-Language': 'en-us,en;q=0.5',
	    		'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
	    		'X-Requested-With': 'XMLHttpRequest',
	    		'X-AjaxNavigation': '1'}
        async with session.get(url, headers=headers) as r:
            stats = await r.json()
            stats["platformName"] = platformData['current']
            stats["platformid"] = strpersonaId['platformid']
            stats["personaId"] = stats["data"]["personaId"]
            stats["avatar"] = strpersonaId["avatar"]
            stats["personaName"] = strpersonaId["personaName"]
            return stats

async def doServerChanges(game, request, params, cookie):
    async with aiohttp.ClientSession() as session:
        code = await authSession.checkGatewaySession(game, session, cookie)
        ids = uuid.uuid1()
        url = "https://sparta-gw.battlelog.com/jsonrpc/web/api"
        headers = await ingame_request_headers(code)
        payload = {
	        "jsonrpc": "2.0",
	        "method": f"{request}",
	        "params": params,
            "id": f"{ids}"
        }
        async with session.post(url, data=json.dumps(payload), headers=headers) as r:
            items = await r.json()
            return items

async def checkBanApi(message):
    async with aiohttp.ClientSession() as session:
        db = SingletonClient.get_data_base()
        userId = await originID(session, message)
        if userId["totalCount"] == 0:
            return {"color":0xe74c3c, "title":"", "description":"Not a valid origin username", "strUserId": None, "playerId": None} # user not found
        else:
            strUserId = userId["userId"]
            playerId = userId["strpersonaId"]
        playerInfo = await db.globalIngameBans.find_one({'_id': str(playerId)})
        if playerInfo is not None:
            servers = ""
            for item in playerInfo["servers"]:
                servers += f'{item}\n'
            return {"color":0xFFA500, "title": f"{playerInfo['displayName']} is banned in:", "description":servers, "strUserId": strUserId, "playerId": playerId}
        else:
            return {"color":0xe74c3c, "title": "", "description":f"{message} isn't in global banlist of manager", "strUserId": strUserId, "playerId": playerId}

async def getMostRecentSession(ctx, playerName):
    db = SingletonClient.get_data_base()
    async with aiohttp.ClientSession() as session:
        strpersonaId = await searchName(None, playerName, session, "tunguska")
    recentStats = []
    i = 1
    async for document in db.playerDiffStats.find({'playerId': int(strpersonaId['personaId'])}, sort=[( 'timeStamp', pymongo.DESCENDING )]):
        recentStats.append(document)
        if i == 5:
            break
        i+=1
    # embed=discord.Embed(color=0xFFA500, title=f"{strpersonaId['personaName']}\'s most recent playsessions")

    # add current stats when the player is still ingame
    try:
        join = await db.playerJoinStats.fine_one({'playerId': int(strpersonaId['personaId'])}, sort=[( 'timeStamp', pymongo.DESCENDING )])
        mostRecentPlayerupdate = await db.playerList.find_one({'_id': int(strpersonaId['personaId'])})
        if len(recentStats) != 0:
            runStats = recentStats[0]["timeStamp"] < mostRecentPlayerupdate["timeStamp"] and join["timeStamp"] < mostRecentPlayerupdate["timeStamp"]
        elif join is None or mostRecentPlayerupdate is None:
            runStats = False
        else:
            runStats = join["timeStamp"] < mostRecentPlayerupdate["timeStamp"]
        joinStats = join["stats"]
        if runStats:
            detailedStats = (await getDataFromEa(ctx, playerName, "Stats.detailedStatsByPersonaId", "tunguska"))
            statsList = [{
                "Wins": int(detailedStats["result"]["basicStats"]["wins"] - joinStats["wins"]),
                "Losses": int(detailedStats["result"]["basicStats"]["losses"] - joinStats["losses"]),
                "Kills": int(detailedStats["result"]["basicStats"]["kills"] - joinStats["kills"]),
                "Deaths": int(detailedStats["result"]["basicStats"]["deaths"] - joinStats["deaths"]),
                "Time played": int(detailedStats["result"]["basicStats"]["timePlayed"] - joinStats["timePlayed"]),
            }]
            
            kits = {}
            for kit in joinStats["kits"]:
                kits[kit["name"]] = kit
            for newKit in detailedStats["result"]["kitStats"]:
                kits[newKit["name"]]["score"] = int(newKit["score"] - kits[newKit["name"]]["score"])
                kits[newKit["name"]]["kills"] = int(newKit["kills"] - kits[newKit["name"]]["kills"])
                kits[newKit["name"]]["timePlayed"] = datetime.timedelta(seconds=newKit["secondsAs"] - kits[newKit["name"]]["timePlayed"])
            kits = list(kits.values())

            gamemodes = {}
            for gamemode in joinStats["gamemodes"]:
                gamemodes[gamemode["name"]] = gamemode
            for newGamemode in detailedStats["result"]["gameModeStats"]:
                gamemodes[newGamemode["name"]]["score"] = int(newGamemode["score"] - gamemodes[newGamemode["name"]]["score"])
                gamemodes[newGamemode["name"]]["wins"] = int(newGamemode["wins"] - gamemodes[newGamemode["name"]]["wins"])
                gamemodes[newGamemode["name"]]["losses"] = int(newGamemode["losses"] - gamemodes[newGamemode["name"]]["losses"])
            gamemodes = list(gamemodes.values())
            
            gamemodeList = [constants.GAMEMODES[d["name"]] for d in gamemodes if d['score'] != 0]

            kitList = [d.values() for d in kits if d['timePlayed'] != datetime.timedelta(seconds=0)]
            if statsList[0]["Time played"] != 0:
                statsStr = f"""
                    ```{tabulate(statsList, headers="keys")}
                    \n{tabulate(kitList, ["Classes", "Score", "Kills", "Time played as"])}
                    \n(servername not shown for privacy) - {"/".join(gamemodeList)}```
                """
                embed.add_field(name="current KD ingame", value=statsStr, inline=False)
    except Exception as e:
        print(e)
        pass
    i = 1
    for info in recentStats:
        stats = info["stats"]
        serverInfo = await db.communityPlayers.find_one({"_id": info["serverId"]})
        for item in stats["kits"]:
            item["timePlayed"] = datetime.timedelta(seconds=item["timePlayed"])
        kitList = [d.values() for d in stats["kits"] if d['timePlayed'] != datetime.timedelta(seconds=0)]
        gamemodeList = [constants.GAMEMODES[d["name"]] for d in stats["gamemodes"] if d['score'] != 0]

        statsList =  [{
            "Wins": stats['wins'],
            "Losses": stats['losses'],
            "Kills": stats['kills'],
            "Deaths": stats['deaths'],
            "Time played": datetime.timedelta(seconds=stats['timePlayed'])
        }]
        statsStr = f"""
            ```{tabulate(statsList, headers="keys")}
            \n{tabulate(kitList, ["Classes", "Score", "Kills", "Time played as"])}
            \n({info["timeStamp"].strftime("%d-%m-%Y - %H:%M")}) - {"/".join(gamemodeList)}```
        """
        embed.add_field(name=serverInfo["info"]["prefix"], value=statsStr, inline=False)
        i+=1
    if len(recentStats) == 0 and runStats == False:
        embed.add_field(name="Play more rounds before trying again", value="It only tracks the session within this week", inline=False)
    embed.set_footer(text="(Only works on servers using our manager)")
    await ctx.send(embed=embed)

async def platoonCheck(playerName):
    try:
        stats = await getDataFromEa(playerName, "Platoons.getActivePlatoon", "tunguska")
        if stats.get("result"):
            return f'[{stats["result"]["name"]}](https://gametools.network/platoons/{stats["result"]["guid"]})'
        else: 
            return "player isn't in any platoon"
    except Exception as e:
        return "player not found"