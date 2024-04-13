import os
import io
from PIL import Image, ImageFont, ImageDraw, ImageChops
import aiohttp
from aiogram import types
import cairosvg


class imageStats:
    async def crop_to_circle(im):
        bigsize = (im.size[0] * 3, im.size[1] * 3)
        mask = Image.new('L', bigsize, 0)
        ImageDraw.Draw(mask).ellipse((0, 0) + bigsize, fill=255)
        mask = mask.resize(im.size, Image.ANTIALIAS)
        mask = ImageChops.darker(mask, im.split()[-1])
        im.putalpha(mask)

    async def imageRender(message: types.Message, stats, gameUrl, game, platform):
        statsFont = ImageFont.truetype(
            f"{os.path.dirname(os.path.realpath(__file__))}/fonts/Futura.ttf", size=38, index=0)
        smallFont = ImageFont.truetype(
            f"{os.path.dirname(os.path.realpath(__file__))}/fonts/Futura.ttf", size=28, index=0)
        img = Image.open(
            f"{os.path.dirname(os.path.realpath(__file__))}/images/{game}-1.png").convert("RGBA")

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url=stats["avatar"]) as r:
                    avatarByte = await r.read()
                    avatar = Image.open(io.BytesIO(avatarByte)).convert('RGBA')
            except:
                async with session.get(url="https://eaassets-a.akamaihd.net/battlelog/defaultavatars/default-avatar-204.png?ssl=1") as r:
                    avatarByte = await r.read()
                    avatar = Image.open(io.BytesIO(avatarByte)).convert('RGBA')
            if stats["rankImg"] == "":
                stats["rankImg"] = "https://cdn.gametools.network/transparent.png"
            async with session.get(url=stats["rankImg"]) as r:
                rankImgByte = await r.read()

        if stats["rankImg"].endswith(".svg"):
            rankImgByte = cairosvg.svg2png(bytestring=rankImgByte)

        await imageStats.crop_to_circle(avatar)
        avatar.thumbnail((130, 130), Image.ANTIALIAS)
        img.paste(avatar, (30, 152), avatar)

        rankImg = Image.open(io.BytesIO(rankImgByte)).convert('RGBA')
        rankImg.thumbnail((48, 48), Image.ANTIALIAS)
        img.paste(rankImg, (182, 240), rankImg)

        if platform in ["origin", "cem_ea_id"]:
            platform = "pc"
        elif platform in ["xbl", "xbox360", "xboxone"]:
            platform = "xbox"
        elif platform in ["ps3", "ps4"]:
            platform = "psn"

        rankImg = Image.open(
            f"{os.path.dirname(os.path.realpath(__file__))}/platforms/{platform}.png").convert('RGBA')
        img.paste(rankImg, (887, 203), rankImg)

        draw = ImageDraw.Draw(img)
        draw.text((182, 193), str(stats["name"]), font=statsFont)
        draw.text((319, 248), str(stats["rank"]), font=smallFont)

        draw.text((30, 375), str(stats["0.0"]), font=statsFont)
        draw.text((200, 375), str(stats["0.1"]), font=statsFont)
        draw.text((392, 375), str(stats["0.2"]), font=statsFont)
        draw.text((587, 375), str(stats["0.3"]), font=statsFont)
        draw.text((820, 375), str(stats["0.4"]), font=statsFont)

        draw.text((30, 521), str(stats["1.0"]), font=statsFont)
        draw.text((200, 521), str(stats["1.1"]), font=statsFont)
        draw.text((392, 521), str(stats["1.2"]), font=statsFont)
        draw.text((587, 521), str(stats["1.3"]), font=statsFont)
        draw.text((820, 521), str(stats["1.4"]), font=statsFont)

        draw.text((30, 667), str(stats["2.0"]), font=statsFont)
        draw.text((200, 667), str(stats["2.1"]), font=statsFont)
        draw.text((392, 667), str(stats["2.2"]), font=statsFont)
        draw.text((587, 667), str(stats["2.3"]), font=statsFont)

        with io.BytesIO() as data_stream:
            img.save(data_stream, format="png")
            data_stream.seek(0)
            await message.reply_photo(data_stream, caption=f"Full stats: {gameUrl}")

    # older than bf3 (bf2)
    async def oldBfImageRender(message: types.Message, stats, gameUrl, game):
        statsFont = ImageFont.truetype(
            f"{os.path.dirname(os.path.realpath(__file__))}/fonts/Futura.ttf", size=38, index=0)
        smallFont = ImageFont.truetype(
            f"{os.path.dirname(os.path.realpath(__file__))}/fonts/Futura.ttf", size=28, index=0)
        smallestFont = ImageFont.truetype(
            f"{os.path.dirname(os.path.realpath(__file__))}/fonts/Futura.ttf", size=24, index=0)
        img = Image.open(
            f"{os.path.dirname(os.path.realpath(__file__))}/images/{game}-1.png").convert("RGBA")

        async with aiohttp.ClientSession() as session:
            async with session.get(url=stats["rankImg"]) as r:
                rankImgByte = await r.read()

        rankImg = Image.open(io.BytesIO(rankImgByte)).convert('RGBA')
        rankImg.thumbnail((48, 48), Image.ANTIALIAS)
        img.paste(rankImg, (250, 295), rankImg)

        draw = ImageDraw.Draw(img)
        draw.text((250, 252), str(stats["name"]), font=statsFont)
        draw.text((376, 304), str(stats["rank"]), font=smallFont)

        draw.text((44, 421), str(stats["0.0"]), font=statsFont)
        draw.text((223, 421), str(stats["0.1"]), font=statsFont)
        draw.text((434, 421), str(stats["0.2"]), font=statsFont)

        w, h = draw.textsize(stats["0.3"], font=statsFont)
        draw.text((710-w, 368), str(stats["0.3"]), font=statsFont)
        w, h = draw.textsize(stats["0.4"], font=smallestFont)
        draw.text((710-w, 420), str(stats["0.4"]), font=smallestFont)

        draw.text((44, 538), str(stats["1.0"]), font=statsFont)
        draw.text((223, 538), str(stats["1.1"]), font=statsFont)
        draw.text((434, 538), str(stats["1.2"]), font=statsFont)

        w, h = draw.textsize(stats["1.3"], font=statsFont)
        draw.text((710-w, 488), str(stats["1.3"]), font=statsFont)
        w, h = draw.textsize(stats["1.4"], font=smallestFont)
        draw.text((710-w, 538), str(stats["1.4"]), font=smallestFont)

        draw.text((223, 662), str(stats["2.0"]), font=statsFont)

        with io.BytesIO() as data_stream:
            img.save(data_stream, format="png")
            data_stream.seek(0)
            await message.reply_photo(data_stream, caption=f"Full stats: {gameUrl}")
