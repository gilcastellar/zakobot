
import discord

def help():

    embed = discord.Embed(title='Instru��es:')
    embed.add_field(name='Para se cadastrar ou alterar seu cadastro, utilize novamente o comando ;cadastro seguido do tipo de obra que aceita',value='',inline=False)
    embed.add_field(name='',value='Exemplos:',inline=False)
    embed.add_field(name='',value=';cadastro anime \n ;cadastro manga \n ;cadastro animanga',inline=False)
    embed.add_field(name="", value="", inline=False)
    embed.add_field(name="--", value="", inline=False)
    embed.add_field(name="", value="", inline=False)
    embed.add_field(name='Para participar da pr�xima roleta, digite ;ativar. Para se ausentar, use ;desativar',value='',inline=False)
    embed.add_field(name="", value="", inline=False)
    embed.add_field(name="--", value="", inline=False)
    embed.add_field(name="", value="", inline=False)
    embed.add_field(name='Para adicionar observa��es, como limite de cours ou volumes utilize o comando ;obs seguido de todas as observa��es em uma s� mensagem',value='',inline=False)
    embed.add_field(name='',value='Exemplo:',inline=False)
    embed.add_field(name='',value=';obs Aceito animes de at� 26 epis�dios e mang�s de at� 10 volumes. \n\n Sem ecchi! \n\nLista: anilist.co/Kaiser',inline=False)            
    embed.add_field(name="", value="", inline=False)
    embed.add_field(name="--", value="", inline=False)
    embed.add_field(name="", value="", inline=False)
    embed.add_field(name='Finalmente, para checar seu perfil utilize o comando ;perfil (para checar o perfil de outro usu�rio, use ;perfil @usuario ou ID)',value='',inline=False)
    embed.add_field(name='',value='Exemplos:',inline=False)
    embed.add_field(name='',value=';perfil @kaiser \n ;perfil 906937520254758973',inline=False) 

    return embed