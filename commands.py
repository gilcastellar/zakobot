
import discord

def ajuda():

    embed = discord.Embed(title='Instruções:')
    embed.add_field(name='Se voc o comando ;cadastro seguido do tipo de obra que aceita',value='',inline=False)
    embed.add_field(name='',value='Exemplos:',inline=False)
    embed.add_field(name='',value=';cadastro anime \n ;cadastro manga \n ;cadastro animanga',inline=False)
    embed.add_field(name="", value="", inline=False)
    embed.add_field(name="--", value="", inline=False)
    embed.add_field(name="", value="", inline=False)
    embed.add_field(name='Para participar da próxima roleta, digite ;ativar. Para se ausentar, use ;desativar',value='',inline=False)
    embed.add_field(name="", value="", inline=False)
    embed.add_field(name="--", value="", inline=False)
    embed.add_field(name="", value="", inline=False)
    embed.add_field(name='Para adicionar observações, como limite de cours ou volumes utilize o comando ;obs seguido de todas as observações em uma só mensagem',value='',inline=False)
    embed.add_field(name='',value='Exemplo:',inline=False)
    embed.add_field(name='',value=';obs Aceito animes de até 26 episódios e mangás de até 10 volumes. \n\n Sem ecchi! \n\nLista: anilist.co/Kaiser',inline=False)            
    embed.add_field(name="", value="", inline=False)
    embed.add_field(name="--", value="", inline=False)
    embed.add_field(name="", value="", inline=False)
    embed.add_field(name='Finalmente, para checar seu perfil utilize o comando ;perfil (para checar o perfil de outro usuário, use ;perfil @usuario ou ID)',value='',inline=False)
    embed.add_field(name='',value='Exemplos:',inline=False)
    embed.add_field(name='',value=';perfil @kaiser \n ;perfil 906937520254758973',inline=False) 

    return embed