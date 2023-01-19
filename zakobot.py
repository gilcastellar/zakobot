# encoding: utf-8

from turtle import color
import discord
import random
import roulettetools
import json
import configparser

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author.id == client.user:
        return
    
    if message.content.startswith(';cadastro'):

        id = message.author.id
        name = message.author.name
        avatar = message.author.avatar

        if message.content == ';cadastro':

            embed = discord.Embed(title='Instruções:')
            embed.add_field(name='Para se cadastrar, utilize novamente o comando ;cadastro seguido do tipo de obra que aceita',value='',inline=False)
            embed.add_field(name='',value='Exemplos:',inline=False)
            embed.add_field(name='',value=';cadastro anime \n ;cadastro manga \n ;cadastro animanga',inline=False)
            embed.add_field(name='',value='\n \n \n \n',inline=False)
            embed.add_field(name='Para adicionar observações, como limite de cours ou volumes utilize o comando ;obs seguido de todas as observações em uma só mensagem',value='',inline=False)
            embed.add_field(name='',value='Exemplos:',inline=False)
            embed.add_field(name='',value=';obs Aceito animes de até 26 episódios e mangás de até 10 volumes. Sem ecchi!',inline=False)            
            embed.add_field(name='',value='\n\n\n\n',inline=False)
            embed.add_field(name='Finalmente, para checar o resultado, utilize o comando ;perfil',value='',inline=False)
            await message.channel.send(embed=embed)
        else:
            while True:
                try:
                    command, content = message.content.split(" ")

                except:
                    await message.channel.send('Algo de errado não está certo. Tente novamente!')
                    break
                
                if content.lower() in ['anime','manga','animanga']:

                    new_member = {'id': id, 'nome': name, 'tipo': content, 'obs': ''}

                    print(new_member)

                    with open('roulette_members.json','r') as file:
                    
                        roulettetools.roulette_members = json.load(file)

                        if any(d['id'] == id for d in roulettetools.roulette_members):
                            for dict in roulettetools.roulette_members:
                                if dict['id'] == id:
                                    if dict['tipo'] == content.lower():
                                        await message.channel.send('Usuário já existente!')
                                    else:
                                        dict['tipo'] = content.lower()
                            with open('roulette_members.json','w') as file:
                                json.dump(roulettetools.roulette_members, file, indent=2)
                                
                        else:
                            roulettetools.roulette_members.append(new_member)

                            with open('roulette_members.json', 'w') as file:
                                print(new_member)
                                json.dump(roulettetools.roulette_members, file, indent=2)

                            await message.channel.send('Cadastro realizado!')
                break

           
    if message.content.startswith(';obs'):
        id = message.author.id

        while True:
            try:
                command, content = message.content.split(" ",1)

            except:
                await message.channel.send('Algo de errado não está certo. Tente novamente!')
                break
            
            with open('roulette_members.json','r') as file:
                    
                roulettetools.roulette_members = json.load(file)

                for d in roulettetools.roulette_members:
                    if d['id'] == id:
                        d['obs'] = content
                        await message.channel.send('Observações atualizadas!')
                    print(d)

                with open('roulette_members.json', 'w') as file:
                    json.dump(roulettetools.roulette_members, file, indent=2)
            break

    if message.content.startswith(';perfil'):

        if message.content == ';perfil':
            id = message.author.id
            name = message.author.name
            avatar = message.author.avatar
        else:
            command, content = message.content.split(" ")
            id = content.strip('<>@')
            user = await client.fetch_user(id)
            print(user)
            print(user.id)
            id = user.id
            name = user.name
            avatar = user.avatar

        embed = discord.Embed(title=name)
        embed.set_thumbnail(url=avatar)
        with open('roulette_members.json','r') as file:
                    
            roulettetools.roulette_members = json.load(file)

            for d in roulettetools.roulette_members:
                print(id)
                if d['id'] == id:
                    print('ok')
                    tipo = d['tipo']
                    if tipo.lower() == 'animanga':
                        tipo = 'Anime & Mangá'
                    elif tipo.lower() == 'manga':
                        tipo = 'Mangá'
                    else:
                        tipo = 'Anime'

                    obs = d['obs']
                    embed.add_field(name='Aceito:',value=tipo,inline=False)
                    #embed.add_field(name='',value=tipo + '\n',inline=False)
                    embed.add_field(name='Obs:',value=obs,inline=False)

        await message.channel.send(embed=embed)

    if message.content.startswith(';radd'):
        command, content = message.content.split(" ")

        if 'roulette' not in globals():
            global roulette 
            roulette = roulettetools.create_roulette()
            await message.channel.send('Roulette created!')

        roulette = roulettetools.add_roulette_member(roulette,content)
        await message.channel.send('New roulette member added!')

    if message.content.startswith(';rremove'):
        command, content = message.content.split(" ")

        roulette = roulettetools.remove_roulette_member(roulette,content)
        await message.channel.send('Roulette member removed!')

    if message.content.startswith(';rmembers'):
        members = ''
        for member in roulette:
            members += member + "\n"
        await message.channel.send(members)

    if message.content.startswith(';test'):
        #command, content = message.content.split(" ")

        #print(content.strip('<>@'))
        await message.channel.send('I found you, <@249670889438838794>')

    if message.content.startswith(';shuffler'):

        global previous_roulette
        previous_roulette = open('original_roulette.txt')
        #print('original: ' + previous_roulette.read().replace(',',' ').title())

        shuffled, previous_roulette = roulettetools.shuffle_roulette(roulette, previous_roulette)

        print(previous_roulette)
        with open('previous_roulette.txt', 'w') as file:
            file.write(previous_roulette)
            
        final_roulette = roulettetools.format(shuffled)

        embed = discord.Embed(title='Roleta formada!', description=final_roulette)
        await message.channel.send(embed=embed)


config = configparser.RawConfigParser()
config.read('app.properties')
token = config.get('Discord', 'token')

client.run(token)