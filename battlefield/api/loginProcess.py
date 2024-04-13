import asyncio
import re
import aiohttp
import urllib.parse
import random
import string

# main
async def requestCookie(email: str, passw: str):
    async with aiohttp.ClientSession() as session:
        fid = await requestFid(session)
        jSessionId, signInCookie, location = await requestJsSessionID(session, fid)
        secondFid = await requestSecondFid(session, jSessionId, signInCookie, location, email, passw)
        return await requestCookieAuth(session, secondFid)

async def requestFid(session: aiohttp.ClientSession):
    data = await session.get("https://accounts.ea.com:443/connect/auth?display=originXWeb%2Flogin&response_type=code&release_type=prod&redirect_uri=https%3A%2F%2Fwww.origin.com%2Fviews%2Flogin.html&locale=zh_TW&client_id=ORIGIN_SPA_ID", allow_redirects=False)
    redirect = data.headers["Location"]
    return redirect.split("=")[1]
    
async def requestJsSessionID(session: aiohttp.ClientSession, fid: str):
    data = await session.get(f"https://signin.ea.com/p/originX/login?fid={fid}", allow_redirects=False)
    location = data.headers["Location"]
    i = 0
    jSessionId = ""
    signInCookie = ""
    for name, data in data.headers.items():
        if name == "Set-Cookie":
            if i == 0:
                jSessionId = re.search(r'=.+?;', data)[0].strip('=').strip(";")
                i += 1
            else:
                signInCookie = re.search(r'\".+\"', data)[0].strip('"')
    return jSessionId, signInCookie, location
 
async def random_char(y):
       return ''.join(random.choice(string.ascii_letters) for x in range(y))
    
async def requestSecondFid(session: aiohttp.ClientSession, jSessionId: str, signInCookie: str, location: str, email: str, passw: str):
    random = await random_char(5)
    data = await session.post(
        url = f"https://signin.ea.com{location}",
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
	        "Referer": f"https://signin.ea.com{location}",
	        "cookie": f"JSESSIONID={jSessionId};",
	        "cookie": f"signin-cookie={signInCookie}"
        },
        data = f"email={urllib.parse.quote(email)}&password={passw}&_eventId=submit&cid={random*42}&showAgeUp=true&thirdPartyCaptchaResponse=&_rememberMe=on&rememberMe=on"
    )
    html = await data.text()
    htmlPart = re.search(r"window\.location(.+?)\n", html)[0]
    redirect =  re.search(r"\"(.+?)\"", htmlPart)[0]
    return redirect.split("=")[-1]
    
async def requestCookieAuth(session: aiohttp.ClientSession, secondFid: str):
    data = await session.get(f"https://accounts.ea.com:443/connect/auth?display=originXWeb%2Flogin&response_type=code&release_type=prod&redirect_uri=https%3A%2F%2Fwww.origin.com%2Fviews%2Flogin.html&locale=zh_TW&client_id=ORIGIN_SPA_ID&fid={secondFid}", allow_redirects=False)
    redirect = data.headers["Location"]
    i = 0
    sid = ""
    remid = ""
    for name, data in data.headers.items():
        if name == "Set-Cookie":
            if i == 0:
                sid = re.search(r'=.+?;', data)[0].strip('=').strip(";")
                i += 1
            else:
                remid = re.search(r'=.+?;', data)[0].strip('=').strip(";")
    access_code = urllib.parse.urlparse(redirect).query.split("=")[1]
    return sid, remid, access_code