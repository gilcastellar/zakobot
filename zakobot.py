import discord
import random
import asyncio



class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def on_message(self, message):
        # we do not want the bot to reply to itself
        if message.author.id == self.user.id:
            return

        if message.content.startswith(';;hi'):
            await message.channel.send('Hi!' + message.content)

        if message.content.startswith(';;anilist'):
            command, content = message.content.split(" ")
            await message.channel.send(content)

        if message.content.startswith(';;newr'):
            global roulette
            roulette = []
            await message.channel.send('Roulette created!')
            #roulette.create_roulette()

        if message.content.startswith(';;radd'):
            command, content = message.content.split(" ")
            roulette.append(content)
            await message.channel.send('New roulette member added!')
            #roulette.add_roulette_member(content)

        if message.content.startswith(';;rmembers'):
            for member in roulette:
                await message.channel.send(member)

        if message.content.startswith(';;guess'):
            await message.channel.send('Guess a number between 1 and 10.')

            def is_correct(m):
                return m.author == message.author and m.content.isdigit()

            answer = random.randint(1, 10)

            try:
                guess = await self.wait_for('message', check=is_correct, timeout=5.0)
            except asyncio.TimeoutError:
                return await message.channel.send(f'Sorry, you took too long it was {answer}.')

            if int(guess.content) == answer:
                await message.channel.send('You are right!')
            else:
                await message.channel.send(f'Oops. It is actually {answer}.')

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)

client.run('MTA2MzM1MTg3MjAwMzUxODQ5NQ.Ga729N.ZK5x4_eIsS3pQNT6iZ_I3VIPdRhCEdSu5-wGUE')
