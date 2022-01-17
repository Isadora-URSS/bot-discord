import discord
from discord.ext import commands, tasks
from plugins.variaveis import ConversorTempo
from typing import Union

import asyncio

class moderação(
    commands.Cog,
    name = f"Moderação",
    description = "Essa categoria contem comandos para a moderação de servidores."
):
    def __init__(self, bot):
        self.bot = bot
        self.emoji = "<:PepeAdmin:804917916499705856>"
    
    @commands.command(
        aliases = ("foder", "fuder", "expulsar"),
        brief = "Kicka alguém do servidor",
        extras = {"alvo": "A pessoa a ser kickada", 
                  "motivo": "O motivo para o registro de auditoria",
                  "exemplos": ("<@531508181654962197>", "531508181654962197 Infrator", "531508181654962197 Aprenda a seguir regras")}
    )
    @commands.has_permissions(kick_members = True)
    @commands.bot_has_permissions(kick_members = True)
    async def kick(self, ctx, alvo: discord.Member, *, motivo = ""):
        """Kicka alguém do servidor."""
        if alvo.id == ctx.author.id:
            return await ctx.send("Você não pode expulsar você mesmo.")
        motivo = f"Kickado por {ctx.author} (ID: {ctx.author.id}). " + motivo
        cargo_autor = ctx.author.top_role
        cargo_alvo = alvo.top_role
        cargo_bot = ctx.guild.me.top_role
        if ctx.guild.roles.index(cargo_autor) <= ctx.guild.roles.index(cargo_alvo):
            await ctx.send("Você não tem poder suficiente para expulsar essa pessoa.")
        elif ctx.guild.roles.index(cargo_bot) <= ctx.guild.roles.index(cargo_alvo):
            await ctx.send("Eu não tenho poder para expulsar dessa pessoa.")
        elif ctx.guild.owner.id == alvo.id:
            await ctx.send("Essa pessoa é dona do servidor.")
        else:
            embed = discord.Embed(
                title = f"{ctx.author} expulsou {alvo}!",
                description = f"Agora a pessoa vai ter que voltar pro servidor kkkkkkkk",
                timestamp = discord.utils.utcnow()
            ).add_field(
                name = "Motivo/registro de auditoria",
                value = motivo
            ).set_image(
                url = "https://cdn.discordapp.com/attachments/803443536363913236/841065814697836614/Will_Smith_Banido.gif"
            )
            await ctx.guild.kick(alvo, reason = motivo)
            if not ctx.guild.me.guild_permissions.embed_links:
                await ctx.send(f"{ctx.author} expulsou {alvo}!\n**Motivo/registro de auditoria:** {motivo}")
            else:
                await ctx.send(embed = embed)
    
    @commands.command(
        aliases = ("comerabunda", "banir", "comerocu"),
        brief = "Bane alguém do servidor",
        extras = {"alvo": "A pessoa a ser banida", 
                  "motivo": "O motivo para o registro de auditoria",
                  "exemplos": ("<@531508181654962197>", "531508181654962197 Infrator", "531508181654962197 Aprenda a seguir regras")}
    )
    @commands.has_permissions(ban_members = True)
    @commands.bot_has_permissions(ban_members = True)
    async def ban(self, ctx, alvo: Union[discord.Member, discord.User], *, motivo = ""):
        """Bane alguém do servidor."""
        if alvo.id == ctx.author.id:
            return await ctx.send("Você não pode comer seu própio cu." if ctx.invoked_with in ("comerabunda", "comerocu") else "Você não pode se banir.")
        motivo = f"Banido por {ctx.author}. " + motivo
        if isinstance(alvo, discord.Member):
            cargo_autor = ctx.author.top_role
            cargo_alvo = alvo.top_role
            cargo_bot = ctx.guild.me.top_role
            if ctx.guild.roles.index(cargo_autor) <= ctx.guild.roles.index(cargo_alvo):
                return await ctx.send("Você não tem poder suficiente para comer o cu dessa pessoa." if ctx.invoked_with in ("comerabunda", "comerocu") else "Você não tem poder para banir essa pessoa.")
            elif ctx.guild.roles.index(cargo_bot) <= ctx.guild.roles.index(cargo_alvo):
                return await ctx.send("Eu não tenho poder para comer o cu dessa pessoa." if ctx.invoked_with in ("comerabunda", "comerocu") else "Eu não tenho poder para banir essa pessoa.")
            elif ctx.guild.owner.id == alvo.id:
                return await ctx.send("Essa pessoa é dona do servidor.")
            elif ctx.invoked_with in ("comerabunda", "comerocu"):
                try:
                    await alvo.send("https://cdn.discordapp.com/attachments/803443536363913236/841068660324171806/Will_Smith_BANIDO_Meme-1.mp4")
                except:
                    pass
        embed = discord.Embed(
            title = f"{ctx.author} comeu o cu de {alvo}!" if ctx.invoked_with in ("comerabunda", "comerocu") else f"{ctx.author} baniu {alvo}!",
            description = "Em outas palavras, isso foi um PERMA BAN KKKKKKKKKKKKKKK",
            timestamp = discord.utils.utcnow()
        ).add_field(
            name = "Motivo/registro de auditoria",
            value = motivo
        )
        await ctx.guild.ban(alvo, delete_message_days = 0, reason = motivo)
        if not ctx.guild.me.guild_permissions.embed_links:
            await ctx.send(f"{ctx.author} baniu {alvo}!\n**Motivo/registro de auditoria:** {motivo}")
        else:
            await ctx.send(embed = embed)
        if ctx.invoked_with in ("comerabunda", "comerocu"):
            await ctx.send("https://cdn.discordapp.com/attachments/803443536363913236/841068660324171806/Will_Smith_BANIDO_Meme-1.mp4")

def setup(bot):
    bot.add_cog(moderação(bot))
