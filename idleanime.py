import random
import time
import asyncio
import discord
from discord.ext import tasks

import anilist

options = ['335','481','383','634','513']


episode = 0

# o bot precisa tomar decisões a cada X tempo
# opções de decisões de macro level:
# começar anime novo, assistir episódio de um anime do watching,
# dropar anime, pausar anime, despausar anime, desdropar anime,
# postar uma atividade, adicionar algo nos favoritos

# tomada de decisão:
# delay: 30 minutos, a menos que esteja assistindo algo
# neste caso empurra a decisão para 5 minutos após finalizar

@tasks.loop(seconds = 20, count = len(options)) # repeat after every 10 seconds
async def start_anime(token):
    anime_id = random.choice(options)
    response = anilist.query_anilist(anime_id)

    o = response.json()

    title = o['data']['Media']['title']['romaji']
    options.remove(anime_id)
    #print(title)

    #anilist.new_anime(anime_id, token)

@tasks.loop(minutes = 24)
async def watch(anime_id, max_episodes, token):
    global episode
    episode += 1
    anilist.update_episode(anime_id, episode, token)
    print(f'Assisti o episódio {episode}')