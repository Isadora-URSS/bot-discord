import discord
from discord.ext import commands
from plugins.paginador import PaginadorMenu
from plugins.variaveis import CooldownEspecial

import os
import sys

# Comentado por motivos de: Lógica confusa que não consigo melhorar # Ta mais bacana agr sla

atributos = {
    "name": "ajuda",
    "aliases": ("help", "a", "info", "about"),
    "help": "Manda uma mensagem de ajuda sobre o bot, que lista os comandos dele. A mensagem também tem outras informações úteis, como o link de convite e do servidor de suporte.",
    "brief": "Manda uma mensagem de ajuda sobre o bot",
    "extras": {"command": "O comando ou categoria para ver informações.", "exemplos": ("hakidorei", "Configurações")},
    "cooldown": commands.DynamicCooldownMapping(CooldownEspecial(3, 40), commands.BucketType.user)
}

class seleção(discord.ui.Select):
    """Classe que representa o menu expandivel com a lista de categorias"""
    def __init__(self, dict_categorias):
        super().__init__(
                placeholder = "Selecione uma categoria...",
                min_values = 1,
                max_values = 1,
                row = 0
            )
        self.dict_categorias = dict_categorias
        for categoria in dict_categorias:
            """Adiciona opções baseadas na lista de categorias (dict)"""
            self.add_option(
                label = getattr(categoria, "qualified_name", "Sumario"),
                value = getattr(categoria, "qualified_name", "Sumario"),
                description = getattr(categoria, "description", "Sumario com a visão geral do bot e de cada categoria."),
                emoji = getattr(categoria, "emoji", "\U0001f44b")
            )
        
    async def callback(self, interação):
        escolhida = self.values[0]
        categoria = self.view.ctx.bot.get_cog(escolhida) # Obtem o objeto de categoria
        self.view.lista_embeds = self.dict_categorias[categoria] # # Obtem a respectiva lista de embeds e muda a lista controlada pelos botṍes
        self.view.posição = 0 # Muda a posição para o primeiro embed por padrão
        await self.view.mostrar_pagina(interação) # Chama o metodo master para mudar paginas

class ajuda(commands.HelpCommand):
    def __init__(self):
        super().__init__(verify_checks = False, command_attrs = atributos)
        self.dict_buckets = {
            commands.BucketType.default: "base global",
            commands.BucketType.user: "usuário",
            commands.BucketType.guild: "servidor",
            commands.BucketType.channel: "canal",
            commands.BucketType.member: "membro",
            commands.BucketType.category: "categoria",
            commands.BucketType.role: "cargo"
        }
    
    async def prepare_help_command(self, ctx, command = None):
        self.autor = ctx.author
        self.timestamp = discord.utils.utcnow()
        self.paginador = ctx.bot.paginador
        self.paginadorAjuda = PaginadorMenu
    
    async def embed_comando(self, comando):
        try:
            pode_usar = await comando.can_run(self.context)
        except:
            pode_usar = False
        embed = discord.Embed(
            title = f"Exibindo informações do comando **{comando}**",
            description = (comando.help or comando.short_doc) + ("" if pode_usar else "\n**Você (ou o bot) não tem as permissões necessárias para usar esse comando.**"),
            timestamp = self.timestamp
        ).set_author(
            name = self.autor,
            icon_url = self.autor.avatar.url
        ).set_footer(
            text = f"<argumento obrigatório> | [argumento opcional] | Reporte erros no servidor de suporte."
        )
        if comando.aliases:
            embed.add_field(
                name = "__Sinônimos__",
                value = ", ".join(comando.aliases),
                inline = False
            )
        if comando.clean_params:
            uso = f"{comando} {comando.signature}"
            uso += "".join(["\n" + parametro + ": " + comando.extras.get(parametro, "Esse parâmetro não tem uma descrição") for parametro in comando.clean_params])
            embed.add_field(
                name = "__Uso__",
                value = uso
            )
            embed.add_field(
                name = "__Exemplos__",
                value = f"{comando.qualified_name} " + f"\n{comando.qualified_name} ".join(comando.extras['exemplos'])
            )
        if isinstance(comando._buckets, commands.DynamicCooldownMapping):
            cooldown = comando._buckets
            if isinstance(comando._buckets._factory, CooldownEspecial):
                info_cooldown = f"**Usos permitidos:** {cooldown._factory.rate} "\
                f"{'vez' if cooldown._factory.rate == 1 else 'vezes'} em intervalos de {cooldown._factory.per} segundos"\
                f" por {self.dict_buckets[cooldown._type]}. {cooldown._factory.info}\n**Nas condições atuais, o cooldown está aplicado?** "
                try:
                    pode_rodar = comando.get_cooldown_retry_after(self.context)
                except:
                    info_cooldown += "Este cooldown não se aplica a você."
                else:
                    info_cooldown += ("Não." if pode_rodar == 0.0 else f"Sim, será liberado em {round(pode_rodar, 2)}s.")
                embed.add_field(
                    name = "__Cooldown__",
                    value = info_cooldown,
                    inline = False
                )
        if comando._max_concurrency:
            embed.add_field(
                name = "__Usos máximos simultâneos__",
                value = f"Esse comando permite {comando._max_concurrency.number} " + ("uso simultâneo por " if comando._max_concurrency.number == 1 else "usos simultâneos por ") + self.dict_buckets[comando._max_concurrency.per] + ".",
                inline = False
            )
        if isinstance(comando, commands.Group):
            embed.add_field(
                name = "__Subcomandos__",
                value = "\n".join([subcomando.full_parent_name + " " + subcomando.name for subcomando in filter(lambda c: not c.hidden, comando.commands)])
            )
        return embed
    
    def resumo_comando(self, comando):
        resumo = (f"`{comando} {comando.signature}`:" if comando.signature else f"`{comando}`:") + f" {comando.short_doc or comando.help}"
        if isinstance(comando, commands.Group):
            resumo += "".join([f"\n→ `{subcomando}`: {subcomando.short_doc or subcomando.help}" for subcomando in filter(lambda c: not c.hidden, comando.commands)])
        return resumo
    
    async def send_bot_help(self, mapa_comandos):
        """------------------Essa função é relativamente simples, mas me gera confusão.------------------
        O objeto final passado para o paginador será uma lista de embeds e para o menu sera um dicionario
        contendo listas de embeds. Para isso, a lista e o dict são criados. Na iteração das categorias, o
        dicionario é incrementado com a categoria e seus embeds, e a lista principal é incrementada com o
        embed da categoria. Ao fim, o embed de súmario é construído e inserido na lista. A lista então  é
        inserida no dict com chave None, e os dois objetos desejados estão prontos."""
        lista_embeds = [] # Lista que alimentará o paginador
        dict_categorias = {} # dicionario de categorias -> lista de embeds relacionados a categoria
        for categoria, lista_comandos in mapa_comandos.items():
            lista_comandos = tuple(filter(lambda c: not c.hidden, lista_comandos))
            if (not lista_comandos) or (not categoria) or categoria.qualified_name == "Desenvolvimento":
                """Retorna se a categoria não for mostrável"""
                continue
            descrições = "\n".join([self.resumo_comando(c) for c in lista_comandos]) # Faz uma lista de resumos (por algum motivo não pode ser feito na criação do embed)
            embed = discord.Embed(
                title = f"Exibindo categoria **{categoria.qualified_name} {categoria.emoji}**",
                description = f"{categoria.description}\n\n__**Lista de Comandos**__\n{descrições}",
                timestamp = self.timestamp
            ).set_author(
                name = self.autor,
                icon_url = self.autor.avatar.url
            )
            lista_embeds.append(embed) # Coloca na lista de embeds
            dict_categorias[categoria] = [await self.embed_comando(comando) for comando in lista_comandos]
            dict_categorias[categoria].insert(0, embed)

        embed = discord.Embed(               
            title = "LOCOMOTIVE BOT - Ajuda",
            description = f"[Suporte]({os.getenv('link_suporte')}) - {os.getenv('bot_dev')} - [Convite do bot]({os.getenv('link_convite')})",
            timestamp = self.timestamp
        ).set_author(
            name = self.autor,
            icon_url = self.autor.avatar.url
        ).add_field(
            name = f"Informações do sistema",
            value = f"```\nPython {sys.version}\nDiscord.py {discord.__version__}\n```",
            inline = False
        ).add_field(
            name = "Categorias",
            value = "\n".join([f"{categoria.qualified_name} {categoria.emoji} - {len(categoria.get_commands())} comandos" for categoria in dict_categorias]),
            inline = False
        ).set_footer(
            text = f"Para mais informações em um comando, use {self.invoked_with} <comando>"
        )
        lista_embeds.insert(0, embed) # Insere na lista de embeds
        dict_categorias = {None: lista_embeds, **dict_categorias} # Insere no dicionario
        menu = seleção(dict_categorias) # Cria o objeto do menu, usando o dict
        paginador = self.paginadorAjuda(lista_embeds, 300, self.context, menu) # cria o objeto de paginação
        await paginador.começar()
    
    async def send_cog_help(self, categoria):
        lista_comandos = tuple(filter(lambda c: not c.hidden, categoria.get_commands()))
        if not lista_comandos:
            return await self.send_error_message(self.command_not_found(categoria.qualified_name))
        descrições = "\n".join([self.resumo_comando(c) for c in lista_comandos])
        embed = discord.Embed(
            title = f"Exibindo categoria **{categoria.qualified_name} {categoria.emoji}**",
            description = f"{categoria.description}\n\n__**Lista de Comandos**__\n{descrições}",
            timestamp = self.timestamp
        ).set_author(
            name = self.autor,
            icon_url = self.autor.avatar.url
        )
        lista_embeds = [embed]
        for comando in lista_comandos:
            lista_embeds.append(await self.embed_comando(comando))
        paginador = self.paginador(lista_embeds, 300, self.context)
        await paginador.começar()
    
    async def send_group_help(self, comando):
        lista_comandos = tuple(filter(lambda c: not c.hidden, comando.commands))
        if not lista_comandos:
            return await self.context.send(embed = await self.embed_comando(comando))
        lista_embeds = []
        lista_embeds.append(await self.embed_comando(comando))
        for subcomando in lista_comandos:
            lista_embeds.append(await self.embed_comando(subcomando))
        paginador = self.paginador(lista_embeds, 300, self.context)
        await paginador.começar()
    
    async def send_command_help(self, comando):
        await self.context.send(embed = await self.embed_comando(comando))
    
    def command_not_found(self, string):
        return f"Não tenho nenhum comando ou categoria com o nome de {string}."
        
    def subcommand_not_found(self, comando, string):
        if isinstance(comando, commands.Group):
            return f"O comando {comando} não tem um subcomando chamado {string}... Os subcomandos desse comando são: {', '.join(comando.commands)}."
        else:
            return f"O comando {comando} não tem subcomandos."
    
    async def send_error_message(self, erro):
        await self.context.send(erro)

def setup(bot):
    bot.help_command = ajuda()
    bot.help_command.cog = bot.get_cog("Informações")
