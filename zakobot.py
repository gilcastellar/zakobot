from random import choice,choices, shuffle, randint

import discord
from discord.ext import tasks
import configparser
import database
import dbservice
import anilist
import json
import time
import datetime
import asyncio

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = discord.Bot(intents=intents)

admins = [906937520254758973,628466603486478336,1050904689685831760,98410347597139968]

test = 'eita'
key = False

rolls_channel = 1065847698214887496

# Edit profile modal
class EditarPerfilModal(discord.ui.Modal):
    def __init__(self, user_id, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
        list_and_obs = dbservice.select('user', ['anime_list','obs'], '', {'id':user_id})

        _list = list_and_obs[0]
        _obs = list_and_obs[1]

        self.add_item(discord.ui.InputText(label="Link do perfil do MAL/Anilist (opcional)", required=False, value=_list))
        self.add_item(discord.ui.InputText(label="Suas observações", style=discord.InputTextStyle.long, required=False, value=_obs))

    async def callback(self, interaction: discord.Interaction):
        #await interaction.response.send_message('Editando...')
        embed = discord.Embed(title="Perfil")
        embed.add_field(name="MAL/Anilist", value=self.children[0].value, inline=False)
        embed.add_field(name="Suas observações", value=self.children[1].value, inline=False)

        user_id = str(interaction.user.id)
        _list = self.children[0].value
        print(_list)
        _obs = self.children[1].value
        print(_obs)

        #sql = 'UPDATE user SET anime_list= "' + _list + '", obs= "' + _obs + '" WHERE id=' + user_id
        #print(sql)
        #database.update(sql)

        dbservice.update('user', ['anime_list', 'obs'], [_list, _obs], {'id': user_id})

        global key
        key = True

        await interaction.response.send_message('Edições realizadas! Utilize o comando /perfil para visualizar.')

top_page = 1
top_list = []

class TopPagination(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
    def __init__(self, msg, page, list, type, min):
        super().__init__()
        #self.ctx = ctx
        self.msg = msg
        self.page = page
        self.list = list
        self.type = type
        self.min = min

    @discord.ui.button(label="<<", row=0, style=discord.ButtonStyle.primary)
    async def first_button_callback(self, button, interaction):
        if self.page > 1:
            self.page -= 1
        await generate_top(self.msg, self.page, self.list, self.type, self.min)
        await interaction.response.send_message('')

    @discord.ui.button(label=">>", row=0, style=discord.ButtonStyle.primary)
    async def second_button_callback(self, button, interaction):
        self.page += 1
        await generate_top(self.msg, self.page, self.list, self.type, self.min)
        await interaction.response.send_message('')

class CollectionPagination(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
    def __init__(self, msg, user_id, page):
        super().__init__()
        #self.ctx = ctx
        self.msg = msg
        self.user_id = user_id
        self.page = page

    @discord.ui.button(label="<<", row=0, style=discord.ButtonStyle.primary)
    async def first_button_callback(self, button, interaction):
        if self.page > 1:
            self.page -= 1
        await generate_collection(self.msg, self.user_id, self.page)
        await interaction.response.send_message('')

    @discord.ui.button(label=">>", row=0, style=discord.ButtonStyle.primary)
    async def second_button_callback(self, button, interaction):
        self.page += 1
        await generate_collection(self.msg, self.user_id, self.page)
        await interaction.response.send_message('')

@bot.event
async def on_ready():
    print(get_timestamp())

    check_time.start()

    #check_activities.start()

    make_rolls.start()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    msg = message.content.split(' ')

    command = msg[0].lower()

    match command:

        case ";r":

            if message.channel.id in [rolls_channel]:

                if len(msg) > 1:
                
                    if int(msg[1]) >= 10:
                        rolls = 10

                    elif int(msg[1]) in range(1,10):
                        rolls = int(msg[1])

                else:

                    rolls = 1

                user_name = dbservice.select('user', ['name'], '', {'id': message.author.id})

                roll_id = dbservice.insert('rolls', ['user', 'quantity'], [user_name, rolls])
            
@tasks.loop(minutes=1)
async def check_time():

    realtime = get_realtime()

    if realtime.hour == 4 and realtime.minute in range(54,58):
        await clean_dailies()
        
    if realtime.hour == 5:
        await dailies()

# Send message
async def send_message(ctx, text, channel_id=''):

    if channel_id != '':
        channel = bot.get_channel(channel_id)
        message = await channel.send(text)
    else:
        message = await ctx.send(text)

    return message

# Send message
async def send_message2(text, channel_id):

    channel = bot.get_channel(channel_id)
    message = await channel.send(text)

    return message

# Send embed
async def send_embed(ctx, embed):

    await ctx.send(embed=embed)

# Send embed
async def send_embed2(embed, channel_id):
    
    channel = bot.get_channel(channel_id)
    await channel.send(embed=embed)

def get_realtime():
    
    epoch = int(datetime.datetime.now().timestamp())

    date_time = datetime.datetime.fromtimestamp(epoch + 14400)
    
    return date_time

def get_timestamp():

    epoch = int(datetime.datetime.now().timestamp())

    date_time = datetime.datetime.fromtimestamp(epoch + 14400)
    
    date = date_time.strftime("%B %d, %Y")
    _time = date_time.strftime("%H:%M:%S")

    return date + ' ' + _time

def from_epoch_to_rt(epoch):

    return datetime.datetime.fromtimestamp(epoch + 14400)

# Fetch user object
async def fetch_user(id):
    user = await bot.fetch_user(id)

    return user

# Get active members
async def get_members_names(ctx: discord.AutocompleteContext):

    #members = database.selectall('SELECT id, name, active, anime_list, receives, gives, obs FROM user ORDER BY active DESC, name')

    members = dbservice.select('user', ['id', 'name', 'active', 'anime_list', 'receives', 'gives', 'obs'], 'ORDER BY active DESC, name')

    print(members)

    #members = from_list_of_tuples_to_list(members)

    #print(members)

    members_names = []

    for member in members:
        members_names.append(member[1])

    #return [name for name in members_names if name.lower().startswith(ctx.value.lower())]
    return [name for name in members_names if ctx.value.lower() in name.lower()]

# Get active members without youself
async def get_members_names2(ctx: discord.AutocompleteContext):

    #members = database.selectall('SELECT id, name, active, anime_list, receives, gives, obs FROM user ORDER BY active DESC, name')

    user_name = dbservice.select('user', ['name'], '', {'id': ctx.interaction.user.id})

    members = dbservice.select('user', ['id', 'name', 'active', 'anime_list', 'receives', 'gives', 'obs'], 'ORDER BY active DESC, name')

    print(members)

    #members = from_list_of_tuples_to_list(members)

    #print(members)

    members_names = []

    for member in members:
        members_names.append(member[1])

    members_names.remove(user_name)

    #return [name for name in members_names if name.lower().startswith(ctx.value.lower())]
    return [name for name in members_names if ctx.value.lower() in name.lower()]

# Get member info
def get_member_info(name):
    
    #member = database.selectall('SELECT id, name, active, anime_list, receives, gives, obs, zakoleta FROM user WHERE name="' + name + '"')

    member = dbservice.select('user', ['id', 'name', 'active', 'anime_list', 'receives', 'gives', 'obs', 'zakoleta'], '', {'name': name})

    print(member)

    id = member[0]
    active = member[2]
    anime_list = member[3]
    receives = member[4]
    gives = member[5]
    obs = member[6]
    zakoleta = member[7]

    return id, active, anime_list, receives, gives, obs, zakoleta

# Get type and id from anilist link
def get_type_and_id_from_anilist_link(link):

    if 'https://' in link:

        link = link.replace('https://','')

    link_parts = link.split('/')

    print(link_parts[1])

    return link_parts[1], link_parts[2]

# Get roulettes
async def get_roletas(ctx: discord.AutocompleteContext):

    #roletas = database.selectall('SELECT name FROM roleta ORDER BY id')
    roletas = dbservice.select('roleta', ['name'], ' ORDER BY id')

    roleta_names = []

    for roleta in roletas:

        roleta_names.append(roleta[0])

    return [name for name in roleta_names if ctx.value.lower() in name.lower()]
    #return roleta_names

async def get_media_names(ctx: discord.AutocompleteContext):

    #members = database.selectall('SELECT id, name, active, anime_list, receives, gives, obs FROM user ORDER BY active DESC, name')

    medias = dbservice.select('media', ['title_romaji'], '')

    #print(medias)

    medias = from_list_of_tuples_to_list(medias)

    #members = from_list_of_tuples_to_list(members)

    #print(members)

    media_names = []

    for media in medias:
        media_names.append(media)

    return [name for name in media_names if ctx.value.lower() in name.lower()]

async def get_collection(ctx):

    user_id = ctx.interaction.user.id
    
    #collection = database.selectall('SELECT chara_name FROM user_has_chara WHERE user_id="' + str(user_id) + '"', True)

    collection = dbservice.select('user_has_chara', ['chara_name'], '', {'user_id': str(user_id)})

    collection = from_list_of_tuples_to_list(collection)

    return [name for name in collection if ctx.value.lower() in name.lower()]

async def get_chara(ctx):

    chara = dbservice.select('chara', ['name'], '')

    chara = from_list_of_tuples_to_list(chara)

    return [name for name in chara if ctx.value.lower() in name.lower()]

@bot.command(name='registro')
async def registro_command(ctx):

    user_id = ctx.author.id
    #exists = database.check_if_exists(str(user_id), 'id', 'user')

    exists = dbservice.check_existence('user', {'id': str(user_id)})

    if exists == 0:

        guild = 1059298932825538661
        name = ctx.author.name
        #database.insert('INSERT INTO user (id, id_guild, name) VALUES (%s,%s,%s)',(user_id, guild, name))

        dbservice.insert('user', ['id', 'id_guild', 'name'], (user_id, guild, name))

        await ctx.respond(f"Seja bem-vindo(a) à roleta, {name}!")

    else:

        await ctx.respond('Você já está cadastrado!')

@bot.slash_command(name='editar_perfil')
async def editar_perfil_command(ctx: discord.ApplicationContext):
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
  
  #sql = 'UPDATE user SET active= "' + is_ativo + '", receives= "' + tipo_que_recebe.lower() + '", gives= "' + tipo_que_envia.lower() +  '" WHERE id=' + user_id
  #database.update(sql)

  dbservice.update('user', ['active','receives','gives'], [is_ativo, tipo_que_recebe.lower(), tipo_que_envia.lower()], {'id': user_id})

  if ativo.lower() == 'inativo':

      await ctx.respond(f'Você está inativo. Bom descanso!')

  else:

      await ctx.respond(f'Você está ativo e quer receber `{tipo_que_recebe.lower()}` e enviar `{tipo_que_envia.lower()}` na roleta!')

@bot.slash_command(name='perfil')
async def perfil_command(
    ctx: discord.ApplicationContext,
    member: discord.Option(str, autocomplete=get_members_names, name='membro')
):
    await ctx.respond(f"Trazendo o perfil escolhido...")

    #print(member)

    id, active, anime_list, receives, gives, obs, zakoletas = get_member_info(member)

    print(id)

    user = await bot.fetch_user(id)

    member = ctx.guild.get_member(int(id))

    print(member)
    avatar = user.avatar
    
    print(get_timestamp() + ': O usuário ' + ctx.author.display_name + ' usou requeriu o /perfil de ' + user.display_name)

    #if member.is_
    print('Status: ' + str(member.is_on_mobile()))
    if anime_list != None:
        if ',' in anime_list:
            list = anime_list.split(',')
            anime_list = list[0]
            anime_list_text = ''
            for anime in list:
                anime_list_text += anime + ' | '
            anime_list_text = anime_list_text.strip("| ")
        else:
            anime_list_text = anime_list

    if active == 1:

        _ativo = 'Ativo(a)'

    else:

        _ativo = 'Inativo(a)'

    if zakoletas == None:
        zakoletas = 0

    user_avg = await get_user_avg(user)

    user_given_avg = 'Sem amostragem'
    user_received_avg = 'Sem amostragem'

    if user_avg != False:
        if user_avg[0] != None:
            user_given_avg = str(user_avg[0]) + '/10'
        if user_avg[1] != None:
            user_received_avg = str(user_avg[1]) + '/10'

    print(id)

    pendencies = get_pendencies(id)

    if pendencies == '':
        pendencies = 'Nenhuma'
        
    embed=discord.Embed(title=member, url=anime_list, color=0xe84545)
    embed.set_thumbnail(url=avatar)
    embed.add_field(name=_ativo,value='',inline=True)
    if zakoletas > 0:
        embed.add_field(name="Ƶ " + str(zakoletas), value="", inline=True)
        embed.add_field(name=" ­­", value=" ", inline=True)
    if anime_list != None:
        embed.add_field(name="Perfil do MAL/Anilist", value=anime_list_text, inline=False)
        embed.add_field(name="", value="", inline=False)
    embed.add_field(name="Roleta:", value="", inline=False)
    if None not in [receives, gives]:
        embed.add_field(name="Quero receber:", value=receives.title(), inline=True)
        embed.add_field(name="Posso enviar:", value=gives.title(), inline=True)
        embed.add_field(name=" ­­", value=" ", inline=True)
    embed.add_field(name='Zakomédias:',value='',inline=False)
    embed.add_field(name="Consumido:", value=user_given_avg, inline=True)
    embed.add_field(name="Recomendado:", value=user_received_avg, inline=True)
    embed.add_field(name=" ­­", value=" ", inline=True)
    embed.add_field(name="Pendências", value=pendencies, inline=False)
    embed.add_field(name='Observações:',value=obs,inline=False)
    embed.set_footer(text="Esse perfil foi gerado por ZAKOBOT e esse rodapé existe pro perfil do JapZ não ficar cagado.")

    await ctx.send(embed=embed)

@bot.slash_command(name='sorteio')
async def sorteio_command(
    ctx: discord.ApplicationContext,
    name: discord.Option(str, name='nome'),
    delay: discord.Option(int, name='delay'),
    real: discord.Option(str, name='real', options=['True','False'])
):
    
    if ctx.author.id in admins:

        #sql = 'SELECT id, gives, receives FROM user WHERE active=1'
        #draw_list = database.selectall(sql)

        draw_list = dbservice.select('user', ['id', 'gives', 'receives'], '', {'active': 1})

        print(draw_list)

        time.sleep(10)

        draw_list = merge_id_with_type(draw_list)

        id = get_last_roulette_id()

        last_two_draws = get_last_draws(id)

        result = roulette_shuffle(draw_list, id, last_two_draws)
        print(type(result))

        result_as_str = draw_to_str(result)
        print(result_as_str)
        print(type(result_as_str))

        time.sleep(10)

        pairs = generate_pairs(result)

        dbservice.insert('roleta', ['id', 'name', 'draw', 'status'], (id+1, name, result_as_str, 'ongoing'))
        
        index = 1

        for pair in pairs:

            time.sleep(delay)

            giver, receiver = pair.split(',')

            giver = await fetch_user(giver)
            receiver = await fetch_user(receiver)

            if real == 'True':
                
                add_zakoleta(ctx.author.id, 50, ' +50 pela participação na roleta de ' + name)

                text = giver.display_name + ' -> ' + receiver.display_name
            
                message = await send_message(ctx,text) # REALIZA O SORTEIO AO VIVO NO CHAT E RETORNA O OBJETO DA MENSAGEM

            dbservice.insert('user_has_roleta', ['idx', 'id_receiver', 'id_giver', 'id_roleta', 'status'], (index, str(receiver.id), str(giver.id), id+1, 'ongoing'))
            
            index += 1

        #board_message = await create_placeholder_message(ctx, 1077070205987082281)

        #print(board_message)
        
        #board_message_id = board_message.id
        #print('board_message_id:')
        #print(board_message_id)

        #board_message_channel_id = board_message.channel.id
        #print('board_message_channel_id:')
        #print(board_message_channel_id)

        #dbservice.update('roleta', ['id_message', 'id_channel'], [board_message_id, board_message_channel_id], {'id': id+1})

        #await board_update(id+1)

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

    #sql = 'SELECT id FROM roleta'
    #result = database.selectall(sql, True)

    result = dbservice.select('roleta', ['id'], '')

    print(result)

    result = from_list_of_tuples_to_list(result)

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

    #sql = 'SELECT draw FROM roleta WHERE id=' + last
    #last_draw = database.select(sql)

    last_draw = dbservice.select('roleta', ['draw'], '', {'id': last})

    #sql = 'SELECT draw FROM roleta WHERE id=' + second_last
    #second_last_draw = database.select(sql)

    second_last_draw = dbservice.select('roleta', ['draw'], '', {'id': second_last})

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
            
    return True

# Creates board message
async def create_placeholder_message(ctx, channel_id):

    return await send_message(ctx, 'Carregando...', channel_id)

# Generate board
async def generate_board(info, message, id=0):

    #name = database.select('SELECT name FROM roleta WHERE id=' + str(id))

    name = dbservice.select('roleta', ['name'], '', {'id': str(id)})

    name = parse_name(name)

    board_text = name + '\n```'

    print('board_text:')
    print(board_text)

    for pairing in info:

        #giver_name = database.select('SELECT name FROM user WHERE id="' + pairing[1] + '"')
        giver_name = dbservice.select('user', ['name'], '', {'id': pairing[1]})
        #receiver_name = database.select('SELECT name FROM user WHERE id="' + pairing[2] + '"')
        receiver_name = dbservice.select('user', ['name'], '', {'id': pairing[2]})

        print('pairing[3]')
        print(pairing[3])

        if pairing[3] != None and pairing[3] != '':

            medias = board_indications_manager(pairing[2], id)

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

        board_text += str(pairing[0]) + '. ' + giver_name + ' -> ' + receiver_name + ' [' + medias + '] ' + status_text + score + '\n'
    
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

    #sql = 'SELECT id_message, id_channel FROM roleta WHERE id=' + str(roleta_id)
    #message_info = database.selectall(sql)

    message_info = dbservice.select('roleta', ['id_message', 'id_channel'], '', {'id': str(roleta_id)})
    
    print('printing message info twice')

    print(message_info)

    message_info = from_list_of_tuples_to_list(message_info)
    
    print(message_info)

    if message == None:

        print("message_info")
        print(message_info)
        print('message_info[0]')
        print(message_info[0])

        channel_id = int(message_info[1])

        channel = bot.get_channel(channel_id)

        message_id = int(message_info[0])

        print('message_id')
        print(message_id)

        message = await channel.fetch_message(message_id)

    #sql = 'SELECT idx, id_giver, id_receiver, received_rec, score, status FROM user_has_roleta WHERE id_roleta="' + str(roleta_id) + '" ORDER BY idx'
    #board_info = database.selectall(sql)

    board_info = dbservice.select('user_has_roleta', ['idx', 'id_giver', 'id_receiver', 'received_rec', 'score', 'status'], 'ORDER BY idx', {'id_roleta': str(roleta_id)})

    print('starting to generate board')
    print('roleta_id:')
    print(roleta_id)

    await generate_board(board_info, message, roleta_id)
    
# Board indications manager
def board_indications_manager(receiver_id, roleta_id):

    media_text = ''

    #medias = database.select('SELECT media_name FROM user_has_roleta WHERE id_receiver="' + receiver_id + '" AND id_roleta=' + str(roleta_id))
    
    medias = dbservice.select('user_has_roleta', ['media_name'], '', {'id_receiver': receiver_id, 'id_roleta': str(roleta_id)})

    if medias != None:

        if '|' not in medias:
            
            media_text += medias

        else:

            medias = medias.split('|')

            for media in medias:

                media_text += media + " | "

        media_text = media_text.strip("| ")

        return media_text
     
    else:

        return ''
    
@bot.slash_command(name='indicar')
async def indicar_command(
    ctx: discord.ApplicationContext,
    media1: discord.Option(str, name='primeira_indicação', description='INSIRA O LINK DO ANILIST DA OBRA', required=True),
    media2: discord.Option(str, name='segunda_indicação', description='INSIRA O LINK DO ANILIST DA OBRA', required=False),
    media3: discord.Option(str, name='terceira_indicação', description='INSIRA O LINK DO ANILIST DA OBRA', required=False)
):
    await ctx.respond(f"Obrigado pela indicação!")

    #roletas = database.selectall('SELECT id FROM roleta', True)

    roletas = dbservice.select('roleta', ['id'], '')

    roleta_atual = max(roletas)

    roleta_atual = 5

    #sql = 'SELECT id_giver FROM user_has_roleta WHERE id_roleta="' + str(roleta_atual) + '"'
    #allowed_givers = database.selectall(sql, True)

    allowed_givers = dbservice.select('user_has_roleta', ['id_giver'], '', {'id_roleta': str(roleta_atual)})

    medias = ''
    medias += media1

    if media2 != None:

        medias += ',' + media2

    if media3  != None:

        medias += ',' + media3

    if str(ctx.author.id) in allowed_givers:

        #sql = 'UPDATE user_has_roleta SET received_rec="' + medias + '" WHERE id_giver="' + str(ctx.author.id) + '" AND id_roleta=' + str(roleta_atual)
        #database.update(sql)

        dbservice.update('user_has_roleta', ['received_rec'], [medias], {'id_giver':ctx.author.id, 'id_roleta':roleta_atual})

    list = []

    if ',' in medias:
        list = medias.split(',')
    else:
        list.append(medias)

    for media in list:
        print('adding media_name to table user_has_roleta:')
        print(media)

        type, id = get_type_and_id_from_anilist_link(media)

        if type == 'anime':

            response = anilist.query_anime_id(id)
                
        else:

            response = anilist.query_manga_id(id)

        media_obj = response.json()
        title = media_obj['data']['Media']['title']['romaji']

        #sql = 'UPDATE user_has_roleta SET media_name="' + title + '" WHERE id_giver="' + str(ctx.author.id) + '" AND id_roleta=' + str(roleta_atual)
        #database.update(sql)

        dbservice.update('user_has_roleta', ['media_name'], [title], {'id_giver':ctx.author.id, 'id_roleta':roleta_atual})
    
    await board_update(roleta_atual)

@bot.slash_command(name='terminei')
async def terminei_command(
    ctx: discord.ApplicationContext,
    roleta: discord.Option(str, name='roleta', description='Escolha a roleta', autocomplete=get_roletas, required=True),
    score: discord.Option(int, name='nota', description='Insira sua nota de 1 a 10', min_value=1, max_value=10, required=True)
):
    await ctx.respond(f"Obrigado pela dedicação! :muscle:")
    
    roleta_id = dbservice.select('roleta', ['id'], '', {'name': roleta})
    
    status = dbservice.select('user_has_roleta', ['status'], '', {'id_receiver': str(ctx.author.id), 'id_roleta': str(roleta_id)})

    name = dbservice.select('roleta', ['name'], '', {'id': str(roleta_id)})

    name = parse_name(name)

    print(roleta_id)
    print(status)
    print(name)


    if status == 'ongoing':
        add_zakoleta(ctx.author.id, 50, ' +50 por terminar suas indicações de ' + name)
        await ctx.send('Você recebeu Ƶ 50 por finalizar sua indicação.')

    #sql = 'UPDATE user_has_roleta SET score=' + str(score) + ',status="finished"' + 'WHERE id_roleta=' + str(roleta_id) + ' AND id_receiver="' + str(ctx.author.id) + '"'
    #database.update(sql)

    dbservice.update('user_has_roleta', ['score','status'], [score,'finished'], {'id_roleta': roleta_id, 'id_receiver': ctx.author.id})

    #await ctx.respond(f"Obrigado pela dedicação! :muscle:")

    #await ctx.response.defer()
    #await asyncio.sleep()
    #await ctx.followup.send()

    await board_update(roleta_id)

@bot.slash_command(name='abandonei')
async def abandonei_command(
    ctx: discord.ApplicationContext,
    roleta: discord.Option(str, name='roleta', description='Escolha a roleta', autocomplete=get_roletas, required=True)
):
    await ctx.respond(f"Obrigado por priorizar sua saúde mental! :health_worker:")
    
    roleta_id = dbservice.select('roleta', ['id'], '', {'name': roleta})
    
    status = dbservice.select('user_has_roleta', ['status'], '', {'id_receiver': str(ctx.author.id), 'id_roleta': str(roleta_id)})
    
    name = dbservice.select('roleta', ['name'], '', {'id': str(roleta_id)})

    name = parse_name(name)

    if status == 'ongoing':
        add_zakoleta(ctx.author.id, 25, ' +25 por abandonar suas indicações de ' + name)
        await ctx.send('Você recebeu Ƶ 25 por abandonar manualmente sua indicação.')

    #sql = 'UPDATE user_has_roleta SET status="abandoned" WHERE id_roleta=' + str(roleta_id) + ' AND id_receiver="' + str(ctx.author.id) + '"'
    #database.update(sql)

    dbservice.update('user_has_roleta', ['status'], ['abandoned'], {'id_roleta':roleta_id, 'id_receiver': ctx.author.id})

    await board_update(roleta_id)

@bot.slash_command(name='placar_roleta')
async def placar_roleta_command(
    ctx: discord.ApplicationContext,
    roleta: discord.Option(str, name='roleta', description='Escolha a roleta que quer visualizar', autocomplete=get_roletas, required=True)
):
    await ctx.respond("Carregando...")

    message = await create_placeholder_message(ctx, ctx.interaction.channel.id)
    #roleta_id = database.select('SELECT id FROM roleta WHERE name="' + roleta + '"')

    roleta_id = dbservice.select('roleta', ['id'], {'name': roleta})

    await board_update(roleta_id, message)
    
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
    await ctx.respond(embed=help_embed())

@bot.command(name='ajuda')
async def ajuda_command(ctx):
    await ctx.respond(embed=help_embed())

# Adds entry to obra table
def add_to_obra(link):

    type, id = get_type_and_id_from_anilist_link(link)

    #exists = database.check_if_exists(id, 'id', 'obra')

    exists = dbservice.check_existence('obra', {'id': str(id)})

    if exists == 0:
    
        if type == 'anime':

            response = anilist.query_anime_id(id)
                
        else:

            response = anilist.query_manga_id(id)

        anime_obj = response.json()
        title = anime_obj['data']['Media']['title']['romaji']

        #sql = 'INSERT INTO obra (id, url, title, type) VALUES (%s,%s,%s,%s)'
        #val = (id, link, title, type)
        #database.insert(sql,val)

        dbservice.insert('obra', ['id', 'url', 'title', 'type'], (id, link, title, type))
    
    else:

        print('obra já existe na tabela obra')

# Add zakoletas
def add_zakoleta(user_id, quantity, text):
    
    datetime = get_timestamp()

    full_text = ',' + datetime + text

    #sql = 'UPDATE user SET zakoleta=zakoleta+' + str(quantity) + ', zakoleta_log=concat(zakoleta_log, "' + full_text + '") WHERE id="' + str(user_id) + '"'
    #database.update(sql)

    #dbservice.update('user', ['zakoleta', 'zakoleta_log'], ['zakoleta + ' + str(quantity), 'concat(zakoleta_log, "' + full_text], {'id': user_id})

    dbservice.update_zakoleta('user', quantity, full_text, user_id, 'add')

    print(full_text)

# Gets user score average
async def get_user_avg(user):

    both_avg = []

    #sql = 'SELECT score FROM user_has_roleta WHERE id_receiver="' + str(user.id) + '" ORDER BY id_roleta'
    #scores_given = database.selectall(sql, True)

    scores_given = dbservice.select('user_has_roleta', ['score'], 'ORDER BY id_roleta', {'id_receiver': str(user.id)})

    scores_given = from_list_of_tuples_to_list(scores_given)

    print('I was tasked with getting ' + str(user.display_name) + '\'s given scores. They are below:')
    print(scores_given)

    quantity = 0
    total = 0

    for score in scores_given:

        if score not in [None, '0']:

            quantity += 1
            total += int(score)

    if total not in [None, 0]:

        avg = float(total/quantity)

        if avg.is_integer():

            avg = int(avg)

        else:

            avg = round(avg,1)

        print('Their given score average is:')
        print(avg)

    else:

        avg = None

    both_avg.append(avg)
    
    #sql = 'SELECT score FROM user_has_roleta WHERE id_giver="' + str(user.id) + '" ORDER BY id_roleta'
    #scores_received = database.selectall(sql, True)
    
    scores_received = dbservice.select('user_has_roleta', ['score'], 'ORDER BY id_roleta', {'id_giver': str(user.id)})

    scores_received = from_list_of_tuples_to_list(scores_received)

    print('I was tasked with getting ' + str(user.display_name) + '\'s received scores. They are below:')
    print(scores_received)

    quantity = 0
    total = 0

    for score in scores_received:

        if score not in [None, '0']:

            quantity += 1
            total += int(score)

    if total not in [None, 0]:

        avg = float(total/quantity)

        if avg.is_integer():

            avg = int(avg)

        else:

            avg = round(avg,1)

        print('Their received score average is:')
        print(avg)

    else:

        avg = None

    both_avg.append(avg)

    if both_avg[0] == None and both_avg[1] == None:

        return False

    else:
        
        return both_avg

def get_pendencies(user_id):
    
    #sql = 'SELECT received_rec FROM user_has_roleta WHERE status="ongoing" AND id_receiver="' + str(user_id) + '"'
    #pendencies = database.selectall(sql, True)

    pendencies = dbservice.select('user_has_roleta', ['received_rec'], '', {'status': 'ongoing', 'id_receiver': str(user_id)})

    if type(pendencies) == list:

        pendencies = from_list_of_tuples_to_list(pendencies)

    else:

        pendencies = [pendencies]
        

    #sql = 'SELECT name FROM user WHERE id="' + str(user_id) + '"'
    #name = database.select(sql)

    name = dbservice.select('user', ['name'], '', {'id': str(user_id)})
    
    pendencies_text = ''

    print('I was tasked with getting ' + name + '\'s pendencies. They are below:')
    for i in pendencies:
        print(i)

        if ',' in i:

            medias = i.split(',')

        else:

            medias = [i]

        for media in medias:

            format, id = get_type_and_id_from_anilist_link(media)

            if format == 'anime':

                response = anilist.query_anime_id(id)
                
            else:

                response = anilist.query_manga_id(id)

            media_obj = response.json()
            title = media_obj['data']['Media']['title']['romaji']

            pendencies_text += '[' + title + '](' + i + ') | '

        pendencies_text = pendencies_text.strip(' | ')

        pendencies_text += '\n'

        print(pendencies_text)

    return pendencies_text

def get_anilist_user_from_link(link):

    print(link)

    if 'https://' in link:

        link = link.replace('https://','')

    if ',' in link:
        link = link.split(',')

    for i in link:
        if 'anilist' in i:
            link = i
            break
    
    link_parts = link.split('/')

    print(link_parts[2])

    return link_parts[2]

anime_utils_options = ['Escolha uma obra do meu Watching','Escolha uma obra do meu Planning']

@bot.slash_command(name='utilidades')
async def utilidades_command(
    ctx: discord.ApplicationCommand,
    utils: discord.Option(str, choices=anime_utils_options, required=True)
):
    await ctx.respond('Executando comando...')

    match utils:

        case 'Escolha uma obra do meu Watching':

            #link = database.select('SELECT anime_list FROM user WHERE id="' + str(ctx.author.id) + '"')
            #print(link)

            link = dbservice.select('user', ['anime_list'], '', {'id': str(ctx.author.id)})
            
            user_name = get_anilist_user_from_link(link)

            anime, anime_link = anime_picker(ctx, user_name, ['CURRENT', 'REPEATING'])

            await ctx.send('Que tal assistir um episódio de ' + anime + '? Link: ' + anime_link)

        case 'Escolha uma obra do meu Planning':

            #link = database.select('SELECT anime_list FROM user WHERE id="' + str(ctx.author.id) + '"')
            
            link = dbservice.select('user', ['anime_list'], '', {'id': str(ctx.author.id)})
            user_name = get_anilist_user_from_link(link)

            anime, anime_link = anime_picker(ctx, user_name, ['PLANNING'])

            await ctx.send('Que tal começar ' + anime + '? Link: ' + anime_link)


def anime_picker(ctx, user_name, status):
    query = '''query ($page: Int, $status_in: [MediaListStatus], $userName: String) {
              Page(page: $page, perPage: 50) {
                pageInfo {
                  total
                  currentPage
                  lastPage
                  hasNextPage
                  perPage
                }
                mediaList(status_in: $status_in, userName: $userName, type: ANIME) {
                  mediaId
                  id
                  userId
                  progress
                  status
                  media {
                    title {
                      romaji
                    }
                  }
                }
              }
            }'''

    hasNextPage = True
    page = 1

    list = []

    while hasNextPage:
        response = anilist.query_list(query, page, user_name, status)

        obj = response.json()
        
        #print(obj['data']['Page']['pageInfo']['hasNextPage'])

        if obj['data']['Page']['pageInfo']['hasNextPage'] == False:
            hasNextPage = False
            
        #print(obj)
        
        for id in obj['data']['Page']['mediaList']:
            dict = {'id': id['mediaId'], 'progress': id['progress']}
            #print(id['mediaId'])
            list.append(dict)

        page += 1

    print(get_timestamp() + ' I was tasked with creating a list of dicts of anime IDs and their progress. Here it is: ')
    idx = 1
    for i in list:
        #print(str(idx) + '. ' + str(i))
        idx += 1

    not_finished = True
        
    while not_finished:

        chosen_anime = choice(list)

        response = anilist.query_anime_id(chosen_anime['id'])

        obj = response.json()

        title = obj['data']['Media']['title']['romaji']
        anime_status = obj['data']['Media']['status']

        if anime_status == 'FINISHED':
            not_finished = False

    link = 'https://anilist.co/anime/' + str(chosen_anime['id'])

    print(title)
    print(status)
    print(link)

    return title, link

@bot.slash_command(name='obra')
async def obra_command(
  ctx: discord.ApplicationContext,
  obra: discord.Option(str, name='obra', autocomplete=get_media_names, description="Link do Anilist"),
  format: discord.Option(str, name='tipo', choices=['Anime', 'Manga'], description="Em caso de homonimos, diferencie o tipo da obra aqui", required=False)
):
    if 'anilist.co/' in obra:
        await ctx.respond('Puxando dados...')
        type, id = get_type_and_id_from_anilist_link(obra)
        await generate_stats(ctx, type, id)
    else:
        await ctx.respond('Puxando dados...')

        exists = dbservice.check_existence('media', {'title_romaji': obra, 'format': format.upper()})

        if exists == 1:

            url = dbservice.select('media', ['url'], '', {'title_romaji': obra, 'format': format.upper()})
            
            type, id = get_type_and_id_from_anilist_link(url)

            await generate_stats(ctx, type, id)
            
        else:

            await ctx.respond('Dado inserido inválido. Ele precisa direcionar à página de uma obra do Anilist.')
            print('O usuário ' + ctx.author.display_name + ' tentou enviar ' + obra + ' no comando "animestats"')

async def generate_stats(ctx, type, id):

    if type == 'anime':

        response = anilist.query_anime_id(id)

    else:

        response = anilist.query_manga_id(id)

    obj = response.json()

    print(obj)

    title = obj['data']['Media']['title']['romaji']

    format = obj['data']['Media']['format']

    cover_img = obj['data']['Media']['coverImage']['large']

    #print(cover_img)

    if format in ['TV', 'TV_SHORT', 'MOVIE', 'SPECIAL', 'OVA', 'ONA', 'MUSIC']:
        episodes = obj['data']['Media']['episodes']
    

    match format:
        case 'TV':
            format = 'Série'
        case 'TV_SHORT':
            format = 'Curto'
        case 'MOVIE':
            format = 'Filme'
        case 'SPECIAL':
            format = 'Especial'
        case 'MUSIC':
            format = 'Música'
        case 'MANGA':
            format = 'Mangá'
        case 'NOVEL':
            format = 'Novel'
        case 'ONE_SHOT':
            format = 'One-shot'

    year = obj['data']['Media']['startDate']['year']

    avg_score = obj['data']['Media']['averageScore']/10

    link = 'https://anilist.co/anime/' + str(id)

    #users_w_list = database.selectall('SELECT anime_list FROM user WHERE NOT anime_list="Null"',True)

    lists = dbservice.select('user', ['anime_list'], '')

    lists = from_list_of_tuples_to_list(lists)

    print(lists)

    anilist_users = []

    for user in lists:
        if 'anilist.co' in user:
            if ',' in user:
                lists = user.split(',')
                for list in lists:
                    if 'anilist.co' in list:
                        anilist_users.append(get_anilist_user_from_link(list))
            else:
                anilist_users.append(get_anilist_user_from_link(user))

    header = 'Membro                      Nota      Status'
    body_text = '```Membro              Nota    Estado\n\n'

    score_total = 0
    idx = 0

    list = []

    for user in anilist_users:
        response = anilist.query_user_list(type, id, user)
        obj = response.json()
        print(user)
        print(obj)

        if obj['data']['MediaList'] != None:
            score = obj['data']['MediaList']['score']
            status = obj['data']['MediaList']['status']
            dict = {'name': user, 'score': score, 'status': status}
            list.append(dict)

    print(list)

    if list != []:

        list = sorted(list, key=lambda d: d['status'], reverse=False)
        list = sorted(list, key=lambda d: d['score'], reverse=True)

        for dict in list:
            text = ''
            text += dict['name']
            while len(text) != 20:
                text += ' '
            print(dict['score']%1)

            if dict['score']%1 != 0:
                text += str(dict['score']) + '   '
                score_total += dict['score']
                idx += 1
            elif dict['score'] == 10:
                text += str(dict['score']) + '    '
                score_total += dict['score']
                idx += 1
            else:
                if dict['score'] == 0:
                    text += '-     '
                else:
                    text += str(dict['score']) + '     '
                    score_total += dict['score']
                    idx += 1
        
            match dict['status']:

                case 'COMPLETED':
                    status = ''

                case 'PAUSED':
                    status = 'Pausado'

                case 'DROPPED':
                    status = 'Dropado'

                case 'PLANNING':
                    continue

                case 'CURRENT':
                    if type == 'anime':
                        status = 'Assistindo'

                    else:
                        status = 'Lendo'

            text += '  ' + status + '\n'

            print(text)

            body_text += text

        if idx > 0:
            avg = round(score_total/idx,2)
            body_text += '\nMédia               ' + str(avg)

        body_text += '\n```'

        print(str(score_total) + ' dividido por ' + str(idx))

        embed = discord.Embed(title=title, url=link, color=0xe84545)
        embed.set_thumbnail(url=cover_img)
        embed.add_field(name='Formato:',value=format,inline=True)
        embed.add_field(name='Ano:',value=year,inline=True)
        embed.add_field(name='Média do Anilist:',value=avg_score,inline=True)
        embed.add_field(name='',value='',inline=False)
        embed.add_field(name='',value='',inline=False)
        #embed.add_field(name=header,value='',inline=False)
        embed.add_field(name='',value=body_text,inline=False)
        embed.add_field(name='',value='',inline=False)
        embed.set_footer(text="Dados gerados em " + get_timestamp())

        await ctx.send(embed=embed)

    else:

        await ctx.send('Ninguém com lista cadastrada consumiu ' + title)
    
@bot.slash_command(name='top')
async def top_command(
    ctx: discord.ApplicationContext,
    type: discord.Option(str,name='tipo', choices=['Anime','Manga'], required=True),
    minimum: discord.Option(int, name='minimo', description="Mínimo de notas", required=True)
):
    #sql = 'SELECT id, title_romaji, mean_hiraeth, number_of_scores FROM media WHERE format="' + type.upper() + '"'
    #list = database.selectall(sql)

    list = dbservice.select('media', ['id', 'title_romaji', 'mean_hiraeth', 'number_of_scores'], '', {'format': type.upper()})

    print(list)

    media_list = []

    for media in list:
        number_of_scores = media[3]

        if number_of_scores >= minimum:
            dict = {'media_id': media[0], 'format': type.upper(), 'title': media[1], 'avg': media[2], 'instances': media[3]}
            print(dict)

            media_list.append(dict)

    media_list = sorted(media_list, key=lambda d: d['avg'], reverse=True)

    if type == 'Anime':
        text = '**Top animes Hiraeth (' + str(minimum) + '+ notas)**\n'

    else:
        text = '**Top mangás Hiraeth (' + str(minimum) + '+ notas)**\n'

    await ctx.respond(text)

    message = await create_placeholder_message(ctx, ctx.interaction.channel.id)

    await generate_top(message, 1, media_list, type, minimum)

async def generate_top(msg, page, list, type, minimum):

    idx = (page * 25) - 24
    
    print("idx")
    print(idx)

    batch = 25

    print('batch:')
    print(batch)

    text = '```'

    for media in list[batch*(page-1):batch*page]:

        avg = str(media['avg'])

        if len(avg) == 3:
            avg += '0'

        if idx < 10:
            text += ' ' + str(idx) + '. ' + avg + ' | ' + str(media['title']) + ' com ' + str(media['instances']) + ' notas dadas\n'
        
        else:
            text += str(idx) + '. ' + avg + ' | ' + str(media['title']) + ' com ' + str(media['instances']) + ' notas dadas\n'
        
        idx += 1

    text += '```'

    print('text:')
    print(text)
    print('length of text:')
    print(len(text))
    
    await msg.edit(text, view=TopPagination(msg, page, list, type, minimum))

@bot.command(name='manual_update_media')
async def manual_update_media(ctx):
    if ctx.author.id in admins:
        print('aqui?')
        await update_media()

async def update_media():
    #users = database.selectall('SELECT link FROM daily_temp', True)

    users = dbservice.select('daily_temp', ['anilist_id'], '')

    users = from_list_of_tuples_to_list(users)

    for id in users:

        exists = dbservice.check_existence('daily_temp2', {'anilist_id': str(id)})
        
        print(id)

        if exists == 0:
            #username = get_anilist_user_from_link(link)
            #print('updating media table using the list of ' + username)
            #list = database.selectall('SELECT media_id FROM user_has_media WHERE anilist_username="' + username + '" GROUP BY media_id', True)

            lista = dbservice.select('user_has_media', ['media_id'], ' GROUP BY media_id', {'anilist_id': id})

            lista = from_list_of_tuples_to_list(lista)

            for media_id in lista:

                title = dbservice.select('user_has_media', ['title'], '', {'media_id': media_id})[0]
                scores = dbservice.select('user_has_media', ['score'], '', {'media_id': media_id})
                format = dbservice.select('user_has_media', ['type'], '', {'media_id': media_id})[0]

                title = title[0]
                format = format[0]

                if type(scores) == list:

                    scores = from_list_of_tuples_to_list(scores)

                else:

                    scores = [scores]

                #print(type(scores))

                #if type(scores) == str:
                #    print('string')
                #    scores = [tuple(scores)]

                #print('scores:')
                #print(scores)

                instances = 0
                total = 0
                valid_scores = []

                for score in scores:

                    #score = score[0]

                    if float(score) > 0:
                        instances += 1
                        total += float(score)
                        valid_scores.append(score)

                if len(valid_scores) >= 2:

                    avg_score = round(total/instances, 2)

                    #print('total:')
                    #print(total)

                    #print('instances:')
                    #print(instances)
                    
                    #print('avg_score')
                    #print(avg_score)

                    #sql = 'INSERT IGNORE INTO media (id, format, url, title_romaji, mean_hiraeth, number_of_scores) VALUES (%s,%s,%s,%s,%s,%s)'
                    #val = (media_id, format, 'https://anilist.co/' + format.lower() + '/' + media_id, title, avg_score, instances)

                    #database.insert(sql,val)

                    exists = dbservice.update('media', ['mean_hiraeth', 'number_of_scores'], [avg_score, instances], {'id': media_id})

                    if exists == 0:

                        dbservice.insert('media', ['id', 'format', 'url', 'title_romaji', 'mean_hiraeth', 'number_of_scores'], (media_id, format, 'https://anilist.co/' + format.lower() + '/' + media_id, title, avg_score, instances), True)

        
        #database.insert('INSERT INTO daily_temp2 (user) VALUES (%s)', (link,))

            dbservice.insert('daily_temp2', ['anilist_id'], (str(id),), True)

            print('lista finalizada e adicionada na tabela daily_temp2')

def from_list_of_tuples_to_list(list):

    new_list = []

    for tuple in list:

        if len(tuple) == 1:

            if tuple[0] != None:

                new_list.append(tuple[0])

        else:

            new_list.append(tuple)

    return new_list

@bot.slash_command(name='anilist_update')
async def anilist_update_command(
    ctx: discord.ApplicationContext,
    link: discord.Option(str, name='link', description="Link do Anilist"),
    user_id: discord.Option(str, name='id', description="ID do Discord")
):
    if ctx.author.id in admins:
        if 'anilist' in link:
            await update_list('ANIME', link, user_id)
            await update_list('MANGA', link, user_id)

async def update_anilists():

    query = dbservice.select('user', ['anilist_id'], '', {'server_active': 1})

    query = from_list_of_tuples_to_list(query)

    print(query)

    total = 0

    for id in query:

        exists = dbservice.check_existence('daily_temp', {'anilist_id': str(id)})

        if exists == 0:

            total += await update_list(id, 'ANIME')
            total += await update_list(id, 'MANGA')

            dbservice.insert('daily_temp', ['anilist_id'], (str(id),), True)
            
            print('lista terminada. ' + get_timestamp())

async def update_list(id, format):

    query = '''query ($userId: Int) {
                  MediaListCollection(userId: $userId, type:''' +  format + ''') {
                    user {
                      name
                    }
                    lists {
                      name
                      isCustomList
                      isSplitCompletedList
                      status
                      entries {
                        media {
                          id
                          type
                          title {
                            romaji
                          }
                        }
                        progress
                        score (format: POINT_10_DECIMAL)
                      }
                    }
                  }
                }
             '''
    
    var = '''{"userId": ''' + str(id) + ''' }'''

    response = anilist.query(query, var)

    response = response.json()

    if 'errors' not in response:

        lists = response['data']['MediaListCollection']['lists']

        idx = 0

        name = response['data']['MediaListCollection']['user']['name']

        print(name + ': ' + format)

        discord_id = dbservice.select('user', ['id'], '', {'anilist_id': str(id)})

        for list in lists:

            if list['isCustomList'] == False:

                #print(list['name'])

                for entry in list['entries']:
                    idx += 1

                    media_id = str(entry['media']['id'])
                    type = entry['media']['type']
                    status = list['status']
                    progress = entry['progress']
                    score = entry['score']
                    title = entry['media']['title']['romaji']

                    val = (discord_id, media_id, id, type, status, progress, score, title)

                    #print("I'm ready to insert the following into the user_has_media table: \n Discord ID: " + discord_id + "")

                    exists = dbservice.update('user_has_media', ['status', 'progress', 'score'], [status, progress, score], {'media_id': media_id, 'anilist_id': id})

                    if exists == 0:
                
                        dbservice.insert('user_has_media', ['user_id', 'media_id', 'anilist_id', 'type', 'status', 'progress', 'score', 'title'], val, True)

                    #print(entry)

        print(idx)

        return idx

    return 0

async def roll_chara(user_name, user_id):

    #chara = database.selectall('SELECT chara_id, name, gender, chara_url, image_url, media_id, media_url, media_title FROM chara ORDER BY RAND() LIMIT 1')

    chara = dbservice.select('chara', ['chara_id', 'favourites', 'name', 'gender', 'chara_url', 'image_url', 'media_id', 'media_url', 'media_title'], ' ORDER BY RAND() LIMIT 1')
    
    print(chara)
        
    #chara = chara[0]
    
    chara_id = chara[0]
    favs = chara[1]
    name = chara[2]
    gender = chara[3]
    chara_url = chara[4]
    image_url = chara[5]
    media_id = chara[6]
    media_title = '[' + chara[8] + '](' + chara[7] + ')'
    
    #exists = database.check_if_exists_two(str(chara[0]), str(user_id), 'chara_id', 'user_id', 'user_has_chara')

    exists = dbservice.check_existence('user_has_chara', {'chara_id': str(chara[0]), 'user_id': str(user_id)})

    if exists == 0:

        #sql = 'INSERT INTO user_has_chara (user_id, chara_id, chara_name, position) VALUES (%s,%s,%s,%s)'
        #val = (user_id, chara_id, name, 9999)

        #database.insert(sql, val)

        dbservice.insert('user_has_chara', ['user_id', 'chara_id', 'chara_name', 'position', 'quantity'], (user_id, chara_id, name, 9999, 1))

        flair = '*new*'

    else:

        flair = ''

        quantity = dbservice.select('user_has_chara', ['quantity'], '', {'chara_id': str(chara[0]), 'user_id': str(user_id)})

        if quantity == None:
            quantity = 1

        dbservice.update('user_has_chara', ['quantity'], [quantity+1], {'chara_id': str(chara[0]), 'user_id': str(user_id)})

    embed = discord.Embed(title=name, url=chara_url)
    if flair != '':
        embed.add_field(name='', value=flair, inline=False)
    embed.add_field(name='', value=media_title)
    embed.set_image(url=image_url)
    embed.set_footer(text='Roll feito por ' + user_name)

    if favs in range(8000,100000):
        delay = 3

    elif favs in range(1000,8000):
        delay = 2

    elif favs in range(200,1000):
        delay = 1

    else:
        delay = 0.5

    if delay >= 1:

        text = '# '

        await asyncio.sleep(1)

        for i in range(delay):
            text += '!'

        await send_message2(text, 1065847698214887496)

        await asyncio.sleep(delay)
    
    else:

        await asyncio.sleep(1)

    await send_embed2(embed, 1065847698214887496)
    
@bot.slash_command(name='editar_coleção')
async def editar_coleção_command(
    ctx: discord.ApplicationContext,
    chara: discord.Option(str, autocomplete=get_collection, name='personagem'),
    position: discord.Option(int, name='posição', description="posição desejada")
):
    user_id = ctx.interaction.user.id

    #database.update('UPDATE user_has_chara SET position=' + str(position) + ' WHERE chara_name="' + chara + '" AND user_id="' + str(user_id) + '"')

    dbservice.update('user_has_chara', ['position'], [position], {'chara_name': chara, 'user_id': user_id})

    await ctx.respond('Posição atualizada')


@bot.command(name='c')
async def c_command(ctx):

    if ctx.channel.id == rolls_channel:

        await ctx.respond('Sua coleção:')

        #characters = database.selectall('SELECT chara_id FROM user_has_chara WHERE user_id="' + str(ctx.author.id) + '" ORDER BY position', True)
        
        msg = await create_placeholder_message(ctx, ctx.interaction.channel.id)

        await generate_collection(msg, ctx.author.id, 1)

async def generate_collection(msg, user_id, page):

    characters = dbservice.select('user_has_chara', ['chara_id'], ' ORDER BY position', {'user_id': str(user_id)})
    
    print(characters)

    #characters = from_list_of_tuples_to_list(characters)

    batch = 25

    indice = (page * 25) - 24

    text = ''

    print('page')
    print(page)

    print('indice:')
    print(indice)

    for chara in characters[batch*(page-1):batch*page]:

        print(indice)

        print('chara')
        print(chara)

        chara = chara[0]
        
        #chara_info = database.selectall('SELECT name, chara_url FROM chara WHERE chara_id=' + str(chara))[0]

        chara_info = dbservice.select('chara', ['name', 'chara_url'], '', {'chara_id': str(chara)})

        print(chara_info)

        #position = database.select('SELECT position FROM user_has_chara WHERE chara_id=' + str(chara) + ' AND user_id="' + str(user_id) + '"')

        position = dbservice.select('user_has_chara', ['position'], '', {'chara_id': str(chara), 'user_id': str(user_id)})
          
        text += str(chara_info[0]) + ' | Posição: ' + str(position) + '\n'
        indice += 1
    
    await msg.edit(text, view=CollectionPagination(msg, user_id, page))
    
@tasks.loop(seconds=1)
async def make_rolls():

    smaller_id = dbservice.select('rolls', ['id'], 'ORDER BY id ASC LIMIT 1')
    
    if smaller_id != []:

        print(smaller_id)

        roll_info = dbservice.select('rolls', ['user', 'quantity'], '', {'id': smaller_id})

        print(roll_info)

        name = roll_info[0]
        user_id = dbservice.select('user', ['id'], '', {'name': name})
        rolls = roll_info[1]

        text = f'Trazendo {str(rolls)} rolls para {name})'

        print(text)
        await send_message2(text, rolls_channel)
        await asyncio.sleep(1)

        for i in range(rolls):

            await roll_chara(name, user_id)

        await asyncio.sleep(2)

        dbservice.delete('rolls', {'id': smaller_id})

        print('deleted ' + str(smaller_id))

@bot.slash_command(name='iniciar_oferta')
async def iniciar_oferta_command(
    ctx: discord.ApplicationContext,
    target: discord.Option(str, autocomplete=get_members_names2, name='membro')
):

    if ctx.channel.id == rolls_channel:
    
        from_id = ctx.author.id
        to_id = dbservice.select('user', ['id'], '', {'name': target})
    
        id = dbservice.insert('chara_ofertas', ['from_id', 'to_id'], [from_id, to_id])

        await ctx.respond(f'Uma janela de troca com {target} foi aberta. O ID dessa oferta é {str(id)}. Utilize o /ofertar e insire esse ID para realizar uma oferta.')

@bot.slash_command(name='ofertar')
async def ofertar_command(
    ctx: discord.ApplicationContext,
    id: discord.Option(int, name='id'),
    own_chara: discord.Option(str, autocomplete=get_collection, name='seu_chara'),
    own_quantity: discord.Option(int, min_value=1, name='sua_quantidade'),
    target_chara: discord.Option(str, autocomplete=get_chara, name='chara_dele'),
    target_quantity: discord.Option(int, min_value=1, name='quantidade_dele')
):
    ... # needs to validate whether both offer and recipient
    ... # have enough copies of the related characters

    user_id = dbservice.select('chara_ofertas', ['to_id'], '', {'id': id})

    columns = ['offering', 'offer_quantity', 'receiving', 'receive_quantity']
    values = [own_chara, own_quantity, target_chara, target_quantity]

    dbservice.update('chara_ofertas', columns, values, {'id': id})

    await ctx.respond(f'Oferta realizada. O usuário <@' + str(user_id) + '> foi notificado. Não foi?')

@bot.slash_command(name='pesquisar_chara')
async def pesquisar_chara_command(
    ctx: discord.ApplicationContext,
    target: discord.Option(str, autocomplete=get_chara, name='chara')
):
    await ctx.respond('Buscando o personagem...')

    result = dbservice.select('user_has_chara', ['user_id', 'quantity'], ' ORDER BY quantity DESC', {'chara_name': target})

    print(result)



    #result = from_list_of_tuples_to_list(result)

    text = '**' + target + '**\n'
    text += '```Usuário:            Cópias:\n\n'
    
    if type(result) == tuple:
        result = [result]

    for user in result:

        user_name = dbservice.select('user', ['name'], '', {'id': user[0]})
        
        quantity = user[1]

        if quantity == None:
            quantity = 1

        text += user_name + '            ' + str(quantity) + '\n'
        
    text += '```'

    await send_message2(text, rolls_channel)

@bot.command(name='ofertas_enviadas')
async def ofertas_enviadas_command(ctx):

    offers = dbservice.select('chara_ofertas', [], 'ORDER BY id ASC', {'from_id': ctx.author.id})

    print(offers)

    if offers != []:

        text = '**Ofertas enviadas:**\n\n```'
        #text += 'Ofereci para       Personagem  #       Quero receber  # \n\n'

        for offer in offers:

            to_id = offer[2]

            user_name = dbservice.select('user', ['name'], '', {'id': to_id})

            my_chara = offer[3]
                
            my_quantity = offer[4]

            their_chara = offer[5]
            
            their_quantity = offer[6]

            print(their_quantity)
            print(type(their_quantity))
            print(str(their_quantity))

            text += f'Oferta ID {str(offer[0])} para {user_name}\n'
            text += f'Meu:     {str(my_quantity)}x - {my_chara}\n'
            text += f'Dele(a): {str(their_quantity)}x - {their_chara}\n\n'
            
        text += '```'

        await send_message2(text, rolls_channel)

    ...


@bot.command(name='ofertas_recebidas')
async def ofertas_recebidas_command(ctx):

    offers = dbservice.select('chara_ofertas', [], 'ORDER BY id ASC', {'to_id': ctx.author.id})
    
    print(offers)

    if offers != []:

        text = '**Ofertas recebidas:**\n```'

        for offer in offers:

            from_id = offer[1]

            user_name = dbservice.select('user', ['name'], '', {'id': from_id})

            their_chara = offer[3]
                
            their_quantity = offer[4]

            my_chara = offer[5]
            
            my_quantity = offer[6]

            text += f'Oferta ID {str(offer[0])} de {user_name}\n'
            text += f'Meu:     {str(my_quantity)}x - {my_chara}\n'
            text += f'Dele(a): {str(their_quantity)}x - {their_chara}\n\n'
        
        text += '```'

        await send_message2(text, rolls_channel)

    ...

@bot.slash_command(name='responder_oferta')
async def responder_oferta_command(
    ctx: discord.ApplicationContext,
    id: discord.Option(int, name='id'),
    decision: discord.Option(str, choices=['Aceitar','Recusar'])
):
    print(decision)

    trade = dbservice.select('chara_ofertas', [], '', {'id': id})
    
    if str(ctx.author.id) == trade[2]:

        match decision:
        
            case 'Aceitar':

                ...

                dbservice.delete('chara_ofertas', {'id': id})

                await ctx.respond(f'Oferta de ID {str(id)} recusada.')

            case 'Recusar':

                dbservice.delete('chara_ofertas', {'id': id})

                await ctx.respond(f'Oferta de ID {str(id)} recusada.')

    else:

        await ctx.respond('Você não pode aceitar ou recusar essa oferta pois ela não é direcionada par você.')

@tasks.loop(seconds=60)
async def check_activities():

    print('começando a checar atividades')
    print(get_timestamp())

    anilist_ids = dbservice.select('user', ['anilist_id'], ' WHERE anilist_id IS NOT NULL')

    anilist_ids = from_list_of_tuples_to_list(anilist_ids)

    query = '''query ($page: Int, $userId: Int, $createdAt_greater: Int) {
                  Page(page: $page, perPage: 50) {
                    pageInfo {
                      total
                      currentPage
                      lastPage
                      hasNextPage
                      perPage
                    }
                    activities(userId: $userId, type: MEDIA_LIST, sort: ID, createdAt_greater: $createdAt_greater) {
                      ... on ListActivity {
                        id
                        status
                        progress
                        media {
                          id
                          type
                          episodes
                          siteUrl
                          title {
                            romaji
                          }
                        }
                        createdAt
                      }
                    }
                  }
                }
                '''

    for id in anilist_ids:

        user_name = dbservice.select('user', ['name'], '', {'anilist_id': str(id)})

        last_update_time = dbservice.select('user', ['last_list_update'], '', {'anilist_id': str(id)})
        
        #last_update_time = 1685009000

        var = '''{ "userId": ''' + str(id) + ''', "createdAt_greater": ''' + str(last_update_time) + ''', "page": 1 }'''

        new_activities = anilist.query(query, var)

        new_activities = new_activities.json()

        now = int(time.time())

        print(new_activities)

        for act in new_activities['data']['Page']['activities']:

            embed = discord.Embed()

            print(act)

            _status = act['status']
            progress = act['progress']
            episodes = act['media']['episodes']
            title = act['media']['title']['romaji']
            media_id = act['media']['id']
            createdAt = act['createdAt']
            url = act['media']['siteUrl']

            match _status:

                case 'watched episode' | 'read chapter':
                    status = 'CURRENT'

                case 'dropped':
                    status = 'DROPPED'

                case 'completed':
                    status = 'COMPLETED'

                case 'paused reading' | 'paused watching':
                    status = 'PAUSED'

                case 'plans to watch' | 'plans to read':
                    status = 'PLANNING'
                 
            print('progress:')
            print(progress)

            if progress != None:

                if '-' in progress:

                    starting, progress = progress.split('-')

                    progress = progress.lstrip(' ')

            rt = from_epoch_to_rt(createdAt)

            exists = dbservice.check_existence('user_has_media', {'media_id': media_id, 'anilist_id': id})

            if exists == 1:

                print('existe')

                if status == 'CURRENT':
               
                    print(f'{user_name} {_status} {progress} of {title} {str(rt)}')

                    previous = dbservice.select('user_has_media', ['progress'], '', {'anilist_id': id, 'media_id': media_id})

                    print('previous var:')
                    print(previous)

                    print('previous progress: ' + str(previous))

                    diff = int(progress) - int(previous)

                    print('diff: ' + str(diff))

                    dbservice.update('user_has_media', ['progress', 'status'], [progress, status], {'anilist_id': id, 'media_id': media_id})
                    
                    embed.add_field(name='', value=f'{user_name} {_status} {progress} of [' + title + '](' + url + ')' + f' at {str(rt)}')
                    await send_embed2(embed, 1110011052025983047)

                elif status == 'COMPLETED':

                    print(f'{user_name} {_status} {title} {str(rt)}')
                
                    dbservice.update('user_has_media', ['status', 'progress'], ['COMPLETED', episodes], {'anilist_id': id, 'media_id': media_id})
                
                    embed.add_field(name='', value=f'{user_name} {_status} [' + title + '](' + url + ')' + f' at {str(rt)}')
                    await send_embed2(embed, 1110011052025983047)
                
                elif status in ['DROPPED', 'PAUSED', 'PLANNING']:

                    print(f'{user_name} {_status} {title} {str(rt)}')

                    dbservice.update('user_has_media', ['status'], [status], {'anilist_id': id, 'media_id': media_id})
                
                    embed.add_field(name='', value=f'{user_name} {_status} [' + title + '](' + url + ')' + f' at {str(rt)}')
                    await send_embed2(embed, 1110011052025983047)

            else:

                print('não existe')

                user_id = dbservice.select('user', ['id'], '', {'anilist_id': id})

                format = act['media']['type']

                if status == 'COMPLETED':
                    progress = episodes

                if progress == None:

                    val = (user_id, media_id, id, format, status, title)
                    dbservice.insert('user_has_media', ['user_id', 'media_id', 'anilist_id', 'type', 'status', 'title'], val, True)
                    embed.add_field(name='', value=f'{user_name} {_status} [' + title + '](' + url + ')' + f' at {str(rt)}')
                
                else:

                    val = (user_id, media_id, id, format, status, progress, title)
                    dbservice.insert('user_has_media', ['user_id', 'media_id', 'anilist_id', 'type', 'status', 'progress', 'title'], val, True)
                    embed.add_field(name='', value=f'{user_name} {_status} {progress} of [' + title + '](' + url + ')' + f' at {str(rt)}')
                
                await send_embed2(embed, 1110011052025983047)


        dbservice.update('user', ['last_list_update'], [now], {'anilist_id': id})

    print(get_timestamp())

async def clean_dailies():

    dbservice.truncate('daily_temp')
    dbservice.truncate('daily_temp2')

    dbservice.update('dailies', ['daily', 'is_done'], ['anilist_update', 0], {'daily':'anilist_update'})
    dbservice.update('dailies', ['daily', 'is_done'], ['media_update', 0], {'daily':'media_update'})
    
    print('daily tables limpas ' + get_timestamp())
    
async def dailies():

    await update_anilists()
    dbservice.update('dailies', ['daily', 'is_done'], ['anilist_update', 1], {'daily':'anilist_update'})
    
    await update_media()
    dbservice.update('dailies', ['daily', 'is_done'], ['media_update', 1], {'daily':'media_update'})
    
    print('daily finalizada ' + get_timestamp())
    
# Auxiliar command
@bot.command(name='aux')
async def aux_command(ctx):

    if ctx.author.id in admins:
        
        #for i in range(477,500):

        #    page = i

        #    query = '''query ($page: Int) {
        #                  Page (page: $page, perPage: 50) {
        #                    pageInfo {
        #                      total
        #                      currentPage
        #                      lastPage
        #                      hasNextPage
        #                      perPage
        #                    }
        #                    characters (sort: FAVOURITES_DESC) {
        #                      id
        #                      favourites
        #                      name {
        #                        userPreferred
        #                      }
        #                      gender
        #                      siteUrl
        #                      image {
        #                        large
        #                      }
        #                      media {
        #                        nodes {
        #                          id
        #                          siteUrl
        #                          title {
        #                            romaji
        #                          }
        #                        }
        #                      }
        #                    }
        #                  }
        #                }
        #                '''


        #    var = '''{ "page": ''' + str(page) + ''' }'''

        #    response = anilist.query(query, var)

        #    response = response.json()

        #    #print(response)

        #    time.sleep(1)

        #    characters = response['data']['Page']['characters']

        #    print(f'{str(page)}: {str(len(characters))} added.')

        #    for chara in characters:

        #        chara_id = chara['id']
        #        favs = chara['favourites']
        #        chara_name = chara['name']['userPreferred']
        #        gender = chara['gender']
        #        chara_url = chara['siteUrl']
        #        chara_img = chara['image']['large']

        #        #print(chara_url)

        #        if chara_id == 183729:
        #            continue

        #        media = chara['media']['nodes'][0]

        #        media_id = media['id']
        #        media_url = media['siteUrl']
        #        media_title = media['title']['romaji']
            
        #        columns = ['chara_id', 'favourites', 'name','gender','chara_url','image_url','media_id','media_url','media_title']
        #        val = (chara_id, favs, chara_name, gender, chara_url, chara_img, media_id, media_url, media_title)

        #        dbservice.insert('chara', columns, val, True)

        print(get_timestamp() + ': Done')
    
config = configparser.RawConfigParser()
config.read('app.properties')
token = config.get('Discord', 'token')
bot.run(token)
