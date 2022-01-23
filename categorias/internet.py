import discord
from discord.ext import commands
import mal #upm package(mal-api)
from dateutil.parser import isoparse as dt_parse #upm package(python-dateutil)
import pytz
from plugins.variaveis import CooldownEspecial
from plugins.paginador import PaginadorExt, FonteUrban, FonteMALAnime, FonteMALManga, FonteReddit, FonteTwitter, FonteSpotify

from datetime import datetime, timedelta
from urllib.parse import quote
import base64
import html
import math
import os

class ViewLink(discord.ui.View):
    def __init__(self, link, texto):
        super().__init__()
        self.add_item(discord.ui.Button(label = texto, url = link))

class internet(
    commands.Cog,
    name = "Internet",
    description = "Essa categoria contem comandos que extraem informações da internet."
):
    def __init__(self, bot):
        self.bot = bot
        self.emoji =  "<:InternetExplorer:804916227696623636>"
        self.bearer_spotify = {
            "token": None,
            "expira": datetime.utcnow() - timedelta(seconds = 1)
        }
    
    @commands.command(
        aliases = ("ub", "urband", "udictionary"),
        brief = "Mostra a definição de um termo de acordo com o Urban Dictionary",
        extras = {"termo": "A palavra chave para pesquisar no Urban Dictionary.",
                  "exemplos": ("pogchamp", "lol")}
    )
    @commands.max_concurrency(2, commands.BucketType.user)
    @commands.dynamic_cooldown(CooldownEspecial(2, 20), type = commands.BucketType.user)
    @commands.bot_has_permissions(embed_links = True)
    async def urbandictionary(self, ctx, *,termo):
        """Mostra a definição de um termo de acordo com o Urban Dictionary. As definições são em inglês pois o site tambem é nessa linguagem."""
        termo = quote(termo)
        async with self.bot.conexão.get(f"https://api.urbandictionary.com/v0/define?term={termo}") as resposta:
            if resposta.status == 200:
                json = await resposta.json()
                resultados = json["list"]
                if not bool(len(resultados)):
                    return await ctx.send(embed = discord.Embed(
                        title = f"Termo inexistente",
                        description = f"A sua pesquisa não gerou nenhum resultado no Urban Dictionary.",
                        color = 0x134FE6,
                        timestamp = discord.utils.utcnow()
                    ).set_footer(
                        text = f"urbandictionary.com",
                        icon_url = "https://cdn.discordapp.com/attachments/803443536363913236/827156974650916874/1617279952253.png"
                    ))
                fonte = FonteUrban(resultados, per_page = 1)
                paginador = PaginadorExt(fonte, 90)
                await paginador.começar(ctx)
            else:
                texto = await resposta.text()
                await ctx.send(embed = discord.Embed(
                    title = f"Erro desconhecido!",
                    description = f"O servidor do Urban Dictionary retornou um código não esperado, e o comando não pode ser executado. Informações do erro: \nCódigo HTTP: {resposta}\nTexto: {texto[0:3000] if len(texto) > 3000 else texto}",
                    color = 0xFF0000,
                    timestamp = discord.utils.utcnow()
                ).set_footer(
                    text = f"urbandictionary.com",
                    icon_url = "https://cdn.discordapp.com/attachments/803443536363913236/827156974650916874/1617279952253.png"
                ))
    
    @commands.command(
        hidden = True,
        extras = {"tags": "As tags do hentai :Trollface:",
                  "exemplos": ("furry", "furry futanari")}
    )
    @commands.is_nsfw()                                         #Não funciona no repl.it.
    @commands.has_permissions(administrator = True)             #Motivo: fodasse não
    @commands.bot_has_permissions(embed_links = True)           #atualizaram os certificado
    @commands.max_concurrency(2, commands.BucketType.user)      #ssl kkkkkkkkkj
    async def rule34(self, ctx, *,tags):
        """Faz a pesquisa de um hentai no site rule34.xxx. Caso duas tags ou mais sejam inseridas, os resultados mostrarão hentais que contenham as duas tags. 
        Comando adicionado para fins de pesquisa, não veja pornografia. O vicio pode destruir sua vida. [Leia mais sobre isso aqui](https://www.yourbrainonporn.com/miscellaneous-resources/start-here-evolution-has-not-prepared-your-brain-for-todays-porn/)"""
        tags = quote(tags)
        async with self.bot.conexão.get(f"https://rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&limit=100&tags={tags}") as resposta:
            if resposta.status != 200:
                texto = await resposta.text()
                await ctx.send(embed = discord.Embed(
                    title = f"Erro desconhecido!",
                    description = f"O servidor do Rule34 retornou um código não esperado, e o comando não pode ser executado. Informações do erro: \nCódigo HTTP: {resposta}\nTexto: {texto[0:3000] if len(texto) > 3000 else texto}",
                    color = 0xFF0000,
                    timestamp = discord.utils.utcnow()
                ).set_footer(
                    text = "rule34.xxx | Degenerado. Pornografia vicia.",
                    icon_url = "https://media.discordapp.net/attachments/803443536363913236/866490340534255646/1665779110029317c5_720x720.jpeg"
                ))
            else:
                json = await resposta.json()
                if not isinstance(json, list):
                    await ctx.send(embed = discord.Embed(
                        title = f"Oppsss... Essa(s) tag(s) não existem {self.bot.emoji['NagatoroFlushed']}",
                        description = "Uma ou mais tags que você inseriu não existe, ou não existe nenhum hentai com a combinação de tags inserida...",
                        color = 0xACE7A7,
                        timestamp = discord.utils.utcnow()
                    ).set_footer(
                        text = "rule34.xxx | Degenerado. Pornografia vicia.",
                        icon_url = "https://media.discordapp.net/attachments/803443536363913236/866490340534255646/1665779110029317c5_720x720.jpeg"
                    ))
                else:
                    lista_embeds = []
                    for hentai in json:
                        tags = hentai["tags"].replace(" ", ", ")
                        description = f"Artista: {hentai['owner']}\nAltura: {hentai['height']}\nLargura: {hentai['width']}\n"\
                        f"Pontuação: {hentai['score']}\n[Link da imagem em maxima resolução]({hentai['file_url']})\nTags: "
                        if len(tags) > 4096 - len(description):
                            tags = tags[0:(4096 - len(description))] + "..."
                        description += tags
                        embed = discord.Embed(
                            title = f"Exibindo resultados da pesquisa de hentai",
                            description = description,
                            color = 0xDDA9DD,
                            timestamp = discord.utils.utcnow()
                        ).set_image(
                            url = hentai['sample_url']
                        ).set_footer(
                            text = "rule34.xxx | Degenerado. Pornografia vicia.",
                            icon_url = "https://media.discordapp.net/attachments/803443536363913236/866490340534255646/1665779110029317c5_720x720.jpeg"
                        )
                        lista_embeds.append(embed)
                    paginador = self.bot.paginador(lista_embeds, 36, ctx)
                    await paginador.começar()
        
    @commands.group(
        invoke_without_command = True,
        aliases = ("mal",),
        brief = "Comandos relativos ao site MyAnimeList"
    )
    async def myanimelist(self, ctx):
        """Comandos relativos ao site MyAnimeList. Os resultados dos subcomandos são sempre em inglês."""
        await ctx.send_help("myanimelist")
    
    @myanimelist.command(
        aliases = ("animesearch", "ap", "as"),
        brief = "Pesquisa um anime no site",
        extras = {"anime": "O nome de anime a se pesquisar",
                  "exemplos": ("One Piece", "Boku no")}
    )
    @commands.max_concurrency(2, commands.BucketType.user)
    @commands.dynamic_cooldown(CooldownEspecial(2, 20), type = commands.BucketType.user)
    @commands.bot_has_permissions(embed_links = True)
    async def animepesquisa(self, ctx, *, anime):
        """Pesquisa um anime no site. As sinopses exibidas aqui não são completas, e são dadas em inglês. Para obter informações detalhadas de um anime especifico, use o comando de anime com o ID do anime."""
        async with ctx.typing():
            pesquisa = await self.bot.loop.run_in_executor(None, mal.AnimeSearch, anime)
        if not bool(len(pesquisa.results)):
            await ctx.send(embed = discord.Embed(
                title = "Pesquisa sem resultados",
                description = f"Sua busca por {anime} não gerou resultados...",
                color = 0x2E51A2,
                timestamp = discord.utils.utcnow()
            ).set_footer(
                text = f"myanimelist.net",
                icon_url = "https://cdn.discordapp.com/attachments/803443536363913236/827631401934913536/MyAnimeList_Logo.png"
            ))
        else:
            fonte = FonteMALAnime(pesquisa.results, per_page = 1)
            paginador = PaginadorExt(fonte, 150)
            await paginador.começar(ctx)
        
    @myanimelist.command(
        aliases = ("ai", "ainfo", "anime", "a"),
        brief = "Mostra informações sobre um anime",
        extras = {"id": "O ID do anime.",
                  "exemplos": ("21", "31964")}
    )
    @commands.dynamic_cooldown(CooldownEspecial(3, 60), type = commands.BucketType.member)
    async def animeinfo(self, ctx, id: int):
        """Mostra as informações sobre um anime, como sinopse e estatísticas. Consiga o ID para usar esse comando por meio do comando de pesquisa."""
        async with ctx.typing():
            try:
                anime = await self.bot.loop.run_in_executor(None, mal.Anime, id)
            except:
                return await ctx.send(embed = discord.Embed(
                    title = "Anime inexistente",
                    description = "Não existe nenhum anime com esse ID no MyAnimeList... Não sabe o ID do seu alvo?  Use o comando de pesquisa com o nome dele e veja o ID por lá.",
                    color = 0x2E51A2,
                    timestamp = discord.utils.utcnow()
                ).set_footer(
                    text = f"myanimelist.net",
                    icon_url = "https://cdn.discordapp.com/attachments/803443536363913236/827631401934913536/MyAnimeList_Logo.png"
                ))
            embed = discord.Embed(
                title = f"Exibindo informações para **{anime.title_english}**",
                description = f"> Sinopse\n{anime.synopsis if len(anime.synopsis) < 1990 else anime.synopsis[0:1989] + '...'}",
                color = 0x2E51A2,
                timestamp = discord.utils.utcnow()
            ).add_field(
                name = "Informações sobre o anime",
                value = f"Nome em japonês: {anime.title_japanese}\nData: {anime.aired.replace('to', 'até')}\nTipo: {anime.type}\n"\
                f"Número de episódios: {anime.episodes}\nDuração dos episódios: {anime.duration}\nGêneros: {', '.join(anime.genres)}\n"\
                f"Favoritadas: {anime.favorites}\nAberturas: {len(anime.opening_themes)}\nEncerramentos: {len(anime.ending_themes)}\n"\
                f"Posição no rank: {anime.rank}\nProdutoras: {', '.join(anime.producers)}\nEstudios: {', '.join(anime.studios)}\n",
                inline = False
            ).add_field(
                name = "Personagens principais",
                value = "\n".join([f'{a.name}({a.voice_actor})' for a in anime.characters]),
                inline = False
            ).set_image(
                url = anime.image_url
            ).set_footer(
                text = f"myanimelist.net | Pontuação: {anime.score}",
                icon_url = "https://cdn.discordapp.com/attachments/803443536363913236/827631401934913536/MyAnimeList_Logo.png"
            )
            await ctx.send(embed=embed, view = ViewLink(anime.url, "Abrir no MAL"))
    
    @myanimelist.command(
        aliases = ("mp", "mangap", "mangapesquisa", "pmanga"),
        brief = "Pesquisa um mangá no site",
        extras = {"manga": "O nome do mangá para pesquisar",
                  "exemplos": ("One Piece", "B gata H kei")}
    )
    @commands.max_concurrency(2, commands.BucketType.user)
    @commands.dynamic_cooldown(CooldownEspecial(2, 20), type = commands.BucketType.user)
    @commands.bot_has_permissions(embed_links = True)
    async def mangápesquisa(self, ctx, *, manga):
        """Pesquisa um mangá no site. As sinopses exibidas não são completas, e estão em inglês. Para obter informações detalhadas de um mangá especifico, use o comando de mangá com o ID do mangá."""
        async with ctx.typing():
            pesquisa = await self.bot.loop.run_in_executor(None, mal.MangaSearch, manga)
        if not bool(len(pesquisa.results)):
            await ctx.send(embed = discord.Embed(
                title = "Pesquisa sem resultados",
                description = f"Sua busca por {anime} não gerou resultados...",
                color = 0x2E51A2,
                timestamp = discord.utils.utcnow()
            ).set_footer(
                text = f"myanimelist.net",
                icon_url = "https://cdn.discordapp.com/attachments/803443536363913236/827631401934913536/MyAnimeList_Logo.png"
            ))
        else:
            fonte = FonteMALManga(pesquisa.results, per_page = 1)
            paginador = PaginadorExt(fonte, 150)
            await paginador.começar(ctx)
    
    @myanimelist.command(
        aliases = ("mangainfo", "mangá", "manga", "mangai", "mangái"),
        brief = "Mostra as informações de um mangá",
        extras = {"id": "O ID do mangá",
                  "exemplos": ("13", "19007")}
    )
    @commands.dynamic_cooldown(CooldownEspecial(3, 60), type = commands.BucketType.member)
    async def mangáinfo(self, ctx, id: int):
        """Mostra as informaçṍes sobre um mangá, como sinopse e estatísticas. Consiga o ID para usar esse comando por meio do comando de pesquisa."""
        async with ctx.typing():
            try:
                manga = await self.bot.loop.run_in_executor(None, mal.Manga, id)
            except:
                return await ctx.send(embed = discord.Embed(
                    title = "Mangá inexistente",
                    description = "Não existe nenhum mangá com esse ID no MyAnimeList... Não sabe o ID do seu alvo?  Use o comando de pesquisa com o nome dele e veja o ID por lá.",
                    color = 0x2E51A2,
                    timestamp = discord.utils.utcnow()
                ).set_footer(
                    text = f"myanimelist.net",
                    icon_url = "https://cdn.discordapp.com/attachments/803443536363913236/827631401934913536/MyAnimeList_Logo.png"
                ))
            embed = discord.Embed(
                title = f"Exibindo informações para **{manga.title_english}**",
                description = f"> Sinopse:\n{manga.synopsis if len(manga.synopsis) < 1990 else manga.synopsis[0:1989]+'...'}",
                timestamp = discord.utils.utcnow()
            ).add_field(
                name = "Informações sobre o mangá",
                value = f"Nome em japonês: {manga.title_japanese}\nData: {manga.published.replace('to', 'até')}\nTipo: {manga.type}\n"\
                f"Número de capítulos: {manga.chapters}\nNúmero de volumes: {manga.volumes}\nGêneros: {', '.join(manga.genres)}\n"\
                f"Favoritadas: {manga.favorites}\nPosição no rank: {manga.rank}\nAutores: {'; '.join(manga.authors)}",
                inline = False
            ).add_field(
                name = "Personagens Principais",
                value = '\n'.join([a.name for a in manga.characters]),
                inline = False
            ).set_image(
                url = manga.image_url
            ).set_footer(
                text = f"myanimelist.net | Pontuação: {manga.score}",
                icon_url = "https://cdn.discordapp.com/attachments/803443536363913236/827631401934913536/MyAnimeList_Logo.png"
            )
            await ctx.send(embed=embed, view = ViewLink(manga.url, "Abrir no MAL"))
    
    @commands.group(
        invoke_without_command = True,
        aliases = ("r", "rd", "redd"),
        brief = "Comandos relativos a rede social Reddit"
    )
    async def reddit(self, ctx):
        """Comandos relativos a rede social Reddit."""
        await ctx.send_help("reddit")
    
    @reddit.command(
        aliases = ("subinfo", "si", "sri", "subredditi"),
        brief = "Exibe as informaçṌes a respeito de um subreddit",
        extras = {"subreddit": "O subreddit para se obter informações",
                  "exemplos": ("Minecraft", "One Piece")}
    )
    @commands.dynamic_cooldown(CooldownEspecial(2, 30), type = commands.BucketType.user)
    @commands.bot_has_permissions(embed_links = True)
    async def subredditinfo(self, ctx, *,subreddit):
        """Exibe informações a respeito de um subreddit. Essas informações incluem descrição, contagem de membros e algumas permissões."""
        subreddit = quote(subreddit)
        async with self.bot.conexão.get(f"https://www.reddit.com/r/{subreddit}/about/.json") as resposta:
            if resposta.status == 429:
                await ctx.send(embed = discord.Embed(
                    title = f"Servidor indisponivel!",
                    description = "Foram feitas muitas requisições ao Reddit e o envio de outras foi bloqueado. Tente usar o comando novamente em alguns segundos...",
                    color = 0xFF0000,
                    timestamp = discord.utils.utcnow()
                ))
            elif resposta.status == 403:
                json = await resposta.json()
                if json['reason'] == 'private':
                    await ctx.send(embed = discord.Embed(
                        title = "Subreddit privado",
                        description = "Esse subreddit foi definido como privado pelos seus moderadores e apenas contas autorizadas podem acessa-lo.",
                        color = 0xff4500,
                        timestamp = discord.utils.utcnow()
                    ).set_footer(
                        text = f"reddit.com",
                        icon_url = "https://media.discordapp.net/attachments/803443536363913236/870861792312709140/reddit_logo.png"
                    ))
                elif json['reason'] == 'quarantined':
                    await ctx.send(embed = discord.Embed(
                        title = "Subreddit em quarentena",
                        description = f"Esse subreddit está em quarentena e não foi possível obter suas informações. Motivo fornecido: {json['quarantine_message']}",
                        color = 0xff4500,
                        timestamp = discord.utils.utcnow()
                    ).set_footer(
                        text = f"reddit.com",
                        icon_url = "https://media.discordapp.net/attachments/803443536363913236/870861792312709140/reddit_logo.png"
                    ))
            elif resposta.status == 404:
                json = await resposta.json()
                if 'reason' in json and json['reason'] == 'banned':
                    await ctx.send(embed = discord.Embed(
                        title = "Subreddit banido",
                        description = f"Esse subreddit foi banido pelo Reddit e não é possivel obter informações dele.",
                        color = 0xff4500,
                        timestamp = discord.utils.utcnow()
                    ).set_footer(
                        text = f"reddit.com",
                        icon_url = "https://media.discordapp.net/attachments/803443536363913236/870861792312709140/reddit_logo.png"
                    ))
                else:
                    await ctx.send(embed = discord.Embed(
                        title = "Subreddit não encontrado",
                        description = "O nome de subreddit inserido não foi encontrado e por consequencia não existe.",
                        color = 0xff4500,
                        timestamp = discord.utils.utcnow()
                    ).set_footer(
                        text = f"reddit.com",
                        icon_url = "https://media.discordapp.net/attachments/803443536363913236/870861792312709140/reddit_logo.png"
                    ))
            elif resposta.status == 200:
                json = await resposta.json()
                if 'dist' in json['data'] and json['data']['dist'] == 0:
                    await ctx.send(embed = discord.Embed(
                        title = f"Subreddit não existe/bloqueado",
                        description = "Não foi possivel obter infomações com o nome dado, o que significa que ou o subreddit é bloqueados para pessoas não cadastradas ou ele não existe.",
                        color = 0xFF4500,
                        timestamp = discord.utils.utcnow()
                    ).set_footer(
                        text = f"reddit.com",
                        icon_url = "https://media.discordapp.net/attachments/803443536363913236/870861792312709140/reddit_logo.png"
                    ))
                else:
                    infos = json['data']
                    if infos['over18'] and not ctx.channel.is_nsfw():
                        return await ctx.send(embed = discord.Embed(
                            title = f"Subreddit NSFW",
                            description = f"Esse subreddit e marcado como conteúdo NSFW e por isso não será exibido em um canal que não é NSFW.",
                            color = 0xff4500,
                            timestamp = discord.utils.utcnow()
                        ).set_footer(
                            text = f"reddit.com",
                            icon_url = "https://media.discordapp.net/attachments/803443536363913236/870861792312709140/reddit_logo.png"
                        ))
                    embed = discord.Embed(
                        title = f"Exibindo informações do sub **{infos['display_name_prefixed']}**",
                        description = html.unescape(f"**Descrição do sub**: {infos['description'] if len(infos['description']) < 3800 else infos['description'][0:3799]+'... **[Texto cortado]**'}"),
                        color = int(infos['primary_color'].replace('#', '0x'), base = 16) if infos['primary_color'] != '' else discord.Embed.Empty,
                        timestamp = pytz.utc.localize(datetime.utcfromtimestamp(int(infos['created'])))
                    ).add_field(
                        name = "Informações do sub",
                        value = f"**Número de membros**: {infos['subscribers']}\n**Número de membros online**: {infos['accounts_active']}\n**ID**: {infos['id']}",
                        inline = False
                    )
                    texto_infos = "...é +18? " + ('u2705' if infos['over18'] else '\U0001f7e5')
                    texto_infos += "\n...permite imagens? " + ("\u2705" if infos['allow_images'] else "\U0001f7e5")
                    texto_infos += "\n...permite galerias? " + ("\u2705" if infos['allow_galleries'] else "\U0001f7e5")
                    texto_infos += "\n...permite videos? " + ("\u2705" if infos['allow_videos'] else "\U0001f7e5")
                    texto_infos += "\n...permite gifs? " + ("\u2705" if infos['allow_videogifs'] else "\U0001f7e5")
                    texto_infos += "\n...permite enquetes? " + ("\u2705" if infos['allow_polls'] else "\U0001f7e5")
                    texto_infos += "\n...permite emojis? " + ("\u2705" if infos['emojis_enabled'] else "\U0001f7e5")
                    texto_infos += "\n...é crosspostável? " + ("\u2705" if infos['is_crosspostable_subreddit'] else "\U0001f7e5")
                    texto_infos += "\n...tem flairs ativados? " + ("\u2705" if infos['link_flair_enabled'] else "\U0001f7e5")
                    texto_infos += "\n...tem postagens restritas? " + ("\u2705" if infos['restrict_posting'] else "\U0001f7e5")
                    texto_infos += "\n...tem comentarios restritos? " + ("\u2705" if infos['restrict_commenting'] else "\U0001f7e5")
                    embed.add_field(
                        name = "Esse sub...",
                        value = texto_infos,
                        inline = False
                    ).set_image(
                        url = html.unescape(infos['banner_background_image'])
                    ).set_thumbnail(
                        url = html.unescape(infos['community_icon'])
                    ).set_footer(
                        text = f"reddit.com | Sub criado em",
                        icon_url = "https://media.discordapp.net/attachments/803443536363913236/870861792312709140/reddit_logo.png"
                    )
                    await ctx.send(embed = embed, view = ViewLink(f"https://www.reddit.com/r/{subreddit}", "Abrir no Reddit"))
            else:
                texto = await resposta.text()
                await ctx.send(embed = discord.Embed(
                    title = f"Erro desconhecido!",
                    description = f"O servidor do Reddit retornou um código não esperado, e o comando não pode ser executado. Informações do erro: \nCódigo HTTP: {resposta}\nTexto: {texto[0:3000] if len(texto) > 3000 else texto}",
                    color = 0xFF0000,
                    timestamp = discord.utils.utcnow()
                ).set_footer(
                    text = f"reddit.com",
                    icon_url = "https://media.discordapp.net/attachments/803443536363913236/870861792312709140/reddit_logo.png"
                ))
    
    @reddit.command(
        aliases = ("subreddit", "subposts", "sub", "subredditp", "/r"),
        brief = "Pesquisa os posts de um subreddit",
        extras = {"subreddit": "O subreddit para se ver os posts",
                  "exemplos": ("Minecraft", "One Piece")}
    )
    @commands.max_concurrency(2, commands.BucketType.user)
    @commands.dynamic_cooldown(CooldownEspecial(2, 40), type = commands.BucketType.user)
    @commands.bot_has_permissions(embed_links = True)
    async def subredditposts(self, ctx, *,subreddit):
        """Pesquisa os posts de um subreddit. Os posts são os mais recentes do subreddit, e até 50 posts podem ser exibidos."""
        subreddit = quote(subreddit)
        async with self.bot.conexão.get(f"https://www.reddit.com/r/{subreddit}/new/.json?limit=50") as resposta:
            if resposta.status == 429:
                await ctx.send(embed = discord.Embed(
                    title = f"Servidor indisponivel!",
                    description = "Foram feitas muitas requisições ao Reddit e o envio de outras foi bloqueado. Tente usar o comando novamente em alguns segundos...",
                    color = 0xFF0000,
                    timestamp = discord.utils.utcnow()
                ))
            elif resposta.status == 403:
                json = await resposta.json()
                if json['reason'] == 'private':
                    await ctx.send(embed = discord.Embed(
                        title = "Subreddit privado.",
                        description = "Esse subreddit foi definido como privado pelos seus moderadores e apenas contas autorizadas podem acessa-lo.",
                        color = 0xff4500,
                        timestamp = discord.utils.utcnow()
                    ).set_footer(
                        text = f"reddit.com",
                        icon_url = "https://media.discordapp.net/attachments/803443536363913236/870861792312709140/reddit_logo.png"
                    ))
                elif json['reason'] == 'quarantined':
                    await ctx.send(embed = discord.Embed(
                        title = "Subreddit em quarentena.",
                        description = f"Esse subreddit está em quarentena e não foi possível obter seus posts. Motivo fornecido: {json['quarantine_message']}",
                        color = 0xff4500,
                        timestamp = discord.utils.utcnow()
                    ).set_footer(
                        text = f"reddit.com",
                        icon_url = "https://media.discordapp.net/attachments/803443536363913236/870861792312709140/reddit_logo.png"
                    ))
            elif resposta.status == 404:
                json = await resposta.json()
                if 'reason' in json and json['reason'] == 'banned':
                    await ctx.send(embed = discord.Embed(
                        title = "Subreddit banido.",
                        description = f"Esse subreddit foi banido pelo Reddit e não é possivel obter informações dele.",
                        color = 0xff4500,
                        timestamp = discord.utils.utcnow()
                    ).set_footer(
                        text = f"reddit.com",
                        icon_url = "https://media.discordapp.net/attachments/803443536363913236/870861792312709140/reddit_logo.png"
                    ))
                else:
                    await ctx.send(embed = discord.Embed(
                        title = "Subreddit não encontrado.",
                        description = "O nome de subreddit inserido não foi encontrado e por consequencia não existe.",
                        color = 0xff4500,
                        timestamp = discord.utils.utcnow()
                    ).set_footer(
                        text = f"reddit.com",
                        icon_url = "https://media.discordapp.net/attachments/803443536363913236/870861792312709140/reddit_logo.png"
                    ))
            elif resposta.status == 200:
                json = await resposta.json()
                if json['data']['dist'] == 0:
                    await ctx.send(embed = discord.Embed(
                        title = f"Subreddit não existe/bloqueado",
                        description = "Não foi possivel obter posts com o nome dado, o que significa que ou o subreddit tem seus posts bloqueados para pessoas não cadastradas ou ele não existe.",
                        color = 0xFF4500,
                        timestamp = discord.utils.utcnow()
                    ).set_footer(
                        text = f"reddit.com",
                        icon_url = "https://media.discordapp.net/attachments/803443536363913236/870861792312709140/reddit_logo.png"
                    ))
                else:
                    fonte = FonteReddit(json["data"]["children"], per_page = 1)
                    paginador = PaginadorExt(fonte, 240)
                    await paginador.começar(ctx)
            else:
                texto = await resposta.text()
                await ctx.send(embed = discord.Embed(
                    title = f"Erro desconhecido!",
                    description = f"O servidor do Reddit retornou um código não esperado, e o comando não pode ser executado. Informações do erro: \nCódigo HTTP: {resposta}\nTexto: {texto[0:3000] if len(texto) > 3000 else texto}",
                    color = 0xFF0000,
                    timestamp = discord.utils.utcnow()
                ).set_footer(
                    text = f"reddit.com",
                    icon_url = "https://media.discordapp.net/attachments/803443536363913236/870861792312709140/reddit_logo.png"
                ))
    
    @reddit.command(
        aliases = ("u", "usuario", "user", "/u"),
        brief = "Pesquisa os posts de um usuário do reddit",
        extras = {"usuario": "O usuário para se ler os posts",
                  "exemplos": ("nomedousuario", "naoseiquemcolocarnoexemplo")}
    )
    @commands.max_concurrency(2, commands.BucketType.user)
    @commands.dynamic_cooldown(CooldownEspecial(2, 40), type = commands.BucketType.user)
    @commands.bot_has_permissions(embed_links = True)
    async def usuário(self, ctx, *, usuario):
        """Pesquisa os posts de um usuário do Reddit. Os posts exibidos são os mais recentes em qualquer subreddit e o número maximo de posts exibidos é 50."""
        usuario = quote(usuario)
        async with self.bot.conexão.get(f"https://www.reddit.com/u/{usuario}/submitted/.json?limit=50") as resposta:
            if resposta.status == 429:
                await ctx.send(embed = discord.Embed(
                    title = f"Servidor indisponivel!",
                    description = "Foram feitas muitas requisições ao Reddit e o envio de outras foi bloqueado. Tente usar o comando novamente em alguns segundos...",
                    color = 0xFF0000,
                    timestamp = discord.utils.utcnow()
                ).set_footer(
                    text = f"reddit.com",
                    icon_url = "https://media.discordapp.net/attachments/803443536363913236/870861792312709140/reddit_logo.png"
                ))
            elif resposta.status == 404:
                await ctx.send(embed = discord.Embed(
                    title = "Usuário não encontrado.",
                    description = "O nome de usuário inserido não foi encontrado e por consequencia não existe.",
                    color = 0xff4500,
                    timestamp = discord.utils.utcnow()
                ).set_footer(
                    text = f"reddit.com",
                    icon_url = "https://media.discordapp.net/attachments/803443536363913236/870861792312709140/reddit_logo.png"
                ))
            elif resposta.status == 200:
                json = await resposta.json()
                if json['data']['dist'] == 0:
                    await ctx.send(embed = discord.Embed(
                        title = f"Usúario não tem posts/bloqueado",
                        description = "Não foi possivel obter posts com o nome dado, o que significa que ou o usúario tem seus posts bloqueados para pessoas não cadastradas ou ele não tem posts.",
                        color = 0xFF4500,
                        timestamp = discord.utils.utcnow()
                    ).set_footer(
                        text = f"reddit.com",
                        icon_url = "https://media.discordapp.net/attachments/803443536363913236/870861792312709140/reddit_logo.png"
                    ))
                else:
                    fonte = FonteReddit(json["data"]["children"], per_page = 1)
                    paginador = PaginadorExt(fonte, 240)
                    await paginador.começar(ctx)
            else:
                texto = await resposta.text()
                await ctx.send(embed = discord.Embed(
                    title = f"Erro desconhecido!",
                    description = f"O servidor do Reddit retornou um código não esperado, e o comando não pode ser executado. Informações do erro: \nCódigo HTTP: {resposta}\nTexto: {texto[0:3000] if len(texto) > 3000 else texto}",
                    color = 0xFF0000,
                    timestamp = discord.utils.utcnow()
                ).set_footer(
                    text = f"reddit.com",
                    icon_url = "https://media.discordapp.net/attachments/803443536363913236/870861792312709140/reddit_logo.png"
                ))
    
    @commands.group(
        invoke_without_command= True,
        aliases = ("t",),
        brief = "Comandos relacionados ao Twitter"
    )
    async def twitter(self, ctx):
        await ctx.send_help("twitter")
    
    @twitter.command(
        aliases = ("u", "userinfo", "usuarioinfo", "usuário"),
        brief = "Mostra as informações de um perfil",
        extras = {"usuario": "O @ do usuário para pesquisa",
                    "exemplos": ("viniccius13", "minecraft")}
    )
    @commands.dynamic_cooldown(CooldownEspecial(2, 45), type = commands.BucketType.user)
    @commands.bot_has_permissions(embed_links = True)
    async def usuario(self, ctx, usuario):
        """Mostra as informações de um perfil do twitter. O tweet fixado também é exibido."""
        url = f"https://api.twitter.com/2/users/by/username/{usuario}?expansions=pinned_tweet_id"\
        "&tweet.fields=author_id,created_at,entities,id,public_metrics,possibly_sensitive,source,text,withheld"\
        "&user.fields=created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,"\
        "protected,public_metrics,url,username,verified,withheld"
        async with self.bot.conexão.get(url, headers = {'Authorization': f"Bearer {os.getenv('twitter_bearer')}"}) as resposta:
            if resposta.status == 400:
                await ctx.send(embed = discord.Embed(
                    title = "Requisição inválida",
                    description = "O nome de usuario inserido não é válido, e por isso não foi possivel obter informações",
                    color = 0xFF0000,
                    timestamp = discord.utils.utcnow()
                ).set_footer(
                    text = "twitter.com",
                    icon_url = "https://media.discordapp.net/attachments/803443536363913236/874767316108341258/580b57fcd9996e24bc43c53e.png"
                ))
            elif resposta.status == 200:
                json = await resposta.json()
                if 'data' not in json:
                    if json['errors'][0]['title'] == "Not Found Error":
                        await ctx.send(embed = discord.Embed(
                            title = "Usuário não encontrado",
                            description = "A pesquisa para o nome de usuário não gerou resultados, o que significa que ele não existe",
                            color = 0x57c7ff,
                            timestamp = discord.utils.utcnow()
                        ).set_footer(
                            text = "twitter.com",
                            icon_url = "https://media.discordapp.net/attachments/803443536363913236/874767316108341258/580b57fcd9996e24bc43c53e.png"
                        ))
                    elif json['errors'][0]['title'] == "Forbidden":
                        await ctx.send(embed = discord.Embed(
                            title = "Usuário suspenso",
                            description = "O usuário pesquisado foi suspenso do Twitter e não foi possivel obter informações dele.",
                            color = 0x57c7ff,
                            timestamp = discord.utils.utcnow()
                        ).set_footer(
                            text = "twitter.com",
                            icon_url = "https://media.discordapp.net/attachments/803443536363913236/874767316108341258/580b57fcd9996e24bc43c53e.png"
                        ))
                    else:
                        await ctx.send(embed = discord.Embed(
                            title = f"Problema desconhecido",
                            description = f"A pesquisa trouxe um problema não conhecido.\nCódigo: **{resposta.status}**\nTexto: {json}",
                            color = 0xFF0000,
                            timestamp = discord.utils.utcnow()
                        ).set_footer(
                            text = "twitter.com",
                            icon_url = "https://media.discordapp.net/attachments/803443536363913236/874767316108341258/580b57fcd9996e24bc43c53e.png"
                        ))
                else:
                    informações = json['data']
                    conteudo = None
                    embed = discord.Embed(
                        title = "Mostrando informações para @" + informações['username'],
                        description = f"**Nome de usuário**: {informações['name']}\n\"{informações['description']}\"",
                        color = 0x57c7FF,
                        timestamp = dt_parse(informações['created_at'])
                    ).set_thumbnail(
                        url = informações['profile_image_url']
                    )
                    infos = f"**ID**: {informações['id']}\n**Seguidores**: {informações['public_metrics']['followers_count']}"\
                    f"\n**Seguindo**: {informações['public_metrics']['following_count']}\n**Tweets**: {informações['public_metrics']['tweet_count']}"
                    if informações['url'] != '':
                        infos += f"\n**Link**: {informações['entities']['url']['urls'][0]['expanded_url'].lower()}"
                    if 'location' in informações:
                        infos += f"\n**Localização**: {informações['location']}"
                    embed.add_field(
                        name = "Informações do perfil",
                        value = infos
                    ).set_footer(
                        text = "twitter.com | Perfil criado em",
                        icon_url = "https://media.discordapp.net/attachments/803443536363913236/874767316108341258/580b57fcd9996e24bc43c53e.png"
                    )
                    if 'pinned_tweet_id' in informações:
                        if 'errors' in json and json['errors'][0]['resource_type'] == 'tweet' and json['errors'][0]['title'] == 'Not Found Error':
                            conteudo = "Devido a um problema do Twitter, o tweet fixado desse perfil (se existir) não será exibido."
                        else:
                            if not json['includes']['tweets'][0]['possibly_sensitive'] or ctx.channel.is_nsfw():
                                tweet = json['includes']['tweets'][0]
                                embed.add_field(
                                    name = "Tweet fixado \U0001f4cc",
                                    value = f"\"{tweet['text']}\"\n\u2764\ufe0f {tweet['public_metrics']['like_count']} | \U0001f4ac {tweet['public_metrics']['reply_count']} | \U0001f5ef\ufe0f {tweet['public_metrics']['quote_count']} | \U0001f501 {tweet['public_metrics']['retweet_count']}"
                                )
                    await ctx.send(conteudo, embed = embed, view = ViewLink(f"https://twitter.com/{usuario}", "Abrir no Twitter"))
            else:
                texto = await resposta.text()
                if len(texto) > 3000:
                    texto = texto[0:3000] + "..."
                await ctx.send(embed = discord.Embed(
                    title = f"Problema desconhecido",
                    description = f"A pesquisa trouxe um problema não conhecido. Informaçṍes dele estão escritas abaixo para analise posterior.\nCódigo: **{resposta.status}**\n{texto}",
                    color = 0xFF0000,
                    timestamp = discord.utils.utcnow()
                ).set_footer(
                    text = "twitter.com",
                    icon_url = "https://media.discordapp.net/attachments/803443536363913236/874767316108341258/580b57fcd9996e24bc43c53e.png"
                ))
    
    @twitter.command(
        aliases = ("p",),
        brief = "Vê os posts recentes de uma conta",
        extras = {"usuario": "O usuário para se ver os posts",
                  "exemplos": ("viniccius13", "minecraft")}
    )
    @commands.max_concurrency(2, commands.BucketType.user)
    @commands.dynamic_cooldown(CooldownEspecial(2, 45), type = commands.BucketType.user)
    @commands.bot_has_permissions(embed_links = True)
    async def posts(self, ctx, usuario):
        """Pesquisa e mostra os tweets recentes de uma conta. O número máximo de posts exibidos é de 25."""
        url = f"https://api.twitter.com/2/tweets/search/recent?query=from:{usuario}&max_results=25"\
        "&expansions=attachments.poll_ids,attachments.media_keys,referenced_tweets.id.author_id,author_id"\
        "&media.fields=media_key,preview_image_url,type,url"\
        "&poll.fields=duration_minutes,end_datetime,id,options,voting_status"\
        "&tweet.fields=attachments,created_at,entities,id,lang,public_metrics,possibly_sensitive,referenced_tweets,source,text,withheld"\
        "&user.fields=name,profile_image_url"
        async with self.bot.conexão.get(url, headers = {'Authorization': f"Bearer {os.getenv('twitter_bearer')}"}) as resposta:
            if resposta.status == 400:
                await ctx.send(embed = discord.Embed(
                    title = "Requisição inválida",
                    description = "O nome de usuario inserido não é válido, e por isso não foi possivel obter informações",
                    color = 0xFF0000,
                    timestamp = discord.utils.utcnow()
                ).set_footer(
                    text = "twitter.com",
                    icon_url = "https://media.discordapp.net/attachments/803443536363913236/874767316108341258/580b57fcd9996e24bc43c53e.png"
                ))
            elif resposta.status == 200:
                json = await resposta.json()
                if json["meta"]["result_count"] == 0:
                    await ctx.send(embed = discord.Embed(
                        title = "Nenhum resultado foi obtido",
                        description = "O número de resultados recebidos foi 0. Os motivos para isso acontecer podem ser:\n-O perfil não tem tweets\n-O perfil não existe\n-O perfil é privado\n-O último tweet do perfil foi a mais de 7 dias",
                        color = 0x57C7FF,
                        timestamp = discord.utils.utcnow()
                    ).set_footer(
                        text = "twitter.com",
                        icon_url = "https://media.discordapp.net/attachments/803443536363913236/874767316108341258/580b57fcd9996e24bc43c53e.png"
                    ))
                else:
                    fonte = FonteTwitter(json["data"], per_page = 1)
                    fonte.adicionar_anexos(json["includes"])
                    paginador = PaginadorExt(fonte, 150)
                    await paginador.começar(ctx)
            else:
                texto = await resposta.text()
                if len(texto) > 3000:
                    texto = texto[0:3000] + "..."
                await ctx.send(embed = discord.Embed(
                    title = f"Problema desconhecido",
                    description = f"A pesquisa trouxe um problema não conhecido. Informaçṍes dele estão escritas abaixo para analise posterior.\nCódigo: **{resposta.status}**\n{texto}",
                    color = 0xFF0000,
                    timestamp = discord.utils.utcnow()
                ).set_footer(
                    text = "twitter.com",
                    icon_url = "https://media.discordapp.net/attachments/803443536363913236/874767316108341258/580b57fcd9996e24bc43c53e.png"
                ))

    async def pegar_token_spotify(self):
        if self.bearer_spotify["expira"] < datetime.utcnow():
            autorização = os.getenv("spotify_client_id") + ":" + os.getenv("spotify_client_secret")
            headers = {"Authorization": "Basic " + base64.b64encode(autorização.encode('ascii')).decode("ascii")}
            data = {"grant_type": "client_credentials"}
            async with self.bot.conexão.post("https://accounts.spotify.com/api/token", data = data, headers = headers) as resposta:
                json = await resposta.json()
                self.bearer_spotify = {
                    "token": json["access_token"],
                    "expira": datetime.utcnow() + timedelta(seconds = json["expires_in"])
                }
                return self.bearer_spotify["token"]
        else:
            return self.bearer_spotify["token"]
            
    @commands.group(
        invoke_without_command = True,
        aliases = ("s", "sp", "Spotify"),
        brief = "Comandos relacionados ao spotify"
    )
    async def spotify(self, ctx):
        """Comandos relacionados ao Spotify."""
        await ctx.send_help("spotify")
    
    @spotify.command(
        name = "usuario",
        aliases = ("u", "ouvindo", "usuário"),
        brief = "Mostra o que alguém está ouvindo agora",
        extras = {"membro": "Id ou menção do membro para ver o que está ouvindo",
                  "exemplos": ("<@531508181654962197>", "531508181654962197")}
    )
    @commands.dynamic_cooldown(CooldownEspecial(2, 10), type = commands.BucketType.member)
    @commands.bot_has_permissions(embed_links = True)
    async def usuario_spotify(self, ctx, membro: discord.Member = None):
        """Mostra o que alguém está ouvindo no Spotify. Para isso, a pessoa deve ter o compartilhamento do Spotify ativo e deve ser membro do servidor."""
        if not membro:
            membro = ctx.author
        spotify = None
        for atividade in membro.activities:
            if isinstance(atividade, discord.Spotify):
                spotify = atividade
                break
        if not spotify:
            return await ctx.send("Parece que esse usuário não está ouvindo nada no Spotify...")
        minutos_total, segundos_total = divmod(spotify.duration.total_seconds(), 60)
        atual = discord.utils.utcnow() - spotify.start
        minutos_atual, segundos_atual = divmod(atual.total_seconds(), 60)
        infos = f"{spotify.title} - {spotify.artist}\nDo albúm **{spotify.album}**\n"
        infos += f"{int(minutos_atual):02}:{int(segundos_atual):02} "
        tempo = spotify.duration.total_seconds()/13
        jafoi = atual.total_seconds()/tempo
        infos += ("━" * math.floor(jafoi)) + "●"  + ("─" * (13 - math.ceil(jafoi)))
        infos += f" {int(minutos_total):02}:{int(segundos_total):02}"
        embed = discord.Embed(
            title = f"{membro} está ouvindo uma música no Spotify!",
            description = infos,
            color = spotify.color,
            timestamp = spotify.created_at or discord.utils.utcnow()
        ).set_footer(
            text = f"Spotify.com",
            icon_url = "https://media.discordapp.net/attachments/803443536363913236/897683078321930261/2048px-Spotify_logo_without_text.svg.png"
        ).set_thumbnail(
            url = spotify.album_cover_url
        )
        await ctx.send(embed = embed, view = ViewLink(f"https://open.spotify.com/track/{spotify.track_id}", "Abrir no Spotify"))
    
    @spotify.command(
        aliases = ("pesquisamusica", "m", "pm"),
        brief = "Mostra informações de uma ou mais músicas",
        extras = {"musica": "O nome da música para pesquisa",
                  "exemplos": ("coma - guns n roses", "death on two legs")}
    )
    @commands.dynamic_cooldown(CooldownEspecial(3, 15), type = commands.BucketType.user)
    @commands.bot_has_permissions(embed_links = True)
    async def musica(self, ctx, *, musica):
        """Mostra informações de uma ou mais músicas. A pesquisa é feita baseada no termo inserido, e mais de um resultado pode ser obtido."""
        musica = quote(musica)
        token = await self.pegar_token_spotify()
        headers = {"Authorization": f"Bearer {token}"}
        async with self.bot.conexão.get(f"https://api.spotify.com/v1/search?q={musica}&type=track", headers = headers) as resposta:
            if resposta.status == 200:
                json = await resposta.json()
                if len(json['tracks']['items']) == 0:
                    await ctx.send(embed = discord.Embed(
                        title = f"Sem resultados!",
                        description = "Nenhum resultado foi obtido para o termo de pesquisa inserido.",
                        color = 0x1db954,
                        timestamp = discord.utils.utcnow()
                    ).set_footer(
                        text = "Spotify.com",
                        icon_url = "https://media.discordapp.net/attachments/803443536363913236/897683078321930261/2048px-Spotify_logo_without_text.svg.png"
                    ))
                else:
                    fonte = FonteSpotify(json["tracks"]["items"], per_page = 1)
                    fonte.escolher_metodo("musica")
                    paginador = PaginadorExt(fonte, 90)
                    await paginador.começar(ctx)
            else:
                await ctx.send(embed = discord.Embed(
                    title = f"Erro desconhecido!",
                    description = f"Ocorreu um erro desconhecido. Segue informações abaixo:\nCódigo **{resposta.status}**\n\n{resposta.text[0:3500] if len(resposta.text) > 3500 else resposta.text}",
                    color = 0xFF0000,
                    timestamp = discord.utils.utcnow()
                ).set_footer(
                    text = f"Spotify.com",
                    icon_url = "https://media.discordapp.net/attachments/803443536363913236/897683078321930261/2048px-Spotify_logo_without_text.svg.png"
                ))

def setup(bot):
    bot.add_cog(internet(bot))
