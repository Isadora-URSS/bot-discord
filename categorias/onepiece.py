import discord
from discord.ext import commands, tasks
from plugins.variaveis import CooldownEspecial, CooldownHaki1, ConversorTempo
import pytz

import asyncio

class onepiece(
    commands.Cog, 
    name = "One Piece", 
    description = "Essa categoria contem comandos relacionados a One Piece, como poderes de Akuma no Mi."
):
    def __init__(self, bot):
        self.bot = bot
        self.emoji = "<:ChapeusDePalha:821012793666699294>"
        self.loop_mute.start()
    
    def cog_unload(self):
        self.loop_mute.stop()
    
    @commands.command(
        aliases = ("haki1","hakiobservação","hakidaobservacao","hakiobservacao","hakio", "hdo"),
        brief = "Manda a última mensagem apagada do servidor"
    )
    @commands.dynamic_cooldown(CooldownHaki1(1, 3600), commands.BucketType.member)
    @commands.bot_has_permissions(embed_links = True)
    async def hakidaobservação(self, ctx):
        """Manda a última mensagem apagada do servidor."""
        infos = await self.bot.database.servidores.find_one(
            {"id_servidor": ctx.guild.id}
        )
        deletada = infos["haki_observacao"]
        embed = discord.Embed(
            title = f"{ctx.author.name} usou o HAKI DA OBSERVAÇÃO!",
            description = f"O haki permitiu que ele detectasse a mensagem apagada:\n{deletada}",
            color = 0x0403e5,
            timestamp = discord.utils.utcnow()
        ).set_image(
            url = "https://cdn.discordapp.com/attachments/803443536363913236/807630862161412146/Hakidaobservacao.gif"
        ).set_footer(
            text = "One Piece - Eiichiro Oda", 
            icon_url = "https://cdn.discordapp.com/attachments/803443536363913236/820486652476522506/strawhat_pirates_jolly_roger.png"
        )
        await ctx.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_message_delete(self, mensagem):
        if mensagem.guild == None:
            return
        conteudo = mensagem.content
        if mensagem.author.id == self.bot.user.id and conteudo in tuple(self.bot.cache[mensagem.guild.id]["auto_respostas"].values()):
            return
        if len(conteudo) > 1500:
            conteudo = conteudo[0:1500] + "...(mensagem cortada)"
        data = f"<t:{int(mensagem.created_at.timestamp())}> (<t:{int(mensagem.created_at.timestamp())}:R>)"
        texto = f"Autor: {mensagem.author}\n"\
        f"Canal: {mensagem.channel}\n"\
        f"Data: {data}\n"\
        f"Conteúdo: {conteudo}"
        if len(mensagem.embeds) != 0:
            texto += f"\n**A mensagem continha {len(mensagem.embeds)} embeds.**"
        await self.bot.database.servidores.update_one(
            {"id_servidor": mensagem.guild.id},
            {"$set":{"haki_observacao": texto}}
        )
    
    @commands.command(
        aliases = ("hakirei", "haki3", "hdr", "hakir", "theworld", "zawarudo"),
        brief = "Bloqueia o canal por um tempo determinado",
        extras = {"tempo": "O tempo para bloquear o canal",
                  "exemplos": ("", "20")}
    )
    @commands.max_concurrency(1, commands.BucketType.channel)
    @commands.has_permissions(manage_channels = True)
    @commands.bot_has_permissions(manage_channels = True, embed_links = True)
    async def hakidorei(self, ctx, tempo: int = 10):
        """Bloqueia o canal por um tempo determinado. Talvez esse comando seja diferente dependendo de como você usar ele..."""
        permissoes_padrao = ctx.channel.overwrites_for(ctx.guild.default_role)
        permissoes_alteradas = ctx.channel.overwrites_for(ctx.guild.default_role)
        permissoes_alteradas.send_messages = False
        permissoes_alteradas.send_messages_in_threads = False
        if ctx.invoked_with == "theworld" or ctx.invoked_with == "zawarudo":
            embed = discord.Embed(
                title = f"{ctx.author} usou o ZA WARUDO",
                description = f"O stand congelou o tempo por {tempo} segundos!",
                color = 0xCB9B19,
                timestamp = discord.utils.utcnow()
            ).set_image(
                url = "https://cdn.discordapp.com/attachments/803443536363913236/843318919182811166/Za_Warudo.gif"
            ).set_footer(
                text = "JoJo's Bizarre Adventures - Hirohiko Araki"
            )
        else:
            embed = discord.Embed(
                title = f"{ctx.author} usou o HAKI DO REI!",
                description = f"os membros estão atordoados por {tempo} segundos!",
                color = 0xFF1010,
                timestamp = discord.utils.utcnow()
            ).set_image(
                url = "https://cdn.discordapp.com/attachments/803443536363913236/807634729347317790/Haki_do_Rei.gif"
            ).set_footer(
                text = "One Piece - Eiichiro Oda",
                icon_url = "https://cdn.discordapp.com/attachments/803443536363913236/820486652476522506/strawhat_pirates_jolly_roger.png"
            )
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite = permissoes_alteradas)
        mensagem = await ctx.send(embed = embed)
        if ctx.invoked_with == "theworld" or ctx.invoked_with == "zawarudo":
            embed.description = "O tempo voltou a fluir normalmente."
        else:
            embed.description = "Os efeitos do haki acabaram e ninguem está atordoado mais."
        await asyncio.sleep(tempo)
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite = permissoes_padrao)
        await mensagem.edit(embed = embed)
    
    @commands.command(
        aliases = ("manemane", "forcesay", "manenomi"),
        brief = "Envia uma mensagem que se passa por outra pessoa",
        extras = {"alvo": "O membro a se passar por", 
                  "mensagem": "A mensagem que ele dirá",
                  "exemplos": ("<@531508181654962197> Eu sou um impostor", "531508181654962197 This is sus", "<@815405417345712170> Olá")}
    )
    @commands.dynamic_cooldown(CooldownEspecial(2, 1800), type = commands.BucketType.member)
    @commands.has_guild_permissions(manage_messages = True)
    @commands.bot_has_permissions(manage_webhooks = True, embed_links = True)
    async def manemanenomi(self, ctx, alvo: discord.Member, *, mensagem):
        """Envia uma mensagem que se passa por outra pessoa. A mensagem enviada será marcada como enviada por um bot no discord devido a ferramenta usada para enviar a mensagem."""
        embed = discord.Embed(
            title = f"{ctx.author} usou os poderes da MANE MANE NO MI!",
            description = f"Com esses poderes, ele se disfarçou de {alvo}.",
            color = 0xFFFFFF,
            timestamp = discord.utils.utcnow()
        ).set_image(
            url = "https://cdn.discordapp.com/attachments/803443536363913236/807264829453631498/giphy.gif"
        ).set_footer(
            text = "One Piece - Eiichiro Oda", 
            icon_url = "https://cdn.discordapp.com/attachments/803443536363913236/820486652476522506/strawhat_pirates_jolly_roger.png"
        )
        msg = await ctx.send(embed = embed)
        webhook = await ctx.channel.create_webhook(name = "manemanenomi")
        await webhook.send(mensagem, username = str(alvo).split("#")[0], avatar_url = alvo.avatar.url, allowed_mentions = discord.AllowedMentions.none())
        await webhook.delete()
        await asyncio.sleep(60)
        try:
            await msg.delete()
        except:
            pass
    
    @commands.command(
        aliases = ("zushizushi", "gravidade", "zushinomi", "zzm"),
        brief = "Revira as mensagens enviadas no chat"
    )
    @commands.max_concurrency(1, commands.BucketType.channel)
    @commands.has_permissions(manage_messages = True)
    @commands.bot_has_permissions(manage_webhooks = True, manage_messages = True, embed_links = True)
    async def zushizushinomi(self, ctx):
        """Revira as mensagens enviadas no chat. O envio de mensagens reviradas usa o mesmo tipo de mensagem do comando manemanenomi."""
        embed = discord.Embed(
            title = f"{ctx.author} usou a ZUSHI ZUSHI NO MI!",
            description = "Ele está usando a gravidade para revirar as mensagens do chat!",
            color = 0x9D4BC2,
            timestamp = discord.utils.utcnow()
        ).set_image(
            url = "https://cdn.discordapp.com/attachments/803443536363913236/807263511167500299/db8ed1230a658476901cadd84ac8b3d07cd8b455_00.gif"
        ).set_footer(
            text = "One Piece - Eiichiro Oda",
            icon_url = "https://cdn.discordapp.com/attachments/803443536363913236/820486652476522506/strawhat_pirates_jolly_roger.png"
        )
        mensagem_embed = await ctx.send(embed=embed)
        embed.description = "Ele deixou de exercer o poder da gravidade e o chat voltou ao normal."
        check = lambda x: x.channel == ctx.channel and x.guild == ctx.guild and not x.author.bot
        webhook = await ctx.channel.create_webhook(name = "zushizushinomi")
        for i in range(10):
            try:
                mensagem = await self.bot.wait_for("message", timeout = 15.0, check=check)
            except asyncio.TimeoutError:
                break
            await mensagem.delete()
            await webhook.send(
                mensagem.content[::-1],
                username = str(mensagem.author).split("#")[0],
                avatar_url = mensagem.author.avatar.url,
                allowed_mentions = discord.AllowedMentions.none()
            )
        await webhook.delete()
        try:
            await mensagem_embed.edit(embed = embed)
        except:
            pass
    
    @commands.command(
        aliases = ("noronoro", "noronoronobeam", "noronomi", "noronobeam", "nnm", "slowmode"),
        brief = "Muda o tempo do modo lento do canal",
        extras = {"delay": "O tempo em segundos do modo lento", 
                  "canal": "O canal para se modificar. o Padrão é o canal que o comando foi usado.",
                  "exemplos": ("15s", "3h 45m 719619736836505644", "15s #conversitas")}
    )
    @commands.has_permissions(manage_channels = True)
    @commands.bot_has_permissions(manage_channels = True, embed_links = True)
    async def noronoronomi(self, ctx, delay: commands.Greedy[ConversorTempo], canal: discord.TextChannel = None):
        """Muda o tempo do modo lento do canal. O maximo permitido são seis horas (21600 segundos). Usar um tempo 0 desativa o modo lento."""
        delay = sum(delay)
        if delay > 21600:
            delay = 21600
        if canal == None:
            canal = ctx.channel
        embed = discord.Embed(
            title = f"{ctx.author} usou a NORO NORO NO MI!",
            description = f"Devido ao noro noro no beam, agora todos terão uum deeeelaaay deee {delay} seguuuuuuundos paaaaaaara caadaaa mensaaaaageeeeemm...",
            color = 0x00DBFF,
            timestamp = discord.utils.utcnow()
        ).set_image(
            url = "https://cdn.discordapp.com/attachments/803443536363913236/813202241963687966/Tumblr_mdlat6tCdk1rq9ifuo1_500.gif"
        ).set_footer(
            text = "One Piece - Eiichiro Oda",
            icon_url = "https://cdn.discordapp.com/attachments/803443536363913236/820486652476522506/strawhat_pirates_jolly_roger.png"
        )
        await canal.edit(slowmode_delay = delay)
        await ctx.send(embed=embed)
    
    @commands.command(
        aliases = ("yamiyami", "yym", "yaminomi", "blackhole", "bh", "purge"),
        brief = "Deleta um número fornecido de mensagens no canal",
        extras = {"quantidade": "O numero de mensagens a serem verificadas", 
                  "usuarios": "Os usuários para se deletar as mensagens.",
                  "exemplos": ("87", "87 531508181654962197", "25 <@531508181654962197> @usuario2")}
    )
    @commands.max_concurrency(1, commands.BucketType.channel)
    @commands.has_permissions(manage_messages = True)
    @commands.bot_has_permissions(manage_messages = True, embed_links = True)
    async def yamiyaminomi(self, ctx, quantidade: int, usuarios: commands.Greedy[discord.User] = None):
        """Deleta um número fornecido de mensagens do canal. Em casos das mensagens serem de um ou mais usuários especificos, o número passado valerá o número de mensagens verificadas, e não deletadas. Por exemplo, se o número passado for 10 e apenas 6 mensagens das 10 ultimas forem dos usuarios, apenas essas 6 serão deletadas. Mensagens de mais de 14 dias atráss não poderão ser deletadas também."""
        if quantidade < 1:
            return await ctx.send("Passe um número de mensagens para serem deletadas!")
        if quantidade > 200:
            return await ctx.send("Para evitar raids, o número máximo de mensagens apagadas foi limitado a 200.")
        if usuarios == None:
            await ctx.message.delete()
            lista = await ctx.channel.purge(limit = quantidade, bulk = True)
            description = f"Ele usou o black hole para sugar {len(lista)} mensagens para a escuridão!"
        else:
            await ctx.message.delete()
            lista = await ctx.channel.purge(limit = quantidade, bulk = True, check = lambda m: m.author.id in [i.id for i in usuario])
            description = f"Ele usou o black hole para sugar {len(lista)} mensagens enviadas por {len(usuarios)} usuários para a escuridão!"
        embed = discord.Embed(
            title = f"{ctx.author} usou a YAMI YAMI NO MI!",
            description = description,
            color = 0x101010,
            timestamp = discord.utils.utcnow()
        ).set_image(
            url = "https://cdn.discordapp.com/attachments/803443536363913236/806367717534990346/202ce163eb30ca9c249066c238441f1e15651407_hq.gif"
        ).set_footer(
            text = "One Piece - Eiichiro Oda",
            icon_url = "https://cdn.discordapp.com/attachments/803443536363913236/820486652476522506/strawhat_pirates_jolly_roger.png"
        )
        await ctx.send(embed = embed)

    @commands.command(
        aliases = ("mute", "mutar", "silenciar"),
        brief = "Silencia um membro",
        extras = {"alvo": "O usuario a ser silenciado",
                  "tempo": "O tempo para que ele fique silenciado",
                  "motivo": " O motivo para o registro de auditoria",
                  "exemplos": ("<@531508181654962197>", "<@531508181654962197> 5d", "531508181654962197 Infringiu a constituição brasileira", "<@531508181654962197> 20m Mandou copypasta da wikipedia")}
        )
    @commands.has_guild_permissions(manage_roles = True)
    @commands.bot_has_guild_permissions(manage_roles = True, embed_links = True)
    async def naginaginomi(self, ctx, alvo: discord.Member, tempo: commands.Greedy[ConversorTempo], *, motivo = ""):
        """Silencia um membro, impedindo-o de enviar mensagens. Para fazer isso, o comando cria um cargo e remove a permissao de fala dele em todos os canais aos quais o bot consegue ver.
        Na primeira vez que o comando é usado, esse cargo e criado e salvo. Se no proximo uso do comando o cargo tiver sido deletado, o bot irá criar outro e realizar o mesmo processo.
        O bot armazena apenas o id do cargo, o que significa que pode-se alterar atributos como nome e cor do mesmo. Se a permissão especial de um canal for deletada, ela não será reposta ao menos que se delete o cargo."""
        motivo = f"Silenciado por {ctx.author} (ID: {ctx.author.id}). " + motivo
        if alvo.id == ctx.author.id:
            return await ctx.send("Você não pode silenciar você mesmo.")
        cargo_autor = ctx.author.top_role
        cargo_alvo = alvo.top_role
        cargo_bot = ctx.guild.me.top_role
        if ctx.guild.roles.index(cargo_autor) <= ctx.guild.roles.index(cargo_alvo):
            return await ctx.send("Você não tem poder suficiente para silenciar essa pessoa.")
        elif ctx.guild.roles.index(cargo_bot) <= ctx.guild.roles.index(cargo_alvo):
            return await ctx.send("Eu não tenho poder o suficiente para silenciar essa pessoa.")
        elif ctx.guild.owner.id == alvo.id:
            return await ctx.send("Essa pessoa é dona do servidor.")
        infos = await self.bot.database.servidores.find_one(
            {"id_servidor": ctx.guild.id}
        )
        for dict_silenciado in infos["mutados"]:
            if dict_silenciado["id_usuario"] == alvo.id:
                return await ctx.send("O usuario que você está tentando silenciar ja foi silenciado antes.")
        id_cargo = infos["cargo_mute"]
        cargo = discord.utils.get(ctx.guild.roles, id = id_cargo)
        if not cargo:
            cargo = await ctx.guild.create_role(
                name  = "Naginagi no mi",
                color = 0x000001,
                reason = "Cargo usado para silenciamentos pelo Locomotive Bot"
            )
            await ctx.send("Configurando o cargo de silenciamento, aguarde... Isso só ocorre na primeira vez em que o comando é usado ou quando o cargo anterior tiver sido deletado (para mais informações veja a ajuda do comando).")
            for canal in ctx.guild.channels:
                await canal.set_permissions(
                    cargo,
                    send_messages = False,
                    send_messages_in_threads = False,
                    speak = False,
                    connect = False,
                    create_private_threads = False,
                    create_public_threads = False
                )
            await self.bot.database.servidores.update_one(
                {"id_servidor": ctx.guild.id},
                {"$set": {"cargo_mute": cargo.id}}
            )
        tempo = sum(tempo)
        dict_mute = {
            "id_usuario": alvo.id,
            "tempo": tempo,
            "data": discord.utils.utcnow()
        }
        await alvo.add_roles(cargo, reason = motivo)
        await self.bot.database.servidores.update_one(
            {"id_servidor": ctx.guild.id},
            {"$push": {"mutados": dict_mute}}
        )
        await self.bot.atualizar_cache(ctx.guild.id)
        embed = discord.Embed(
            title = "Usuario silenciado!",
            description = f"O usuario {alvo.mention} foi silenciado por {ctx.author.mention}.",
            color = 0x221F3D,
            timestamp = discord.utils.utcnow()
        ).set_image(
            url = "https://cdn.discordapp.com/attachments/803443536363913236/931732003961839676/calm-nagi-nagi-no-mi.gif"
        ).set_footer(
            text = "One Piece - Eiichiro Oda",
            icon_url = "https://cdn.discordapp.com/attachments/803443536363913236/820486652476522506/strawhat_pirates_jolly_roger.png"
        ).add_field(
            name = "Motivo / registro de auditoria",
            value = motivo
        )
        await ctx.send(embed = embed)
    
    @commands.command(
        aliases = ("desmute", "desmutar", "desilenciar"),
        brief = "Desilencia um usuário",
        extras = {"alvo": "A pessoa que irá poder falar normalmente",
                  "exemplos": ("<@531508181654962197>", "531508181654962197")}
    )
    @commands.has_guild_permissions(manage_roles = True)
    @commands.bot_has_guild_permissions(manage_roles = True)
    async def unmute(self, ctx, alvo: discord.Member):
        """Desilencia alguém silenciado anteriormente pelo bot. Isso é feito por base na database do bot, o que significa que um usuario silenciado sem o bot não será desilenciado mesmo que tenha o cargo de silenciamento."""
        if alvo.id == ctx.author.id:
            return await ctx.send("Você não pode silenciar você mesmo.")
        cargo_autor = ctx.author.top_role
        cargo_alvo = alvo.top_role
        cargo_bot = ctx.guild.me.top_role
        if ctx.guild.roles.index(cargo_autor) <= ctx.guild.roles.index(cargo_alvo):
            return await ctx.send("Você não tem poder suficiente para alterar essa pessoa.")
        elif ctx.guild.roles.index(cargo_bot) <= ctx.guild.roles.index(cargo_alvo):
            return await ctx.send("Eu não tenho poder o suficiente para alterar essa pessoa.")
        elif ctx.guild.owner.id == alvo.id:
            return await ctx.send("Essa pessoa é dona do servidor.")
        infos = await self.bot.database.servidores.find_one(
            {"id_servidor": ctx.guild.id}
        )
        for dict_silenciado in infos["mutados"]:
            if alvo.id == dict_silenciado["id_usuario"]:
                break
        else:
            return await ctx.send("Esse usuario não está silenciado.")
        cargo_id = infos["cargo_mute"]
        cargo = discord.utils.get(ctx.guild.roles, id = cargo_id)
        if not cargo:
            await self.bot.database.servidores.update_one(
                {"id_servidor": ctx.guild.id},
                {"$pull": {"mutados": dict_silenciado}}
            )
            await self.bot.atualizar_cache(ctx.guild.id)
            return await ctx.send("O cargo de silenciamento foi deletado, o que signfica que não é possivel desilenciar alguem que não está silenciado.")
        await alvo.remove_roles(cargo, reason = f"Silenciamento retirado por {ctx.author} (ID: {ctx.author.id})")
        await self.bot.database.servidores.update_one(
            {"id_servidor": ctx.guild.id},
            {"$pull": {"mutados": dict_silenciado}}
        )
        await self.bot.atualizar_cache(ctx.guild.id)
        await ctx.send("Usuario desilenciado.")
    
    @commands.Cog.listener()
    async def on_member_join(self, membro):
        servidor = membro.guild
        infos = await self.bot.database.servidores.find_one(
            {"id_servidor": servidor.id}
        )
        mutados = infos["mutados"]
        for dict_mute in mutados:
            if dict_mute["id_usuario"] == membro.id:
                cargo = discord.utils.get(servidor.roles, id = infos["cargo_mute"])
                try:
                    await membro.add_roles(cargo, reason = "Silenciamento automaticamente efetivado.")
                except:
                    pass

    @tasks.loop()
    async def loop_mute(self):
        for servidor_id in self.bot.cache:
            if servidor_id == 0:
                continue
            infos_servidor = self.bot.cache[servidor_id]
            for dict_mute in infos_servidor["mutados"]:
                if dict_mute['tempo'] == 0:
                    continue
                data = discord.utils.utcnow() - pytz.utc.localize(dict_mute['data'])
                segundos = int(data.total_seconds())
                if segundos > dict_mute['tempo']:
                    servidor = self.bot.get_guild(infos_servidor["id_servidor"])
                    cargo = discord.utils.get(servidor.roles, id = infos_servidor["cargo_mute"])
                    membro = servidor.get_member(dict_mute["id_usuario"])
                    try:
                        await membro.remove_roles(cargo, reason = "Silenciamento expirado.")
                    except:
                        pass
                    await self.bot.database.servidores.update_one(
                        {"id_servidor": infos_servidor["id_servidor"]},
                        {"$pull": {"mutados": dict_mute}}
                    )
                    await self.bot.atualizar_cache(infos_servidor["id_servidor"])
    
    @loop_mute.before_loop
    async def esperar(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(onepiece(bot))
