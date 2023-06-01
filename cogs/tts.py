import discord
import asyncio
import os
import re
import shutil
import uuid
from discord import app_commands
from discord.ext import commands
from gtts import gTTS
from collections import deque

regex = r"https?://.*?( |$)"
joincall = False


class tts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.jcall = False
        
    group = app_commands.Group(name='tts', description='tts')

    @group.command(name='connect', description='VCに接続します')
    @app_commands.guild_only()
    @app_commands.guilds(1111683749969657938)
    async def join(self, interaction: discord.Interaction, joinannounce: bool = False):
            global joincall
            if interaction.guild.voice_client is None:
                if interaction.user.voice.channel is interaction.channel:
                        await interaction.channel.connect()
                        if joinannounce is True:
                            joincall = True
                        await interaction.response.send_message('接続しました')
                        try:
                            shutil.rmtree("./tts")
                            os.mkdir("./tts")
                        except:
                            pass
                else:
                    await interaction.response.send_message('接続に失敗しました\nこのコマンドは接続しているVCの聞き専チャンネルで使用してください')
            else:
                await interaction.response.send_message('他のチャンネルですでにbotが使用されているため使用できません')

    @group.command(name='disconnect', description='VCから切断します')
    @app_commands.guild_only()
    async def leave(self, interaction: discord.Interaction):
        if interaction.guild.voice_client is not None:
            if interaction.channel is interaction.guild.voice_client.channel:
                if interaction.user.voice.channel is interaction.guild.voice_client.channel:
                    await interaction.response.send_message('切断しました')
                    return
        await interaction.response.send_message('失敗しました')

    # stopコマンド
    @group.command(name='stop', description='読み上げを停止します')
    async def stop(self, interaction: discord.Interaction):
        if interaction.channel is interaction.guild.voice_client.channel:
            try:
                interaction.guild.voice_client.stop()
                await interaction.response.send_message('読み上げを停止しました')
            except:
                await interaction.response.send_message('なぜか実行できませんでした', ephemeral=True)
        else:
            await interaction.response.send_message('なぜか実行できませんでした', ephemeral=True)

    # メッセージ取得
    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):
        try:
                if message.author.bot is False:
                        message_queue = deque([])
                        i = 0
                        for m in [message async for message in message.channel.history(limit=2)]:
                            if i == 0:
                                m1 = m.author.id
                            else:
                                m2 = m.author.id
                            i = +1
                        usernick = message.author.display_name
                        message = message.content[:100]
                        message = re.sub(regex, "URL ", message, flags=re.MULTILINE)
                        if m1 == m2:
                            pass
                        else:
                            message = usernick + ":" + message
                        if not message.guild.voice_client.is_playing():
                            g_tts = gTTS(text=message, lang='ja', tld='jp')
                            name = uuid.uuid1()
                            g_tts.save(f'./.tts_voice/{name}.mp3')
                            message.guild.voice_client.play(discord.FFmpegPCMAudio(f"./.tts_voice/{name}.mp3"))
                        else:
                            message_queue.append(message)
                            while message.guild.voice_client.is_playing():
                                await asyncio.sleep(0.1)
                            g_tts = gTTS(message_queue.popleft(), lang='ja', tld='jp')
                            name = uuid.uuid1()
                            g_tts.save(f'./.tts_voice/{name}.mp3')
                            message.guild.voice_client.play(discord.FFmpegPCMAudio(f"./.tts_voice/{name}.mp3"))
        except TypeError:
            return
    """
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # Botは弾く
        if member.bot is False:
            # 入退出以外は弾く
            if before.channel != after.channel:
                a = 0
                b = 0
                # TTS実行中か判断&入退出判断
                # 退出
                try:
                    if joincall is True:
                        call_queue = deque([])
                        if afterinfo is not None:
                            message = (f'{member.name}:が移動しました')
                        else:
                            message = (f'{member.name}:が退室しました')
                    else:
                        b = 1
                except TypeError:
                    b = 1
                    pass
                #入室
                try:
                    call_queue = deque([])
                    if afterinfo['joincall'] is True:
                        message = (f'{member.name}:が入室しました')
                    else:
                        a = 1
                except TypeError:
                    a = 1
                    pass

                if b+a == 2:
                    return

                if not self.bot.guild.voice_client.is_playing():
                    g_tts = gTTS(text=message, lang='ja', tld = 'jp')
                    name = uuid.uuid1()
                    g_tts.save(f'./.tts_voice/{name}.mp3')
                    self.bot.guild.voice_client.play(discord.FFmpegPCMAudio(f"./.tts_voice/{name}.mp3"))
                else:
                    call_queue.append(message)
                    while self.bot.guild.voice_client.is_playing():
                        await asyncio.sleep(0.1)
                    g_tts = gTTS(call_queue.popleft(), lang='ja', tld='jp')
                    name = uuid.uuid1()
                    g_tts.save(f'./.tts_voice/{name}.mp3')
                    self.bot.guild.voice_client.play(discord.FFmpegPCMAudio(f"./.tts_voice/{name}.mp3"))
        elif member.id is self.bot.user.id:
            if before.channel is not None and after.channel is None and beforeinfo['tts'] is True:
                await self.bot.guild.voice_client.disconnect()
        """


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(tts(bot))