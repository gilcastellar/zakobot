import discord

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have loggeg in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith(';;hi'):
        await message.channel.send('Hi!')

client.run('MTA2MzM1MTg3MjAwMzUxODQ5NQ.Ga729N.ZK5x4_eIsS3pQNT6iZ_I3VIPdRhCEdSu5-wGUE')
