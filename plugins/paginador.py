import discord
from discord.ext import commands, menus
from dateutil.parser import isoparse as dt_parse #upm package(python-dateutil)
import pytz

import html
import asyncio
from datetime import datetime

class Paginador(discord.ui.View):
    def __init__(self, lista_embeds, timeout, contexto):
        super().__init__(timeout = timeout)
        self.lista_embeds = lista_embeds # Uma lista de objetos discord.Embed
        self.avisados = [] # A lista de quem já foi avisado que não pode interagir
        self.posição = 0 
        self.ctx = contexto # contexto para ser usado com o metodo começar
        self.trava = asyncio.Lock() # trava para evitar que a pessoa use o pulo duas vezes
      
    async def interaction_check(self, interação):
        if self.ctx.author.id == interação.user.id:
            return True
        else:
            if interação.user.id in self.avisados:
                await interação.response.defer()
                return False
            else:
                self.avisados.append(interação.user.id)
                await interação.response.send_message("Esse não é seu paginador!", ephemeral = True)
                return False
    
    def adicionar_itens(self):
        """Para quando for preciso reordenar os botões. Isso adiciona todos os cinco presentes na paginação."""
        self.add_item(self.retornar_ao_inicio)
        self.add_item(self.retroceder)
        self.add_item(self.atual)
        self.add_item(self.avançar)
        self.add_item(self.pular_pro_final)
        self.add_item(self.parar)
    
    async def começar(self):
        """Verifica se o bot tem permissao de mandar embeds e verifica se a lista contem mais de um embed, se tudo estiver ok ele começa a pagina,ão"""
        if not self.ctx.channel.permissions_for(self.ctx.me).embed_links:
            await self.ctx.send("Eu não tenho a permissão de `Inserir Links` nesse canal/servidor, e por isso não é possível enviar o resultado desse comando.")
            return
        if len(self.lista_embeds) == 1:
            await self.ctx.send(embed = self.lista_embeds[self.posição])
        else:
            """for embed in self.lista_embeds:
                if embed.footer.text is discord.Embed.Empty:
                    embed.set_footer(text = f"Página {self.lista_embeds.index(embed) + 1}/{len(self.lista_embeds)}")
                else:
                    embed.set_footer(text = embed.footer.text + f" | Página {self.lista_embeds.index(embed) + 1}/{len(self.lista_embeds)}")"""
            self.mensagem = await self.ctx.send(embed = self.lista_embeds[self.posição], view = self)
    
    async def on_timeout(self):
        """dá um fim em tudo"""
        self.clear_items()
        await self.mensagem.edit(view = None)
        self.stop()
    
    async def mostrar_pagina(self, interação):
        """Faz as mudanças necessarias nos textos dos botões e muda a pagina baseado no atributo posição que é modificado na corrotina do botão."""
        self.retornar_ao_inicio.disabled = not self.posição
        self.pular_pro_final.disabled = self.posição == len(self.lista_embeds) - 1
        self.atual.label = f"{self.posição + 1}/{len(self.lista_embeds)}"
        #self.retroceder.label = str(self.posição)
        self.retroceder.label = None
        self.retroceder.disabled = False
        #self.avançar.label = str(self.posição + 2)
        self.avançar.label = None
        self.avançar.disabled = False
        if self.posição == 0:
            self.retroceder.label = "..."
            self.retroceder.disabled = True
        elif self.posição == len(self.lista_embeds) - 1:
            self.avançar.label = "..."
            self.avançar.disabled = True
        if interação.response.is_done():
            await self.mensagem.edit(embed = self.lista_embeds[self.posição], view = self)
        else:
            await interação.response.edit_message(embed = self.lista_embeds[self.posição], view = self)
        
    @discord.ui.button(emoji = "\u23ea", disabled = True)
    async def retornar_ao_inicio(self, botão, interação):
        """Botão para voltar ao inicio"""
        self.posição = 0
        await self.mostrar_pagina(interação)
    
    @discord.ui.button(label = "Anterior", style = discord.ButtonStyle.blurple, emoji = "\u25c0\ufe0f", disabled = True)
    async def retroceder(self, botão, interação):
        """botão que retorna uma pagina"""
        self.posição -= 1
        await self.mostrar_pagina(interação)
    
    @discord.ui.button(label = "Atual", emoji = "\U0001f522")
    async def atual(self, botão, interação):
        """Mostra a posição atual E dá a opção de pular para uma pagina especifica. Se for dado como desativado não irá ativar no meio da paginação (Bom para quando se tem menus)"""
        if self.trava.locked():
            await interação.response.send_message("Eu estou aguardando sua resposta...", ephemeral = True)
            return
        async with self.trava:
            def check(mensagem):
                return mensagem.author.id == self.ctx.author.id and mensagem.channel.id == self.ctx.channel.id and mensagem.content.isdigit()
            await interação.response.send_message("Diga para qual página você deseja pular...", ephemeral = True)
            try:
                mensagem = await self.ctx.bot.wait_for("message", check = check, timeout = 20.0)
            except asyncio.TimeoutError:
                await interação.followup.send("Você demorou demais.", ephemeral = True)
            else:
                pagina = int(mensagem.content) - 1
                if pagina + 1 > len(self.lista_embeds):
                    pagina = len(self.lista_embeds) - 1
                self.posição = pagina
                await self.mostrar_pagina(interação)
    
    @discord.ui.button(label = "Próximo", style = discord.ButtonStyle.blurple, emoji = "\u25b6\ufe0f")
    async def avançar(self, botão, interação):
        """avança uma pagina"""
        self.posição += 1
        await self.mostrar_pagina(interação)
    
    @discord.ui.button(emoji = "\u23e9")
    async def pular_pro_final(self, botão, interação):
        """vai para a ultima pagina"""
        self.posição = len(self.lista_embeds)-1
        await self.mostrar_pagina(interação)

    @discord.ui.button(label = "Parar", style = discord.ButtonStyle.grey)
    async def parar(self, botão, interação):
        await self.on_timeout()

class PaginadorMenu(Paginador):
    """subclasse do paginador que implementa o menu expansivel"""
    def __init__(self, lista_embeds, timeout, contexto, seleção):
        super().__init__(lista_embeds, timeout, contexto)
        self.clear_items() # Para ordenar os botṍes
        self.add_item(seleção) # Adiciona o menu
        self.adicionar_itens() # Readiciona os botões
        self.remove_item(self.parar)

class PaginadorExt(discord.ui.View, menus.MenuPages):
    def __init__(self, formatador, timeout):
        super().__init__(timeout = timeout)
        self._source = formatador
        self.current_page = 0
        self.avisados = []
        self.trava = asyncio.Lock()
      
    async def interaction_check(self, interação):
        if self.ctx.author.id == interação.user.id:
            return True
        else:
            if interação.user.id in self.avisados:
                await interação.response.defer()
                return False
            else:
                self.avisados.append(interação.user.id)
                await interação.response.send_message("Esse não é seu paginador!", ephemeral = True)
                return False

    async def começar(self, ctx): #MUDAR!!!!!!! verificar se é content ou embed
        if not ctx.channel.permissions_for(ctx.me).embed_links:
            await ctx.send("Eu não tenho a permissão de `Inserir Links` nesse canal/servidor, e por isso não é possível enviar o resultado desse comando.")
            return
        if self._source.get_max_pages() == 1:
            self.clear_items()
            atributos = await self._get_kwargs_from_page(await self._source.get_page(0))
            await ctx.send(**atributos)
        else:
            self.ctx = ctx
            self.message = await self.send_initial_message(ctx, ctx.channel)

    def arrumar_botões(self):
        self.retornar_ao_inicio.disabled = not self.current_page
        self.retroceder.disabled = not self.current_page
        self.pular_pro_final.disabled = self.current_page == self._source.get_max_pages() - 1
        self.avançar.disabled = self.current_page == self._source.get_max_pages() - 1
        self.atual.label = f"{self.current_page + 1}/{self._source.get_max_pages()}"
    
    async def _get_kwargs_from_page(self, pagina):
        valor = await super()._get_kwargs_from_page(pagina)
        self.arrumar_botões()
        if "view" not in valor:
            valor["view"] = self
        return valor
    
    @discord.ui.button(emoji = "\u23ea")
    async def retornar_ao_inicio(self, botão, interação):
        """Botão para voltar ao inicio"""
        await self.show_page(0)
    
    @discord.ui.button(style = discord.ButtonStyle.blurple, emoji = "\u25c0\ufe0f")
    async def retroceder(self, botão, interação):
        """botão que retorna uma pagina"""
        await self.show_checked_page(self.current_page - 1)

    @discord.ui.button(label = "Atual", emoji = "\U0001f522")
    async def atual(self, botão, interação):
        if self.trava.locked():
            await interação.response.send_message("Eu estou aguardando sua resposta...", ephemeral = True)
            return
        async with self.trava:
            def check(mensagem):
                return mensagem.author.id == self.ctx.author.id and mensagem.channel.id == self.ctx.channel.id and mensagem.content.isdigit()
            await interação.response.send_message("Diga para qual página você deseja pular...", ephemeral = True)
            try:
                mensagem = await self.ctx.bot.wait_for("message", check = check, timeout = 20.0)
            except asyncio.TimeoutError:
                await interação.followup.send("Você demorou demais.", ephemeral = True)
            else:
                await self.show_checked_page(int(mensagem.content) - 1)

    @discord.ui.button(style = discord.ButtonStyle.blurple, emoji = "\u25b6\ufe0f")
    async def avançar(self, botão, interação):
        """avança uma pagina"""
        await self.show_checked_page(self.current_page + 1)
    
    @discord.ui.button(emoji = "\u23e9")
    async def pular_pro_final(self, botão, interação):
        """vai para a ultima pagina"""
        await self.show_page(self._source.get_max_pages() - 1)

    @discord.ui.button(label = "Parar", style = discord.ButtonStyle.red)
    async def parar(self, botão, interação):
        await self.on_timeout()

    def adicionar_itens(self):
        """Para quando for preciso reordenar os botões. Isso adiciona todos os seis presentes na paginação."""
        self.add_item(self.retornar_ao_inicio)
        self.add_item(self.retroceder)
        self.add_item(self.atual)
        self.add_item(self.avançar)
        self.add_item(self.pular_pro_final)
        self.add_item(self.parar)
    
    async def on_timeout(self):
        """dá um fim em tudo"""
        self.clear_items()
        try:
            await self.message.edit(view = None)
        except:
            pass
        self.stop()

class FonteUrban(menus.ListPageSource):
    adicionou_botão = False
    def format_page(self, menu, resultado):
        embed = discord.Embed(
            title = f"Exibindo resultados para pesquisa de **{resultado['word']}**",
            description = f"> Definição:\n{resultado['definition']}\n> Exemplos:\n{resultado['example']}\n"\
            f"> Outras informações:\nAutor: {resultado['author']}\n"\
            f"{resultado['thumbs_up']} \U0001f44d | {resultado['thumbs_down']} \U0001f44e",
            color = 0x134FE6,
            timestamp = dt_parse(resultado["written_on"])
        ).set_footer(
            text = f"urbandictionary.com | Publicado em",
            icon_url = "https://cdn.discordapp.com/attachments/803443536363913236/827156974650916874/1617279952253.png"
        )
        if self.adicionou_botão:
            self.botão.url = resultado["permalink"]
        else:
            self.botão = discord.ui.Button(url = resultado["permalink"], label = "Abrir no Urban Dictionary")
            menu.add_item(self.botão)
            self.adicionou_botão = True
        return embed

class FonteMALAnime(menus.ListPageSource):
    adicionou_botão = False
    def format_page(self, menu, anime):
        embed = discord.Embed(
            title = f"Anime {anime.title}",
            description = f"> Sinopse\n{(anime.synopsis if len(anime.synopsis)<1500 else anime.synopsis[0:1499]+'...')}\n"\
            f"> Informações\nNúmero de episodios: {anime.episodes}\nPontuação: {anime.score}\nID: {anime.mal_id}\nTipo: {anime.type}",
            color = 0x2E51A2,
            timestamp = discord.utils.utcnow()
        ).set_thumbnail(
            url = anime.image_url
        ).set_footer(
            text = f"myanimelist.net",
            icon_url = "https://cdn.discordapp.com/attachments/803443536363913236/827631401934913536/MyAnimeList_Logo.png"
        )
        if self.adicionou_botão:
            self.botão.url = anime.url
        else:
            self.botão = discord.ui.Button(url = anime.url, label = "Abrir no MAL")
            menu.add_item(self.botão)
            self.adicionou_botão = True
        return embed

class FonteMALManga(menus.ListPageSource):
    adicionou_botão = False
    def format_page(self, menu, manga):
        embed = discord.Embed(
            title = f"Mangá {manga.title}",
            description = f"> Sinopse:\n{manga.synopsis}\n> Informações:\nNúmero de volumes: {manga.volumes}\n"\
            f"Pontuação: {manga.score}\nID: {manga.mal_id}\nTipo: {manga.type}",
            timestamp = discord.utils.utcnow()
        ).set_thumbnail(
            url = manga.image_url
        ).set_footer(
            text = f"myanimelist.net",
            icon_url = "https://cdn.discordapp.com/attachments/803443536363913236/827631401934913536/MyAnimeList_Logo.png"
        )
        if self.adicionou_botão:
            self.botão.url = manga.url
        else:
            self.botão = discord.ui.Button(url = manga.url, label = "Abrir no MAL")
            menu.add_item(self.botão)
            self.adicionou_botão = True
        return embed

class FonteReddit(menus.ListPageSource):
    adicionou_botão = False
    def format_page(self, menu, post):
        post = post["data"]
        if post['over_18'] == True and not menu.ctx.channel.is_nsfw():
            embed = discord.Embed(
                title = f"Post NSFW",
                description = f"Esse post foi marcado como NSFW e só pode ser visto nesse tipo de canal.",
                color = 0xff0000,
                timestamp = pytz.utc.localize(datetime.utcfromtimestamp(int(post['created'])))
            ).set_footer(
                text = f"reddit.com",
                icon_url = "https://media.discordapp.net/attachments/803443536363913236/870861792312709140/reddit_logo.png"
            )
            if self.adicionou_botão:
                menu.remove_item(self.botão)
                self.adicionou_botão = False
            return embed
        descrição = f"**Título**: {post['title']}\n"
        if post['selftext'] != '':
            if len(post['selftext']) < 3500:
                descrição += html.unescape(f"**Conteúdo**: {post['selftext']}\n")
            else:
                descrição += html.unescape(f"**Conteúdo**: {post['selftext'][0:3499]}... **[Post cortado]**\n")
        descrição += f"\n{post['ups']} \u2b06\ufe0f | {post['downs']} \u2b07\ufe0f | {post['num_comments']} \U0001f4ac"
        embed = discord.Embed(
            title = f"Post por **{post['author']}** em **{post['subreddit_name_prefixed']}**",
            description = descrição,
            color = 0xff4500,
            timestamp = pytz.utc.localize(datetime.utcfromtimestamp(int(post['created'])))
        ).set_footer(
            text = f"reddit.com",
            icon_url = "https://media.discordapp.net/attachments/803443536363913236/870861792312709140/reddit_logo.png"
        )
        if 'author_flair_type' in post and post['author_flair_type'] == "richtext":
            link_flair_autor = discord.Embed.Empty
            if 'u' in post["author_flair_richtext"][0]:
                link_flair_autor = post["author_flair_richtext"][0]["u"]
            embed.set_author(
                name = post['author_flair_text'],
                icon_url = link_flair_autor
            )
        if post['link_flair_type'] == "richtext":
            embed.add_field(
                name = "Categoria",
                value = post['link_flair_text']
            )
            if post['link_flair_background_color'] != '':
                embed.color = int(post['link_flair_background_color'].replace('#', '0x'), base = 16)
        if "post_hint" in post:
            if post["post_hint"] == 'image':
                if post['url'] != 'spoiler':
                    embed.add_field(
                        name = "Mídias",
                        value = f"Existe uma imagem anexada ao post."
                    ).set_image(
                        url = post['url']
                    )
                else:
                    embed.add_field(
                        name = f"Mídias",
                        value = f"Existe uma imagem marcada como **spoiler** no post."
                    )
            elif post['post_hint'] == 'hosted:video':
                embed.add_field(
                    name = "Mídias",
                    value = f"Existe um [video]({post['media']['reddit_video']['fallback_url']}) anexado ao post."
                ).set_image(
                    url = post['preview']['images'][0]['source']['url'].replace("&amp;", "&")
                )
            elif post['post_hint'] == "rich:video":
                if post['media']['type'] == 'gfycat.com':
                    link_embedly = post['media']['oembed']['thumbnail_url'].replace("https://i.embed.ly/1/image?url=", "")
                    link_gif = link_embedly.split("&")[0].replace("%2F", "/").replace("%3A", ":")
                    embed.add_field(
                        name = "Mídias",
                        value = f"Existe um [gif do Gyfcat]({post['url']}) anexado ao post."
                    ).set_image(
                        url = link_gif
                    )
                elif post['media']['type'] == 'redgifs.com':
                    embed.add_field(
                        name = "Mídias",
                        value = f"Existe um gif do RedGifs no post. Ele **não** será exibido pois o bot não suporta gifs pornográficos."
                    )
                elif post['media']['type'] == 'youtube.com':
                    embed.add_field(
                        name = "Mídias",
                        value = f"Existe um [vídeo do Youtube]({post['url']}) anexado ao post."
                    ).set_image(
                        url = post['secure_media']['oembed']['thumbnail_url']
                    )
            elif post['post_hint'] == 'link':
                if post['domain'] == 'i.imgur.com':
                    embed.add_field(
                        name = "Mídias",
                        value = f"Existe um gif do Imgur anexado ao post."
                    ).set_image(
                        url = post['url'].replace("gifv", "gif")
                    )
                elif 'crosspost_parent' in post:
                    embed.description += f"\nEsse post é um crosspost. [Link do post original]({'https://www.reddit.com'+post['crosspost_parent_list'][0]['permalink']})."
        elif "is_gallery" in post and post['is_gallery']:
            if post["media_metadata"]:
                embed.add_field(
                    name = "Mídias",
                    value = f"Esse post contem uma galeria com [{len(post['gallery_data']['items'])} imagens]({post['url']})."
                ).set_image(
                    url = post['media_metadata'][post['gallery_data']['items'][0]['media_id']]['p'][0]['u'].replace("preview", "i").split('?')[0]
                )
        elif 'poll_data' in post:
            opções = ''
            for opção in post['poll_data']['options']:
                opções += f"\nOpção {post['poll_data']['options'].index(opção)+1}: **{opção['text']}**"
            embed.add_field(
                name = "Enquete",
                value = f"Número total de votos: {post['poll_data']['total_vote_count']}" + opções
            )
        if self.adicionou_botão:
            self.botão.url = f"https://www.reddit.com{post['permalink']}"
        else:
            self.botão = discord.ui.Button(url = f"https://www.reddit.com{post['permalink']}", label = "Abrir no Reddit")
            menu.add_item(self.botão)
            self.adicionou_botão = True
        return embed

class FonteTwitter(menus.ListPageSource):
    adicionou_botão = False
    menção = None
    def adicionar_anexos(self, anexos):
        self.anexos = anexos

    def format_page(self, menu, post):
        anexos = self.anexos
        if post["possibly_sensitive"] and not menu.ctx.channel.is_nsfw():
            embed = discord.Embed(
                title = "Tweet NSFW",
                description = "Esse tweet é NSFW e só pode ser visto em canais apropriados.",
                color = 0x57C7FF,
                timestamp = discord.utils.utcnow()
            ).set_footer(
                text = "twitter.com",
                icon_url = "https://media.discordapp.net/attachments/803443536363913236/874767316108341258/580b57fcd9996e24bc43c53e.png"
            )
            if self.menção:
                if self.adicionou_botão:
                    menu.remove_item(self.botão)
                    self.adicionou_botão = False
            return embed
        autor = "Não foi possivel conseguir o nome do autor"
        for usuario in anexos['users']:
            if usuario['id'] == post['author_id']:
                autor = usuario['name']
                self.menção = usuario["username"]
        embed = discord.Embed(
            title = f"Exibindo tweet de **@{autor}**",
            description = "\"" + post['text'] + "\"",
            color = 0x57c7FF,
            timestamp = dt_parse(post['created_at'])
        ).add_field(
            name = "Informações do Tweet",
            value = f"Postado de \"{post['source']}\"\nID: {post['id']}\n\u2764\ufe0f {post['public_metrics']['like_count']} | \U0001f4ac {post['public_metrics']['reply_count']} | \U0001f5ef\ufe0f {post['public_metrics']['quote_count']} | \U0001f501 {post['public_metrics']['retweet_count']}",
            inline = False
        ).set_footer(
            text = "twitter.com | Tweet feito em",
            icon_url = "https://media.discordapp.net/attachments/803443536363913236/874767316108341258/580b57fcd9996e24bc43c53e.png"
        )
        if 'referenced_tweets' in post:
            for tweet_referenciado in post['referenced_tweets']:
                if tweet_referenciado['type'] == 'replied_to':
                    id_tweet = tweet_referenciado['id']
                    if anexos.get('tweets'):
                        for tweet in anexos['tweets']:
                            if tweet['id'] == id_tweet:
                                nome_autor_referenciado = "(Não foi possível obter o nome do autor)"
                                for usuario in anexos['users']:
                                    if usuario['id'] == tweet['author_id']:
                                        nome_autor_referenciado = usuario['name']
                                        break
                                embed.add_field(
                                    name = "Resposta",
                                    value = f"Esse tweet responde a um tweet postado originalmente por {nome_autor_referenciado}.\n**Conteúdo**: \"{tweet['text']}\""
                                )
                                break
                        else:
                            embed.add_field(
                                name = "Resposta",
                                value = "Esse tweet responde a outro tweet, mas o autor privou seu perfil então ele não será exibido aqui."
                            )
                    else:
                        embed.add_field(
                            name = "Resposta",
                            value = "Esse tweet responde a outro tweet, mas o autor privou seu perfil então ele não será exibido aqui."
                        )
        if 'attachments' in post:
            if 'media_keys' in post['attachments']:
                id_midia = post['attachments']['media_keys'][0]
                for midia in anexos['media']:
                    if midia['media_key'] == id_midia:
                        if midia['type'] == 'photo':
                            embed.set_image(
                                url = midia['url']
                            ).add_field(
                                name = "Anexos",
                                value =  f"Tipo de mídia anexada: Imagem\nNúmero de mídias: {len(post['attachments']['media_keys'])}",
                                inline = False
                            )
                            break
                        elif midia['type'] == 'video':
                            embed.set_image(
                                url = midia['preview_image_url']
                            ).add_field(
                                name = "Anexos",
                                value = "Tipo de mídia anexada: Vídeo (exibindo thumbnail)",
                                inline = False
                            )
                            break
                        elif midia['type'] == 'animated_gif':
                            embed.set_image(
                                url = midia['preview_image_url']
                            ).add_field(
                                name = "Anexos",
                                value = "Tipo de mídia anexada: Gif (Exibindo thumbnail)",
                                inline = False
                            )
                            break
            elif 'poll_ids' in post['attachments']:
                id_enquete = post['attachments']['poll_ids'][0]
                for enquete in anexos['polls']:
                    if enquete['id'] == id_enquete:
                        enquete['options'].sort(key = lambda e: str(e['position']))
                        embed.add_field(
                            name = "Enquete",
                            value = f"Termina em: {enquete['end_datetime'].replace('-', '/').replace('T', '  ')}",
                            inline = False
                        ).add_field(
                            name = "Opções",
                            value = "\n".join([infos['label'] for infos in enquete['options']]),
                            inline = True
                        ).add_field(
                            name = "Votos",
                            value = "\n".join([str(infos['votes']) for infos in enquete['options']]),
                            inline = True
                        )
                        break
        if self.menção:
            if self.adicionou_botão:
                self.botão.url = f"https://twitter.com/{self.menção}/status/{post['id']}"
            else:
                self.botão = discord.ui.Button(url = f"https://twitter.com/{self.menção}/status/{post['id']}", label = "Abrir no Twitter")
                menu.add_item(self.botão)
                self.adicionou_botão = True
        return embed

class FonteSpotify(menus.ListPageSource):
    adicionou_botão = False
    def escolher_metodo(self, metodo: str):
        if metodo == "musica":
            self.format_page = self.musica

    def musica(self, menu, resultado):
        descrição = f"**Artista**: {', '.join([('[' + artista['name'] + '](' + artista['external_urls']['spotify'] + ')') for artista in resultado['artists']])}\n"
        segundos, milisegundos = divmod(resultado['duration_ms'], 1000)
        minutos, segundos = divmod(segundos, 60)
        descrição += f"**Duração**: {minutos:02}:{segundos:02}\n**Popularidade**: {resultado['popularity']}/100\n"\
        f"**Posição**: {resultado['track_number']}/{resultado['album']['total_tracks']}\n**Disco**: {resultado['disc_number']}"
        embed = discord.Embed(
            title = resultado['name'],
            description = descrição,
            color = 0x1db954,
            timestamp = discord.utils.utcnow()
        ).add_field(
            name = "Informações do álbum",
            value = f"**Nome**: [{resultado['album']['name']}]({resultado['album']['external_urls']['spotify']})"\
            f"\n**Tipo**: {resultado['album']['album_type']}\n"\
            f"**Data de lançamento**: {resultado['album']['release_date']}\n"\
            f"**Artista**: {', '.join(artista['name'] for artista in resultado['album']['artists'])}"
        ).set_image(
            url = resultado['album']['images'][0]['url']
        ).set_footer(
            text = f"Spotify.com",
            icon_url = "https://media.discordapp.net/attachments/803443536363913236/897683078321930261/2048px-Spotify_logo_without_text.svg.png"
        )
        if self.adicionou_botão:
            self.botão.url = resultado['external_urls']['spotify']
        else:
            self.botão = discord.ui.Button(url = resultado['external_urls']['spotify'], label = "Abrir no Spotify")
            menu.add_item(self.botão)
            self.adicionou_botão = True
        return embed

def setup(bot):
    bot.paginador = Paginador
