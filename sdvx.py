import mysql.connector
import random
import asyncio
import discord
import os
from discord import app_commands
from dotenv import load_dotenv


load_dotenv()

intents = discord.Intents.default()
client = discord.Client(intents = intents)
tree = app_commands.CommandTree(client)


@client.event
async def on_ready():
    await tree.sync()
    while True:
        cnx = connectToDB()
        target = select(cnx, random.randint(1, 20))

        if cnx is not None and cnx.is_connected():
            cnx.close()

        await client.change_presence(activity = discord.Activity(name = f"{target[0]} [{target[2]}] Lv.{target[3]}", type = discord.ActivityType.playing))
        await asyncio.sleep(180)


@tree.command(name = "sdvx", description = "おうちボルテ曲ガチャだよ")
@app_commands.rename(level = "レベル")
@app_commands.describe(level = "レベルを1～20の間で指定します")
@app_commands.rename(diff = "難易度")
@app_commands.describe(diff = "譜面難易度を「EXH」や「MXM」のように指定します")
@app_commands.rename(cond = "プレイ条件")
@app_commands.describe(cond = "楽曲パック名などのプレイ条件を部分一致検索します")
async def sdvx(interaction: discord.Interaction, level: int, diff: str = None, cond: str = None):
    cnx = connectToDB()
    target = select(cnx, level, difficulty = diff, condition = cond)

    emoji = discord.utils.get(client.emojis, name = target[2].lower())
    embed = discord.Embed(title = "おうちボルテガチャ", description = f"【{target[0]} {str(emoji)} Lv.{target[3]}】をプレイしなさい！", color = 0xee17ca)
    embed.set_footer(text = f"プレイ条件は【{target[4]}】よ") 
    await interaction.response.send_message(embed = embed)

    if cnx is not None and cnx.is_connected():
        cnx.close()


def connectToDB():
    try:
        cnx = mysql.connector.connect(
                user = os.getenv('DB_USER'),
                password = os.getenv('DB_PASSWORD'),
                host = os.getenv('DB_HOST'),
                port = os.getenv('DB_PORT'),
                database = os.getenv('DB_NAME')
        )

        return cnx
    except Exception as e:
        print(f"Error occurred: {e}")


def select(cnx, level, difficulty = None, condition = None):
    sql = "select * from HouseSDVX where level = %s"
    param = (level,)

    if difficulty:
        sql = f"{sql} and difficulty = %s"
        param += (difficulty,)
    if condition:
        sql = f"{sql} and `condition` like %s"
        param += ("%" + condition + "%",)

    cursor = cnx.cursor()

    cursor.execute(sql, param)
    target = random.choice(cursor.fetchall())

    return target

#    return f"{target[0]}:{target[2]}: Lv.{target[3]}\nプレイ条件は【{target[4]}】よ"

if __name__ == '__main__':
    client.run(os.getenv('DISCORD_TOKEN'))

