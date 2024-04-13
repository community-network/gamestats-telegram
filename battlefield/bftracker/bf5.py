
from ..imageStats.main import imageStats
from ..api.searchPlayer import bfTrackerPlatformSelect
import urllib.parse
import aiohttp
from aiogram import types
from ..commands import grapher

async def bf5stat(message: types.Message):
    try:            
        result = await bfTrackerPlatformSelect(message.text)
        async with aiohttp.ClientSession() as session:
            gameUrl = f"https://battlefieldtracker.com/bfv/profile/{result['current']}/{urllib.parse.quote(' '.join(result['new_message']))}/overview"
            url = f"https://api.tracker.gg/api/v2/bfv/standard/profile/{result['current']}/{urllib.parse.quote(' '.join(result['new_message']))}"
            async with session.get(url) as r:
                stats = await r.json()
                mainStats = stats["data"]["segments"][0]["stats"]
                try:
                    headshotPercent = str(round((mainStats["headshots"]["value"]/mainStats["kills"]["value"])*100,2))+"%"
                except: 
                    headshotPercent = "0%"
                stats = {
                    "onlyName": stats["data"]["platformInfo"]["platformUserHandle"],
                    "name": stats["data"]["platformInfo"]["platformUserHandle"],
                    "avatar": stats["data"]["platformInfo"]["avatarUrl"],
                    "rank": mainStats["rank"]["displayValue"],
                    "rankImg": mainStats["rank"]["metadata"]["imageUrl"],
                    "0.0": mainStats["killsPerMinute"]["displayValue"],
                    "0.1": mainStats["scorePerMinute"]["displayValue"],
                    "0.2": mainStats["saviorKills"]["displayValue"],
                    "0.3": mainStats["kdRatio"]["displayValue"],
                    "0.4": mainStats["longestHeadshot"]["displayValue"],
                    "1.0": mainStats["wlPercentage"]["displayValue"],
                    "1.1": headshotPercent,
                    "1.2": mainStats["shotsAccuracy"]["displayValue"],
                    "1.3": mainStats["assists"]["displayValue"],
                    "1.4": mainStats["killStreak"]["displayValue"],
                    "2.0": mainStats["revives"]["displayValue"],
                    "2.1": mainStats["repairs"]["displayValue"],
                    "2.2": mainStats["resupplies"]["displayValue"],
                    "2.3": mainStats["timePlayed"]["displayValue"],
                }
                await imageStats.imageRender(message, stats, gameUrl, "bfv", result['current'])
    except:
        await message.reply("player not found")

async def bf5weapongraph(message: types.Message):
    try:
        result = await bfTrackerPlatformSelect(message.text)
        async with aiohttp.ClientSession() as session:
            url = f"http://api.tracker.gg/api/v1/bfv/profile/{result['current']}/{urllib.parse.quote(' '.join(result['new_message']))}/weapons"
            async with session.get(url) as r:
                stats = await r.json()
                weapons = []
                for weapon in stats["data"]["children"]:
                    weapons.append({"name": weapon["metadata"]["name"], "kills": weapon["stats"][0]["value"]})
                graphing = sorted(weapons, key=lambda k: k['kills'], reverse=True) 
                await grapher.main(message, graphing, stats, "bf5", "weapons")
    except:
        await message.reply("player not found")

async def bf5vehiclegraph(message: types.Message):
    try:
        result = await bfTrackerPlatformSelect(message.text)
        async with aiohttp.ClientSession() as session:
            url = f"http://api.tracker.gg/api/v1/bfv/profile/{result['current']}/{urllib.parse.quote(' '.join(result['new_message']))}/vehicles"
            async with session.get(url) as r:
                stats = await r.json()
                vehicles = []
                for vehicle in stats["data"]["children"]:
                    vehicles.append({"name": vehicle["metadata"]["name"], "kills": vehicle["stats"][0]["value"]})
                graphing = sorted(vehicles, key=lambda k: k['kills'], reverse=True) 
                await grapher.main(message, graphing, stats, "bf5", "vehicles")
    except:
        await message.reply("player not found")
