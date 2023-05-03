# token = MTA5OTU5NTIwMDQyODUyMzUzMA.GAqCqA.T2W3Bn9lPCwcTfEHx8IO1s6BK2HBAN4nM9RYeI

from imaplib import Commands
from importlib.metadata import requires
from posixpath import split
from random import choices, shuffle

import discord
import configparser
import database
import anilist
import json
import time
intents = discord.Intents.default()
intents.members = True
bot = discord.Bot(intents=intents)
admins = [906937520254758973,628466603486478336,1050904689685831760,98410347597139968]
test = 'eita'
key = False

# Edit profile modal
class EditarPerfilModal(discord.ui.Modal):
    def __init__(self, user_id, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
        _lista = database.select('SELECT anime_list FROM user WHERE id=' + str(user_id))
        print(_lista)
        _obs = database.select('SELECT obs FROM user WHERE id=' + str(user_id))
        print(_obs)

        self.add_item(discord.ui.InputText(label="Link do perfil do MAL/Anilist (opcional)", required=False, value=_lista))
        self.add_item(discord.ui.InputText(label="Suas observações", style=discord.InputTextStyle.long, required=False, value=_obs))

    async def callback(self, interaction: discord.Interaction):
        #await interaction.response.send_message('Editando...')
        embed = discord.Embed(title="Perfil")
        embed.add_field(name="MAL/Anilist", value=self.children[0].value, inline=False)
        embed.add_field(name="Suas observações", value=self.children[1].value, inline=False)

        user_id = str(interaction.user.id)
        _lista = self.children[0].value
        print(_lista)
        _obs = self.children[1].value
        print(_obs)

        sql = 'UPDATE user SET anime_list= "' + _lista + '", obs= "' + _obs + '" WHERE id=' + user_id
        print(sql)
        database.update(sql)

        global key
        key = True
        await interaction.response.send_message('Edições realizadas! Utilize o comando /perfil para visualizar.')

# Send message
async def send_message(ctx, text, channel_id=''):

    if channel_id != '':
        channel = bot.get_channel(channel_id)
        message = await channel.send(text)
    else:
        message = await ctx.send(text)

    return message

# Send embed
async def send_embed(ctx,embed):

    await ctx.send(embed=embed)

# Fetch user object
async def fetch_user(id):
    user = await bot.fetch_user(id)

    return user

@bot.command(name='registro')
async def registro_command(ctx):

    user_id = ctx.author.id
    exists = database.check_if_exists(str(user_id), 'id', 'user')

    if exists == 0:

        guild = 1059298932825538661
        name = ctx.author.name
        database.insert('INSERT INTO user (id, id_guild, name) VALUES (%s,%s,%s)',(user_id, guild, name))

        await ctx.respond(f"Seja bem-vindo(a) à roleta, {name}!")

    else:

        await ctx.respond('Você já está cadastrado!')

@bot.slash_command(name='editar_perfil')
async def editar_perfil_command(ctx: discord.ApplicationContext):
    """Shows an example of a modal dialog being invoked from a slash command."""
    user_id = ctx.author.id
    modal = EditarPerfilModal(user_id, title="Editar perfil da roleta")
    await ctx.send_modal(modal)

# SLASH PRA SE CADASTRAR NA ROLETA
@bot.slash_command(name='configurar')
async def configurar_command(
  ctx: discord.ApplicationContext,
  ativo: discord.Option(str, choices=['Ativo','Inativo'], name='status', description='Sua situação na roleta'),
  tipo_que_recebe: discord.Option(str, choices=['Anime', 'Mangá', 'Anime e Mangá'], name='recebo', description='Tipo de obra que quer receber recomendações'),
  tipo_que_envia: discord.Option(str, choices=['Anime', 'Mangá', 'Anime e Mangá'], name='envio', description='Tipo de obra que quer recomendar')
):
  user_id = str(ctx.author.id)

  if ativo.lower() == 'ativo':

      is_ativo = 1

  else:

      print(ativo.lower())
      is_ativo = 0
  
  is_ativo = str(is_ativo) 
  
  sql = 'UPDATE user SET active= "' + is_ativo + '", receives= "' + tipo_que_recebe.lower() + '", gives= "' + tipo_que_envia.lower() +  '" WHERE id=' + user_id
  database.update(sql)

  if ativo.lower() == 'inativo':

      await ctx.respond(f'Você está inativo. Bom descanso!')

  else:

      await ctx.respond(f'Você está ativo e quer receber `{tipo_que_recebe.lower()}` e enviar `{tipo_que_envia.lower()}` na roleta!')

# Get active members
async def get_members_names(ctx: discord.AutocompleteContext):

    members = database.selectall('SELECT id, name, active, anime_list, receives, gives, obs FROM user WHERE active=1')
    members_names = []

    for member in members:
        members_names.append(member[1])

    sorted_members_names = sorted(members_names, key=str.lower)

    return sorted_members_names

# Get member info
def get_member_info(name):
    
    member = database.selectall('SELECT id, name, active, anime_list, receives, gives, obs, zakoleta FROM user WHERE name="' + name + '"')

    id = member[0][0]
    active = member[0][2]
    anime_list = member[0][3]
    receives = member[0][4]
    gives = member[0][5]
    obs = member[0][6]
    zakoleta = member[0][7]

    return id, active, anime_list, receives, gives, obs, zakoleta

@bot.slash_command(name='perfil')
async def perfil_command(
    ctx: discord.ApplicationContext,
    member: discord.Option(str, autocomplete=get_members_names, name='membro')
):

    id, active, anime_list, receives, gives, obs, zakoletas = get_member_info(member)

    user = await bot.fetch_user(id)
    avatar = user.avatar

    if active == 1:

        _ativo = 'Ativo'

    else:

        _ativo = 'Inativo'

    if zakoletas == None:
        zakoletas = 0

    user_avg = await get_user_avg(user)

    embed=discord.Embed(title=member, url=anime_list, color=0xe84545)
    embed.set_thumbnail(url=avatar)
    embed.add_field(name=_ativo,value='',inline=True)
    embed.add_field(name="Ƶ " + str(zakoletas), value="", inline=True)
    embed.add_field(name="", value="", inline=False)
    embed.add_field(name="Perfil MAL/Anilist", value=anime_list, inline=False)
    embed.add_field(name="", value="", inline=False)
    embed.add_field(name="Roleta:", value="", inline=False)
    embed.add_field(name="Quero receber:", value=receives, inline=True)
    embed.add_field(name="Posso enviar:", value=gives, inline=True)
    embed.add_field(name="Nota média:", value=str(user_avg) +'/10', inline=False)
    embed.add_field(name='Observações:',value=obs,inline=False)
    

    await ctx.respond(embed=embed)

@bot.slash_command(name='sorteio')
async def sorteio_command(
    ctx: discord.ApplicationContext,
    name: discord.Option(str, name='nome'),
    delay: discord.Option(int, name='delay'),
    reward: discord.Option(str, name='recompensa', options=['True','False'])
):
    
    if ctx.author.id in admins:
        sql = 'SELECT id, gives, receives FROM user WHERE active=1'
        draw_list = database.selectall(sql)

        print(draw_list)

        draw_list = merge_id_with_type(draw_list)

        id = get_last_roulette_id()

        last_two_draws = get_last_draws(id)

        result = roulette_shuffle(draw_list, id, last_two_draws)
        print(type(result))

        result_as_str = draw_to_str(result)
        print(result_as_str)
        print(type(result_as_str))

        pairs = generate_pairs(result)

        sql = 'INSERT INTO roleta (id, name, draw, status) VALUES (%s,%s,%s,%s)'
        val = (id+1, name, result_as_str, 'ongoing')
        database.insert(sql, val)
        
        index = 1

        for pair in pairs:

            time.sleep(delay)

            giver, receiver = pair.split(',')

            if reward == 'True':
                
                add_zakoleta(ctx.author.id, 50)

            giver = await fetch_user(giver)
            receiver = await fetch_user(receiver)

            text = giver.display_name + ' -> ' + receiver.display_name
            
            message = await send_message(ctx,text) # REALIZA O SORTEIO AO VIVO NO CHAT E RETORNA O OBJETO DA MENSAGEM
            
            sql = 'INSERT INTO user_has_roleta (idx, id_receiver, id_giver, id_roleta, status) VALUES (%s,%s,%s,%s,%s)'
            val = (index, str(receiver.id), str(giver.id), id+1, 'ongoing')
            database.insert(sql, val)

            

            index += 1

        board_message = await create_board_message(ctx, 1077070205987082281)

        print(board_message)
        
        board_message_id = board_message.id
        print('board_message_id:')
        print(board_message_id)

        board_message_channel_id = board_message.channel.id
        print('board_message_channel_id:')
        print(board_message_channel_id)

        sql = 'UPDATE roleta SET id_message="' + str(board_message_id) + '", id_channel="' + str(board_message_channel_id) + '" WHERE id="' + str(id+1) + '"'
        database.update(sql)



        await board_update(id+1)

# Merges ID with type values for the validation of a pair in the Sorteio function
def merge_id_with_type(list):

    new_list = []

    for item in list:

        id = item[0]
        gives = parse_type(item[1])
        receives = parse_type(item[2])

        new_list.append(id + '_' + str(gives) + '_' + str(receives))

    print(new_list)

    return new_list

# Parses type values
def parse_type(type):

    match type:

        case 'anime':
            return 1

        case 'mangá':
            return 2

        case 'anime e mangá':
            return 3
    
# Turns a draw list into a str
def draw_to_str(list):

    new_list = ''
    last = len(list)-1

    print(last)

    index = 0

    for id in list:

        if id != list[last]: # CONTROL SO THE LAST ID CAN BE CORRECTLY HANDED

            new_list += id + ','
            continue

        else:

            new_list += id + ',' + list[0]

        index += 1

    return new_list

# Get last roulette ID
def get_last_roulette_id():

    sql = 'SELECT id FROM roleta'
    result = database.selectall(sql, True)

    print(result)

    last_roulette_id = max(result)

    print(last_roulette_id)

    return last_roulette_id

# Roulette shuffle
def roulette_shuffle(list, roulette_id, last_two_draws):

    while True:

        shuffle(list)

        is_valid = roulette_validator(list, last_two_draws)

        if is_valid:

            print('sorteio válido')
            print(list)
            break

        else:
            ...
            #print('recomeçando sorteio')

    ids_only_list = []

    for item in list:
        id, gives, receives = item.split('_')
        ids_only_list.append(id)

    return ids_only_list

# Get last 2 draws
def get_last_draws(id):

    last = str(int(id))
    second_last = str(int(id) - 1)

    print('sorteio será comparado com os draws das roletas de índice ' + second_last + ' e ' + last)

    sql = 'SELECT draw FROM roleta WHERE id=' + last
    last_draw = database.select(sql)

    sql = 'SELECT draw FROM roleta WHERE id=' + second_last
    second_last_draw = database.select(sql)

    last_two_draws = (last_draw, second_last_draw)

    return last_two_draws

# Generate list of pairs
def generate_pairs(list):

    head_of_list = list[0]
    pairs = []
    new_pair = ''

    index = 0

    for id in list:

        if id == head_of_list: # CONTROL SO THE FIRST ID CAN BE CORRECTLY HANDED

            previous_id = id
            continue

        else:

            new_pair = previous_id + ',' + id

        previous_id = id
        pairs.append(new_pair)

        index += 1

    new_pair = list[index] + ',' + head_of_list # CREATES THE LAST PAIR
    pairs.append(new_pair)

    return pairs

# Roulette validator
def roulette_validator(list, last_two_draws):

    ids_only_list = []

    for item in list:
        id, gives, receives = item.split('_')
        ids_only_list.append(id)

    pairs = generate_pairs(ids_only_list)

    #print('lista de pares:')
    #print(pairs)

    #print('checando compatibilidade...')

    for pair in pairs:

        # VALIDATING IF PAIR DIDN'T HAPPEN IN THE LAST 2 ROULETTES

        if pair in last_two_draws[0]:
            
            return False

        if pair in last_two_draws[1]:
            
            return False

        # VALIDATING IF PAIR TYPES ARE COMPATIBLE

    pairs_with_types = generate_pairs(list)

    for pair in pairs_with_types:

        giver, receiver = pair.split(',',1)

        giver = giver.split('_')
        print('giver:')
        print(giver)
        receiver = receiver.split('_')
        print('receiver:')
        print(receiver)

        if '3' not in (giver[1], receiver[2]):
            if giver[1] != receiver[2]:
                return False



        #giver_type = database.select('SELECT gives FROM user WHERE id="' + giver + '"')

        #receiver_type = database.select('SELECT receives FROM user WHERE id="' + receiver + '"')

        #if 'anime e mangá' not in (giver_type, receiver_type):

        #    if receiver_type == 'anime' and giver_type == 'mangá':
        #        return False

        #    if receiver_type == 'mangá' and giver_type == 'anime':
        #        return False
            
    return True

# Creates board message
async def create_board_message(ctx, channel_id):

    return await send_message(ctx, 'Carregando...', channel_id)

# Generate board
async def generate_board(info, message, id=0):

    name = database.select('SELECT name FROM roleta WHERE id=' + str(id))

    name = parse_name(name)

    board_text = name + '\n```'

    print('board_text:')
    print(board_text)

    for pairing in info:

        giver = await bot.fetch_user(pairing[1])
        receiver = await bot.fetch_user(pairing[2])

        print('pairing[3]')
        print(pairing[3])

        if pairing[3] != None and pairing[3] != '':

            medias = board_indications_manager(pairing[3])

        else:

            medias = ''

        status = pairing[5]

        match status:

            case 'ongoing':
                status_text = ''

            case 'finished':
                status_text = '✅ '

            case 'abandoned':
                status_text = '❌ ABANDONADO'

            case '':
                status_text = ''


        score = str(pairing[4]) + '/10'

        if score == '/10' or score == '0/10':

            score = ''

        board_text += str(pairing[0]) + '. ' + giver.display_name + ' -> ' + receiver.display_name + ' [' + medias + '] ' + status_text + score + '\n'
    
    board_text = board_text.replace('None/10','')
    board_text = board_text.replace('[]','')
    board_text += '```'

    await message.edit(board_text)

# Parse roulette name
def parse_name(name):

    nome_da_roleta = '**Roleta de '

    year, month = name.split('_')

    year = str(year)

    nome_da_roleta += month.title() + '/' + year + '**'

    return nome_da_roleta

# Board update
async def board_update(roleta_id, message=None):

    sql = 'SELECT id_message, id_channel FROM roleta WHERE id=' + str(roleta_id)
    message_info = database.selectall(sql)

    if message == None:

        print("message_info")
        print(message_info)
        print('message_info[0]')
        print(message_info[0])

        channel_id = int(message_info[0][1])

        channel = bot.get_channel(channel_id)

        message_id = int(message_info[0][0])

        print('message_id')
        print(message_id)

        message = await channel.fetch_message(message_id)

    sql = 'SELECT idx, id_giver, id_receiver, received_rec, score, status FROM user_has_roleta WHERE id_roleta="' + str(roleta_id) + '" ORDER BY idx'
    board_info = database.selectall(sql)

    print('starting to generate board')
    print('roleta_id:')
    print(roleta_id)

    await generate_board(board_info, message, roleta_id)
    
# Board indications manager
def board_indications_manager(medias):

    media_text = ''

    if medias != None:

        if ',' not in medias:

            print('pegando nome de ' + medias + '...')

            type, id = get_type_and_id_from_anilist_link(medias)

            sql = 'SELECT title FROM obra WHERE id=' + id
            media_text += database.select(sql)

        else:

            medias = medias.split(',')

            for media in medias:
                print('pegando nome de ' + media + '...')

                type, id = get_type_and_id_from_anilist_link(media)
                
                sql = 'SELECT title FROM obra WHERE id=' + id
                media_text += database.select(sql) + ' ; '

        media_text = media_text.strip("; ")

        return media_text
     
    else:

        return ''

# Get type and id from anilist link
def get_type_and_id_from_anilist_link(link):

    if 'https://' in link:

        link = link.replace('https://','')

    link_parts = link.split('/')

    print(link_parts[1])

    return link_parts[1], link_parts[2]

@bot.slash_command(name='indicar')
async def indicar_command(
    ctx: discord.ApplicationContext,
    media1: discord.Option(str, name='primeira_indicação', description='INSIRA O LINK DO ANILIST DA OBRA', required=True),
    media2: discord.Option(str, name='segunda_indicação', description='INSIRA O LINK DO ANILIST DA OBRA', required=False),
    media3: discord.Option(str, name='terceira_indicação', description='INSIRA O LINK DO ANILIST DA OBRA', required=False)
):
    roletas = database.selectall('SELECT id FROM roleta', True)
    roleta_atual = max(roletas)

    roleta_atual = 5

    sql = 'SELECT id_giver FROM user_has_roleta WHERE id_roleta="' + str(roleta_atual) + '"'
    allowed_givers = database.selectall(sql, True)

    medias = ''
    medias += media1

    if media2 != None:

        medias += ',' + media2

    if media3  != None:

        medias += ',' + media3

    if str(ctx.author.id) in allowed_givers:

        sql = 'UPDATE user_has_roleta SET received_rec="' + medias + '" WHERE id_giver="' + str(ctx.author.id) + '" AND id_roleta=' + str(roleta_atual)
        database.update(sql)
    
    await ctx.respond(f"Obrigado pela indicação!")

    list = []

    if ',' in medias:
        list = medias.split(',')
    else:
        list.append(medias)

    for media in list:
        print('adding media to table obra:')
        print(media)
        add_to_obra(media)
    
    await board_update(roleta_atual)

# Get roulettes
async def get_roletas(ctx: discord.AutocompleteContext):

    roletas = database.selectall('SELECT name FROM roleta ORDER BY id')
    roletas_names = []

    for roleta in roletas:

        roletas_names.append(roleta[0])

    return roletas_names

@bot.slash_command(name='terminei')
async def terminei_command(
    ctx: discord.ApplicationContext,
    roleta: discord.Option(str, name='roleta', description='Escolha a roleta', autocomplete=get_roletas, required=True),
    score: discord.Option(int, name='nota', description='Insira sua nota de 1 a 10', min_value=1, max_value=10, required=True)
):

    roleta_id = database.select('SELECT id FROM roleta WHERE name="' + roleta + '"')

    status = database.select('SELECT status FROM user_has_roleta WHERE id_receiver=' + str(ctx.author.id) + ' AND id_roleta=' + str(roleta_id))

    if status == 'ongoing':
        add_zakoleta(ctx.author.id, 50)

    sql = 'UPDATE user_has_roleta SET score=' + str(score) + ',status="finished"' + 'WHERE id_roleta=' + str(roleta_id) + ' AND id_receiver="' + str(ctx.author.id) + '"'
    database.update(sql)

    await ctx.respond(f"Obrigado pela dedicação! :muscle:")

    await board_update(roleta_id)

@bot.slash_command(name='abandonei')
async def abandonei_command(
    ctx: discord.ApplicationContext,
    roleta: discord.Option(str, name='roleta', description='Escolha a roleta', autocomplete=get_roletas, required=True)
):

    roleta_id = database.select('SELECT id FROM roleta WHERE name="' + roleta + '"')

    status = database.select('SELECT status FROM user_has_roleta WHERE id_receiver=' + str(ctx.author.id) + ' AND id_roleta=' + str(roleta_id))

    if status == 'ongoing':
        add_zakoleta(ctx.author.id, 25)

    sql = 'UPDATE user_has_roleta SET status="abandoned" WHERE id_roleta=' + str(roleta_id) + ' AND id_receiver="' + str(ctx.author.id) + '"'
    database.update(sql)

    await ctx.respond(f"Indicação abandonada. Obrigado por priorizar sua saúde mental! :health_worker:")

    await board_update(roleta_id)

@bot.slash_command(name='placar_roleta')
async def placar_roleta_command(
    ctx: discord.ApplicationContext,
    roleta: discord.Option(str, name='roleta', description='Escolha a roleta que quer visualizar', autocomplete=get_roletas, required=True)
):

    message = await create_board_message(ctx, ctx.interaction.channel.id)
    roleta_id = database.select('SELECT id FROM roleta WHERE name="' + roleta + '"')

    await board_update(roleta_id, message)

    await ctx.respond("Carregando...")

# Help embed
def help_embed():

    embed = discord.Embed(title='Lista de comandos')
    embed.add_field(name='Comandos para participar da roleta:',value='',inline=False)
    embed.add_field(name='/registro',value='Se nunca participou de uma roleta, utilize esse comando para se cadastrar',inline=False)
    embed.add_field(name='/configurar',value='Utilize esse comando para configurar sua situação na roleta.\n Permite se ativar/desativar e selecionar o tipo de obra que gostaria de receber e indicar.',inline=False)
    embed.add_field(name='/editar_perfil',value='Utilize esse comando para adicionar informações como link do seu MAL/anilist ao seu perfil da roleta.',inline=False)
    embed.add_field(name='',value='',inline=False)
    embed.add_field(name='Outros comandos da roleta:',value='',inline=False)
    embed.add_field(name='/perfil',value='Permite visualizar o perfil de alguém da roleta à escolha',inline=False)
    embed.add_field(name='/placar_roleta',value='Permite visualizar o placar de uma roleta à escolha.',inline=False)
    embed.add_field(name='/indicar',value='Utilize esse comando para oficializar uma indicação da roleta. Deve ser utilizado APÓS aceite de quem receberá a indicação.',inline=False)
    embed.add_field(name='/terminei',value='Utilize esse comando para oficializar o término de uma indicação da roleta. A nota deve contemplar o conjunto de obras que compõe a indicação e ser um número inteiro de 1 a 10.',inline=False)
    embed.add_field(name='/abandonei',value='Utilize esse comando para oficializar o abandono de uma indicação da roleta. Caso termine a obra um dia, é só utilizar o /terminei!',inline=False)
    #embed.add_field(name='Outros comandos:',value='',inline=False)
    #embed.add_field(name='/arakaki:',value='',inline=False)

    return embed

@bot.command(name='comandos')
async def comandos_command(ctx):
    await ctx.respond(embed=help_embed)

@bot.command(name='ajuda')
async def ajuda_command(ctx):
    await ctx.respond(embed=help_embed)

# Adds entry to obra table
def add_to_obra(link):

    type, id = get_type_and_id_from_anilist_link(link)

    exists = database.check_if_exists(id, 'id', 'obra')

    if exists == 0:
    
        if type == 'anime':

            response = anilist.query_anime_id(id)
                
        else:
            response = anilist.query_manga_id(id)

        anime_obj = response.json()
        title = anime_obj['data']['Media']['title']['romaji']

        sql = 'INSERT INTO obra (id, url, title, type) VALUES (%s,%s,%s,%s)'
        val = (id, link, title, type)
        database.insert(sql,val)
    
    else:

        print('obra já existe na tabela obra')

# Add zakoletas
def add_zakoleta(user_id, quantity):

    sql = 'UPDATE user SET zakoleta=zakoleta+' + str(quantity) + ' WHERE id="' + str(user_id) + '"'
    database.update(sql)

# Gets user score average
async def get_user_avg(user):

    sql = 'SELECT score FROM user_has_roleta WHERE id_receiver="' + str(user.id) + '" ORDER BY id_roleta'
    scores = database.selectall(sql, True)

    print('I was tasked with getting ' + str(user.display_name) + '\'s scores. They are below:')
    print(scores)

    quantity = 0
    total = 0

    for score in scores:
        if score not in [None, '0']:
            quantity += 1
            total += int(score)

    avg = float(total/quantity)

    if avg.is_integer():
        avg = int(avg)
    else:
        avg = round(avg,1)
    print('Their score average is:')
    print(avg)

    return avg

# Auxiliar command
@bot.command(name='debug')
async def debug_command(ctx):

    if ctx.author.id in admins:


        #print(await get_roletas(ctx))

        #await board_update(5)
        #print(get_type_and_id_from_anilist_link('https://anilist.co/anime/141911/Skip-to-Loafer/'))

        #message = await create_board_message(ctx, ctx.interaction.channel.id)

        #await message.edit('691095708866183229,163447617005551616,129635640122933248,115555588397727751,98410347597139968,273325876530380800,92484473207144448,324731795138674689,266340550267895808,1050904689685831760,315599461399265280,95565745009733632,252946147973267456,351647595527143434,188504910059274240,450498161895538708,125944165958680576,98437897933299712,128322474059235328,691095708866183229')

        #await board_update(1, message)

        #jan23 = '691095708866183229,163447617005551616,129635640122933248,115555588397727751,98410347597139968,273325876530380800,92484473207144448,324731795138674689,266340550267895808,1050904689685831760,315599461399265280,95565745009733632,252946147973267456,351647595527143434,188504910059274240,450498161895538708,125944165958680576,98437897933299712,128322474059235328,691095708866183229'
        #fev23 = '273325876530380800,98437897933299712,92484473207144448,98410347597139968,252946147973267456,125944165958680576,745062616493326408,158024279882072064,324731795138674689,129635640122933248,270061072487153664,128322474059235328,235808827662925825,95565745009733632,115555588397727751,1050904689685831760,188504910059274240,266340550267895808,163447617005551616,315599461399265280,273325876530380800'
        #mar23 = '287766312808349696,115555588397727751,163447617005551616,188504910059274240,158024279882072064,691095708866183229,252946147973267456,324731795138674689,745062616493326408,1050904689685831760,128322474059235328,98437897933299712,125944165958680576,129635640122933248,273325876530380800,95565745009733632,92484473207144448,315599461399265280,235808827662925825,98410347597139968,392050013116694528,287766312808349696'
        #abr23 = '98410347597139968,92484473207144448,115555588397727751,125944165958680576,392050013116694528,128322474059235328,235808827662925825,170007555907518464,252946147973267456,691095708866183229,158024279882072064,1050904689685831760,188504910059274240,98437897933299712,315599461399265280,745062616493326408,273325876530380800,287766312808349696,324731795138674689,163447617005551616,129635640122933248,95565745009733632,98410347597139968'
    

        #index = 1

        #roleta = abr23.split(',')
        #print(roleta)
        #print(roleta[1])

        #for id in roleta:
        #    if index < len(roleta):
        #        idx = index
        #        receiver = roleta[index]
        #        giver = id
        #        roleta_id = 4
        #        recs = ''
        #        score = 0
        #        status = ''
        #        index += 1
            
        #        sql = 'INSERT INTO user_has_roleta (idx, id_receiver, id_giver, id_roleta, received_rec, score, status) VALUES (%s,%s,%s,%s,%s,%s,%s)'
        #        val = (idx, str(receiver), str(giver), str(roleta_id), recs, str(score), status)
        #        print('inserting ' + str(giver))
        #        database.insert(sql, val)

        sql = 'SELECT received_rec FROM user_has_roleta WHERE id_roleta=5'
        obras = database.selectall(sql,True)

        print('obras:')
        print(obras)

        for link in obras:
            time.sleep(1)
            if link == None:
                continue
            if ',' not in link:
                print('adicionando ' + link + ' na tabela de obras...')
                add_to_obra(link)

            else:
                links = link.split(',')
                for new_link in links:
                    print('adicionando ' + new_link + ' na tabela de obras...')
                    add_to_obra(new_link)
        
        #sql = 'SELECT id FROM user'
        #users = database.selectall(sql, True)

        #print(users)
        #value = 50

        #for user in users:
        #    times = database.select('SELECT COUNT(1) FROM user_has_roleta WHERE id_giver="' + user + '"')
        #    print('user:')
        #    print(user)
        #    print('times participated:')
        #    print(times)
            
        #    for i in range(times):
        #        sql = 'UPDATE user SET zakoleta=zakoleta+' + str(value) + ' WHERE id="' + user + '"'
        #        #sql = 'UPDATE user SET zakoleta=0 WHERE id="' + user + '"'
        #        database.update(sql)

        print('done')
    
config = configparser.RawConfigParser()
config.read('app.properties')
token = config.get('Discord', 'token')
#bot.run("MTA5OTU5NTIwMDQyODUyMzUzMA.GAqCqA.T2W3Bn9lPCwcTfEHx8IO1s6BK2HBAN4nM9RYeI")
bot.run(token)