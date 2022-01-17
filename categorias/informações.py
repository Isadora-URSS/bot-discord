import discord
from discord.ext import commands
from plugins.variaveis import CooldownEspecial

import time

class informações(
    commands.Cog, 
    name = "Informações", 
    description = "Essa categoria contem comandos que retornam informações do discord e do bot."
):
    def __init__(self, bot):
        self.bot = bot
        self.emoji = "\U0001f9d0"
    
    def cog_unload(self):
        self.bot.help_command.cog = None
    
    @commands.command(
        aliases = ("pong", "latência", "latencia", "ms"),
        brief = "Envia a latência do bot"
    )
    async def ping(self, ctx):
        """Envia a latência do bot."""
        começo = time.perf_counter()
        mensagem = await ctx.send("Calculando...")
        fim = time.perf_counter()
        duração = round((fim - começo)*1000, 2)
        começo2 = time.perf_counter()
        await self.bot.conexao_motor.admin.command({"ping": 1})
        fim2 = time.perf_counter()
        duração_database = round((fim2 - começo2)*1000,2)
        duração_websocket = round(self.bot.latency*1000, 2)
        await mensagem.edit(
            content = f"{ctx.author.mention}, calculei!\nTempo para envio de mensagem: {duração}ms.\nLatência do websocket: {duração_websocket}ms.\nLatência da database: {duração_database}ms."
        )
    
    @commands.command(
        aliases = ("tempodeatividade", "ta", "up", "ut"),
        brief = "Manda o tempo de atividade do bot"
    )
    async def uptime(self, ctx):
        """Manda o tempo de atividade do bot."""
        await ctx.send(f"O bot está ativo desde <t:{int(self.bot.ligou.timestamp())}> (<t:{int(self.bot.ligou.timestamp())}:R>)")
    
    @commands.command(
        aliases = ("ui","infousuario","iu"),
        brief = "Envia informações sobre um usuário do discord",
        extras = {"usuário": "Id ou menção do usuário a se ver as informações",
                  "exemplos": ("<@531508181654962197>", "531508181654962197")}
    )
    @commands.bot_has_permissions(embed_links = True)
    async def userinfo(self, ctx, usuário: discord.User = None):
        """Envia informações sobre um usuário do discord. Se o usuário estiver no servidor, algumas informações mais detalhadas serão exibidas, como a data de entrada no servidor."""
        usuário = usuário or ctx.author
        texto = f"**Nome de usuário:** {usuário}"
        texto += f"\n**Se registrou em** <t:{int(usuário.created_at.timestamp())}:F> (<t:{int(usuário.created_at.timestamp())}:R>)"
        texto += f"\n**ID:** {usuário.id}"
        if usuário.bot:
            texto += "\n-Esse usuário é um bot \U0001f916"
            if usuário.public_flags.verified_bot:
                texto += " (e foi verificado pelo discord)"
        if usuário.public_flags.staff:
            texto += f"\n-Esse usuário é parte da equipe do discord {self.bot.emoji['PepeAdmin']}"
        if usuário.public_flags.partner:
            texto += f"\n-Esse usuário é parceiro do discord \U0001f91d"
        if usuário.public_flags.hypesquad:
            texto += f"\n-Esse usuário faz parte dos eventos da HypeSquad"
        if usuário.public_flags.bug_hunter:
            texto += f"\n-Esse usuário é caçador de bugs \U0001fab2"
        if usuário.public_flags.early_supporter:
            texto += f"\n-Esse usuário é apoiador desde o começo do discord"
        if usuário.public_flags.system:
            texto += f"\n-Esse usuário é um usuário do sistema do discord {self.bot.emoji['DiscordLoading']}"
        if usuário.public_flags.verified_bot_developer:
            texto += f"\n-Esse usuário é um desenvolvedor de bots desde o começo do discord \U0001f5a5\ufe0f"
        embed = discord.Embed(
            title = f"Exibindo informações para {usuário.name}",
            description = texto,
            timestamp = discord.utils.utcnow()
        ).set_thumbnail(
            url = usuário.display_avatar.url
        )
        if usuário.banner:
            embed.set_image(
                url = usuário.banner.url
            )
        membro = ctx.guild.get_member(usuário.id)
        if membro:
            texto_membro = f"**Apelido:** {membro.nick}"
            texto_membro += f"\n**Entrou no servidor em** <t:{int(membro.joined_at.timestamp())}:F> (<t:{int(membro.joined_at.timestamp())}:R>)"
            texto_membro += f"\n**Status:** {membro.raw_status}"
            if membro.premium_since:
                texto_membro += f"\n-Esse membro usou um nitro boost no servidor em <:t:{int(membro.premium_since.timestamp())}>"
            texto_membro += f"\n**Maior cargo:** {membro.top_role.mention}"
            for atividade in membro.activities:
                if isinstance(atividade, discord.CustomActivity):
                    texto_membro += f"\n**Status customizado:** {atividade.name}"
                if isinstance(atividade, discord.Spotify):
                    texto_membro += f"\n`Esse usuário está ouvindo algo no Spotify. Use o comando spotify para ver o que é.`"
            embed.add_field(
                name = "Informações do usuario no servidor",
                value = texto_membro
            )
            embed.color = membro.color
        await ctx.send(embed=embed)
    
    @commands.command(
        aliases = ("pfp","profilepicture","fotoperfil"),
        brief = "Mostra a foto de perfil de alguém",
        extras = {"usuário": "Id ou menção do usuário a se ver as informações",
                  "exemplos": ("<@531508181654962197>", "531508181654962197")}
    )
    @commands.bot_has_permissions(embed_links = True)
    async def avatar(self, ctx, usuário: discord.User = None):
        """Mostra a foto de perfil de alguém. Você também tera a opção de baixa-la em alguns formatos."""
        usuário = usuário or ctx.author
        description = "Faça download em:\n"
        url_png = usuário.display_avatar.with_format("png").url
        description += f"[PNG]({url_png})"
        url_jpg = usuário.display_avatar.with_format("jpg").url
        description += f" - [JPG]({url_jpg})"
        url_webp = usuário.display_avatar.with_format("webp").url
        description += f" - [WEBP]({url_webp})"
        if usuário.display_avatar.is_animated():
            url_gif = usuário.display_avatar.with_format("gif").url
            description += f" - [GIF]({url_gif})"
        embed = discord.Embed(
            title = f"Exibindo avatar de {usuário}",
            description = description,
            timestamp = discord.utils.utcnow()
        ).set_image(
            url = usuário.display_avatar.with_static_format("png").url
        )
        await ctx.send(embed=embed)
    
    @commands.command(
        aliases = ("b", "capa", "cover"),
        brief = "Mostra o banner de alguém",
        extras = {"usuário": "Id ou menção do usuário a se ver as informações",
                  "exemplos": ("<@531508181654962197>", "531508181654962197")}
    )
    @commands.bot_has_permissions(embed_links = True)
    async def banner(self, ctx, usuário: discord.User = None):
        """Mostra o banner de alguém. Você também tera a opção de baixa-lo em alguns formatos."""
        usuário = usuário or ctx.author
        if not usuário.banner:
            return await ctx.send("O usuário que você me passou não tem um banner.")
        description = "Faça download em:\n"
        url_png = usuário.banner.with_format("png").url
        description += f"[PNG]({url_png})"
        url_jpg = usuário.banner.with_format("jpg").url
        description += f" - [JPG]({url_jpg})"
        url_webp = usuário.banner.with_format("webp").url
        description += f" - [WEBP]({url_webp})"
        if usuário.banner.is_animated():
            url_gif = usuário.banner.with_format("gif").url
            description += f" - [GIF]({url_gif})"
        embed = discord.Embed(
            title = f"Exibindo banner de {usuário}",
            description = description,
            timestamp = discord.utils.utcnow()
        ).set_image(
            url = usuário.banner.with_static_format("png").url
        )
        await ctx.send(embed=embed)
    
    @commands.command(
        aliases = ("infoservidor", "serverinfo", "infoserver", "is"),
        brief = "Mostra informações do servidor atual"
    )
    @commands.bot_has_permissions(embed_links = True)
    async def servidorinfo(self, ctx):
        """Mostra informações do servidor atual."""
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
        await ctx.send(embed = embed)
    
    @commands.command(
        aliases = ("guildicon", "iconguild", "servericon", "iconserver", "iconeservidor", "servidoricone"),
        brief = "Manda o ícone do servidor"
    )
    @commands.bot_has_permissions(embed_links = True)
    async def icone(self, ctx):
        """Manda o ícone do servidor."""
        if not ctx.guild.icon:
            return await ctx.send("Esse servidor não tem um ícone para ser mostrado.")
        description = "Faça download em:\n"
        url_png = ctx.guild.icon.with_format("png").url
        description += f"[PNG]({url_png})"
        url_jpg = ctx.guild.icon.with_format("jpg").url
        description += f" - [JPG]({url_jpg})"
        url_webp = ctx.guild.icon.with_format("webp").url
        description += f" - [WEBP]({url_webp})"
        if ctx.guild.icon.is_animated():
            url_gif = ctx.guild.icon.with_format("gif").url
            description += f" - [GIF]({url_gif})"
        embed = discord.Embed(
            title = f"Exibindo o ícone do servidor",
            description = description,
            timestamp = discord.utils.utcnow()
        ).set_image(
            url = ctx.guild.icon.with_static_format("png").url
        )
        await ctx.send(embed=embed)
    
    @commands.command(
        aliases = ("sugestao",),
        brief = "Mande uma sugestão para o bot",
        extras = {"sugestão": "Sua sugestão",
                  "exemplos": ("Melhorar o bot", "Comandos indecentes")}
    )
    @commands.dynamic_cooldown(CooldownEspecial(1, 43200), type = commands.BucketType.user)
    async def sugestão(self, ctx, *, sugestão):
        """Mande uma sugestão para o bot. Ela será enviada ao proprietário do bot, que ira ler e avaliar se será adicionada. Usar esse comando de forma indevida pode te render um banimento."""
        canal_sugestão = self.bot.get_guild(801185265363845140).get_channel(820983803035385867)
        embed = discord.Embed(
            title = f"Sugestão por {ctx.author} (ID: {ctx.author.id})",
            description = sugestão,
            color = 0x0000FF,
            timestamp = discord.utils.utcnow()
        )
        await canal_sugestão.send(embed = embed)
        await ctx.send("Sua sugestão foi enviada.")

def setup(bot):
  bot.add_cog(informações(bot))
