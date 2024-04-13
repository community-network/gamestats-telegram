import urllib.parse
import io
from aiogram import types

"""add plotting(graphs)"""
import matplotlib.pyplot as plt
#matplotlib inline
plt.style.use('ggplot')

async def main(message: types.Message, graphing, stats, game, type):
    """makes the graphs for all the bfgraph commands"""
    try:
        if game == "tunguska":
            gameUrl = f"https://gametools.network/stats/pc/name/{urllib.parse.quote(stats['personaName'])}?game=bf1"
        elif game == "bf1": # bftracker
            gameUrl = f"https://battlefieldtracker.com/bf1/profile/{stats['platformid']}/{urllib.parse.quote(message.text)}/{type}"
        elif game == "bf2":
            gameUrl = f"https://www.bf2hub.com/stats/{urllib.parse.quote(stats['pid'])}"
        elif game == "bf5":
            gameUrl = f"https://battlefieldtracker.com/bfv/profile/origin/{urllib.parse.quote(message.text)}/{type}"
        else:
            pid = str(stats["personaId"])
            gameUrl = f"https://battlelog.battlefield.com/{game}/soldier/{urllib.parse.quote(message.text)}/{type}/{pid}/{stats['platformid']}/"
        x1 = []
        y1 = []
        x = []
        y = []
        t = 0
        [ x1.append(key["name"]) for (key) in graphing ]
        [ y1.append(key["kills"]) for (key) in graphing ]
        for i in range(len(x1)):
            if t != 20:
                x.append(x1[i])
                y.append(y1[i])
            else:
                break
            t+=1
        x_pos = [i for i, _ in enumerate(x)]
        with io.BytesIO() as data_stream:
            plt.figure(facecolor="#151829")
            plt.bar(x_pos, y, color='#00aaff')
            plt.xticks(x_pos, x, color='#ffffff', rotation=45, horizontalalignment='right')
            plt.yticks(color='#ffffff')
            plt.grid(b=False)
            ax=plt.gca()
            ax.set_facecolor('#151829')
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)

            plt.savefig(data_stream, format='png', transparent=False)
            plt.close()
            data_stream.seek(0)
            await message.reply_photo(data_stream, caption=f"Top 20 {type}\n{gameUrl}")
    except:
        await message.reply("player not found")
