import discord
import roulettetools
import json


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

def cadastro(msg, info):
    if len(msg) != 2:
        return 'Você enviou informações demais (ou de menos). Para se cadastrar, envie apenas ;cadastro + tipo de cadastro.'

    if msg[1].lower() in ['anime','manga','mangá','animanga','animangá']:
        if msg[1].lower() in ['mangá','animangá']:
            msg[1] = msg[1].replace('á','a')
        new_member = {'id': info['id'], 'nome': info['display_name'], 'ativo': 'Não', 'pontos': 0, 'tipo': msg[1], 'obs': ''}

        with open('roulette_members.json','r') as file:
                    
            roulettetools.roulette_members = json.load(file)

            if any(d['id'] == id for d in roulettetools.roulette_members):
                for dict in roulettetools.roulette_members:
                    if dict['id'] == id:
                        dict['tipo'] = msg[1].lower()
                        return 'Cadastro atualizado!'

                with open('roulette_members.json','w') as file:
                    json.dump(roulettetools.roulette_members, file, indent=2)
                                
            else:
                roulettetools.roulette_members.append(new_member)

                with open('roulette_members.json', 'w') as file:
                    print(new_member)
                    json.dump(roulettetools.roulette_members, file, indent=2)

                return 'Cadastro realizado!'
