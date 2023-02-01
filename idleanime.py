import random
import time
import asyncio
import discord
from discord.ext import tasks

options = ['335','481','383','634','513']

# o bot precisa tomar decisões a cada X tempo
# opções de decisões de macro level:
# começar anime novo, assistir episódio de um anime do watching,
# dropar anime, pausar anime, despausar anime, desdropar anime,
# postar uma atividade, adicionar algo nos favoritos

# tomada de decisão:
# delay: 30 minutos, a menos que esteja assistindo algo
# neste caso empurra a decisão para 5 minutos após finalizar

@tasks.loop(seconds = 1) # repeat after every 10 seconds
async def start_anime():
    print('boa')
