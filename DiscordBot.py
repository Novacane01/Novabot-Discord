import discord
from discord.ext import commands
import asyncio
import urllib.request
import re
import random


startup_extensions = ["Music"]

owner_id = '239504944296755202'

# Bot stuff
bot_token = 'NDczNzcwNDE2Nzg0MTQ2NDQy.DkI81w.VIZxFQnzD_Hy0BsdCVsF15V-CTA'
bot = commands.Bot('!', description='')
#

# Audio stuff
bot.voice = None
bot.player = None
bot.queue = []
#


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.event
async def on_member_join(member):
    await bot.send_message(bot.get_channel("473597571466526721"),
                           "Hey {0.mention}, did you just blow in from Stupid Town?".format(member))


@bot.command()
async def load(extension_name : str):
    """Loads an extension."""
    try:
        bot.load_extension(extension_name)
    except (AttributeError, ImportError) as e:
        await bot.say("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
        return
    await bot.say("{} loaded.".format(extension_name))

@bot.command()
async def unload(extension_name : str):
    """Unloads an extension."""
    bot.unload_extension(extension_name)
    await bot.say("{} unloaded.".format(extension_name))


@bot.command(pass_context=True)
async def test(ctx, *, msg):
    await bot.send_message(ctx.message.channel, "{} said: ".format(ctx.message.author) + msg, tts=True)


@bot.command(pass_context=True, name="kick")
@commands.has_permissions(kick_members=True)
async def kick_user(ctx, member: discord.Member):
    await bot.say("Are you sure you would like to kick {}?".format(member.display_name))

    def check(msg):
        return msg.author.id == owner_id

    msg = await bot.wait_for_message(author=ctx.message.author, check=check)
    if msg.content.lower() == "yes":
        await bot.kick(member)
        await bot.say("L8ter")
    elif msg.content.lower() == "no":
        await bot.say("One day...")
    else:
        await bot.say("It was a yes or no question bitch")


@bot.command(name="members_server")
async def get_members_server():
    users = "Members: \n"
    i = 1
    for u in bot.get_all_members():
        users += "{}. {}\n".format(str(i), u.display_name)
        i += 1

    await bot.say(users)

if __name__ == "__main__":
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))


bot.run(bot_token)
