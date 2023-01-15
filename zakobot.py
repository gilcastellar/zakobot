import discord
import random
import asyncio
import roulettetools

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def on_message(self, message):
        # we do not want the bot to reply to itself
        if message.author.id == self.user.id:
            return

        if message.content.startswith(';;salve'):
            await message.channel.send('SALVE O CORINTHIANS!!')

        if message.content.startswith(';;hi'):
            await message.channel.send('Hi ' + str(message.author))


        if message.content.startswith(';;anilist'):
            command, content = message.content.split(" ")
            await message.channel.send(content)

        if message.content.startswith(';;shini'):
            adjetivos = ['gay','viadao','homossexual','boiola','bicha','senta-fofo','morde-fronhas','maricas','pederasta','baitola']
            await message.channel.send('O Shini eh muito ' + random.choice(adjetivos))

        if message.content.startswith(';;radd'):
            command, content = message.content.split(" ")

            if 'roulette' not in globals():
                global roulette 
                roulette = roulettetools.create_roulette()
                await message.channel.send('Roulette created!')

            roulette = roulettetools.add_roulette_member(roulette,content)
            await message.channel.send('New roulette member added!')
            #roulette.add_roulette_member(content)

        if message.content.startswith(';;rmembers'):
            #global members
            members = ''
            for member in roulette:
                members += member + "\n"
            await message.channel.send(members)

        if message.content.startswith(';;shuffler'):
            await message.channel.send(roulette)

            shuffled = roulettetools.shuffle_roulette(roulette)

            await message.channel.send(shuffled)

            final_roulette = roulettetools.format(shuffled)

            await message.channel.send('**Roulette shuffled!** \n' + final_roulette)

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)

#@client.command()
#async def embed(ctx):
#    embed = discord.Embed(title='Example Dmbed', description='this is an embed')
#    await ctx.send(embed=embed)


client.run('MTA2MzM1MTg3MjAwMzUxODQ5NQ.Ga729N.ZK5x4_eIsS3pQNT6iZ_I3VIPdRhCEdSu5-wGUE')
