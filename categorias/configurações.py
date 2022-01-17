import discord
from discord.ext import commands, menus
from plugins.variaveis import ConversorTempo

import asyncio


class configurações(
    commands.Cog,
    name = "Configurações",
    description = "Essa categoria contem comandos para configurar o bot no servidor atual."
    ):
    
    def __init__(self, bot):
        self.bot = bot
        self.emoji = "\u2699\ufe0f"
    
    @commands.group(
        aliases = ("prefix", "pfx", "prefixos"),
        brief = "Lista todos os prefixos que o bot atende",
        invoke_without_command = True
    )
    async def prefixo(self, ctx):
        """Lista os prefixos que o bot atende no servidor. Também estão disponíveis dois subcomandos para adicionar e remover prefixos."""
        infos = await self.bot.database.servidores.find_one(
            {"id_servidor":ctx.guild.id}
        )
        prefixos = infos["prefixos"]
        texto = f"Olá, {ctx.author.mention}! Para me usar nesse servidor, você pode usar um dos prefixos abaixo:\n{', '.join(prefixos)}"
        await ctx.send(texto, allowed_mentions = discord.AllowedMentions(everyone = False))
    
    @prefixo.command(
        aliases = ("novo", "acrescentar"),
        brief = "Adiciona um novo prefixo",
        extras = {"prefixo": "O novo prefixo para registrar",
                  "exemplos": ("+", "--")}
    )
    @commands.has_guild_permissions(manage_guild = True)
    async def adicionar(self, ctx, prefixo):
        """Adiciona um novo prefixo para o bot atender no servidor."""
        if len(prefixo) > 15:
            return await ctx.send("O prefixo inserido é muito grande, insira um menor. (limite de caracteres: 15)")
        infos = await self.bot.database.servidores.find_one(
            {"id_servidor": ctx.guild.id}
        )
        prefixos = infos["prefixos"]
        if prefixo in prefixos:
            await ctx.send("O prefixo que você me passou ja foi adicionado.")
        elif prefixo not in prefixos:
            await self.bot.database.servidores.update_one(
                {"id_servidor": ctx.guild.id},
                {"$push":{"prefixos": prefixo}}
            )
            await self.bot.atualizar_cache(ctx.guild.id)
            await ctx.send(f"Prefixo adicionado. Agora você pode me chamar usando `{prefixo}`.", allowed_mentions = discord.AllowedMentions().none())
    
    @prefixo.command(
        aliases = ("tirar",),
        brief = "Remove um prefixo existente",
        extras = {"prefixo": "O prefixo a ser removido",
                  "exemplos": ("+", "--")}
    )
    @commands.has_guild_permissions(manage_guild = True)
    async def remover(self, ctx, prefixo):
        """Remove um prefixo para o bot não atende-lo mais no servidor."""
        infos = await self.bot.database.servidores.find_one(
            {"id_servidor": ctx.guild.id}
        )
        prefixos = infos["prefixos"]
        if len(prefixos) == 1:
            await ctx.send("Você não pode remover meu último prefixo!")
        elif prefixo not in prefixos:
            await ctx.send("O prefixo que você quer remover não foi registrado ainda.")
        elif prefixo in prefixos:
            await self.bot.database.servidores.update_one(
                {"id_servidor": ctx.guild.id},
                {"$pull":{"prefixos":prefixo}}
            )
            await self.bot.atualizar_cache(ctx.guild.id)
            await ctx.send("prefixo removido!")
    
    @commands.group(
        aliases = ("autor","arespostas","aresp","ar"),
        brief = "Mostra as autorespostas registradas",
        invoke_without_command = True
    )
    @commands.bot_has_permissions(embed_links = True)
    async def autorespostas(self, ctx):
        """Mostra as autorespostas do servidor. Existem também alguns subcomandos para gerencia-las."""
        infos = await self.bot.database.servidores.find_one(
            {"id_servidor": ctx.guild.id}
        )
        autorespostas = infos["auto_respostas"]
        if len(autorespostas) == 0:
            await ctx.send("Infelizmente ainda não existem autorespostas adicionadas nesse servidor... Que tal adicionar uma com o comando \"autorespostas adicionar\"?")
        else:
            lista_embeds = []
            for gatilho in autorespostas:
                embed = discord.Embed(
                    title = "Exibindo autorespostas do servidor",
                    description = f"**Gatilho:** {gatilho}\n**Resposta**: {autorespostas[gatilho]}",
                    timestamp = discord.utils.utcnow()
                )
                lista_embeds.append(embed)
            paginador = self.bot.paginador(lista_embeds, 180, ctx)
            await paginador.começar()
    
    @autorespostas.command(
        aliases = ("nova","acrescentar"),
        name = "adicionar",
        brief = "Acrescenta uma nova autoresposta",
        extras = {"gatilho": "O gatilho que irá ativar a resposta", 
                  "resposta": "A resposta que será enviada",
                  "exemplos": ("bot Estou aqui!","\"bom dia\" Bom dia nada, tá de noite", "\"eu vou\" Não vai não")}
    )
    @commands.has_guild_permissions(manage_messages = True)
    async def adicionarautoresposta(self, ctx, gatilho, *,resposta):
        """Acrescenta um novo gatilho e uma nova resposta para o bot responder. Os gatilhos são convertidos para letras minúsculas, pois as mensagens também são."""
        if len(gatilho) > 30:
            return await ctx.send("O gatilho inserido é muito longo (limite de caracteres: 30)")
        elif len(resposta) > 2000:
            return await ctx.send("A resposta inserida é muito longa (limite de caracteres: 2000)")
        infos = await self.bot.database.servidores.find_one(
            {"id_servidor": ctx.guild.id}
        )
        autorespostas = infos["auto_respostas"]
        if gatilho.lower() not in autorespostas:
            await self.bot.database.servidores.update_one(
                {"id_servidor": ctx.guild.id},
                {"$set":{f"auto_respostas.{gatilho.lower()}": resposta}}
            )
            await self.bot.atualizar_cache(ctx.guild.id)
            await ctx.send(f"Registrado com sucesso!\n**Novo gatilho**:\n{gatilho.lower()}\n**Nova resposta**:\n{resposta}", allowed_mentions = discord.AllowedMentions(everyone = False))
        elif gatilho.lower() in autorespostas:
            await ctx.send("Esse gatilho já está registrado!")
    
    @autorespostas.command(
        aliases = ("tirar",),
        name = "remover",
        brief = "Remove uma autoresposta",
        extras = {"gatilho": "O gatilho que irá ser excluido",
                  "exemplos": ("bot", "bom dia")}
    )
    @commands.has_guild_permissions(manage_messages = True)
    async def removerautoresposta(self, ctx, *,gatilho):
        """Remove um gatilho e sua resposta equivalente."""
        infos = await self.bot.database.servidores.find_one(
            {"id_servidor": ctx.guild.id}
        )
        autorespostas = infos["auto_respostas"]
        if gatilho.lower() not in autorespostas:
            await ctx.send("O gatilho passado não está registrado.")
        elif gatilho.lower() in autorespostas:
            await self.bot.database.servidores.update_one(
                {"id_servidor": ctx.guild.id},
                {"$unset":{f"auto_respostas.{gatilho.lower()}": ""}}
            )
            await self.bot.atualizar_cache(ctx.guild.id)
            await ctx.send(f"O gatilho `{gatilho.lower()}` foi removido.", allowed_mentions = discord.AllowedMentions().none())
    
    @autorespostas.command(
        aliases = ("deletarresposta",),
        brief = "Habilita ou desabilita que as respostas sejam apagadas",
        extras = {"tempo": "O tempo para esperar antes de apagar a resposta. Se for inserido 0 elas não serão apagadas",
                  "exemplos": ("2m 15s", "40s")}
    )
    @commands.has_guild_permissions(manage_messages = True)
    async def apagarresposta(self, ctx, *tempo: ConversorTempo):
        """Habilita ou desabilita que as respostas enviadas sejam apagadas. O tempo é o tempo que o bot ira esperar (em segundos) antes de apagar a mensagem. Caso esse valor seja 0, então nenhuma mensagem será apagada."""
        tempo = sum(tempo)
        await self.bot.database.servidores.update_one(
            {"id_servidor": ctx.guild.id},
            {"$set": {"auto_respostas_apagar": tempo}}
        )
        await self.bot.atualizar_cache(ctx.guild.id)
        if tempo == 0:
            await ctx.send("Agora as respostas enviadas não serão apagadas.")
        elif tempo > 0:
            await ctx.send(f"Agora as respostas serão apagadas após o tempo determinado depois de seu envio.")
    
    @autorespostas.command(
        aliases = ("limpar", "limparmensagens"),
        brief = "Deleta respostas enviadas pelo bot",
        extras = {"numero": "O número de mensagens para se procurar por respostas",
                  "exemplos": ("20", "15")}
    )
    #@commands.has_permissions(manage_messages = True)
    @commands.max_concurrency(1, commands.BucketType.channel)
    async def limparrespostas(self, ctx, numero: int):
        """Deleta respostas enviadas pelo bot. É usada aqui a mesma lógica do comando de purge, então se atente ao numero inserido."""
        if numero <= 0:
            return await ctx.send("Me de um numero maior do que zero.")
        infos = await self.bot.database.servidores.find_one(
            {"id_servidor": ctx.guild.id}
        )
        check = lambda m: m.content in infos["auto_respostas"].values() and m.author.id == ctx.guild.me.id
        try:
            await ctx.message.delete()
        except:
            pass
        lista = await ctx.channel.purge(limit = numero, check = check)
        if len(lista) == 0:
            await ctx.send("Não deletei nenhuma resposta. Se esse não foi o resultado esperado, tente novamente com um numero maior.")
        else:
            await ctx.send(f"Foram deletadas {len(lista)} respostas.", delete_after = 5)
    
    @commands.command(
        aliases = ("desabilitarcomando", "desligarcomando"),
        brief = "Desativa um comando no servidor",
        extras = {"comando": "O comando que deve ser desabilitado",
                  "exemplos": ("genius", "mal animeinfo")}
    )
    @commands.has_guild_permissions(manage_guild = True)
    async def desativarcomando(self, ctx, *,comando):
        """Desativa um comando no servidor. Por razões obvias, não é possivel desabilitar o comando de ativar ou desativar comandos.
        Se você desativar um grupo de comandos, todos seus subcomandos serão desativados. Porém, ainda é possivel desativar apenas um subcomando"""
        comando = self.bot.get_command(comando)
        if comando:
            if comando == self.bot.get_command("desativarcomando") or comando == self.bot.get_command("ativarcomando"):
                await ctx.send("Ei! Você não pode desativar os comandos que ativam ou desativam comandos!")
                return
            infos = await self.bot.database.servidores.find_one(
                {"id_servidor": ctx.guild.id}
            )
            comandos_desativados = infos["comandos_desativados"]
            if comando.qualified_name in comandos_desativados:
                await ctx.send("O comando que você queria desativar já está desativado.")
            elif comando.qualified_name not in comandos_desativados:
                await self.bot.database.servidores.update_one(
                    {"id_servidor": ctx.guild.id},
                    {"$push": {"comandos_desativados": comando.qualified_name}}
                )
                await self.bot.atualizar_cache(ctx.guild.id)
                await ctx.send(f"O comando {comando.qualified_name} foi desativado")
        else:
            await ctx.send("Comando inválido. Verifique sua ortografia.")
    
    @commands.command(
        aliases = ("habilitarcomando", "ligarcomando"),
        brief = "Ativa um comando no servidor",
        extras = {"comando": "O comando a ser ativado",
                  "exemplos": ("genius", "mal animeinfo")}
    )
    @commands.has_guild_permissions(manage_guild = True)
    async def ativarcomando(self, ctx, *,comando):
        """Ativa um comando no servidor. Se um grupo de comandos **e** um subcomando estavam desativados e o grupo for ativado, o subcomando ainda estará desativado."""
        comando = self.bot.get_command(comando)
        if comando:
            infos = await self.bot.database.servidores.find_one(
                {"id_servidor": ctx.guild.id}
            )
            comandos_desativados = infos["comandos_desativados"]
            if comando.qualified_name in comandos_desativados:
                await self.bot.database.servidores.update_one(
                    {"id_servidor": ctx.guild.id},
                    {"$pull": {"comandos_desativados": comando.qualified_name}}
                )
                await self.bot.atualizar_cache(ctx.guild.id)
                await ctx.send(f"O comando {comando.qualified_name} foi ativado novamente.")
            else:
                await ctx.send("O comando que voce passou nao esta desativado.")
        else:
            await ctx.send("Comando invalido. Verifique sua ortografia.")
    
    @commands.command()
    async def comandosdesativados(self, ctx):
        """Mostra os comandos desativados do servidor"""
        infos = await self.bot.database.servidores.find_one(
            {"id_servidor": ctx.guild.id}
        )
        comandos_desativados = infos["comandos_desativados"]
        if len(comandos_desativados) == 0:
            await ctx.send("Nenhum comando foi desativado nesse servidor.")
        else:
            embed = discord.Embed(
                title = "Comandos Desativados",
                description = "Os comandos desativados para esse servidor são:\n" + "\n".join(comandos_desativados),
                timestamp = discord.utils.utcnow()
            )
            await ctx.send(embed = embed)
    
    @commands.command(
        aliases = ("ignorarcanal", "desabilitarcanal", "dc"),
        brief = "Faz o bot deixar de detectar comandos em um canal",
        extras = {"canal": "O canal para ser ignorado",
                  "exemplos": ("#conversitas", "719619736836505644")}
    )
    @commands.has_guild_permissions(manage_guild = True)
    async def desativarcanal(self, ctx, canal: discord.TextChannel):
        """Faz o bot deixar de detectar comandos em  um canal. Ele ainda irá responder a autorespostas nesse canal."""
        infos = await self.bot.database.servidores.find_one(
            {"id_servidor": ctx.guild.id}
        )
        canais_desativados = infos["canais_desativados"]
        if canal.id in canais_desativados:
            await ctx.send("Esse canal já está sendo ignorado.")
        else:
            if len(canais_desativados) == len(ctx.guild.text_channels)-1:
                await ctx.send("Você não pode ignorar todos os canais!")
            else:
                await self.bot.database.servidores.update_one(
                    {"id_servidor": ctx.guild.id},
                    {"$push": {"canais_desativados": canal.id}}
                )
                await self.bot.atualizar_cache(ctx.guild.id)
                await ctx.send(f"Pronto! Agora o canal {canal.mention} está sendo ignorado.")
    
    @commands.command(
        aliases = ("habilitarcanal", "ac"),
        brief = "Faz o bot voltar a responder comandos em um canal",
        extras = {"canal": "O canal para deixar de ser ignorado",
                  "exemplos": ("#conversitas", "719619736836505644")}
    )
    @commands.has_guild_permissions(manage_guild = True)
    async def ativarcanal(self, ctx, canal: discord.TextChannel):
        """Faz o bot voltar a responder comandos em um canal."""
        infos = await self.bot.database.servidores.find_one(
            {"id_servidor": ctx.guild.id}
        )
        canais_desativados = infos["canais_desativados"]
        if canal.id not in canais_desativados:
            await ctx.send("Esse canal não estava sendo ignorado.")
        else:
            await self.bot.database.servidores.update_one(
                {"id_servidor": ctx.guild.id},
                {"$pull": {"canais_desativados": canal.id}}
            )
            await self.bot.atualizar_cache(ctx.guild.id)
            await ctx.send(f"Pronto! O canal {canal.mention} não sera mais ignorado.")
    
    @commands.command()
    @commands.bot_has_permissions(embed_links = True)
    async def canaisdesativados(self, ctx):
        """Mostra os canais desativados de um servidor"""
        infos = await self.bot.database.servidores.find_one(
            {"id_servidor": ctx.guild.id}
        )
        canais_desativados = infos["canais_desativados"]
        if len(canais_desativados) == 0:
            await ctx.send("Esse servidor não desativou nenhum canal ainda.")
        else:
            texto = "Os canais desativados para esse servidor são:\n"
            lista_atualizada = list(filter(lambda id: discord.utils.get(ctx.guild.channels, id = id) is not None, canais_desativados))
            if lista_atualizada != canais_desativados:
                await self.bot.database.servidores.update_one(
                    {"id_servidor": ctx.guild.id},
                    {"$set": {"canais_desativados": lista_atualizada}}
                )
                await self.bot.atualizar_cache(ctx.guild.id)
                canais_desativados = lista_atualizada
            texto += "\n".join([ctx.guild.get_channel(id).mention for id in canais_desativados])
            embed = discord.Embed(
                title = "Canais desativados",
                description = texto,
                timestamp = discord.utils.utcnow()
            )
            await ctx.send(embed = embed)

def setup(bot):
    bot.add_cog(configurações(bot))
