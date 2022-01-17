from discord.ext import commands
from os import getenv
from dotenv import load_dotenv

import re

load_dotenv()

class Banido(commands.CheckFailure):
    pass
class TempoInvalido(commands.BadArgument):
    def __init__(self, texto):
        self.texto = texto
class CanalDesativado(commands.CheckFailure):
    pass
    
class ConversorTempo(commands.Converter):
    async def convert(self, ctx, entrada):
        regex_tempo = r"([0-9]{1,5}(?:[.,]?[0-9]{1,2})?)([smhday])"
        dict_tempo = {"s":1, "m":60, "h":3600, "d":86400, "a": 31536000, "y": 31536000}
        resultado = re.fullmatch(regex_tempo, entrada.lower())
        if not resultado:
            raise TempoInvalido(entrada)
        grupos = resultado.groups()
        return float(grupos[0].replace(',', '.')) * dict_tempo[grupos[1]]

class CooldownEspecial:
    info = "Este cooldown se aplica a todos os usuários do bot."
    def __init__(self, rate, per):
        self.rate = rate
        self.per = per
    
    def __call__(self, mensagem):
        if mensagem.author.id in bot_admin:
            return None
        return commands.Cooldown(self.rate, self.per)

class CooldownHaki1(CooldownEspecial):
    info =  "Este cooldown não se aplica a pessoas com a permissão de editar o servidor."
    def __call__(self, mensagem):
        if mensagem.author.id in bot_admin:
            return None
        elif mensagem.author.guild_permissions.manage_guild:
            return None
        return commands.Cooldown(self.rate, self.per)

bot_admin_1 = int(getenv("bot_admin_1"))
bot_admin_2 = int(getenv("bot_admin_2"))
bot_admin = set((bot_admin_1, bot_admin_2))
