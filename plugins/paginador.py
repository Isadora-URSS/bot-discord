import discord
from discord.ext import commands

import asyncio

#agradecimento especial a Rapptz/Danny, esse paginador teve seu estilo inspirado em seu paginador usado no bot Robo Danny.
#special thanks to Rapptz/Danny, their paginator style used in r. Danny inspired me to do mine.

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

def setup(bot):
    bot.paginador = Paginador
