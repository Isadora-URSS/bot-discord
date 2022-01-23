import discord
from discord.ext import commands
from jishaku.cog import STANDARD_FEATURES, OPTIONAL_FEATURES
from jishaku.features.baseclass import Feature
"""DEVON É UM COMPLETO HERÓI"""

class desenvolvimento(
    *STANDARD_FEATURES, 
    *OPTIONAL_FEATURES,
    name = "Desenvolvimento",
    description = "Comandos exclusivos"
):
    emoji = ":sunglasses:"
    
    @Feature.Command(aliases = ("sl", "svl", "serverlist", "ls"))
    @commands.is_owner()
    async def listaservidores(self, ctx):
        """Mostra os servidores que o bot participa"""
        lista_embeds = []
        servidor_original = ctx.guild
        for servidor in self.bot.guilds:
            ctx.guild = servidor
            descrição = f"Nome: **{ctx.guild.name}**\nDono(a): {ctx.guild.owner}\nID: {ctx.guild.id}\nNível de boost: {ctx.guild.premium_tier}"
            estatisticas = f"Membros totais: **{ctx.guild.member_count}**\nCanais: **{len(ctx.guild.channels)}** (**{len(ctx.guild.text_channels)}**"\
            f" canais de texto e **{len(ctx.guild.voice_channels)}** canais de voz)\nCategorias: **{len(ctx.guild.categories)}**\n"\
            f"Cargos: **{len(ctx.guild.roles)}**\nEmojis: **{len(ctx.guild.emojis)}/{ctx.guild.emoji_limit}**\nBoosts: **{ctx.guild.premium_subscription_count}**"
            embed = discord.Embed(
                title = "Exibindo informações de servidor",
                description = descrição,
                color = ctx.guild.me.color,
                timestamp = ctx.guild.created_at
            ).add_field(
                name = f"Estatísticas",
                value = estatisticas
            ).set_footer(
                text = f"Criado em"
            )
            if ctx.guild.icon:
                embed.set_thumbnail(
                    url = ctx.guild.icon.url
                )
            if ctx.guild.banner or ctx.guild.splash:
                imagem = ctx.guild.banner or ctx.guild.splash
                embed.set_image(
                    url = imagem.url
                )
            lista_embeds.append(embed)
        ctx.guild = servidor_original
        paginador = self.bot.paginador(lista_embeds, 300, ctx)
        await paginador.começar()
    
    @Feature.Command(
        invoke_without_command = True,
        aliases = ("pv", "dm", "md", "directmessage")
    )
    @commands.is_owner()
    async def mensagensdiretas(self, ctx):
        """comandos relacionados a mensagens diretas"""
        await ctx.send_help("mensagensdiretas")
    
    @Feature.Command(
        parent = "mensagensdiretas",
        aliases = ("ler",),
        extras = {"usuario": "O usuário para ver as mensagens",
                  "exemplos": ("<@531508181654962197>", "531508181654962197")}
    )
    @commands.is_owner()
    async def ver(self, ctx, usuario: discord.User):
        """Verifica as mensagens diretas do bot"""
        lista_mensagens = []
        async for mensagem in usuario.history(limit=None):
            if mensagem.author.id == usuario.id:
                embed = discord.Embed(
                    title = f"Mensagem enviada por {usuario}",
                    description = mensagem.content,
                    color = 0x00FF00,
                    timestamp = mensagem.created_at
                ).set_author(
                    name = str(mensagem.author),
                    icon_url = mensagem.author.avatar.url
                )
                if len(mensagem.attachments) > 0:
                    embed.add_field(
                        name = "Anexos",
                        value = f"{mensagem.attachments}"
                    )
                lista_mensagens.append(embed)
            else:
                if len(mensagem.embeds) > 0:
                    embed = discord.Embed(
                        title = f"Embed enviado pelo bot",
                        description = f"Titulo do embed: {mensagem.embeds[0].title}\nDescrição do embed: {mensagem.embeds[0].description}",
                        color = 0x0000FF,
                        timestamp = mensagem.created_at
                    ).set_author(
                        name = str(mensagem.author),
                        icon_url = mensagem.author.avatar.url
                    )
                else:
                    embed = discord.Embed(
                        title = f"Mensagem enviada pelo bot",
                        description = mensagem.content,
                        color = 0xFF0000,
                        timestamp = mensagem.created_at
                    ).set_author(
                        name = str(mensagem.author),
                        icon_url = mensagem.author.avatar.url
                    )
                    if len(mensagem.attachments) > 0:
                        embed.add_field(
                            name = "Anexos",
                            value = f"{mensagem.attachments}"
                        )
                lista_mensagens.append(embed)
        if len(lista_mensagens) == 0:
            return await ctx.send("Não tenho mensagens com o usuário solicitado")
        paginador = self.bot.paginador(lista_mensagens, 120, ctx)
        await paginador.começar()
    
    @Feature.Command(
        parent = "mensagensdiretas",
        aliases = ("mandar",),
        extras = {"usuario": "O usuário para se enviar a mensagem",
                  "mensagem": "A mensagem a ser enviada",
                  "exemplos": ("<@531508181654962197> Eu sou o bot e estou no seu privado.", "531508181654962197 Mensagem.", "<@531508181654962197> <:Trollface:805987983273623612>")}
    )
    @commands.is_owner()
    async def enviar(self, ctx, usuario: discord.User, *, mensagem):
        try:
            await usuario.send(mensagem)
            await ctx.message.add_reaction("\u2714\ufe0f")
        except discord.HTTPException:
            await ctx.message.add_reaction("\u274c")
    
    @Feature.Command(
        invoke_without_command = True,
        aliases = ("ln", "blacklist", "bl")
    )
    @commands.is_owner()
    async def listanegra(self, ctx):
        """Lista os usuários banidos do bot"""
        infos = await self.bot.database.botinfos.find_one({})
        if len(infos["banidos"]) == 0:
            await ctx.send("Não tem ninguem banido do bot")
        else:
            banidos = [await self.bot.fetch_user(id) for id in infos["banidos"]]
            banidos2 = [f"{usuario.id} - {usuario} - {len(usuario.mutual_guilds)} servidores em comum" for usuario in banidos]
            embed = discord.Embed(
                title = f"Usuarios banidos do bot",
                description = "\n".join(banidos2),
                timestamp = discord.utils.utcnow()
            )
            await ctx.send(embed = embed)
    
    @Feature.Command(
        parent = "listanegra",
        aliases = ("ban", "adicionar"),
        extras = {"usuario": "O usuário para banir do bot",
                  "exemplos": ("<@531508181654962197>", "531508181654962197")}
    )
    @commands.is_owner()
    async def botban(self, ctx, usuario):
        """Impede alguém de usar o bot"""
        infos = await self.bot.database.botinfos.find_one({})
        if usuario.id in infos["banidos"]:
            await ctx.message.add_reaction("\u274c")
        else:
            await self.bot.database.botinfos.update_one(
                {},
                {"$push": {"banidos": usuario.id}}
            )
            self.bot.cache[0] = await self.bot.database.botinfos.find_one({})
            await ctx.message.add_reaction("\u2714\ufe0f")
    
    @Feature.Command(
        parent = "listanegra",
        aliases = ("unban", "remover"),
        extras = {"usuario": "O usuário para desbanir do bot",
                  "exemplos": ("<@531508181654962197>", "531508181654962197")}
    )
    @commands.is_owner()
    async def botunban(self, ctx, usuario):
        """Desimpede alguém de usar o bot"""
        infos = await self.bot.database.botinfos.find_one({})
        if usuario.id not in infos["banidos"]:
            await ctx.message.add_reaction("\u274c")
        else:
            await self.bot.database.botinfos.update_one(
                {},
                {"$pull": {"banidos": usuario.id}}
            )
            self.bot.cache[0] = await self.bot.database.botinfos.find_one({})
            await ctx.message.add_reaction("\u2714\ufe0f")
            
    
def setup(bot):
    bot.add_cog(desenvolvimento(bot = bot))
