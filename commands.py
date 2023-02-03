import discord
import roulettetools
import json


def ajuda():

    embed = discord.Embed(title='Instruções:')
    embed.add_field(name='Se você quer se cadastrar ou alterar o tipo de obra que aceita receber, utilize o comando ;cadastro seguido do tipo',value='',inline=False)
    embed.add_field(name='',value='Exemplos:',inline=False)
    embed.add_field(name='',value=';cadastro anime \n ou \n;cadastro manga \n ou \n;cadastro animanga',inline=False)
    embed.add_field(name="", value="", inline=False)
    embed.add_field(name="--", value="", inline=False)
    embed.add_field(name="", value="", inline=False)
    embed.add_field(name='Para participar da próxima roleta, use ;ativar. Para se ausentar, use ;desativar',value='',inline=False)
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
        new_member = {'id': info['id'], 'nome': info['display_name'], 'ativo': 'Não', 'pontos': 0, 'tipo': msg[1].lower(), 'obs': ''}

        with open('roulette_members.json','r') as file:
            roulettetools.roulette_members = json.load(file)

            if any(d['id'] == info['id'] for d in roulettetools.roulette_members):
                for dict in roulettetools.roulette_members:
                    if dict['id'] == info['id']:
                        dict['tipo'] = msg[1].lower()
                        with open('roulette_members.json','w') as file:
                            json.dump(roulettetools.roulette_members, file, indent=2)
                        return 'Cadastro atualizado!'
            else:
                roulettetools.roulette_members.append(new_member)
                with open('roulette_members.json', 'w') as file:
                    print(new_member)
                    json.dump(roulettetools.roulette_members, file, indent=2)
                return 'Cadastro realizado!'

def gerar_placar(users, info, admins):
    if info['id'] not in admins:
        return [], ''

    embed = discord.Embed(title='Roleta:')
    pairs = []

    recs = ['Jungle wa Itsumo Hare nochi Guu','Haiyore! Nyaruko-san','Fire Punch','Sanctuary','Cross Over','Megumi no Daigo','Yugami-kun ni wa Tomodachi ga Inai','Kokoro ni Haha wo!; Uramichi Oniisan','Paradise Kiss','BECK: Mongolian Chop Squad','Gungrave','Tsuki no Laika to Nosferatu','ef: a tale of memories','Futoku no Guild','Chainsaw Man','Harmony; Aura','Noragami','Haibane Renmei','Kemonozume','Fune o Amu']

    index = 0
    linha = 1

    for user in users:
        if index < len(users) - 1:
            pairs.append(str(linha) + '. ' + users[index].display_name + ' -> ' + users[index+1].display_name + '   :   ' + recs[index] + ' ')
            embed.add_field(name='', value=pairs[index], inline=False)
            index += 1
            linha += 1

    with open('placar.txt','w') as file:
        for i in pairs:
            file.write(i + ',')
            
    return pairs, embed

def editar_placar(msg, pares, info, admins):
    if info['id'] not in admins:
        return [], ''
    if len(msg) != 3:
        return 
    par = msg[1]
    nota = msg[2]

    pairs = []
     
    embed = discord.Embed(title='Roleta:')

    linha = 1
    
    with open(pares, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if linha == int(par):
                if '✅' in line:
                    text, trash = line.split('✅')
                else:
                    text = line
                extra = '✅ ' + nota + '/10'
            else:
                text = line
                extra = ''
            embed.add_field(name='', value=text + extra, inline=False)
            newline = text + extra
            pairs.append(newline)
            linha += 1

    with open(pares, 'w') as newfile:
        index = 0
        for i in pairs:
            if index < len(pairs):
                newfile.write(newline + ',')
                index += 1

    return pares, embed

def terminei(msg, info, pares):
    nota = msg[1]

    if '/10' in nota:
        nota = nota.replace('/10','')
    
    user = '-> ' + info['display_name']
    
    pairs = []

    embed = discord.Embed(title='Roleta:')

    linha = 1
    
    with open(pares, 'r') as file:
        lines = file.read().split(',')
        for line in lines:
            print(line)
            if user in line:
                print('user in line')
                if '✅' in line:
                    print('✅ in line')
                    text, trash = line.split('✅')
                    print(text)
                else:
                    text = line
                extra = '✅ ' + nota + '/10'
            else:
                text = line
                extra = ''
            embed.add_field(name='', value=text + extra, inline=False)
            newline = text + extra
            print('newline = ' + text + extra)
            pairs.append(newline)
            linha += 1
    
    with open(pares, 'w') as newfile:
        for i in pairs:
            newfile.write(i + ',')

    return pares, embed