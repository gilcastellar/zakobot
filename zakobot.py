# encoding: utf-8

from csv import reader
from platform import python_revision
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
    
    if message.content.lower().startswith(';ajuda'):

        embed = discord.Embed(title='Instruções:')
        embed.add_field(name='Para se cadastrar ou alterar seu cadastro, utilize novamente o comando ;cadastro seguido do tipo de obra que aceita',value='',inline=False)
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
        await message.channel.send(embed=embed)

    if message.content.lower().startswith(';cadastro'):

        id = message.author.id
        name = message.author.name
        avatar = message.author.avatar

        while True:
            try:
                command, content = message.content.split(" ")

            except:
                await message.channel.send('Algo de errado não está certo. Tente novamente!')
                break
                
            if content.lower() in ['anime','manga','animanga']:

                new_member = {'id': id, 'nome': name, 'ativo': 'Sim', 'pontos': '', 'tipo': content, 'obs': ''}

                with open('roulette_members.json','r') as file:
                    
                    roulettetools.roulette_members = json.load(file)

                    if any(d['id'] == id for d in roulettetools.roulette_members):
                        for dict in roulettetools.roulette_members:
                            if dict['id'] == id:
                                if dict['tipo'] == content.lower():
                                    await message.channel.send('Cadastro atualizado!')
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

           
    if message.content.lower().startswith(';obs'):
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

                with open('roulette_members.json', 'w') as file:
                    json.dump(roulettetools.roulette_members, file, indent=2)
            break

    if message.content.lower().startswith(';ativar'):
        id = message.author.id
        with open('roulette_members.json','r') as file:
                    
            roulettetools.roulette_members = json.load(file)

            for d in roulettetools.roulette_members:
                if d['id'] == id:
                    d['ativo'] = 'Sim'
                    await message.channel.send('Cadastro atualizado!')

            with open('roulette_members.json', 'w') as file:
                json.dump(roulettetools.roulette_members, file, indent=2)

    if message.content.lower().startswith(';desativar'):
        id = message.author.id
        with open('roulette_members.json','r') as file:
                    
            roulettetools.roulette_members = json.load(file)

            for d in roulettetools.roulette_members:
                if d['id'] == id:
                    d['ativo'] = 'Não'
                    await message.channel.send('Cadastro atualizado!')

            with open('roulette_members.json', 'w') as file:
                json.dump(roulettetools.roulette_members, file, indent=2)

    if message.content.lower().startswith(';perfil'):

        if message.content.lower() == ';perfil':
            id = message.author.id
            name = message.author.name
            avatar = message.author.avatar
        else:
            command, content = message.content.split(" ")
            id = content.strip('<>@')
            user = await client.fetch_user(id)
            id = user.id
            name = user.name
            avatar = user.avatar

        embed = discord.Embed(title=name)
        embed.set_thumbnail(url=avatar)
        with open('roulette_members.json','r') as file:
                    
            roulettetools.roulette_members = json.load(file)

            for d in roulettetools.roulette_members:
                if d['id'] == id:
                    tipo = d['tipo']
                    ativo = d['ativo']
                    if tipo.lower() == 'animanga':
                        tipo = 'Anime & Mangá'
                    elif tipo.lower() == 'manga':
                        tipo = 'Mangá'
                    else:
                        tipo = 'Anime'

                    obs = d['obs']
                    embed.add_field(name='Ativo:',value=ativo,inline=False)
                    embed.add_field(name='Aceito:',value=tipo,inline=False)
                    embed.add_field(name='Observações:',value=obs,inline=False)

        await message.channel.send(embed=embed)

    if message.content.startswith(';membros'):
        embed = discord.Embed(title='Membros ativos na roleta:')

        with open('roulette_members.json','r') as file:
                    
            roulettetools.roulette_members = json.load(file)
            for member in roulettetools.roulette_members:
                if member['ativo'].lower() == 'sim':
                    embed.add_field(name='',value=member['nome'],inline=False)
            await message.channel.send(embed=embed)

    if message.content.startswith(';shuffle'):

        #global previous_roulette
        with open('previous_roulette.txt') as file:
            previous_roulette = file.read().split(',')
        #print('original: ' + previous_roulette.read().replace(',',' ').title())

        formatted, shuffled = roulettetools.shuffle_roulette(previous_roulette)

        with open('roulette.txt', 'w') as file:
            list = ''
            i = 0
            for member in shuffled:
                if i != len(shuffled) - 1:
                    list += str(member) + ','
                else:
                    list += str(member) + ',' + str(shuffled[0])
                i += 1
            file.write(list)

        embed = discord.Embed(title='Roleta formada!', description=formatted)
        await message.channel.send(embed=embed)


config = configparser.RawConfigParser()
config.read('app.properties')
token = config.get('Discord', 'token')

client.run(token)