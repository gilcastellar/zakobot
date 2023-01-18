# encoding: utf-8

from turtle import color
import discord
import random
import roulettetools
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
        embed = discord.Embed(title='Instruções:')
        embed.add_field(name='',value='Para se cadastrar, utilize o comando ;novo seguido de seu @.',inline=False)
        embed.add_field(name='Exemplo:',value=';novo @kaiser',inline=False)
        embed.add_field(name='',value='Lembre-se: é preciso efetivamente se marcar para que possamos pegar seu ID!')
        await message.channel.send(embed=embed)

    if message.content.startswith(';novo'):
        command, content = message.content.split(" ")

        print(content.strip('<>@')) 

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