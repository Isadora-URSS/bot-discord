import discord
from discord.ext import commands
from .variaveis import TempoInvalido, Banido, CanalDesativado
import aiohttp

class logerros(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        titulo = "Titulo inexistente?"
        descrição = "Se você esta vendo esse texto significa que o erro que ocorreu nao tem uma mensagem de erro associada. Se você esta vendo isso, avise ao dono do bot por meio do servidor de suporte (disponível no comando de ajuda)."
        rodapé = f"Se achar que algo está errado, entre em contato com o dono."
        uso = "Esse comando não tem uso definido (isso provavelmente é um erro)"
        if ctx.command != None:
            uso = f"{ctx.prefix}{ctx.invoked_with} {ctx.command.signature}"
        if isinstance(error, commands.UserInputError):
            if isinstance(error, commands.MissingRequiredArgument):
                titulo = f"{self.bot.emoji['PepePuto']} Você não chamou o comando inteiro"
                descrição = f"Você não passou todos os argumentos do comando. Veja quais argumentos esse comando tem:\n`{uso}`\nVocê não passou o argumento `{error.param}`."
            elif isinstance(error, commands.BadArgument):
                if isinstance(error, commands.MessageNotFound):
                    titulo = f"{self.bot.emoji['PepeRage']} Você não me passou uma mensagem valida"
                    descrição = f"Você não me apontou a uma mensagem válida. Se lembre de que eu consigo encontrar mensagens pelo ID delas (ou pela forma [ID do canal]-[ID da mensagem]), então me passe um de uma mensagem que eu consiga ver. Na dúvida, veja como deve ser chamado o comando: \n`{uso}`."
                elif isinstance(error, commands.MemberNotFound):
                    titulo = f"{self.bot.emoji['PepeThink']} Você não apontou para um membro"
                    descrição = f"Eu não achei o membro especificado. Eu procuro baseado em menções, IDs ou o nome por extenso. Tenha atenção de que o usuário deve estar no servidor. Na duvida, veja como o comando deve ser chamado:\n`{uso}`."
                elif isinstance(error, commands.UserNotFound):
                    titulo = f"{self.bot.emoji['PepeSad']} Você não me passou um usuário"
                    descrição = f"Eu não achei o usuário especificado. Eu procuro baseado em menções e em IDs, e o usuário não precisa estar no servidor. Para caso de duvidas, veja como o comando tem que ser chamado: \n`{uso}`."
                elif isinstance(error, commands.ChannelNotFound):
                    titulo = f"{self.bot.emoji['PepeDown']} Você não passou um canal válido"
                    descrição = f"Eu não achei o canal passado. Eu procuro por ID e por #link-ao-canal. Para caso de duvidas, veja como o comando deve ser chamado: \n`{uso}`."
                elif isinstance(error, commands.ChannelNotReadable):
                    titulo = f"{self.bot.emoji['PepeClown']} Eu não consigo ver esse canal"
                    descrição = "Eu consigo detectar o canal, mas não consigo visualizar seu conteúdo."
                elif isinstance(error, commands.RoleNotFound):
                    titulo = f"{self.bot.emoji['PepeNo']} Você não me passou um cargo válido"
                    descrição = f"Eu não achei o cargo especificado. Eu procuro os cargos usando menções ou IDs, então me passe um desses (obs: Cargos criados quando um bot entra no servidor não são validos). Na dúvida, veja como deve ser chamado o comando: \n`{uso}`."
                elif isinstance(error, commands.EmojiNotFound):
                    titulo = f"{self.bot.emoji['PepeBoomer']} Você não me passou um emoji"
                    descrição = f"Eu não consegui achar o emoji que você passou. Na dúvida, veja como o comando deve ser chamado: \n`{uso}`"
                elif isinstance(error, TempoInvalido):
                    titulo = f"{self.bot.emoji['PepeDown']} Você inseriu um marcador de tempo inválido"
                    descrição = f"O tempo que você passou está inválido. Eu aceito tempos compostos de número + sufixo de escala (`s` para segundos, `m` para minutos, `h` para horas, `d` para dias e `y` ou `a` para anos). Você errou ao inserir `{error.texto}`\nNa dúvida, veja como o comando deve ser invocado: \n`{uso}`"
                else:
                    titulo = f"{self.bot.emoji['PepePropelerSad']} Argumento inválido!"
                    descrição = f"Não sei bem em qual parte do comando você errou, mas algo que você me passou esta errado. Na dúvida, veja como o comando deve ser chamado:\n `{uso}`."
            elif isinstance(error, commands.BadUnionArgument):
                titulo = "Você não passou um argumento valido"
                descrição = f"O comando que você chamou tem um parâmetro que faz buscas por múltiplos objetos (exemplo: procura um membro e se não achar, procura um usuário no geral) e seu argumento não se adequou ao que ele procurava. Veja como o comando deve ser chamado: \n`{uso}`\nE você passou o argumento {error.param} errado."
            else:
                titulo = f"{self.bot.emoji['PepePropelerSad']} Problemas na sua mensagem"
                descrição = f"Você me passou algum parâmetro errado na hora de chamar o comando, mas infelizmente eu não consigo identificar o que foi. Veja como o comando deve ser chamado:\n`{uso}`"
            descrição += "\n\n**Tipo de erro:** Erro de entrada. (argumento inserido erroneamente)"
        elif isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.CheckFailure):
            if isinstance(error, commands.NoPrivateMessage):
                titulo = f"{self.bot.emoji['PepeNo']} Sem mensagens privadas!"
                descrição = "Eu não atendo mensagens privadas."
            elif isinstance(error, commands.NotOwner):
                return
            elif isinstance(error, commands.MissingPermissions):
                titulo = f"{self.bot.emoji['PepeSoviet']} Você não tem permissões para isso"
                descrição = "Você não tem permissões para executar esse comando no servidor atual. As permissões necessárias são:"
                for permissão in error.missing_permissions:
                    descrição += "\n-`" + permissão + "`"
            elif isinstance(error, commands.BotMissingPermissions):
                titulo = f"{self.bot.emoji['PepeDown']} O bot não pode realizar o comando"
                descrição = "O bot não tem permissões para executar o comando solicitado. As permissões necessárias são:"
                for permissão in error.missing_permissions:
                    descrição += "\n-`" + permissão + "`"
            elif isinstance(error, commands.NSFWChannelRequired):
                titulo = f"{self.bot.emoji['YumekoConfused']} Esse canal não é NSFW"
                descrição = "Esse comando que você está tentando executar é um comando NSFW e consequentemente só pode ser visto em canais NSFW."
            elif isinstance(error, Banido):
                titulo = f"{self.bot.emoji['PepeSoviet']} Você não pode usar comandos"
                descrição = "Você foi BANIDO do bot e não pode usá-lo até que o dono te desbana."
            elif isinstance(error, CanalDesativado):
                return
            else:
                titulo = f"{self.bot.emoji['PepeSoviet']} Você não está autorizado!"
                descrição = "Esse comando tem um critério para ser usado, e você devido a algum motivo não passou no critério."
            descrição += f"\n\n**Tipo de erro:** Erro de autorização (usuário não autorizado a usar o comando."
        elif isinstance(error, commands.DisabledCommand):
            titulo = "Esse comando está desabilitado!"
            descrição = "O comando que você está tentando usar está desabilitado, isso pode ser uma configuração do servidor ou o comando está desabilitado no bot todo.\n\n**Tipo de erro:** Comando desativado."
        elif isinstance(error, commands.CommandOnCooldown):
            titulo = "Comando em cooldown!"
            descrição = f"Esse comando está em cooldown, ou seja, seu limite de usos em um janela de tempo se esgotou.\nSão permitidos `{error.cooldown.rate}` usos em um intervalo de tempo de `{error.cooldown.per}` segundos."
            usar_em = int(discord.utils.utcnow().timestamp() + error.retry_after)
            usar_em = f"<t:{usar_em}:R> (<t:{usar_em}:T>)"
            if error.type is commands.BucketType.default:
                descrição += f"\nO comando só podera ser usado novamente {usar_em}."
            elif error.type is commands.BucketType.user:
                descrição += f"\nVocê só podera usar o comando novamente {usar_em}."
            elif error.type is commands.BucketType.guild:
                descrição += f"\nO comando só poderá ser usado no servidor novamente {usar_em}."
            elif error.type is commands.BucketType.channel:
                descrição += f"\nO comando só poderá ser usado no canal {usar_em}."
            elif error.type is commands.BucketType.member:
                descrição += f"\nVocê só poderá usar o comando no servidor novamente {usar_em}."
            elif error.type is commands.BucketType.category:
                descrição += f"\nO comando só poderá ser usado na categoria novamente {usar_em}."
            elif error.type is commands.BucketType.role:
                descrição += f"\nO comando só poderá ser usado pelo cargo limitado novamente {usar_em}."
            descrição += "\n\n**Tipo de erro:** Comando em cooldown."
        elif isinstance(error, commands.MaxConcurrencyReached):
            titulo = "O comando ja alcançou seus usos máximos!"
            descrição = f"Esse comando já alcançou os usos máximos simultâneos dele, o que significa que você deve esperar um dos comandos em execução acabar.\nO número máximo de usos desse comando simultaneamente é de `{error.number}` por "
            if error.per is commands.BucketType.default:
                descrição = descrição[0:-5]
            elif error.per is commands.BucketType.user:
                descrição += "usuário."
            elif error.per is commands.BucketType.guild:
                descrição += "servidor."
            elif error.per is commands.BucketType.channel:
                descrição += "canal."
            elif error.per is commands.BucketType.member:
                descrição += "membro."
            elif error.per is commands.BucketType.category:
                descrição += "categoria."
            elif error.per is commands.BucketType.role:
                descrição += "cargo."
            descrição += "\n\n**Tipo de erro:** Usos máximos alcançados"
        else:
            error = error.original
            if isinstance(error, discord.Forbidden):
                descrição = "O bot não tem permissões para realizar alguma ação demandada pelo comando. Se você está vendo isso, significa que a verificação das permissões não é realizada previamente, o que é um erro do código. Por favor, reporte ao dono no servidor de suporte (disponivel no comando de ajuda)"
                titulo = "Erro de permissão"
            else:    
                titulo = f"Erro desconhecido! {self.bot.emoji['Suicidio']}"
                servidor = self.bot.get_guild(801185265363845140)
                canal = servidor.get_channel(802626994633834576)
                botinfos = await self.bot.database.botinfos.find_one({})
                numero_erro = botinfos["erro"]
                descrição = f"Ocorreu um erro não esperado no bot (provavelmente não ligado ao usuário). O erro foi informado ao desenvolvedor do bot, com o código `{numero_erro}`.\n\n**Tipo de erro:** Erro desconhecido."
                await self.bot.database.botinfos.update_one({}, {"$inc": {"erro": 1}})
                await canal.send(f"Ocorreu um erro não esperado. Abaixo as informações:\n================================\nCódigo: **#{numero_erro}**\nId do servidor: {ctx.guild.id}\nId canal: {ctx.channel.id}\nAutor: {ctx.author} - {ctx.author.id}\nMensagem: {ctx.message.content[0:700]}\n================================\n{repr(error)}\n================================")
        
        if not ctx.me.guild_permissions.embed_links:
            await ctx.send(descrição + "\n\n" + rodapé, delete_after = 30)
        else:
            embed = discord.Embed(
                title = titulo,
                description = descrição,
                color = 0xFF0000,
                timestamp = discord.utils.utcnow()
            ).set_footer(
                text = rodapé
            )
            await ctx.send(embed=embed, delete_after = 30)

def setup(bot):
    bot.add_cog(logerros(bot))
