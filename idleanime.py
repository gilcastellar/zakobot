import random
import time
import asyncio
import discord
from discord.ext import tasks

options = ['335','481','383','634','513']

# o bot precisa tomar decis�es a cada X tempo
# op��es de decis�es de macro level:
# come�ar anime novo, assistir epis�dio de um anime do watching,
# dropar anime, pausar anime, despausar anime, desdropar anime,
# postar uma atividade, adicionar algo nos favoritos

# tomada de decis�o:
# delay: 30 minutos, a menos que esteja assistindo algo
# neste caso empurra a decis�o para 5 minutos ap�s finalizar

@tasks.loop(seconds = 1) # repeat after every 10 seconds
async def start_anime():
    print('boa')
