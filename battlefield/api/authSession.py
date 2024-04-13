import uuid
import urllib
import json

from . import constants

code = {}

async def checkGatewaySession(game, session, cookie: str = None, platform: str = "pc"):
    """check if X-GatewaySession is valid for bf5"""
    custom = False
    ids = uuid.uuid1()
    global code
    if game == "casablanca":
        gameUrl = f"https://sparta-gw-bfv.battlelog.com/jsonrpc/{platform}/api"
    else:
        gameUrl = f"https://sparta-gw.battlelog.com/jsonrpc/{platform}/api"
    payload = {
            "jsonrpc":"2.0",
            "method":"Stats.detailedStatsByPersonaId",
            "params":{"personaId": "794397421", "game": game},
            "id":f"{ids}"
    }
    # check if still valid
    if code.get(f'{game}:{platform}', None) is not None and cookie is None:
        headers = {
            "content-type": "application/json",
            "X-GatewaySession": f"{code[f'{game}:{platform}']}",
            "X-ClientVersion": "companion-4569f32f"
        }
        async with session.post(url=gameUrl, headers=headers, data=json.dumps(payload)) as r:
            result = await r.json()
    else:
        result = "error"
    if cookie is not None:
        custom = True
    else:
        # set cookie after cookie check
        cookie = constants.COOKIE
    if "error" in result:
        # get new one if fails
        if platform == "xboxone":
            authPlatform = "xone"
        else:
            authPlatform = platform
        url = f"https://accounts.ea.com/connect/auth?client_id=sparta-backend-as-user-{authPlatform}&response_type=code&release_type=none"
        headers = {
            "User-Agent": "Mozilla/5.0 EA Download Manager Origin/10.5.89.45622",
            "X-Origin-Platform": "PCWIN",
            "Cookie": f"sid={constants.COOKIE['sid']}; remid={constants.COOKIE['remid']}; _ga=GA1.2.1989678628.1594206869; _nx_mpcid=c002360c-1ab0-4ce2-83d8-9a850d649e13; ealocale=nl-nl; ak_bmsc=E1AB16946A53CE2E1495B6BBF258CB7758DDA1073361000061E5405FB2BC7035~pl1h1xXQwIfdbF9zU3hMOujtpJ70BXJaFRqFWYPsE32q4qwE4onR+N6sn+T0KrqdpyZaf2ir3u+Xh68W3cEjOb+VLrQvI0jwTr1GFp5bgZXU812telOSjDjYPK3ddYJ7kOfbHtEglOs9UhdzOFi+UIWIAFdwcNq5ZoPv9Z0i53SspWuI4W3POlFqX70LxwwXcLMTQZgnGVs8R98goScJjo0Oo4D/+8LLzJsJfIUpr4AcgSC5B/ks2m5yz8ft9nh+9w; bm_sv=0B8CB6864011B573F81CA53CE1A570AD~qrTfU4mNBNCod1jfAFpeU+tG5OJ7w4r7lIg/ezmX6RLIIemuAT6EnFMcuhkUGHhJQSwjeV1kpadZtdXJAlbDoPxAafNmbaeQC/hteaiVlTMVV7R6gKPT8kWM22cFv6Y3Axp/S5XFhd6/Aw4cH6+Bng==; notice_behavior=implied,eu; _gid=GA1.2.827595775.1598088932; _gat=1",
            "Host": "accounts.ea.com"
            }
        async with session.get(url=url, headers=headers, allow_redirects=False) as r:
            redirect = r.headers["Location"]
            access_code = urllib.parse.urlparse(redirect).query.split("=")[1]
            headers = {
                "User-Agent": "ProtoHttp 1.3/DS 15.1.2.1.0 (Windows)",
                "X-Guest": "no-session-id",
                "X-ClientVersion": "release-bf1-lsu35_26385_ad7bf56a_tunguska_all_prod",
                "X-DbId": "Tunguska.Shipping2PC.Win32",
	            "X-CodeCL": "3779779",
	            "X-DataCL": "3779779",
	            "X-SaveGameVersion": "26",
	            "X-HostingGameId": "tunguska",
	            "X-Sparta-Info": "tenancyRootEnv=unknown; tenancyBlazeEnv=unknown",
                }
            payload = {
	            "jsonrpc": "2.0",
	            "method": "Authentication.getEnvIdViaAuthCode",
	            "params": {
	            	"authCode": f"{access_code}",
	            	"product": None,
	            	"dtab": None,
	            	"locale": "en-us",
	            	"branchName": "Tunguska",
	            	"changeListNumber": "3779779",
	            	"minutesToUTC": "60"
	                },
	            "id": f"{ids}"
	            }
            async with session.post(url=gameUrl, headers=headers, data=json.dumps(payload)) as r:
                result = await r.json()
                if custom:
                    return result["result"]["sessionId"]
                code[f'{game}:{platform}'] = result["result"]["sessionId"]
                return code
    else:
        return code