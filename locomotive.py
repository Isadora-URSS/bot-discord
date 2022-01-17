import discord
from discord.ext import commands
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import aiohttp
from plugins.variaveis import Banido, TempoInvalido, CanalDesativado
from servidor import manter_ativo

import asyncio
import logging
from socket import gethostname
from os import getenv
import sys
import re

print(
"""\033[33m####################################################
 | |                               | | (_)          
 | | ___   ___ ___  _ __ ___   ___ | |_ ___   _____ 
 | |/ _ \ / __/ _ \| '_ ` _ \ / _ \| __| \ \ / / _  
 | | (_) | (__ (_) | | | | | | (_) | |_| |\ V /  __/
 |_|\___/ \___\___/|_| |_| |_|\___/ \__|_| \_/ \___|
                 Iniciando script...
####################################################\033[0m"""
)

load_dotenv()

if gethostname() == getenv("host_name"):
    log = logging.getLogger("discord")
    log.setLevel(logging.DEBUG)
    
    handler_arquivo = logging.FileHandler(filename = "discord.log", encoding = "utf-8", mode = "w")
    handler_arquivo.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
    handler_arquivo.setLevel(logging.DEBUG)
    log.addHandler(handler_arquivo)
    
    handler_terminal = logging.StreamHandler(sys.stdout)
    handler_terminal.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
    handler_terminal.setLevel(logging.INFO)
    log.addHandler(handler_terminal)

class MeuBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conexao_motor = AsyncIOMotorClient(getenv("link_database"))
        self.database = self.conexao_motor.DiscordBot
        self.cache = {}
        self.cache_pronto = False
        self.conexão = aiohttp.ClientSession()
        self.emoji = {}
    
    async def close(self):
        embed = discord.Embed(
            title = "Bot offline",
            description = f"Estou deslogando da conta {self.user} (ID: {self.user.id}) em {gethostname()}",
            color = 0xFF0000,
            timestamp = discord.utils.utcnow()
        )
        webhook = discord.Webhook.from_url(getenv("webhook_url"), session = self.conexão)
        await webhook.send(embed = embed)
        await self.conexão.close()
        self.conexao_motor.close()
        print("\033[31mConexões fechadas, desligando o bot...\033[0m")
        await super().close()
    
    async def atualizar_cache(self, id):
        resultado = await self.database.servidores.find_one(
            {"id_servidor": id}
        )
        self.cache[id] = resultado
        
    def dict_padrao(self, id):
        return {
            "id_servidor": id,
            "auto_respostas": {},
            "auto_respostas_apagar": 0,
            "prefixos": ["l!","locomotive!"],
            "comandos_desativados": [],
            "categorias_desativadas": [],
            "canais_desativados": [],
            "cargo_mute": None,
            "mutados": [],
            "cargo_dimensao_espelhos": None,
            "haki_observacao": "Nenhuma mensagem apagada foi capturada ainda."
        }

    async def on_ready(self):
        print(f"\033[34mEstou logado no Discord! Irei verificar a database. Enquanto isso, ignorarei qualquer mensagem recebida. Versão Python: {sys.version} // Versão d.py: {discord.__version__}\033[0m")
        for servidor in self.guilds:
            resultado = await self.database.servidores.find_one({"id_servidor": servidor.id})
            dict_padrao = self.dict_padrao(servidor.id)
            if resultado == None:
                await self.database.servidores.insert_one(dict_padrao)
                print(f"\033[31mUm servidor não tinha entrada na database. Erro corrigido, id do servidor: {servidor.id}...\033[0m")
            else:
                atualizado = False
                for chave in dict_padrao:
                    if chave not in resultado:
                        await self.database.servidores.update_one(
                            {"id_servidor": servidor.id},
                            {"$set": {chave: dict_padrao[chave]}}
                        )
                        atualizado = True
                if atualizado:
                    print(f"\033[31mO servidor de id {servidor.id} estava com chaves faltando. Erro corrigido...\033[0m")
                else:
                    print(f"\033[32mO servidor de id {servidor.id} está nas conformidades com a database...\033[0m")
            await self.atualizar_cache(servidor.id)
        print("\033[34mTerminei de verificar as databases e fiz o cachê necessário. Todos os servidores agora estão abrangidos...\033[0m")
        emojis = self.get_guild(801185265363845140).emojis
        for emoji in emojis:
            self.emoji[emoji.name] = str(emoji)
        self.cache[0] = await self.database.botinfos.find_one({})
        self.cache_pronto = True
        print("\033[32mEstou pronto para receber comandos!\033[0m")
        embed = discord.Embed(
            title = "Bot online",
            description = f"Estou logado como {self.user} (ID: {self.user.id}) em {gethostname()}",
            color = 0x00FF00,
            timestamp = discord.utils.utcnow()
        )
        webhook = discord.Webhook.from_url(getenv("webhook_url"), session = self.conexão)
        await webhook.send(embed = embed)

    async def on_guild_join(self, servidor):
        dict = self.dict_padrao(servidor.id)
        resultados = self.database.servidores.find({"id_servidor": servidor.id})
        lista_de_resultados = await resultados.to_list(None)
        if len(lista_de_resultados) == 0:
            await self.database.servidores.insert_one(dict)
            print(f"\033[34mEntrei em um servidor. Id: {servidor.id}. Foi criado um documento relativo a esse servidor.\033[0m")
            await self.atualizar_cache(servidor.id)
        else:
            print(f"\033[34mEntrei em um servidor. Id: {servidor.id}. Já existia uma configuração para esse servidor anteriormente.\033[0m")
            await self.atualizar_cache(servidor.id)

    async def on_message(self, mensagem):
        if not self.cache_pronto:
            print("\033[31mUma mensagem foi enviada, porem o cache do bot nao esta pronto e por isso ela foi ignorada.\033[0m")
            return
        if mensagem.author.bot or not mensagem.guild:
            return
        if re.fullmatch(rf"<@!?{self.user.id}>", mensagem.content):
            await mensagem.channel.send(f"Meu primeiro prefixo nesse servidor é {self.cache[mensagem.guild.id]['prefixos'][0]}", allowed_mentions = discord.AllowedMentions().none())
        infos = self.cache[mensagem.guild.id]
        autorespostas = infos["auto_respostas"]
        for gatilho in autorespostas:
            if gatilho in mensagem.content.lower():
                if infos["auto_respostas_apagar"] == 0:
                    await mensagem.channel.send(autorespostas[gatilho])
                    break
                elif infos["auto_respostas_apagar"] > 0:
                    await mensagem.channel.send(autorespostas[gatilho], delete_after = infos['auto_respostas_apagar'])
                    break
        await self.process_commands(mensagem)

async def prefixo(bot, mensagem):
    if mensagem.guild and bot.cache_pronto:
        prefixos = bot.cache[mensagem.guild.id]["prefixos"]
        return commands.when_mentioned_or(*prefixos)(bot, mensagem)
    else:
        return "l!"

intents = discord.Intents.all()
intents.invites = False
intents.voice_states = False
intents.typing = False

bot = MeuBot(
    command_prefix = prefixo,
    description = "Locomotive Bot",
    intents = intents,
    activity = discord.Activity(
        type = discord.ActivityType.listening,
        name = "Use o comando de ajuda."
    ),
    status = discord.Status.idle
)

@bot.check
async def global_check(ctx):
    if not ctx.guild:
        raise commands.NoPrivateMessage
    if ctx.channel.id in ctx.bot.cache[ctx.guild.id]["canais_desativados"]:
        raise CanalDesativado
    if ctx.author.id in ctx.bot.cache[0]["banidos"]:
        raise Banido
    comandos_desativados = ctx.bot.cache[ctx.guild.id]["comandos_desativados"]
    if ctx.command.qualified_name in comandos_desativados:
        raise commands.DisabledCommand
    for comandopai in ctx.command.parents:
        if comandopai.qualified_name in comandos_desativados:
            raise commands.DisabledCommand
    return True

modulos = ("categorias.ajuda", "categorias.atividade", "categorias.configurações", "categorias.desenvolvimento",
           "categorias.diversão", "categorias.informações", "categorias.internet", "categorias.moderação",
           "categorias.onepiece", "plugins.paginador", "plugins.erros")
for modulo in modulos:
    bot.load_extension(modulo)

if not (gethostname() == getenv("host_name")):
    manter_ativo()
bot.ligou = discord.utils.utcnow()
bot.run(getenv("numeros_magicos"))
