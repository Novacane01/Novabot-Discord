import discord
import asyncio

client = discord.client()

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    discord.Client.eve