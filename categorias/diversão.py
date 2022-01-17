import discord
from discord.ext import commands
from plugins.variaveis import CooldownEspecial

from urllib.parse import quote
import random
import asyncio

class botãojogodavelha(discord.ui.Button):
    def __init__(self, x, y):
        super().__init__(style = discord.ButtonStyle.blurple, label = "\u2800", row = y)
        self.x = x
        self.y = y

    async def callback(self, interação):
        if self.view.campo[self.x][self.y] != 0:
            return await interação.response.send_message("Esse quadrado já foi preenchido!", ephemeral = True)
        self.label = ""
        if self.view.jogador == self.view.X:
            self.emoji = "\u274c"
            conteudo = "Vez do jogador \u2b55"
            self.view.campo[self.x][self.y] = self.view.X
            self.view.jogador = self.view.O
        else:
            self.emoji = "\u2b55"
            conteudo = "Vez do jogador \u274c"
            self.view.campo[self.x][self.y] = self.view.O
            self.view.jogador = self.view.X
        ganhador = self.view.ver_ganhador()
        if ganhador:
            if ganhador == self.view.X:
                conteudo = "Jogador \u274c ganhou o jogo!"
            elif ganhador == self.view.O:
                conteudo = "Jogador \u2b55 ganhou o jogo!"
            else:
                conteudo = "Jogo empatado!"
            for botão in self.view.children:
                botão.disabled = True
        await interação.response.edit_message(content = conteudo, view=self.view)

class viewjogodavelha(discord.ui.View):
    X = 1
    O = -1
    Empate = 2
    def __init__(self, jogador_x, jogador_o, ctx):
        super().__init__(timeout = 90)
        self.jogador_x = jogador_x.id
        self.jogador_o = jogador_o.id
        self.ctx = ctx
        self.jogador = self.X
        self.campo = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ]
        self.avisados = []
        for x in range(3):
            for y in range(3):
                self.add_item(botãojogodavelha(x, y))

    async def interaction_check(self, interação):
        if self.jogador == self.X and interação.user.id == self.jogador_o:
            await interação.response.send_message("Não é a sua vez agora!", ephemeral = True)
            return False
        elif self.jogador == self.O and interação.user.id == self.jogador_x:
            await interação.response.send_message("Não é a sua vez agora!", ephemeral = True)
            return False
        elif interação.user.id != self.jogador_x and interação.user.id != self.jogador_o:
            if interação.user.id not in self.avisados:
                await interação.response.send_message("Você não está nesse jogo.", ephemeral = True)
                self.avisados.append(interação.user.id)
            else:
                await interação.response.defer()
            return False
        else:
            return True

    def ver_ganhador(self):
        for horizontal in self.campo:
            valor = sum(horizontal)
            if valor == 3:
                return self.X
            elif valor == -3:
                return self.O

        for coluna in range(3):
            valor = self.campo[0][coluna] + self.campo[1][coluna] + self.campo[2][coluna]
            if valor == 3:
                return self.X
            elif valor == -3:
                return self.O

        valor = self.campo[0][2] + self.campo[1][1] + self.campo[2][0]
        if valor == 3:
            return self.X
        elif valor == -3:
            return self.O

        valor = self.campo[0][0] + self.campo[1][1] + self.campo[2][2]
        if valor == 3:
            return self.X
        elif valor == -3:
            return self.O

        if all(i != 0 for linha in self.campo for i in linha):
            return self.Empate
        return None

    async def on_timeout(self):
        await self.ctx.send("O jogo da velha foi cancelado devido a inatividade.", delete_after = 10)
        self.stop()

class viewgenius(discord.ui.View):
    VERMELHO = 1
    AMARELO = 2
    VERDE = 3
    AZUL = 4
    def __init__(self, ctx):
        super().__init__(timeout = 5)
        self.ctx = ctx
        self.avisados = []
        self.sequencia = [random.choice((self.VERMELHO, self.AMARELO, self.VERDE, self.AZUL))]
        self.posição = 0
        self.emojis = {
            self.VERMELHO: "\U0001f7e5",
            self.AMARELO: "\U0001f7e8",
            self.VERDE: "\U0001f7e9",
            self.AZUL: "\U0001f7e6"
        }

    def embed_cores(self):
        embed = discord.Embed(
            title = "Genius",
            description = "Decore a sequência abaixo:\n" + "".join([self.emojis[cor] for cor in self.sequencia]),
            color = 0x5757FF,
            timestamp = discord.utils.utcnow()
        ).set_footer(
            text = self.ctx.author,
            icon_url = self.ctx.author.avatar.url
        )
        return embed

    def embed_aguardando(self):
        embed = discord.Embed(
            title = "Genius",
            description = "Reaja na ordem da sequência...",
            color = 0x5757FF,
            timestamp = discord.utils.utcnow()
        ).set_footer(
            text = self.ctx.author,
            icon_url = self.ctx.author.avatar.url
        )
        return embed

    def embed_proxima(self):
        embed = discord.Embed(
            title = "Genius",
            description = "Parabens! Você acertou essa sequência e agora pode prosseguir para a proxima... Aguarde.",
            color = 0x5757FF,
            timestamp = discord.utils.utcnow()
        ).set_footer(
            text = self.ctx.author,
            icon_url = self.ctx.author.avatar.url
        )
        return embed

    def embed_perdeu_errou(self):
        embed = discord.Embed(
            title = "Genius",
            description = f"Você reagiu a cor errada e perdeu o jogo. Pontuação: {len(self.sequencia)-1}.",
            color = 0xFF1010,
            timestamp = discord.utils.utcnow()
        ).set_footer(
            text = self.ctx.author,
            icon_url = self.ctx.author.avatar.url
        )
        return embed

    def embed_perdeu_tempo(self):
        embed = discord.Embed(
            title = "Genius",
            description = f"Você demorou a reagir e perdeu o jogo. Pontuação: {len(self.sequencia)-1}.",
            color = 0xFF1010,
            timestamp = discord.utils.utcnow()
        ).set_footer(
            text = self.ctx.author,
            icon_url = self.ctx.author.avatar.url
        )
        return embed

    async def interaction_check(self, interação):
        if self.ctx.author.id == interação.user.id:
            return True
        else:
            if interação.user.id in self.avisados:
                await interação.response.defer()
                return False
            else:
                self.avisados.append(interação.user.id)
                await interação.response.send_message("Esse não é seu jogo!", ephemeral = True)
                return False
    
    async def começar(self):
        self.mensagem = await self.ctx.send(embed = self.embed_cores(), view = self)
        for botão in self.children:
            botão.disabled = False
        await asyncio.sleep(2.5)
        await self.mensagem.edit(embed = self.embed_aguardando(), view = self)

    async def proxima_sequencia(self, interação):
        for botão in self.children:
            botão.disabled = True
        self.timeout = None
        await interação.response.edit_message(embed = self.embed_proxima(), view = self)
        self.sequencia = [random.choice((self.VERMELHO, self.AMARELO, self.VERDE, self.AZUL)) for i in range(len(self.sequencia)+1)]
        self.posição = 0
        await asyncio.sleep(4)
        await self.mensagem.edit(embed = self.embed_cores(), view = self)
        for botão in self.children:
            botão.disabled = False
        await asyncio.sleep(25-25*0.95**len(self.sequencia))
        await self.mensagem.edit(embed = self.embed_aguardando(), view = self)
        self.timeout = 10-10*0.8**len(self.sequencia)
    
    @discord.ui.button(style = discord.ButtonStyle.red, emoji = "\U0001f7e5", disabled = True)
    async def botãovermelho(self, botão, interação):
        if self.sequencia[self.posição] == self.VERMELHO:
            if self.posição < len(self.sequencia)-1:
                self.posição += 1
                await interação.response.defer()
            else:
                await self.proxima_sequencia(interação)
        else:
            for botão in self.children:
                botão.disabled = True
            await interação.response.edit_message(embed = self.embed_perdeu_errou(), view = self)
            self.stop()

    @discord.ui.button(style = discord.ButtonStyle.gray, emoji = "\U0001f7e8", disabled = True)
    async def botãoamarelo(self, botão, interação):
        if self.sequencia[self.posição] == self.AMARELO:
            if self.posição < len(self.sequencia)-1:
                self.posição += 1
                await interação.response.defer()
            else:
                await self.proxima_sequencia(interação)
        else:
            for botão in self.children:
                botão.disabled = True
            await interação.response.edit_message(embed = self.embed_perdeu_errou(), view = self)
            self.stop()

    @discord.ui.button(style = discord.ButtonStyle.green, emoji = "\U0001f7e9", disabled = True)
    async def botãoverde(self, botão, interação):
        if self.sequencia[self.posição] == self.VERDE:
            if self.posição < len(self.sequencia)-1:
                self.posição += 1
                await interação.response.defer()
            else:
                await self.proxima_sequencia(interação)
        else:
            for botão in self.children:
                botão.disabled = True
            await interação.response.edit_message(embed = self.embed_perdeu_errou(), view = self)
            self.stop()

    @discord.ui.button(style = discord.ButtonStyle.blurple, emoji = "\U0001f7e6", disabled = True)
    async def botãoazul(self, botão, interação):
        if self.sequencia[self.posição] == self.AZUL:
            if self.posição < len(self.sequencia)-1:
                self.posição += 1
                await interação.response.defer()
            else:
                await self.proxima_sequencia(interação)
        else:
            for botão in self.children:
                botão.disabled = True
            await interação.response.edit_message(embed = self.embed_perdeu_errou(), view = self)
            self.stop()

    async def on_timeout(self):
        for botão in self.children:
            botão.disabled = True
        await self.mensagem.edit(embed = self.embed_perdeu_tempo(), view = self)
        self.stop()

class diversão(
    commands.Cog, 
    name = "Diversão", 
    description = "Essa categoria contém comandos relativos a diversão, como comandos de piada e gozação."
):
    def __init__(self, bot):
        self.bot = bot
        self.emoji = "<:PepeClown:802380972233719910>"
    
    @commands.command(
      aliases = ("joke", "charada"),
      brief = "Envia uma piada no chat"
    )
    async def piada(self, ctx):
        """Envia uma piada no chat. As piadas são retiradas da API \"https://api-charada.herokuapp.com/puzzle?lang=ptbr\"."""
        mensagem = await ctx.send(f"Aguardando piada... Isso pode demorar um pouco no primeiro uso do comando. {self.bot.emoji['WindowsLoading']}")
        async with self.bot.conexão.get("https://api-charada.herokuapp.com/puzzle?lang=ptbr") as resposta:
            json = await resposta.json()
            await mensagem.edit(content = f"{json['question']}\n\n||{json['answer']}||")
    
    @commands.command(extras = {"alvo": "No que você vai gozar",
                                "exemplos": ("Quem ta lendo", "João Gameplays 9500")})
    async def gozar(self, ctx, *,alvo):
        """Goza em qualquer coisa que você inserir. (Comando SFW)"""
        if len(alvo) > 100:
            alvo = alvo[0:100]
        await ctx.send(
            f"""{ctx.author.mention}
\U0001f60e
(\\
8=\U0001f44a=D
|\              \U0001f4a6
\U0001f45f\U0001f45f           \U0001f4a6
                       {alvo}""",
            allowed_mentions = discord.AllowedMentions(everyone = False, roles = False)
        )
    
    @commands.command(
        aliases = ("question", "8ball", "p"),
        brief = "Responde a uma pergunta com sim ou não",
        extras = {"pergunta": "A pergunta a ser respondida",
                  "exemplos": ("O bot é bom?", "O bot é ruim?")}
    )
    async def pergunta(self, ctx, *,pergunta):
        """Responde a uma pergunta com afirmações ou negações. Apenas frases terminadas com \"?\" são consideradas perguntas."""
        if pergunta.endswith("?"):
            respostas = [
                "Lógico que não, tá na cara", "Meus cálculos extensivos dizem que não", "Com toda a certeza não!", 
                "Definitivamente não", "Não", "\U0001f44e\U0001f3fb", "Provavelmente não", "Acho que não", "Talvez não", 
                "Não sei...", "Talvez sim", "Acho que sim", "Provavelmente sim", "\U0001f44d\U0001f3fb", "Sim", 
                "Definitivamente sim", "Com toda a certeza sim!", "Meus cálculos extensivos dizem que sim", 
                "Lógico que sim, tá na cara"
            ]
            await ctx.send(random.choice(respostas))
        else:
            await ctx.send("Isso não foi uma pergunta!")
    
    @commands.command(
        aliases = ("pinto", "pau", "piroca", "jiromba"),
        brief = "Manda o tamanho do pênis de alguém",
        extras = {"membro": "A menção ou ID de alguém do servidor",
                  "exemplos": ("<@531508181654962197>", "531508181654962197")}
    )
    @commands.bot_has_permissions(embed_links = True)
    async def penis(self, ctx, membro: discord.Member = None):
        """Manda o tamanho do pênis de alguém."""
        membro = membro or ctx.author
        medida = random.randint(0,40)
        penis = "8"
        i = 0
        while i < medida:
            penis += "="
            i += 2
        penis += "D"
        embed = discord.Embed(
            title = f"{membro.name} tem {medida}cm de pinto!",
            description = penis,
            color = membro.color,
            timestamp = discord.utils.utcnow()
        )
        if random.randint(0,50) == 1:
            embed.description = "Espera... Ele também tem 4 bolas? que? O_O\n8" + embed.description
        await ctx.send(embed=embed)
    
    @commands.command(
        name = "ascii",
        brief = "Transforma uma frase em caracteres especiais",
        extras = {"frase": "A frase a ser convertida",
                  "exemplos": ("Teste", "Locomotive Bot")}
    )
    async def _ascii(self, ctx, *,frase):
        """Transforma uma frase em caracteres especiais. A conversão é feita usando a API \"https://artii.herokuapp.com/make\"."""
        if len(frase) > 20:
            frase = frase[:20]
        frase = quote(frase)
        async with self.bot.conexão.get(f"https://artii.herokuapp.com/make?text={frase}") as resposta:
            await ctx.send(f"```\n{await resposta.text()}\n```")

    @commands.command(
        brief = "Joga jogo da velha com alguém",
        aliases = ("jdv", "jv", "ttt", "tictactoe"),
        extras = {"jogador": "A pessoa com quem você jogará o jogo da velha.",
                  "exemplos": ("<@531508181654962197>", "531508181654962197")}
    )
    @commands.dynamic_cooldown(CooldownEspecial(3, 45), type = commands.BucketType.member)
    async def jogodavelha(self, ctx, jogador: discord.Member):
        """Joga jogo da velha com alguém por meio de botões."""
        if jogador == ctx.author:
            return await ctx.send("Você não pode jogar com si mesmo.")
        elif jogador.bot:
            return await ctx.send("Você não pode jogar com um bot.")
        if bool(random.randint(0,1)):
            jogodavelha = viewjogodavelha(ctx.author, jogador, ctx)
            await ctx.send(f"O jogo foi iniciado ({ctx.author.name} começa).", view = jogodavelha)
        else:
            jogodavelha = viewjogodavelha(jogador, ctx.author, ctx)
            await ctx.send(f"O jogo foi iniciado ({jogador.name} começa).", view = jogodavelha)

    @commands.command(
        brief = "Jogue genius/simon usando o bot",
        aliases = ("simon",)
    )
    @commands.max_concurrency(1,commands.BucketType.member)
    @commands.bot_has_permissions(embed_links = True)
    async def genius(self, ctx):
        """Jogue genius/simon usando o bot."""
        genius = viewgenius(ctx)
        await genius.começar()
    
def setup(bot):
    bot.add_cog(diversão(bot))
