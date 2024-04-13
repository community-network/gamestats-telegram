# default bf1 api stuff
import aiohttp
import json
import re

from pymongo.collation import Collation

from ..api import constants
from .authSession import checkGatewaySession
from .redisDB import get_routes_from_cache, set_routes_to_cache
import requests
from ..mongo import SingletonClient

access_token = ""

async def getAccessToken():
    global access_token
    headers = {"Cookie": f"sid={constants.COOKIE['sid']}; remid={constants.COOKIE['remid']};"}
    x = requests.get("https://accounts.ea.com/connect/auth?client_id=ORIGIN_JS_SDK&response_type=token&redirect_uri=nucleus:rest&prompt=none&release_type=prod", headers=headers)
    jsonaccess_token = x.json()["access_token"]
    access_token = str(jsonaccess_token)
    
async def bfTrackerPlatformSelect(message):
    oldmessage = message.split()
    current = "origin"
    platforms = ["pc", "origin", "ps4", "psn", "xbox", "xbl", "one"]
    for platform in platforms:
        if platform in oldmessage:
            if platform == "pc":
                current = "origin"
            elif platform == "ps4" or platform == "psn":
                current = "psn"
            elif platform == "xbox" or platform == "xbl" or platform == "one":
                current = "xbl"
            else:
                current = platform
    new_message = [string for string in oldmessage if string not in platforms]
    # if new_message[0].lower() in ["me"]:
    #     new_message = [await checkMe(self, ctx)]
    return {"current": current, "new_message": new_message}

async def platformSelect(message):
    """if platform is filled in, find platform. otherwise use default: origin (pc)"""
    oldmessage = message.split()
    current = "cem_ea_id"
    platformid = 1
    platforms = ["pc", "origin", "ps4", "psn", "playstation", "ps", "ps3", "xboxone", "xbl", "one", "xbox", "360", "xbox360"]
    for platform in platforms:
        if platform in oldmessage:
            if platform.lower() in ["pc", "origin"]:
                current = "cem_ea_id"
                platformid = 1
            elif platform.lower() in ["ps4", "psn", "playstation", "ps"]:
                current = "ps4"
                platformid = 32
            elif platform.lower() in ["ps3"]:
                current = "ps3"
                platformid = 4
            elif platform.lower() in ["xboxone", "xbl", "one", "xbox"]:
                current = "xboxone"
                platformid = 64
            elif platform.lower() in ["360", "xbox360"]:
                current = "xbox360"
                platformid = 2
            else:
                current = platform
                platformid = 1
    new_message = [string for string in oldmessage if string not in platforms]

    return {"current": current, "new_message": ' '.join(map(str, new_message)), "platformid": platformid}

async def originID(session, message):
    """get origin id"""
    db = SingletonClient.get_data_base()
    playerInfo = await db.playerList.find_one({'playerName': message}, collation=Collation(locale='en', strength=2, alternate="shifted"))
    if playerInfo is not None:
        if playerInfo["userId"] is not None:
            return {"totalCount": 1, "userId": str(playerInfo["userId"]), "strpersonaId": str(playerInfo["_id"])}
    
    global access_token
    url = f"https://api4.origin.com/xsearch/users?userId=2800753812&searchTerm={message}&start=0"
    headers = {"authtoken": f"{access_token}"}
    userId = {}
    try:
        async with session.get(url, headers=headers) as r:
            userIdGet = await r.json()
            userId["totalCount"] = userIdGet["totalCount"]
            userId["userId"] = userIdGet["infoList"][0]["friendUserId"]
            url = f"https://api2.origin.com/atom/users?userIds={userId['userId']}"
            async with session.get(url, headers=headers) as r:
                personaId = await r.text()
                regexPersonaId = r'(?<=\<personaId>).+?(?=\</personaId>)'
                userId["strpersonaId"] = re.findall(regexPersonaId, personaId)[0]
    except:
        playerInfo =  await getPlayerFromProxy(message)
        return {"totalCount": 1, "userId": str(playerInfo["originId"]), "strpersonaId": str(playerInfo["personaId"])}
    return userId

async def eaDesktopSearch(name):
    async with aiohttp.ClientSession() as session:
        db = SingletonClient.get_data_base()
        accessToken = await db.globals.find_one({"_id": "deskopToken"})
        url = "https://service-aggregation-layer.juno.ea.com/graphql"
        headers = {
            "Host": "service-aggregation-layer.juno.ea.com",
            "accept": "*/*",
            "authorization": "Bearer " + accessToken["key"],
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) QtWebEngine/5.15.2 Chrome/83.0.4103.122 Safari/537.36",
            "content-type": "application/json", "Origin": "https://pc.ea.com", "Referer": "https://pc.ea.com/zh-hans",
            "Accept-Encoding": "gzip, deflate, br"}

        payload = {"operationName": "SearchPlayer",
             "variables": {"searchText": name, "pageNumber": 1, "pageSize": 20, "locale": "zh-hans"},
             "extensions": {"persistedQuery": {"version": 1,
                                               "sha256Hash": "83da6f3045ee524f6cb62a1c23eea908c9432f15e87b30dd33b89974ff83c657"}},
             "query": "query SearchPlayer($searchText: String!, $pageNumber: Int!, $pageSize: Int!) {\n  players(searchText: $searchText, paging: {pageNumber: $pageNumber, pageSize: $pageSize}) {\n    items {\n      ...PlayerWithMutualFriendsCount\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment PlayerWithMutualFriendsCount on Player {\n  ...Player\n  mutualFriends {\n    totalCount\n    __typename\n  }\n  __typename\n}\n\nfragment Player on Player {\n  id: pd\n  pd\n  psd\n  displayName\n  uniqueName\n  nickname\n  avatar {\n    ...Avatar\n    __typename\n  }\n  relationship\n  __typename\n}\n\nfragment Avatar on AvatarList {\n  large {\n    ...image\n    __typename\n  }\n  medium {\n    ...image\n    __typename\n  }\n  small {\n    ...image\n    __typename\n  }\n  __typename\n}\n\nfragment image on Image {\n  height\n  width\n  path\n  __typename\n}\n"}
        
        async with session.post(url=url, headers=headers, data=json.dumps(payload)) as r:
            result = await r.json()
            player = result["data"]["players"]["items"][0]
        return {
                    "personaId": player["psd"],
                    "personaName": player["displayName"],
                    "avatar": player["avatar"]["large"]["path"],
                    "battlelog": False
                }

async def searchNameBattlelog(player_name: str, game: str, platform: str):
    async with aiohttp.ClientSession() as session:
        # Get Battlelog platform id, defaulting to pc (1)
        platform_id = constants.BATTLELOG_PLATFORM_NUMBERS.get(platform, 1)
        # Get Battlelog game id (bfh: 8192, bf4: 2048, bf3: 2)
        game_id = constants.BATTLELOG_GAME_NUMBERS.get(game)
        payload = aiohttp.FormData()
        payload.add_field("query", player_name)
        url = "https://battlelog.battlefield.com/search/query/"
        async with session.post(url, data=payload) as r:
            results = await r.json()
            if game not in ["tunguska", "casablanca"]:
                for persona in results["data"]:
                    """
                    Return persona which matches name exactly and owns current game on current platform, which is determined
                    based on Battlelog's enumeration flags using bitwise AND.
                    If a player owns only BF3, BF4 and BFH, on PC, their "games" attribute will be dict equal to: 
                    {'1': '10242'} with '1' being the platform id (1 for pc) and 10242 being the sum of the game ids:
                    2 (bf3) + 2048 (bf4) + 8192 (bfh). Using that, we can check if a player owns bf4 by checking if the game
                    id sum contains bf4's id like so: 10242 & 2048 (which is 2048) == 2048
                    """
                    if persona["personaName"].lower() == player_name.lower() and str(platform_id) in persona["games"] and \
                            int(persona["games"][str(platform_id)]) & game_id == game_id:
                        return {
                            "personaId": persona["personaId"],
                            "personaName": persona["personaName"],
                            "platformid": platform_id,
                            "platformName": platform,
                            "avatar": f'https://secure.gravatar.com/avatar/{persona["user"]["gravatarMd5"]}?'
                                      f's=204&d=https://eaassets-a.akamaihd.net/battlelog/defaultavatars/default-avatar-36.png',
                            "battlelog": True
                        }
            else:
                for persona in results["data"]:
                    if "cem_ea_id" in persona["namespace"] and persona["personaName"].lower() == player_name.lower():
                        return {
                            "personaId": persona["personaId"],
                            "personaName": persona["personaName"],
                            "platformid": platform_id,
                            "platformName": platform,
                            "avatar": f'https://secure.gravatar.com/avatar/{persona["user"]["gravatarMd5"]}?'
                                      f's=204&d=https://eaassets-a.akamaihd.net/battlelog/defaultavatars/default-avatar-36.png',
                            "battlelog": True
                        }

async def getFromDb(message):
    try:
        db = SingletonClient.get_data_base()
        playerInfo = await db.playerList.find_one({'playerName': message}, collation=Collation(locale='en', strength=2, alternate="shifted"))
        if playerInfo is not None:
            if playerInfo["userId"] is not None:
                try:
                    async with aiohttp.ClientSession() as session:
                        global access_token
                        headers = {"authtoken": f"{access_token}"}
                        url = f"https://api3.origin.com/avatar/user/{playerInfo['userId']}/avatars?size=1"
                        async with session.get(url=url, headers={'Accept': 'application/json', **headers}) as r:
                            avatarJson = await r.json()
                            avatar = avatarJson['users'][0]['avatar']['link']
                except Exception as e:
                    print(f"getFromDb: {e}")
                    return None # if failed to get avatar
            else:
                return None
            return {
                "personaId": playerInfo["_id"],
                "personaName": playerInfo["playerName"],
                "platformid": 1,
                "avatar": avatar,
                "battlelog": False
            }
    except:
        return None

async def getPlayerFromProxy(message):
    try:
        async with aiohttp.ClientSession() as session:
            global access_token
            url = f"https://gateway.ea.com/proxy/identity/personas?displayName={message}&namespaceName=cem_ea_id"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
                "Accept": "application/vnd.origin.v3+json; x-cache/force-write",
                "Accept-Encoding": "gzip, deflate, br",
                "X-ZuluTime-Format": "true",
                "Origin": "https://www.origin.com",
                "Referer": "https://www.origin.com/",
                'X-Expand-Results': 'true',
                "Authorization": f"Bearer {access_token}",
            }
            async with session.get(url=url, headers=headers) as r:
                playerInfo = await r.json()
                user = playerInfo["personas"]["persona"][0]
                try:
                    headers = {"authtoken": f"{access_token}"}
                    url = f"https://api3.origin.com/avatar/user/{user['pidId']}/avatars?size=1"
                    async with session.get(url=url, headers={'Accept': 'application/json', **headers}) as r:
                        avatarJson = await r.json()
                        return {
                            "personaName": user["displayName"],
                            "originId": user["pidId"],
                            "personaId": user["personaId"],
                            "avatar": avatarJson['users'][0]['avatar']['link'],
                            "battlelog": False,
                            "platformid": 1
                        }
                except Exception as e:
                    print(f"getAvatarSeachPlayer: {e}")
                    return {
                        "personaName": user["displayName"],
                        "originId": user["pidId"],
                        "personaId": user["personaId"],
                        "avatar": "https://eaassets-a.akamaihd.net/battlelog/defaultavatars/default-avatar-36.png",
                        "battlelog": False,
                        "platformid": 1
                    }
    except:
        return None
     
async def searchName(originId, name, session, game, platform="pc"):
    # if name.lower() in ["me"]:
    #     name = await checkMe(self, ctx)
    data = await get_routes_from_cache(key=f'names:{originId}:{name}:{game}:{platform}')
    await checkGatewaySession(game, session)
    if data is not None:
        strpersonaId = json.loads(data)
        return strpersonaId
    else:
        global access_token
        # If game is a sparta game (BF1, BFV), try searching via Origin API 
        userId = {}
        headers = {"authtoken": f"{access_token}"}
        if platform == "pc" and originId is None:  
            try:
                url = f"https://api1.origin.com/xsearch/users?userId=2800753812&searchTerm={name}&start=0"
                async with session.get(url, headers=headers) as r:
                    userId = await r.json()
            except:
                pass
        # If player was not found (or no search was attempted because game is not a sparta game), search via Battlelog
        if userId.get("totalCount", 0) == 0 and originId is None:
            try:
                strpersonaId = await searchNameBattlelog(name, game, platform)
            except Exception as e:
                strpersonaId = None
            if strpersonaId is None and game == "tunguska" and platform == "pc":
                strpersonaId = await getFromDb(name)
            if strpersonaId is None and game in constants.SPARTA_GAMES:
                strpersonaId = await getPlayerFromProxy(name)
            if strpersonaId is None and game in constants.SPARTA_GAMES:
                strpersonaId = await eaDesktopSearch(name)
            data = json.dumps(strpersonaId)
            await set_routes_to_cache(key=f'names:{originId}:{name}:{game}:{platform}', value=data, ttl=604800) #1 week
            return strpersonaId
        else:
            # get personaId based on userId
            if originId is None:
                strUserId = userId["infoList"][0]["friendUserId"]
            else:
                strUserId = originId
            strpersonaId = {"personaId": None}
            url = f"https://api2.origin.com/atom/users?userIds={strUserId}"
            async with session.get(url, headers={'Accept': 'application/json', **headers}) as r:
                userJson = await r.json()
                strpersonaId = {
                    'personaId': userJson['users'][0]['personaId'],
                    'personaName': userJson['users'][0]['eaId']
                }
            # get user avatar
            url = f"https://api3.origin.com/avatar/user/{strUserId}/avatars?size=1"
            async with session.get(url=url, headers={'Accept': 'application/json', **headers}) as r:
                avatarJson = await r.json()
                strpersonaId["avatar"] = avatarJson['users'][0]['avatar']['link']
            strpersonaId["battlelog"] = False
            data = json.dumps(strpersonaId)
            await set_routes_to_cache(key=f'names:{originId}:{name}:{game}:{platform}', value=data, ttl=604800) #1 week
            return strpersonaId

async def checkMe(self, ctx):
    playerInfo = await self.bot.stickyPlayerName.find(ctx.author.id)
    if playerInfo is not None:
        return playerInfo["name"]
    else:
        await ctx.send("You haven't setup the \"me\" option (!bfsetme playername), trying with your nickname in this server..")
        return re.sub(r'\[[^)]*\]', '', ctx.author.display_name)