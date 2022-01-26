import discord
from discord.ext import commands, menus
from plugins.paginador import PaginadorMenu, PaginadorExt
from plugins.variaveis import CooldownEspecial

import os
import sys

class BotãoGrupo(discord.ui.Button):
    def __init__(self, grupo, ajuda):
        super().__init__(style = discord.ButtonStyle.blurple, label = "Ver subcomandos")
        self.grupo = grupo
        self.ajuda = ajuda

    async def callback(self, interação):
        lista_subcomandos = list(filter(lambda c: not c.hidden, self.grupo.commands))
        lista_embeds = [await self.ajuda.embed_comando(c) for c in lista_subcomandos]
        await interação.response.send_message(embeds = lista_embeds, ephemeral = True)

class FonteAjuda(menus.ListPageSource):
    adicionou_botão = False
    async def format_page(self, menu, item):
        if self.adicionou_botão:
            menu.remove_item(self.botão)
            self.adicionou_botão = False
        if item is None:
            assert self.entries[0] is None
            lista_categorias = self.entries.copy()
            lista_categorias.pop(0)
            embed = discord.Embed(               
                title = "LOCOMOTIVE BOT - Ajuda",
                description = f"[Suporte]({os.getenv('link_suporte')}) - {os.getenv('bot_dev')} - [Convite do bot]({os.getenv('link_convite')})",
                timestamp = menu.ajuda.timestamp
            ).set_author(
                name = menu.ajuda.autor,
                icon_url = menu.ajuda.autor.avatar.url
            ).add_field(
                name = f"Informações do sistema",
                value = f"```\nPython {sys.version}\nDiscord.py {discord.__version__}\n```",
                inline = False
            ).add_field(
                name = "Categorias",
                value = "\n".join([f"{categoria.qualified_name} {categoria.emoji} - {len(categoria.get_commands())} comandos" for categoria in lista_categorias]),
                inline = False
            ).set_footer(
                text = f"Para mais informações em um comando, use {menu.ajuda.invoked_with} <comando>"
            )
            return embed
        elif isinstance(item, commands.Cog):
            return await menu.ajuda.embed_categoria(item)
        elif isinstance(item, commands.Group):
            lista_subcomandos = list(filter(lambda c: not c.hidden, item.commands))
            if len(lista_subcomandos) > 0 and len(lista_subcomandos) < 11:
                self.botão = BotãoGrupo(item, menu.ajuda)
                menu.add_item(self.botão)
                self.adicionou_botão = True               
            return await menu.ajuda.embed_comando(item)
        elif isinstance(item, commands.Command):
            return await menu.ajuda.embed_comando(item)
    
class SeleçãoAjuda(discord.ui.Select):
    def __init__(self, listas):
        super().__init__(
            placeholder = "Selecione uma categoria...",
            min_values = 1,
            max_values = 1,
            row = 0
        )
        self.listas = listas
        for categoria in listas[0]:
            self.add_option(
                label = getattr(categoria, "qualified_name", "Sumario"),
                value = getattr(categoria, "qualified_name", "Sumario"),
                description = getattr(categoria, "description", "Sumario com a visão geral do bot e de cada categoria."),
                emoji = getattr(categoria, "emoji", "\U0001f44b")
            )

    async def callback(self, interação):
        escolhida = self.values[0]
        categoria = self.view.ctx.bot.get_cog(escolhida) # Obtem o objeto de categoria
        numero = self.listas[0].index(categoria)
        fonte = FonteAjuda(self.listas[numero], per_page = 1)
        await self.view.mudar_fonte(fonte)
        
class PaginadorAjuda(PaginadorExt):
    def __init__(self, formatador, timeout, cog_ajuda):
        super().__init__(formatador, timeout)
        self.ajuda = cog_ajuda

    def adicionar_menu(self, menu_seleção):
        self.clear_items()
        self.add_item(menu_seleção)
        self.adicionar_itens()
        self.remove_item(self.parar)

    async def mudar_fonte(self, fonte):
        if self._source.adicionou_botão:
            self.remove_item(self._source.botão)
        await fonte._prepare_once()
        self._source = fonte
        await self.show_page(0)

atributos = {
    "name": "ajuda",
    "aliases": ("help", "a", "info", "about"),
    "help": "Manda uma mensagem de ajuda sobre o bot, que lista os comandos dele. A mensagem também tem outras informações úteis, como o link de convite e do servidor de suporte.",
    "brief": "Manda uma mensagem de ajuda sobre o bot",
    "extras": {"command": "O comando ou categoria para ver informações.", "exemplos": ("hakidorei", "Configurações")},
    "cooldown": commands.DynamicCooldownMapping(CooldownEspecial(3, 40), commands.BucketType.user)
}

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

    async def embed_categoria(self, categoria):
        lista_comandos = tuple(filter(lambda c: not c.hidden, categoria.get_commands()))
        descrições = "\n".join([self.resumo_comando(c) for c in lista_comandos])
        embed = discord.Embed(
            title = f"Exibindo categoria **{categoria.qualified_name} {categoria.emoji}**",
            description = f"{categoria.description}\n\n__**Lista de Comandos**__\n{descrições}",
            timestamp = self.timestamp
        ).set_author(
            name = self.autor,
            icon_url = self.autor.avatar.url
        )
        return embed
    
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
            lista_subcomandos = list(filter(lambda c: not c.hidden, comando.commands))
            if bool(len(lista_subcomandos)):
                embed.add_field(
                    name = "__Subcomandos__",
                    value = "\n".join([subcomando.full_parent_name + " " + subcomando.name for subcomando in lista_subcomandos])
                )
        return embed
    
    def resumo_comando(self, comando):
        resumo = (f"`{comando} {comando.signature}`:" if comando.signature else f"`{comando}`:") + f" {comando.short_doc or comando.help}"
        if isinstance(comando, commands.Group):
            resumo += "".join([f"\n→ `{subcomando}`: {subcomando.short_doc or subcomando.help}" for subcomando in filter(lambda c: not c.hidden, comando.commands)])
        return resumo
    
    async def send_bot_help(self, mapa_comandos):
        listas_cogs = [[None]]
        for categoria, lista_comandos in mapa_comandos.items():
            lista_comandos = tuple(filter(lambda c: not c.hidden, lista_comandos))
            if (not lista_comandos) or (not categoria) or categoria.qualified_name == "Desenvolvimento":
                continue
            lista_comandos = [categoria, *lista_comandos]
            listas_cogs.append(lista_comandos)
            listas_cogs[0].append(categoria)
        fonte = FonteAjuda(listas_cogs[0], per_page = 1)
        menu = SeleçãoAjuda(listas_cogs)
        paginador = PaginadorAjuda(fonte, 180, self)
        paginador.adicionar_menu(menu)
        await paginador.começar(self.context)
    
    async def send_cog_help(self, categoria):
        lista_comandos = tuple(filter(lambda c: not c.hidden, categoria.get_commands()))
        if not lista_comandos:
            return await self.send_error_message(self.command_not_found(categoria.qualified_name))
        fonte = FonteAjuda([categoria, *lista_comandos], per_page = 1)
        paginador = PaginadorAjuda(fonte, 120, self)
        await paginador.começar(self.context)
    
    async def send_group_help(self, comando):
        lista_comandos = tuple(filter(lambda c: not c.hidden, comando.commands))
        if not lista_comandos:
            return await self.context.send(embed = await self.embed_comando(comando))
        fonte = FonteAjuda([comando, *lista_comandos], per_page = 1)
        paginador = PaginadorAjuda(fonte, 90, self)
        await paginador.começar(self.context)
    
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
