import discord
from discord.ext import commands
import asyncio
import urllib.request
import re


class VoiceEntry:
    def __init__(self, message, player):
        self.requester = message.author
        self.channel = message.channel
        self.player = player

    def __str__(self):
        fmt = '*{0.title}* uploaded by {0.uploader} and requested by {1.display_name}'
        duration = self.player.duration
        if duration:
            fmt = fmt + ' [length: {0[0]}m {0[1]}s]'.format(divmod(duration, 60))
        return fmt.format(self.player, self.requester)


class VoiceState:
    def __init__(self, bot):
        self.bot = bot
        self.current = None
        self.voice = None
        self.play_next_song = asyncio.Event()
        self.songs = asyncio.Queue()
        self.audio_player = self.bot.loop.create_task(self.audio_player_task())

    def is_playing(self):
        if self.voice is None or self.current is None:
            return False
        player = self.current.player
        return not player.is_done()

    @property
    def player(self):
        return self.current.player

    def skip(self):
        if self.is_playing():
            self.player.stop()

    def toggle_next(self):
        self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    async def audio_player_task(self):
        while True:
            self.play_next_song.clear()
            self.current = await self.songs.get()
            await self.bot.send_message(self.current.channel, 'Now playing ' + str(self.current))
            self.current.player.start()
            await self.play_next_song.wait()


class Music:
    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, server):
        state = self.voice_states.get(server.id)
        if state is None:
            state = VoiceState(self.bot)
            self.voice_states[server.id] = state

        return state

    async def create_voice_client(self, channel):
        voice = await self.bot.join_voice_channel(channel)
        state = self.get_voice_state(channel.server)
        state.voice = voice

    @commands.command(pass_context=True)
    async def join(self, ctx):
        user = ctx.message.author
        if user.voice_channel:
            if self.voice_states.get(ctx.message.server.id) is None:
                try:
                    await self.create_voice_client(user.voice_channel)
                except discord.ClientException:
                    await self.bot.say("Already in a channel")
                else:
                    await self.bot.say("Ready when you are jimbo")
        else:
            await self.bot.say("I'm to scared to go into a voice channel alone :(")

    @commands.command(pass_context=True)
    async def summon(self, ctx):
        user = ctx.message.author
        summoned_channel = user.voice_channel
        if not user.voice_channel:
            await self.bot.say("You aren't in a voice channel")
            return False

        state = self.get_voice_state(user.server)
        if state.voice is None:
            state.voice = await state.bot.join_voice_channel(user.voice_channel)
        elif state.voice.channel is not summoned_channel:
            await state.bot.say("_poof_")
            await state.voice.move_to(user.voice_channel)
        else:
            await state.bot.say("I'm already in this channel")

        return True

    @commands.command(pass_context=True, aliases=["play", "pl"])
    async def play_music(self, ctx, *, args=None):
        user = ctx.message.author
        channel = user.voice_channel

        state = self.get_voice_state(user.server)

        if state.voice is None:
            success = await ctx.invoke(self.summon)
            if not success:
                return
        try:
            request = urllib.request.urlopen(
                "https://www.youtube.com/results?search_query={}".format(str(args).replace(" ", "+")))
            html = request.read()
            pattern = re.compile("watch\?v=\S+\"")
            url = re.findall(pattern, str(html))[0]
            player = await state.voice.create_ytdl_player("https://www.youtube.com/{}".format(url),
                                                          after=state.toggle_next)
        except Exception as e:
            fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
            await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))
        else:
            player.volume = 0.6
            entry = VoiceEntry(ctx.message, player)
            await self.bot.say('Enqueued ' + str(entry))
            await state.songs.put(entry)

    @commands.command(pass_context = True, aliases= ["n","next"])
    async def skip(self,ctx):
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            state.skip()

    @commands.command(pass_context=True, aliases= ["s"])
    async def stop(self, ctx):
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            state.player.stop()
        try:
            state.audio_player.cancel()
            del self.voice_states[ctx.message.server.id]
            await state.voice.disconnect()
        except Exception:
            pass

    @commands.command(pass_context = True, aliases= ["r"])
    async def resume(self,ctx):
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            state.player.resume()

    @commands.command(pass_context=True, aliases= ["p"])
    async def pause(self, ctx):
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            state.player.pause()

    @commands.command(pass_context = True, aliases= ["v","volume"])
    async def set_volume(self,ctx,volume_level:float):
        state = self.get_voice_state(ctx.message.server)
        state.player.volume = volume_level


    # @commands.command(name="stop")
    # async def stop_music(self):
    #     if self.
    #         self.bot.player.stop()

    # @commands.command(name="add")
    # async def add_to_queue(self,ctx, *, args):
    #     state = self.get_voice_state(ctx.message.server)
    #     await state.songs.put()
    #     await self.bot.say(str(args) + " added to queue")


def setup(bot):
    bot.add_cog(Music(bot))
