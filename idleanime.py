import random
import time
import asyncio
import discord
from discord.ext import tasks

import anilist

options = ['335','481','383','634','513']

action_options = ['START','WATCH','DROP','UNDROP','PAUSE','UNPAUSE','PLAN','STARTPLAN','BINGE','WRITE','FAV']

status_options = ['DROPPED', 'PAUSED', 'WATCHING']

# o bot precisa tomar decisões a cada X tempo
# opções de decisões de macro level:
# começar anime novo, assistir episódio de um anime do watching,
# dropar anime, pausar anime, despausar anime, desdropar anime,
# postar uma atividade, adicionar algo nos favoritos

# tomada de decisão:
# delay: 30 minutos, a menos que esteja assistindo algo
# neste caso empurra a decisão para 5 minutos após finalizar

@tasks.loop(minutes = 1)
async def think():
    print('pensando')
    action = random.choice(action_options)

    match action:
        case 'START':
            zakobot.send_message('Comecei um novo anime')
        case 'WATCH':
            zakobot.send_message('Vi um episódio')
        case 'DROP':
            zakobot.send_message('Dropei um anime')
        case 'UNDROP':
            zakobot.send_message('Desdropei um anime')
        case 'PAUSE':
            zakobot.send_message('Pausei um anime')
        case 'UNPAUSE':
            zakobot.send_message('Despausei um anime')
        case 'PLAN':
            zakobot.send_message('Coloquei um anime no planning')
        case 'STARTPLAN':
            zakobot.send_message('Comecei um anime do planning')
        case 'BINGE':
            zakobot.send_message('Vou maratonar um anime')
        case 'WRITE':
            zakobot.send_message('Postei uma atividade no anilist')
        case 'FAV':
            zakobot.send_message('Favoritei algo no anilist')
            
def start_anime(token):
    anime_id = random.choice(options)
    response = anilist.query_anilist(anime_id)

    o = response.json()

    title = o['data']['Media']['title']['romaji']
    options.remove(anime_id)
    print(title)

    anilist.new_anime(anime_id, token)

def watch(anime_id, user_name, token):
    max_episodes = anilist.check_max_episodes(anime_id)
    episode = anilist.check_episode(anime_id, user_name)
    if episode != max_episodes:
        episode += 1
        anilist.update_episode(anime_id, episode, token)
        print(f'Assisti o episódio {episode}')
    else:
        watch.stop()

def update_status(anime_id, user_name, status, token):
    anilist.update_anime_status(anime_id, user_name, status, token)

#def drop(anime_id, user_name, token):
#    anilist.drop_anime(anime_id, user_name, token)

#def pause(anime_id, user_name, token):
#    anilist.pause_anime(anime_id, user_name, token)
