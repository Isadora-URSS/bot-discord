import discord
from discord.ext import commands, tasks

import random
import base64
import os
import re
import asyncio

class atividade(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mudar_musica.start()
    
    async def on_cog_unload(self):
        self.mudar_musica.stop()
        await self.bot.change_presence(
            activity = discord.Activity(
                type = discord.ActivityType.playing,
                name = "Me marque para ver meus prefixos no servidor."
            ))
    
    @tasks.loop()
    async def mudar_musica(self):
        musica = self.musicas[self.posição]["track"]
        remastered = r" - ([0-9]{2,4} (remastered|remaster)|(remastered|remaster) [0-9]{2,4})"
        nome = re.sub(remastered, "", musica["name"], flags = re.IGNORECASE)
        atividade = f"{nome} - {musica['artists'][0]['name']} - {musica['album']['name']}"
        await self.bot.change_presence(
            activity = discord.Activity(
                type = discord.ActivityType.listening,
                name = atividade,
                url = musica["external_urls"]["spotify"]
            ))
        self.posição += 1
        if self.posição == len(self.musicas):
            self.posição = 0
        await asyncio.sleep(musica["duration_ms"]//1000)
    
    @mudar_musica.before_loop
    async def salvar_playlist(self):
        client_id = os.getenv("spotify_client_id")
        client_secret = os.getenv("spotify_client_secret")
        playlist_id = os.getenv("playlist_id")
        autorização = client_id + ":" + client_secret
        headers = {"Authorization": "Basic " + base64.b64encode(autorização.encode('ascii')).decode("ascii")}
        data = {"grant_type": "client_credentials"}
        async with self.bot.conexão.post("https://accounts.spotify.com/api/token", data = data, headers = headers) as resposta:
            json = await resposta.json()
            token = json["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}"\
        "?fields=tracks.items(track(name,artists(name),album(name),external_urls(spotify),duration_ms))"
        async with self.bot.conexão.get(url, headers = headers) as resposta:
            json = await resposta.json()
            self.musicas = json["tracks"]["items"]
        self.posição = random.randint(0, len(self.musicas)-1)
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(atividade(bot))