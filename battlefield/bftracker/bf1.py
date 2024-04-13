import aiohttp
from lxml import html
import re
from ..imageStats.main import imageStats
import urllib.parse
from aiogram import types
from ..commands import grapher

async def bf1TrackerPlatformSelect(message: str):
    oldmessage = message.split()
    current = "pc"
    platforms = ["pc", "origin", "ps4", "psn", "xbox", "xbl", "one"]
    for platform in platforms:
        if platform in oldmessage:
            if platform == "pc":
                current = "pc"
            elif platform == "ps4" or platform == "psn":
                current = "psn"
            elif platform == "xbox" or platform == "xbl" or platform == "one":
                current = "xbox"
            else:
                current = platform
    new_message = [string for string in oldmessage if string not in platforms]
    return {"current": current, "new_message": str(' '.join(new_message))}

async def top10WeaponGraph(message, result):
    """returns top weapons for bf1 graph"""
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://battlefieldtracker.com/bf1/profile/{result['current']}/{urllib.parse.quote(result['new_message'])}/weapons"
            async with session.get(url=url) as r:
                tree = html.fromstring(await r.text())
        graphing = []
        i = 1
        while i != 20:
            try:
                weaponName = tree.xpath(f'/html/body/div[1]/div[1]/div[3]/div/div[2]/div[4]/table/tbody/tr[{i}]/td[1]/div[1]/text()')[0].strip()
                kills = int(''.join(filter(str.isdigit, tree.xpath(f'/html/body/div[1]/div[1]/div[3]/div/div[2]/div[4]/table/tbody/tr[{i}]/td[2]/div[1]/text()')[0].strip())))
                try:
                    graphing.append({"name": weaponName, "kills": int(kills)})
                    i+=1
                except:
                    pass
            except:
                break
        stats = {"platformid": result['current']}
        await grapher.main(message, graphing, stats, "bf1", "weapons")
    except:
        await message.reply("player not found")

async def top10VehicleGraph(message, result):
    """returns top weapons for bf1"""
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://battlefieldtracker.com/bf1/profile/{result['current']}/{urllib.parse.quote(result['new_message'])}/vehicles"
            async with session.get(url=url) as r:
                tree = html.fromstring(await r.text())
        graphing = []
        i = 1
        while i != 20:
            try:
                weaponName = tree.xpath(f'/html/body/div[1]/div[1]/div[3]/div/div[1]/div[3]/table/tbody/tr[{i}]/td[1]/div/text()')[0].strip()
                kills = tree.xpath(f'/html/body/div[1]/div[1]/div[3]/div/div[1]/div[3]/table/tbody/tr[{i}]/td[2]/div[1]/text()')[0].strip()
                try:
                    graphing.append({"name": weaponName, "kills": int(kills)})
                    i+=1
                except:
                    pass
            except:
                break
        stats = {"platformid": result['current']}
        await grapher.main(message, graphing, stats, "bf1", "vehicles")
    except:
        await message.reply("player not found")


async def bf1Tracker(message: types.Message, result):
    """returns stats for bf4 and bf1"""
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://battlefieldtracker.com/bf1/profile/{result['current']}/{urllib.parse.quote(result['new_message'])}"
            async with session.get(url=url) as r:
                tree = html.fromstring(await r.text())
        stats = {
            "onlyName": str('%20'.join(result['new_message'])),
            "name": str(result['new_message']),
            "avatar": "https://eaassets-a.akamaihd.net/battlelog/defaultavatars/default-avatar-204.png?ssl=1",
            "rank": re.findall(r'\d+',tree.xpath('/html/body/div[1]/div[1]/div[3]/div[1]/div[1]/div/span/text()')[0])[0],
            "rankImg": "https://battlefieldtracker.com" + tree.xpath('/html/body/div[1]/div[1]/div[3]/div[1]/div[1]/img/@src')[0],
            "0.0": tree.xpath('/html/body/div[1]/div[1]/div[3]/div[2]/div[1]/div[2]/div/div[8]/div[2]/text()')[0].strip(),
            "0.1": tree.xpath('/html/body/div[1]/div[1]/div[3]/div[2]/div[1]/div[2]/div/div[3]/div[2]/text()')[0].strip(),
            "0.2": tree.xpath('/html/body/div[1]/div[1]/div[3]/div[2]/div[1]/div[6]/div/div[6]/div[2]/text()')[0].strip(),
            "0.3": tree.xpath('/html/body/div[1]/div[1]/div[3]/div[2]/div[1]/div[2]/div/div[5]/div[2]/text()')[0].strip(),
            "0.4": tree.xpath('/html/body/div[1]/div[1]/div[3]/div[2]/div[1]/div[16]/div/div[7]/div[2]/text()')[0].strip(),
            "1.0": tree.xpath('/html/body/div[1]/div[1]/div[3]/div[1]/div[2]/div[1]/div[3]/div[2]/text()')[0].strip(),
            "1.1": tree.xpath('/html/body/div[1]/div[1]/div[3]/div[2]/div[1]/div[16]/div/div[5]/div[2]/text()')[0].strip(),
            "1.2": tree.xpath('/html/body/div[1]/div[1]/div[3]/div[2]/div[1]/div[6]/div/div[7]/div[2]/text()')[0].strip(),
            "1.3": tree.xpath('/html/body/div[1]/div[1]/div[3]/div[2]/div[1]/div[2]/div/div[10]/div[2]/text()')[0].strip(),
            "1.4": tree.xpath('/html/body/div[1]/div[1]/div[3]/div[2]/div[1]/div[16]/div/div[6]/div[2]/text()')[0].strip(),
            "2.0": tree.xpath('/html/body/div[1]/div[1]/div[3]/div[2]/div[1]/div[12]/div/div[6]/div[2]/text()')[0].strip(),
            "2.1": tree.xpath('/html/body/div[1]/div[1]/div[3]/div[2]/div[1]/div[10]/div/div[1]/div[2]/text()')[0].strip(),
            "2.2": tree.xpath('/html/body/div[1]/div[1]/div[3]/div[2]/div[1]/div[10]/div/div[2]/div[2]/text()')[0].strip(),
            "2.3": tree.xpath('/html/body/div[1]/div[1]/div[3]/div[2]/div[1]/div[2]/div/div[9]/div[2]/text()')[0].strip()
        }
        await imageStats.imageRender(message, stats, url, "bf1", result['current'])
    except:
        await message.reply("player not found or no playername given, usage:\n /bf1stat (platform) name")