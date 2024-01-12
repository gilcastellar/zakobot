####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################

# HOW TO SOLVE THE MODULE DISCORD HAS NO ATTRIBUTE 'BOT'
# GO TO SPARKED HOST > STARTUP > PYTHON PACKAGES > INPUT A OLDER VERSION OF PYCORD LIKE py-cord==2.4.0

####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################


from faulthandler import dump_traceback
from html.entities import name2codepoint
from lib2to3.pgen2 import grammar
from pydoc import describe
from random import choice,choices, shuffle, randint
import random
from re import T, U, X
from xml.dom.expatbuilder import theDOMImplementation

import discord
from discord.ext import tasks
from discord.ext import commands
import configparser

# from discord.ext.commands.flags import F
# from discord.utils import P
import database
import dbservice
import anilist
import json
import time
import datetime
from zoneinfo import ZoneInfo
import asyncio
import re
from math import ceil, e, floor


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = discord.Bot(intents=intents)

admins = [906937520254758973,628466603486478336,1050904689685831760,98410347597139968]

test = 'eita'
key = False
rolls_channel = 1107765031245988060

# Edit profile modal
class EditarPerfilModal(discord.ui.Modal):
    def __init__(self, user_id, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
        list_and_obs = dbservice.select('user', ['anime_list','obs'], '', {'id':user_id})

        _list = list_and_obs[0]
        _obs = list_and_obs[1]

        self.add_item(discord.ui.InputText(label="Link do perfil do MAL/Anilist (opcional)", required=False, value=_list))
        self.add_item(discord.ui.InputText(label="Suas observações", style=discord.InputTextStyle.long, required=False, value=_obs, max_length=900))

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
    def __init__(self, msg, page, last_page, list, type, min):
        super().__init__()
        #self.ctx = ctx
        self.msg = msg
        self.page = page
        self.last_page = last_page
        self.list = list
        self.type = type
        self.min = min

        
    @discord.ui.button(label="<<", row=0, style=discord.ButtonStyle.primary)
    async def first_button_callback(self, button, interaction):
        if self.page > 1:
            self.page -= 1
        await generate_top(self.msg, self.page, self.last_page, self.list, self.type, self.min)
        await interaction.response.send_message('')

    @discord.ui.button(label=">>", row=0, style=discord.ButtonStyle.primary)
    async def second_button_callback(self, button, interaction):
        if self.page < self.last_page:
            self.page += 1
        await generate_top(self.msg, self.page, self.last_page, self.list, self.type, self.min)
        await interaction.response.send_message('')

class QuestBoardPagination(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
    def __init__(self, msg, page, last_page, data):
        super().__init__()
        #self.ctx = ctx
        self.msg = msg
        self.page = page
        self.last_page = last_page
        self.data = data

    @discord.ui.button(label="<<", row=0, style=discord.ButtonStyle.primary)
    async def first_button_callback(self, button, interaction):
        if self.page > 1:
            self.page -= 1
        await gerar_quest_board(self.msg, self.page, self.last_page, self.data)
        await interaction.response.send_message('')

    @discord.ui.button(label=">>", row=0, style=discord.ButtonStyle.primary)
    async def second_button_callback(self, button, interaction):
        if self.page < self.last_page:
            self.page += 1
        await gerar_quest_board(self.msg, self.page, self.last_page, self.data)
        await interaction.response.send_message('')
        
class CollectionPagination(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
    def __init__(self, msg, user_id, page, last_page):
        super().__init__()
        #self.ctx = ctx
        self.msg = msg
        self.user_id = user_id
        self.page = page
        self.last_page = last_page

    @discord.ui.button(label="<<", row=0, style=discord.ButtonStyle.primary)
    async def first_button_callback(self, button, interaction):
        if self.page > 1:
            self.page -= 1
        await generate_collection(self.msg, self.user_id, self.page, self.last_page)
        await interaction.response.send_message('')

    @discord.ui.button(label=">>", row=0, style=discord.ButtonStyle.primary)
    async def second_button_callback(self, button, interaction):
        if self.page < self.last_page:
            self.page += 1
        await generate_collection(self.msg, self.user_id, self.page, self.last_page)
        await interaction.response.send_message('')

@bot.event
async def on_ready():
    print(f'{get_timestamp()}: Started')
    
    # check_quests.start()

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

        case ";registro" | ';cadastro' | ';registrar' | ';cadastrar':

            await registro_command(message)

        case ";ajuda" | ";comandos" | ";help" | ";commands":

            await send_embed2(help_embed(), message.channel.id)

        case ";r" | ';roll':

            if message.channel.id in [rolls_channel]:

                roll_cost = dbservice.select('values_chart', ['value_value'], '', {'value_name': 'roll'})

                if len(msg) > 1:
                
                    if int(msg[1]) >= 10:
                        rolls = 10

                    elif int(msg[1]) in range(1,10):
                        rolls = int(msg[1])

                else:

                    rolls = 1

                wallet = dbservice.select('user', ['zakoleta'], '', {'id': message.author.id})

                total_cost = roll_cost * rolls

                if wallet < total_cost:
                    
                    send_message2('Você não tem Zakoleta o suficiente para realizar esse roll.')

                else:
                    ...
                    #add_zakoleta(str(message.author.id), total_cost, f' -{str(total_cost)} por rodar {str(rolls)} vezes.', 'sub')
                    
                user_name = dbservice.select('user', ['name'], '', {'id': message.author.id})

                roll_id = dbservice.insert('rolls', ['user', 'quantity'], [user_name, rolls])
            
        case ';enviadas':

            await ofertas_enviadas_command(message)

        case ';recebidas':

            await ofertas_recebidas_command(message)

    rag_commands = ['classe', 'stat', 'skill']

    classe1 = ['super aprendiz', 'espadachim', 'gatuno', 'mago', 'noviço', 'mercador', 'arqueiro', 'taekwon', 'justiceiro', 'ninja']

    stats = ['força', 'agilidade', 'vitalidade', 'inteligencia', 'destreza', 'sorte']

    if command in rag_commands:

        if message.channel.id == 1151990929864007680:

            if command == 'classe':

                result = choice(classe1)

                print(random.randint(1,7))

            elif command == 'stat':

                result = choice(stats)

                print(random.randint(1,7))

            elif command == 'skill':

                rag_col = random.randint(1,7)

                rag_fil = random.randint(1,8)

                result = 'coluna ' + str(rag_col) + ' e fileira ' + str(rag_fil)

                print(rag_col)
                print(rag_fil)
                print(result)

            await send_message2(result, 1151990929864007680)

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
async def send_message2(text, channel_id, silent=False):

    channel = bot.get_channel(channel_id)
    if False:
        message = await channel.send(text)
    else:
        message = await channel.send(text, silent=True)

    return message

# Send embed
async def send_embed(ctx, embed):

    await ctx.send(embed=embed)

# Send embed
async def send_embed2(embed, channel_id):
    
    channel = bot.get_channel(channel_id)
    await channel.send(embed=embed)

def print_use(ctx, extra):

    print(f'{get_timestamp()}: {ctx.author.name} used {extra}.')

def get_value(column):

    return dbservice.select('values', [column], '')

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

# Get active members without the user own's name
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

    id_collection = dbservice.select('user_has_chara', ['chara_id'], '', {'user_id': str(user_id)})
    name_collection = dbservice.select('user_has_chara', ['chara_name'], '', {'user_id': str(user_id)})
    
    id_collection = from_list_of_tuples_to_list(id_collection)
    name_collection = from_list_of_tuples_to_list(name_collection)

    repeated = []

    for idx, chara in enumerate(name_collection):

        title_and_id = dbservice.select('chara', ['media_title', 'chara_id'], '', {'chara_id': id_collection[idx]})

        name_collection[idx] = chara + ' (' + title_and_id[0] + ') ID (' + str(title_and_id[1]) + ')'

    return [name for name in name_collection if ctx.value.lower() in name.lower()]

async def get_chara(ctx):

    collection = dbservice.select('chara', ['name', 'media_title', 'chara_id'], '')

    print(collection)

    name_collection = []

    for idx, item in enumerate(collection):

        name_collection.append(item[0] + ' (' + item[1] + ') ID (' + str(item[2]) + ')')

    return [name for name in name_collection if ctx.value.lower() in name.lower()]

#@bot.command(name='registro')
async def registro_command(message):

    #print message.author.id

    user_id = message.author.id
            
    exists = dbservice.check_existence('user', {'id': str(user_id)})

    if exists == 0:

        guild = 1059298932825538661
        name = message.author.name
        #database.insert('INSERT INTO user (id, id_guild, name) VALUES (%s,%s,%s)',(user_id, guild, name))

        dbservice.insert('user', ['id', 'id_guild', 'name'], (user_id, guild, name))

        await send_message2(f"Seja bem-vindo(a) à Hiraeth, {name}!", message.channel.id)

    else:

        await send_message2('Você já está cadastrado!', message.channel.id)

@bot.command(name='editar_perfil')
async def editar_perfil_command(ctx):
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
    # if zakoletas > 0:
    #     embed.add_field(name="Ƶ " + str(zakoletas), value="", inline=True)
    #     embed.add_field(name=" ­­", value=" ", inline=True)
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

@bot.slash_command(name='sorteio', description='UTILIZAR NO CANAL #ROLETA-PLACAR')
async def sorteio_command(
    ctx: discord.ApplicationContext,
    name: discord.Option(str, name='nome'),
    delay: discord.Option(int, name='delay'),
    real: discord.Option(str, name='real', choices=['True','False'])
):
    
    if ctx.author.id in admins:

        draw_channel = 1065408178923245589

        draw_list = dbservice.select('user', ['id', 'gives', 'receives'], '', {'active': 1})

        print(draw_list)

        draw_list = merge_id_with_type(draw_list)

        id = get_last_roulette_id()

        last_two_draws = get_last_draws(id)

        result = await roulette_shuffle(draw_list, id, last_two_draws)
        print(type(result))

        result_as_str = draw_to_str(result)
        print(result_as_str)
        print(type(result_as_str))

        pairs = generate_pairs(result)

        print('chamando o insert')

        if real == True:
            dbservice.insert('roleta', ['id', 'name', 'draw', 'status'], (id+1, name, result_as_str, 'ongoing'))
        
        index = 1

        for pair in pairs:

            time.sleep(delay)

            giver, receiver = pair.split(',')

            giver = await fetch_user(giver)
            receiver = await fetch_user(receiver)

            if real == 'True':

                text = giver.display_name + ' -> ' + receiver.display_name
            
                message = await send_message(ctx, text) # REALIZA O SORTEIO AO VIVO NO CHAT E RETORNA O OBJETO DA MENSAGEM
            
            if real == True:
                dbservice.insert('user_has_roleta', ['idx', 'id_receiver', 'id_giver', 'id_roleta', 'status'], (index, str(receiver.id), str(giver.id), id+1, 'ongoing'))
            
            index += 1

        board_message = await create_placeholder_message(ctx, 1077070205987082281)

        print(board_message)
        
        board_message_id = board_message.id
        print('board_message_id:')
        print(board_message_id)

        board_message_channel_id = board_message.channel.id
        print('board_message_channel_id:')
        print(board_message_channel_id)

        dbservice.update('roleta', ['id_message', 'id_channel'], [board_message_id, board_message_channel_id], {'id': id+1})

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

    #sql = 'SELECT id FROM roleta'
    #result = database.selectall(sql, True)

    result = dbservice.select('roleta', ['id'], '')

    print(result)

    result = from_list_of_tuples_to_list(result)

    last_roulette_id = max(result)

    print(last_roulette_id)

    return last_roulette_id

# Roulette shuffle
async def roulette_shuffle(list, roulette_id, last_two_draws):

    while True:

        shuffle(list)

        is_valid = await roulette_validator(list, last_two_draws)

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
async def roulette_validator(list, last_two_draws):

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
        #print('giver:')
        #print(giver)
        receiver = receiver.split('_')
        #print('receiver:')
        #print(receiver)

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

    #roleta_id = roleta_id[0]

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

    print(board_info)

    print('starting to generate board')
    print('roleta_id:')
    print(roleta_id)

    await generate_board(board_info, message, roleta_id)
    
# Board indications manager
def board_indications_manager(receiver_id, roleta_id):

    media_text = ''

    #medias = database.select('SELECT media_name FROM user_has_roleta WHERE id_receiver="' + receiver_id + '" AND id_roleta=' + str(roleta_id))
    
    medias = dbservice.select('user_has_roleta', ['media_name'], '', {'id_receiver': receiver_id, 'id_roleta': str(roleta_id)})

    print('medias:')
    print(medias)

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
    print_use(ctx, '/indicar')

    print(media1)
    print(media2)
    print(media3)

    if not media1.startswith('https://anilist.co'):

        await ctx.respond('Você inseriu algo errado. Cada indicação deve conter apenas um link do Anilist.')
    
    elif media2 != None:

        if not media2.startswith('https://anilist.co'):

            await ctx.respond('Você inseriu algo errado. Cada indicação deve conter apenas um link do Anilist.')
    
    elif media3 != None:

        if not media3.startswith('https://anilist.co'):

            await ctx.respond('Você inseriu algo errado. Cada indicação deve conter apenas um link do Anilist.')
    
    if media1 != None:

        print('ok')

        await ctx.respond(f"Obrigado pela indicação!")

        roletas = database.selectall('SELECT id FROM roleta', True)

        roletas = dbservice.select('roleta', ['id'], '')

        roleta_atual = max(roletas)[0]

        print(roleta_atual)

        sql = 'SELECT id_giver FROM user_has_roleta WHERE id_roleta="' + str(roleta_atual) + '"'
        allowed_givers = database.selectall(sql, True)

        allowed_givers = dbservice.select('user_has_roleta', ['id_giver'], '', {'id_roleta': str(roleta_atual)})

        allowed_givers = from_list_of_tuples_to_list(allowed_givers)

        medias = ''
        medias += media1

        if media2 != None:

            medias += ',' + media2

        if media3  != None:

            medias += ',' + media3

        if str(ctx.author.id) in allowed_givers:

            sql = 'UPDATE user_has_roleta SET received_rec="' + medias + '" WHERE id_giver="' + str(ctx.author.id) + '" AND id_roleta=' + str(roleta_atual)
            database.update(sql)

            dbservice.update('user_has_roleta', ['received_rec'], [medias], {'id_giver':ctx.author.id, 'id_roleta':roleta_atual})

        list = []

        if ',' in medias:
            list = medias.split(',')
        else:
            list.append(medias)

        print(list)

        title = ''

        for media in list:
            print('adding media_name to table user_has_roleta:')
            print(media)

            type, id = get_type_and_id_from_anilist_link(media)

            if type == 'anime':

                response = anilist.query_anime_id(id)
                
            else:

                response = anilist.query_manga_id(id)

            media_obj = response.json()
            title += media_obj['data']['Media']['title']['romaji'] + '|'

            print(title)

        title = title.rstrip('|')

        print(title)

        is_new = dbservice.select('user_has_roleta', ['media_name'], '', {'id_giver': ctx.author.id, 'id_roleta': roleta_atual})
        
        if is_new == None:

            reward = dbservice.select('values_chart', ['value_value'], '', {'value_name': 'roleta_indicar'})

            add_zakoleta(ctx.author.id, reward, f' +{str(reward)} pela participação na roleta de ' + ctx.author.name, 'add')
    
        dbservice.update('user_has_roleta', ['media_name'], [title], {'id_giver': ctx.author.id, 'id_roleta': roleta_atual})
        
        await board_update(roleta_atual)

@bot.slash_command(name='terminar')
async def terminar_command(
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

        reward = dbservice.select('values_chart', ['value_value'], '', {'value_name': 'roleta_terminei'})

        add_zakoleta(ctx.author.id, reward, f' +{str(reward)} por terminar suas indicações de ' + name, 'add')
        await ctx.send(f'Você recebeu Ƶ {str(reward)} por finalizar sua indicação.')

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

        reward = dbservice.select('values_chart', ['value_value'], '', {'value_name': 'roleta_abandonei'})

        add_zakoleta(ctx.author.id, reward, f' +{str(reward)} por abandonar suas indicações de ' + name, 'add')
        await ctx.send(f'Você recebeu Ƶ {str(reward)} por abandonar manualmente sua indicação.')

    #sql = 'UPDATE user_has_roleta SET status="abandoned" WHERE id_roleta=' + str(roleta_id) + ' AND id_receiver="' + str(ctx.author.id) + '"'
    #database.update(sql)

    dbservice.update('user_has_roleta', ['status'], ['abandoned'], {'id_roleta':roleta_id, 'id_receiver': ctx.author.id})

    await board_update(roleta_id)

@bot.slash_command(name='placar_roleta')
async def placar_roleta_command(
    ctx: discord.ApplicationContext,
    roleta: discord.Option(str, name='roleta', description='Escolha a roleta que quer visualizar', autocomplete=get_roletas, required=True)
):
    #await ctx.respond("")

    print(ctx.interaction.channel.id)

    message = await create_placeholder_message(ctx, ctx.interaction.channel.id)
    
    roleta_id = dbservice.select('roleta', ['id'], '', {'name': roleta})

    print(roleta_id)

    await board_update(roleta_id, message)
    
# Help embed
def help_embed():

    embed = discord.Embed(title='Lista de comandos')
    embed.add_field(name='Comandos para participar da roleta:',value='',inline=False)
    embed.add_field(name=';registro',value='Se nunca participou de uma roleta, utilize esse comando para se cadastrar',inline=False)
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

#@bot.command(name='comandos')
#async def comandos_command(ctx):
#    await ctx.respond(embed=help_embed())

#@bot.command(name='ajuda')
#async def ajuda_command(ctx):
#    await ctx.respond(embed=help_embed())

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
def add_zakoleta(user_id, quantity, text, type):
    
    datetime = get_timestamp()

    full_text = ',' + datetime + text

    dbservice.update_zakoleta('user', quantity, full_text, user_id, type)

    print(full_text)

# Gets user score average
async def get_user_avg(user):

    both_avg = []

    #sql = 'SELECT score FROM user_has_roleta WHERE id_receiver="' + str(user.id) + '" ORDER BY id_roleta'
    #scores_given = database.selectall(sql, True)

    scores_given = dbservice.select('user_has_roleta', ['score'], 'ORDER BY id_roleta', {'id_receiver': str(user.id)})

    if scores_given == None:
        scores_given = []

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
    
    if scores_received == None:
        scores_received = []

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

    print('both_avg:')
    print(both_avg)

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

        if pendencies != None:

            pendencies = [pendencies]
            
    print(pendencies)

    if pendencies != None:

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

    else:

        pendencies_text = ''

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

            random_media = dbservice.select('user', ['random_anime'], '', {'id': ctx.author.id})

            if random_media != 0:

                anime_url = 'https://anilist.co/anime/' + str(random_media)

                exists = dbservice.check_existence('media', {'url': anime_url})

                if exists == 1:

                    media_title = dbservice.select('media', ['title_romaji'], '', {'url': anime_url})

                else:

                    result = anilist.query_anime_id(str(random_media))

                    result = result.json()

                    media_title = result['data']['Media']['title']['romaji']

                await ctx.send(f'Na última vez que pediu uma indicação, recomendei {media_title} mas pelo que vi você ainda não assistiu ao episódio. Caso tenha visto, utilize o comando /vi ou /li. Caso queira uma nova indicação, utilize o comando "/utilidades resetar" e resete a opção anime por 3 zakoletas.')

            link = dbservice.select('user', ['anime_list'], '', {'id': str(ctx.author.id)})
            
            user_name = get_anilist_user_from_link(link)

            anime, anime_link = anime_picker(ctx, user_name, ['CURRENT', 'REPEATING'])

            await ctx.send('Que tal assistir um episódio de ' + anime + '? Link: ' + anime_link)

        case 'Escolha uma obra do meu Planning To Watch':
            
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
  format: discord.Option(str, name='tipo', choices=['Anime', 'Manga'], description="Em caso de homonimos, diferencie o tipo da obra aqui")
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

    await generate_top(message, 1, 0, media_list, type, minimum)

async def generate_top(msg, page, last_page, list, type, minimum):

    print('len(list)')
    print(len(list))

    print(len(list) / 25)
    print(round(len(list) / 25))

    idx = (page * 25) - 24
    
    #print("idx")
    #print(idx)

    batch = 25

    #print('batch:')
    #print(batch)

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

    last_page = ceil(len(list) / 25)

    #print('last_page')
    #print(last_page)

    #print('text:')
    #print(text)
    #print('length of text:')
    #print(len(text))

    if page <= last_page:
    
        await msg.edit(text, view=TopPagination(msg, page, last_page, list, type, minimum))

#@bot.command(name='manual_update_media')
#async def manual_update_media(ctx):
#    if ctx.author.id in admins:
#        print('aqui?')
#        await update_media()

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

#@bot.slash_command(name='anilist_update')
#async def anilist_update_command(
#    ctx: discord.ApplicationContext,
#    link: discord.Option(str, name='link', description="Link do Anilist"),
#    user_id: discord.Option(str, name='id', description="ID do Discord")
#):
#    if ctx.author.id in admins:
#        if 'anilist' in link:
#            await update_list('ANIME', link, user_id)
#            await update_list('MANGA', link, user_id)

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


@bot.slash_command(name='coleção')
async def coleção(
    ctx: discord.ApplicationContext,
    target: discord.Option(str, autocomplete=get_members_names2, required=False)
):

    if ctx.channel.id == rolls_channel:

        if target != None:

            await ctx.respond(f'Coleção de {target}')

            user_id = int(dbservice.select('user', ['id'], '', {'name': target}))

        else:

            await ctx.respond('Sua coleção:')

            user_id = ctx.author.id

        #characters = database.selectall('SELECT chara_id FROM user_has_chara WHERE user_id="' + str(ctx.author.id) + '" ORDER BY position', True)
        
        msg = await create_placeholder_message(ctx, ctx.interaction.channel.id)

        await generate_collection(msg, user_id, 1, 0)

async def generate_collection(msg, user_id, page, last_page):

    characters = dbservice.select('user_has_chara', ['chara_id'], ' ORDER BY position', {'user_id': str(user_id)})
    
    print(characters)

    #characters = from_list_of_tuples_to_list(characters)

    batch = 10

    indice = (page * batch) - (batch - 1)

    text = '```Personagem                                                                                        #     Pos.\n\n'

    print('page')
    print(page)

    print('indice:')
    print(indice)

    last_page = ceil(len(characters) / batch)

    for chara in characters[batch*(page-1):batch*page]:

        print(indice)

        print('chara')
        print(chara)

        chara = chara[0]
        
        #chara_info = database.selectall('SELECT name, chara_url FROM chara WHERE chara_id=' + str(chara))[0]

        chara_info = dbservice.select('chara', ['name', 'media_title'], '', {'chara_id': str(chara)})

        print(chara_info)

        copies = dbservice.select('user_has_chara', ['quantity'], '', {'chara_id': str(chara), 'user_id': str(user_id)})

        position = dbservice.select('user_has_chara', ['position'], '', {'chara_id': str(chara), 'user_id': str(user_id)})
          
        chara_text = f'{str(chara_info[0])} ({chara_info[1]}) '

        while len(chara_text) < 95: 
            chara_text += '-'

        copies_text = ' ' + (' ' * (3 - len(str(copies)))) + str(copies)

        while len(copies_text) < 9:
            copies_text += ' '

        position_text = str(position)

        while len(position_text) < 10:
            position_text += ' '

        text += chara_text + copies_text + position_text + '\n'
        indice += 1

    text += '```'
    
    if page <= last_page:

        await msg.edit(text, view=CollectionPagination(msg, user_id, page, last_page))
    
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

        text = f'Trazendo {str(rolls)} rolls para {name}'

        print(text)
        await send_message2(text, rolls_channel)
        await asyncio.sleep(1)

        for i in range(rolls):

            await roll_chara(name, user_id)

        await asyncio.sleep(2)

        dbservice.delete('rolls', {'id': smaller_id})

        print('deleted ' + str(smaller_id))

ofertas = bot.create_group('ofertas', 'Comandos de ofertas')

@ofertas.command(name='iniciar')
async def iniciar_command(
    ctx: discord.ApplicationContext,
    target: discord.Option(str, autocomplete=get_members_names2, name='membro')
):

    if ctx.channel.id == rolls_channel:
    
        from_id = ctx.author.id
        to_id = dbservice.select('user', ['id'], '', {'name': target})
    
        id = dbservice.insert('chara_ofertas', ['from_id', 'to_id'], [from_id, to_id])

        await ctx.respond(f'Uma janela de troca com {target} foi aberta. O ID dessa oferta é {str(id)}. Utilize o "/ofertas finalizar" e insira esse ID para realizar uma oferta.')

@ofertas.command(name='finalizar')
async def finalizar_oferta_command(
    ctx: discord.ApplicationContext,
    id: discord.Option(int, name='id'),
    own_chara: discord.Option(str, autocomplete=get_collection, name='seu_chara'),
    own_quantity: discord.Option(int, min_value=1, name='sua_quantidade'),
    target_chara: discord.Option(str, autocomplete=get_chara, name='chara_dele'),
    target_quantity: discord.Option(int, min_value=1, name='quantidade_dele')
):

    exists = dbservice.check_existence('chara_ofertas', {'id': id})

    if exists == 1:

        own_chara, own_title, own_chara_id = own_chara.split('(')
        own_chara = own_chara.rstrip(' ')
        own_chara_id = own_chara_id.rstrip(')')

        target_chara, target_title, target_chara_id = target_chara.split('(')
        target_chara = target_chara.rstrip(' ')
        target_chara_id = target_chara_id.rstrip(')')

        own_id = str(ctx.author.id)
        target_id = dbservice.select('chara_ofertas', ['to_id'], '', {'id':id})

        max_own = dbservice.select('user_has_chara', ['quantity'], '', {'user_id': own_id, 'chara_id': own_chara_id})
        max_target = dbservice.select('user_has_chara', ['quantity'], '', {'user_id': target_id, 'chara_id': target_chara_id})
    
        print('max chara values:')
        print(max_own)
        print(max_target)

        if type(max_own) != int:
            max_own = from_list_of_tuples_to_list(max_own)

        if type(max_target) != int:
            max_target = from_list_of_tuples_to_list(max_target)

        if max_own == None:
            max_own = 1

        if max_target == None:
            max_target = 1

        print('max chara values:')
        print(max_own)
        print(max_target)

        if own_quantity > max_own and target_quantity > max_target:
            await ctx.respond('Você está tentando negociar mais cópias de personagem do que você e o outro usuário têm disponíveis.')
    
        elif own_quantity > max_own:
            await ctx.respond('Você está entando oferecer mais cópias de personagem do que tem disponível.')

        elif target_quantity > max_target:
            await ctx.respond('O outro usuário não possui cópias suficientes do personagem selecionado.')
        
        else:

            user_id = dbservice.select('chara_ofertas', ['to_id'], '', {'id': id})

            columns = ['offering', 'offer_quantity', 'receiving', 'receive_quantity']
            values = [own_chara_id, own_quantity, target_chara_id, target_quantity]

            dbservice.update('chara_ofertas', columns, values, {'id': id})

            #await ctx.respond(f'Oferta realizada. O usuário <@' + str(user_id) + '> foi notificado. Não foi?')
            await ctx.respond(f'Oferta realizada.')

    else:

        await ctx.respond(f'A oferta de ID {str(id)} não existe. Por favor corrija ou crie uma oferta utilizando /ofertas iniciar.')

@bot.slash_command(name='pesquisar_chara')
async def pesquisar_chara_command(
    ctx: discord.ApplicationContext,
    target: discord.Option(str, autocomplete=get_chara, name='chara')
):
    await ctx.respond('Buscando o personagem...')

    result = dbservice.select('user_has_chara', ['user_id', 'quantity'], ' ORDER BY quantity DESC', {'chara_name': target})

    print(result)

    header = '**' + target + '**\n'
    body = header + '```Usuário:            Cópias:\n\n'
    
    if type(result) == tuple:
        result = [result]

    for user in result:
        text = ''

        user_name = dbservice.select('user', ['name'], '', {'id': user[0]})
        
        quantity = user[1]

        if quantity == None:
            quantity = 1

        text += user_name

        while len(text) != 20:
            text += ' '

        text += str(quantity) + '\n'

        body += text
        
    body += '```'

    await send_message2(body, rolls_channel)
    
async def ofertas_enviadas_command(message):

    offers = dbservice.select('chara_ofertas', [], 'ORDER BY id ASC', {'from_id': message.author.id})

    print(offers)

    if type(offers) == tuple:
        offers = [offers]

    if offers != []:

        text = '**Ofertas enviadas:**\n```'
        #text += 'Ofereci para       Personagem  #       Quero receber  # \n\n'

        for offer in offers:

            to_id = offer[2]

            user_name = dbservice.select('user', ['name'], '', {'id': to_id})

            my_chara_id = offer[3]
                
            my_quantity = offer[4]

            my_chara_info = dbservice.select('chara', ['name', 'media_title'], '', {'chara_id': my_chara_id})

            their_chara_id = offer[5]
            
            their_quantity = offer[6]
            
            their_chara_info = dbservice.select('chara', ['name', 'media_title'], '', {'chara_id': their_chara_id})

            print(their_quantity)
            print(type(their_quantity))
            print(str(their_quantity))

            text += f'Oferta ID {str(offer[0])} para {user_name}\n'
            text += f'Meu:     {str(my_quantity)}x - {my_chara_info[0]} ({my_chara_info[1]})\n'
            text += f'Dele(a): {str(their_quantity)}x - {their_chara_info[0]} ({their_chara_info[1]})\n\n'
            
        text += '```'

        await send_message2(text, rolls_channel)

async def ofertas_recebidas_command(message):

    offers = dbservice.select('chara_ofertas', [], 'ORDER BY id ASC', {'to_id': message.author.id})
    
    print(offers)

    if type(offers) == tuple:
        offers = [offers]

    if offers != []:

        text = '**Ofertas recebidas:**\n```'

        for offer in offers:

            from_id = offer[1]

            user_name = dbservice.select('user', ['name'], '', {'id': from_id})

            their_chara_id = offer[3]
                
            their_quantity = offer[4]
            
            their_chara_info = dbservice.select('chara', ['name', 'media_title'], '', {'chara_id': their_chara_id})

            my_chara_id = offer[5]
            
            my_quantity = offer[6]

            my_chara_info = dbservice.select('chara', ['name', 'media_title'], '', {'chara_id': my_chara_id})

            text += f'Oferta ID {str(offer[0])} de {user_name}\n'
            text += f'Meu:     {str(my_quantity)}x - {my_chara_info[0]} ({my_chara_info[1]})\n'
            text += f'Dele(a): {str(their_quantity)}x - {their_chara_info[0]} ({their_chara_info[1]})\n\n'
        
        text += '```'

        await send_message2(text, rolls_channel)

@ofertas.command(name='responder')
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

                await make_trade(trade)

                dbservice.delete('chara_ofertas', {'id': id})

                await ctx.respond(f'Oferta de ID {str(id)} aceita.')

            case 'Recusar':

                dbservice.delete('chara_ofertas', {'id': id})

                await ctx.respond(f'Oferta de ID {str(id)} recusada.')

    else:

        await ctx.respond('Você não pode aceitar ou recusar essa oferta pois ela não é direcionada par você.')

async def make_trade(trade):

    user1 = trade[1]
    user2 = trade[2]

    user1_chara_name = trade[3]
    user2_chara_name = trade[5]
    
    user1_chara_id = dbservice.select('chara', ['chara_id'], '', {'name': user1_chara_name})
    user2_chara_id = dbservice.select('chara', ['chara_id'], '', {'name': user2_chara_name})

    user1_chara_quantity = trade[4]
    user2_chara_quantity = trade[6]

    # USER 1

    exists = dbservice.check_existence('user_has_chara', {'user_id': user1, 'chara_id': user2_chara_id})

    if exists == 0:

        columns = ['user_id', 'chara_id', 'position', 'chara_name', 'quantity']
        val = [user1, user2_chara_id, 9999, user2_chara_name, user2_chara_quantity]

        dbservice.insert('user_has_chara', columns, val)

    else:

        original_quantity = dbservice.select('user_has_chara', ['quantity'], '', {'user_id': user1, 'chara_id': user2_chara_id})

        new_quantity = user2_chara_quantity + original_quantity

        columns = ['quantity']
        val = [new_quantity]
        where = {'user_id': user1, 'chara_id': user2_chara_id}

        dbservice.update('user_has_chara', columns, val, where)
        
    # USER 2

    exists = dbservice.check_existence('user_has_chara', {'user_id': user2, 'chara_id': user1_chara_id})

    if exists == 0:

        columns = ['user_id', 'chara_id', 'position', 'chara_name', 'quantity']
        val = [user2, user1_chara_id, 9999, user1_chara_name, user1_chara_quantity]

        dbservice.insert('user_has_chara', columns, val)

    else:

        original_quantity = dbservice.select('user_has_chara', ['quantity'], '', {'user_id': user2, 'chara_id': user1_chara_id})

        new_quantity = user1_chara_quantity + original_quantity

        columns = ['quantity']
        val = [new_quantity]
        where = {'user_id': user2, 'chara_id': user1_chara_id}

        dbservice.update('user_has_chara', columns, val, where)

    # deducting quantities
    
    user1_total = dbservice.select('user_has_chara', ['quantity'], '', {'user_id': user1, 'chara_id': user1_chara_id})
    user2_total = dbservice.select('user_has_chara', ['quantity'], '', {'user_id': user2, 'chara_id': user2_chara_id})

    if user1_chara_quantity == user1_total:

        dbservice.delete('user_has_chara', {'user_id': user1, 'chara_id': user1_chara_id})

    else:

        columns = ['quantity']
        val = user1_total - user1_chara_quantity
        where = {'user_id': user1, 'chara_id': user1_chara_id}

        dbservice.update('user_has_chara', columns, val, where)

    if user2_chara_quantity == user2_total:

        dbservice.delete('user_has_chara', {'user_id': user2, 'chara_id': user2_chara_id})

    else:

        columns = ['quantity']
        val = user2_total - user2_chara_quantity
        where = {'user_id': user2, 'chara_id': user2_chara_id}

        dbservice.update('user_has_chara', columns, val, where)

@ofertas.command(name='cancelar')
async def cancelar_oferta_command(
    ctx: discord.ApplicationContext,
    id: discord.Option(int, name='id')
):

    trade = dbservice.select('chara_ofertas', [], '', {'id': id})
    
    if str(ctx.author.id) == trade[1]:

        dbservice.delete('chara_ofertas', {'id': id})

        await ctx.respond(f'Oferta de ID {str(id)} cancelada.')

corrigir = bot.create_group('corrigir', 'Comandos para correções diversas')
@corrigir.command(name='personagem')
async def corrigir_personagem_command(
    ctx: discord.ApplicationContext,
    chara: discord.Option(str, autocomplete=get_chara, name='personagem'),
    correct_media: discord.Option(str, name='midia_correta', description='apenas o link da obra no anilist')
):
    await ctx.respond('Obrigado pela correção!')

    # adicionar zakoleta

    reward = dbservice.select('values_chart', ['value_value'], '', {'value_name': 'chara_correction'})

    add_zakoleta(ctx.author.id, reward, f'+{str(reward)} Zakoleta por corrigir a mídia de um personagem', 'add')

    # realizar a correção
    type, id = get_type_and_id_from_anilist_link(correct_media)

    if type == 'ANIME':

        result = anilist.query_anime_id(id)

    else:

        result = anilist.query_manga_id(id)

    result = result.json()

    print(result)

    media_title = result['data']['Media']['title']['romaji']

    chara, old_title, chara_id = chara.split('(')
    chara = chara.rstrip(' ')
    chara_id = chara_id.rstrip(')')

    column = ['media_title']

    value = [media_title]

    where = {'chara_id': chara_id}

    dbservice.update('chara', column, value, where)

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

            calculate_reward(user_id, url)

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

            quantity = 0

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

                    quantity = diff

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

def calculate_reward(user_id, media_url, quantity=None):

    type, media_id = get_type_and_id_from_anilist_link(media_url)

    exists = dbservice.check_existence('user_has_media', {'media_id': media_id, 'user_id': user_id})
    
    if quantity == None:

        user_name = dbservice.select('user', ['anime_list'], '', {'id': user_id}).lstrip('https://anilist.co/user/').rstrip('/')
        
        if exists == 1:

            previous_progress = dbservice.select('user_has_media', ['progress'], '', {'media_id': media_id, 'user_id': user_id})
            
            new_progress = anilist.check_progress(media_id, user_name)

            quantity = new_progress - previous_progress

        else:

            quantity = anilist.check_progress(media_id, user_name)
    
    if type == 'ANIME':

        result = anilist.query_anime_id(media_id)

        result = result.json()

        duration = result['data']['Media']['duration']
        format = result['data']['Media']['format']

        if duration <= 9:
            size = 'shorter'

        elif duration <= 19:
            size = 'short'

        elif duration <= 29:
            size = 'common'

        if size in ['shorter', 'short', 'common']:

            size = 'episode_' + size

            multiplier = 1

        else:

            size = 'episode_common'

            multiplier = ceil(duration / 30)

        reward = dbservice.select('values_chart', ['value_value'], '', {'value_name': size}) * multiplier
    
    else:

        reward = dbservice.select('values_chart', ['value_value'], '', {'value_name': 'chapter'})

    total = reward * quantity

    # needs to check if media was chosen in the /random

    roulette_bonus = dbservice.select('values_chart', ['value_value'], '', {'value_name': 'roleta_episode'})

    last_roulette_id = get_last_roulette_id()

    roulette_media = dbservice.select('user_has_roleta', ['received_rec'], '', {'id_roleta': last_roulette_id, 'id_receiver': user_id})
    
    if ',' in roulette_media:
        recs = roulette_media.split(',')

        for media in recs:

            type, id = get_type_and_id_from_anilist_link(media)

            if str(id) == str(media_id):

                total += roulette_bonus

    else:

        type, id = get_type_and_id_from_anilist_link(roulette_media)

        if str(id) == str(media_id):

            total += roulette_bonus

    if total > 0:

        add_zakoleta(user_id, total, f'+ {str(total)} zakoletas adicionar por ver/ler algo.', 'add')



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

def values_options():

    values_options = from_list_of_tuples_to_list(dbservice.select('values_chart', ['value_name'], ''))

    return values_options

@bot.slash_command(name='change_values')
async def change_values_command(
    ctx: discord.ApplicationContext,
    value_to_change: discord.Option(str, choices=values_options(), name='value_name'),
    value: discord.Option(int, name='value')
):
    if ctx.author.id in admins:
        dbservice.update('values_chart', ['value_value'], [value], {'value_name': value_to_change})@bot.slash_command(name='change_values')

## MERCADO TO DO ##
#
# Project: create a functional animanga market
#
# Confirmed features:
#
# - The users should be able to insert animanga through zakoletas <
# - The users should be able to acquire animanga from the market + free buys <
# - By finishing the bought animanga they always get more zakoleta than they've spent <
# - Insertions will be anonymous
# - rewarding is 50/50
# - custo pra compra = 100 / lucro = proporcional ao tamanho

# custo_inserção = 100 (fixo)

# custo_compra = 100 (base fixa)

# lucro_vendedor = (50% do fixo + x/2 no término), onde x = lucro_comprador

# lucro_comprador = (100 * fator_duração * fator_valorização (min 101)) no término

# valor_inicial = 100
# fator_valorização = 1.x

# limites = 3 venda / 2 compra

# FATOR DURAÇÃO

# 0 minutos = fator 1

# 5 min = fator 1.06

# 300 min (1 cour) = fator 2

# 150 min = fator 1.5

# FATOR VALORIZAÇÃO

# momento 0 = fator 1

# momento 1 dia = fator 1.03

# momento 1 mês = fator 2

# 
# "Might happen" features:
#
# - The bot should populate the market every X days with new random animanga
# - The worth of animanga grows larger with time
# - The users will be able to abandon and throw an aniamnga back to the market
# - Previously abandoned animanga are worth more
# - A way for users to report wrongly chosen animanga by the bot and get rewarded
# - The users should use spoiler tags to insert animanga and the bot will delete then immediatelly
#
# Stuff that needs to be decided
#
# - The frequency in which the bot adds animanga
# - The cost of acquiring animanga from the market
# - The formula to determine the reward. Probably something like an arbitraty value x * number of episodes * time mod * abandoned mod

guilda = bot.create_group('guilda', 'Comandos da guilda')

# mercado_commands = ['Colocar à venda', 'Comprar', 'Terminar', 'Abandonar', 'Calcular valor']

quest_flavors = [
    'Enfrente * e saia vivo para contar ao mundo!', 
    'Procure pela cidade perdida de * pelo cálice sagrado!', 
    'Vasculhe as ruínas de * atrás de ouro!', 
    'Passe por * sem tomar dano!', 
    'Sobreviva a *!', 
    'Percorra as masmorras de * e salve a princesa!', 
    'Decifre os textos rúnicos de * e obtenha a sabedoria suprema!', 
    'Derrote * e conquiste suas terras!', 
    'Desvende os segredos de *!', 
    'Subjugue as forças de * e salve o mundo!', 
    'Liberte o mundo das forças malignas de *!', 
    'Faça uma peregrinação espiritual por * e traga a paz mundial!', 
    'Reencarne em * e salve seus amigos!', 
    'Vire uma garota mágica em * e salve sua cidade!'
    ]

class SellingBtn(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
    def __init__(self, anilist_id, insertion, type, reward, sender, title, date, flavor):
        super().__init__()
        self.anilist_id = anilist_id
        self.insertion = insertion
        self.type = type
        self.reward = reward
        self.sender = sender
        self.title = title
        self.date = date
        self.flavor = flavor
        
    @discord.ui.button(label="Criar quest", style=discord.ButtonStyle.primary, emoji="📋") # Create a button with the label "😎 Click me!" with color Blurple
    async def button_callback(self, button, interaction):
        dbservice.insert('quests', ['id_anilist', 'item_url', 'item_name', 'item_type', 'sender', 'is_available', 'value', 'date_inserted', 'flavor_text'], [self.anilist_id, self.insertion, self.title, self.type, self.sender, 'true', self.reward, self.date, self.flavor])

        await interaction.response.send_message("Quest criada com sucesso.", ephemeral=True) # Send a message when the button is clicked
        
        flavor1, flavor2 = dbservice.select('quests', ['flavor_text'], '', {'id_anilist': self.anilist_id}).split('*')
        
        msg = f'✍️ A quest *{flavor1}**{self.title} ({self.type})**{flavor2}* acabou de ser criada, está valendo ${str(self.reward)} e já está disponível no quadro!'
    
        await generate_guild_log(msg)


@guilda.command(name='criar_quest', description='Este comando permite que se crie uma quest')
async def guilda_criar_quest_command(
    ctx: discord.ApplicationContext,
    insertion: discord.Option(str, name='obra', description='Insira o link do anilist da obra')
):
    sender = str(ctx.author.id)

    seller_slots = dbservice.select('quests', ['sender'], '', {'sender': sender, 'is_available': 'true', 'abandoned':'false'})

    if seller_slots == str(sender):
        seller_slots = 1
        
    else:
        seller_slots = len(seller_slots)
    
    print('slots: ' + str(seller_slots))
    
    # max_seller_slots = int(dbservice.select('user', ['quest_selling_slots'], '', {'id': sender}))

    max_seller_slots = 3

    if seller_slots >= max_seller_slots:

        print(dbservice.select('user', ['quest_selling_slots'], '', {'id': sender}))
        
        # await send_message(ctx, 'Você não tem espaço para vender uma nova obra.')
        await ctx.response.send_message('Você não tem espaço para criar uma nova quest.', ephemeral=True)
    
    else:

        if 'anilist.co' in insertion:
        
            type, anilist_id = get_type_and_id_from_anilist_link(insertion)
        
            exists = dbservice.check_existence('quests', {'id_anilist': str(anilist_id), 'is_available': str('true')})

            if exists == 0:     
            
                if type == 'anime':

                    response = anilist.query_anime_id(anilist_id)
                
                    media_obj = response.json()
                
                    duration = media_obj['data']['Media']['duration']

                    episodes = media_obj['data']['Media']['episodes']
                    print(duration)
                    print(episodes)

                    if duration == None:
                        await ctx.response.send_message('Você provavelmente tentou inserir uma obra sem a informação de duração no Anilist.', ephemeral=True)
                        return                        

                    elif episodes == None:
                        await ctx.response.send_message('Você provavelmente tentou inserir uma obra que não contém o número de episódios/capítulos ou está em lançamento no Anilist.', ephemeral=True)
                        return
                    
                    else:
                        total_duration = duration * episodes
                        type_factor = 0.004

                        print(total_duration)
                
                else:

                    response = anilist.query_manga_id(anilist_id)

                    media_obj = response.json()
                    chapters = media_obj['data']['Media']['chapters']
                    volumes = media_obj['data']['Media']['volumes']
                    duration = 45
                    
                    if volumes == None:
                        if chapters == 1:
                            duration = 20
                            volumes = 1
                        else:
                            await ctx.response.send_message('Você provavelmente tentou inserir uma obra que não contém o número de episódios/volumes ou está em lançamento no Anilist.', ephemeral=True)
                            return
                        
                    elif volumes == 1 and chapters == 1:
                        duration = 20
                    
                    total_duration = volumes * duration
                    type_factor = 0.004

                title = media_obj['data']['Media']['title']['romaji']
                
                print(title)

                duration_factor = 1 + (total_duration * type_factor)
                
                hours = floor(total_duration / 60)
                
                size_factor = 1 + ((hours - 1)/20)
                print('size factor')
                print(str(size_factor))
            
                reward = ceil(((100 * duration_factor) - 100) * size_factor)

                type_factor = 0.004
                
                duration_factor = 1 + (total_duration * type_factor)
                
                hours = floor(total_duration / 60)

                size_factor = 1

                if hours >= 2:
                    size_factor += 2 * 0.055
                if hours >= 10:
                    size_factor += 8 * 0.04
                if hours >= 20:
                    size_factor += 10 * 0.027
                if hours >= 40:
                    size_factor += 20 * 0.015
                if hours >= 80:
                    size_factor += (hours - 40) * 0.005

                # size_factor = 1 + ((hours - 1) * 0.05)

                # size_factor = 1 + ((hours - 1)/20)

                print('size factor')

                print(str(size_factor))
            
                # reward = math.ceil(((100 * duration_factor) - 100) * size_factor)

                reward = ceil((duration_factor * size_factor) * 100) - 100

                date = datetime.datetime.now(ZoneInfo('America/Sao_Paulo'))
                
                timestamp = int(datetime.datetime.now().timestamp())

                flavor = random.choice(dbservice.select('quest_flavors', ['flavor'], ''))[0]
                print(flavor)
            
                await ctx.response.send_message('A quest ' + title + ' terá uma recompensa de $' + str(reward) + '. Para formalizar a criação da quest, clique no botão abaixo.', ephemeral=True, view=SellingBtn(anilist_id, insertion, type, reward, sender, title, timestamp, flavor))

            else:
                await ctx.response.send_message("A quest já existe.", ephemeral=True)

        else:
            await send_message(ctx, 'É preciso inserir um link do Anilist.')

async def get_quests_options(ctx: discord.AutocompleteContext):
    
    quests_options = dbservice.select('quests', ['item_name', 'value', 'is_available', 'item_type'], '')

    print(quests_options)

    if not isinstance(quests_options, list):
        quests_options = [quests_options]
        print('test:')
        print(quests_options)

    names = []

    for name in quests_options:
        
        if name[2] == 'true':

            names.append(name[0] + ' (' + name[3] + ')')
            
    print(names)

    return [name for name in names if ctx.value.lower() in name.lower()]

class AcquiringBtn(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
    def __init__(self, value, user_id, sender_id, real_name, _type):
        super().__init__()
        self.value = value
        self.user_id = user_id
        self.sender_id = sender_id
        self.real_name = real_name
        self._type = _type

    @discord.ui.button(label="Aceitar", style=discord.ButtonStyle.primary, emoji="🤝") # Create a button with the label "😎 Click me!" with color Blurple
    async def button_callback(self, button, interaction):
        is_available = dbservice.select('quests', ['is_available'], '', {'item_name':self.real_name, 'item_type': self._type})
        print(self._type)
        
        if is_available == 'false':
            await interaction.response.send_message("A quest já foi pega por outra pessoa.", ephemeral=True) # Send a message when the button is clicked
        else:
            dbservice.update('quests', ['buyer'], [self.user_id], {'item_name': self.real_name, 'item_type': self._type})
            dbservice.update('quests', ['is_available'], ['false'], {'item_name': self.real_name, 'item_type': self._type})
            
            await interaction.response.send_message("Quest aceita com sucesso.", ephemeral=True) # Send a message when the button is clicked
            
            timestamp = int(datetime.datetime.now().timestamp())
            # date = 
            
            dbservice.update('quests', ['date_bought'], [int(timestamp)], {'item_name': self.real_name, 'item_type': self._type})
            
            flavor1, flavor2 = dbservice.select('quests', ['flavor_text'], '', {'buyer': self.user_id, 'item_name': self.real_name, 'item_type': self._type}).split('*')
            
            if dbservice.select('user', ['sexo'], '', {'id': self.user_id}) == 'm':
                msg = f"🫡 A aventureira <@{str(self.user_id)}> aceitou a quest *{flavor1}**{self.real_name} ({self._type})**{flavor2}* pela recompensa de ${str(self.value)}"
            else:
                msg = f"🫡 O aventureiro <@{str(self.user_id)}> aceitou a quest *{flavor1}**{self.real_name} ({self._type})**{flavor2}* pela recompensa de ${str(self.value)}"
            
            await generate_guild_log(msg)

async def pay_quest(quest, type, user_id, sender_id, buyer_reward, sender_reward):
    
    exists = dbservice.check_existence('quests', {'item_name': quest, 'item_type': type})
    
    if exists == 1:

        dbservice.update_zakoleta('user', sender_reward, '+' + str(sender_reward) + ' zakoletas porque alguém finalizou sua quest.', sender_id, 'add')
        dbservice.update_zakoleta('user', buyer_reward, '+' + str(buyer_reward) + ' zakoletas por completar uma quest.', user_id, 'add')
        
    return

# Resenha modal
class ResenhaModal(discord.ui.Modal):
    def __init__(self, user_id, sender_id, item_name, buyer_reward, sender_reward, type, url, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.user_id = user_id
        self.sender_id = sender_id
        self.item_name = item_name
        self.buyer_reward = buyer_reward
        self.sender_reward = sender_reward
        self.type = type
        self.url = url
        
        self.add_item(discord.ui.InputText(label="Comentário/Resenha", style=discord.InputTextStyle.long, required=True, max_length=4000))
        self.add_item(discord.ui.InputText(label="Nota (número inteiro de 0 a 10)", required=False, max_length=2))

    async def callback(self, interaction: discord.Interaction):

        user_id = str(interaction.user.id)
        review = self.children[0].value
        
        score = self.children[1].value
        
        print(review)
        print('score:')
        print(str(score))
        
        if score.isnumeric() == False:
            dbservice.insert('quests_reviews', ['id_user', 'item_name', 'review'], [self.user_id, self.item_name, review])
        else:
            dbservice.insert('quests_reviews', ['id_user', 'item_name', 'review', 'score'], [self.user_id, self.item_name, review, score])
           
        user_name = dbservice.select('user', ['name'], '', {'id': self.user_id})    
        sender_name = dbservice.select('user', ['name'], '', {'id': self.sender_id})    

        text = f'Resenha de **{self.item_name}**\nLink: <{self.url}>\nQuest criada por: {sender_name}\nResenha por: {user_name}\n\n{review}'
        if score.isnumeric() == True:
            text += f'\n\nNota: {str(score)}/10'
            
        await send_message2(text, 1193562729198407701)
            
        bonus = ceil(int(self.buyer_reward) * 0.05)
        
        dbservice.update_zakoleta('user', int(bonus), '+' + str(bonus) + ' por escrever uma resenha para quest', self.user_id, 'add')

        await interaction.response.send_message(f'Comentário/resenha enviada. A Guilda agradece!', ephemeral=True)
        
        flavor1, flavor2 = dbservice.select('quests', ['flavor_text'], '', {'buyer': self.user_id, 'item_name': self.item_name}).split('*')
        sender_id = dbservice.select('quests', ['sender'], '', {'buyer': self.user_id, 'item_name': self.item_name})
        
        if dbservice.select('user', ['sexo'], '', {'id': self.user_id}) == 'm':
            msg = f'💪 A aventureira <@{str(self.user_id)}> completou e entregou a quest *{flavor1}**{self.item_name} ({self.type})**{flavor2}* criada por <@{str(sender_id)}>! A recompensa distribuída foi de ${str(self.buyer_reward)} e ${str(self.sender_reward)} respectivamente. Além de um bônus de {str(bonus)} pela resenha para o aventureiro.'
        else:    
            msg = f'💪 O aventureiro <@{str(self.user_id)}> completou e entregou a quest *{flavor1}**{self.item_name} ({self.type})**{flavor2}* criada por <@{str(sender_id)}>! A recompensa distribuída foi de ${str(self.buyer_reward)} e ${str(self.sender_reward)} respectivamente. Além de um bônus de {str(bonus)} pela resenha para o aventureiro.'
        
        await pay_quest(self.item_name, self.type, self.user_id, self.sender_id, self.buyer_reward, self.sender_reward)
        
        dbservice.delete('quests', {'buyer': self.user_id, 'item_name': self.item_name})

        if str(self.user_id) != str(334509476428251137):
            await generate_guild_log(msg)         

class ReviewBtn(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
    def __init__(self, ctx, user_id, sender_id, real_name, type, buyer_reward, sender_reward, url):
        super().__init__()
        self.ctx = ctx
        self.user_id = user_id
        self.sender_id = sender_id
        self.real_name = real_name
        self.type = type
        self.buyer_reward = buyer_reward
        self.sender_reward = sender_reward
        self.url = url

    @discord.ui.button(label="Deixar comentário ou resenha", row=0, style=discord.ButtonStyle.primary, emoji="📝") # Create a button with the label "😎 Click me!" with color Blurple
    async def first_button_callback(self, button, interaction):
        url = dbservice.select('quests', ['item_url'], '', {'item_name': self.real_name})
        modal = ResenhaModal(self.user_id, self.sender_id, self.real_name, self.buyer_reward, self.sender_reward, self.type, self.url, title="Escrever resenha")
        await interaction.response.send_modal(modal)
        
    @discord.ui.button(label="Entregar a quest sem bônus", row=0, style=discord.ButtonStyle.primary, emoji="💰") # Create a button with the label "😎 Click me!" with color Blurple
    async def second_button_callback(self, button, interaction):
        obra = dbservice.select('quests', ['item_name'], '', {'buyer': self.user_id, 'item_name': self.real_name})
        flavor1, flavor2 = dbservice.select('quests', ['flavor_text'], '', {'buyer': self.user_id, 'item_name': self.real_name}).split('*')
        
        await pay_quest(self.real_name, self.type, self.user_id, self.sender_id, self.buyer_reward, self.sender_reward)
        
        dbservice.delete('quests', {'buyer': self.user_id, 'item_name': self.real_name})
        
        if dbservice.select('user', ['sexo'], '', {'id': self.user_id}) == 'm':
            msg = f'💪 A aventureira <@{str(self.user_id)}> completou e entregou a quest *{flavor1}**{obra} ({self.type})**{flavor2}* criada por <@{str(self.sender_id)}>! A recompensa distribuída foi de ${str(self.buyer_reward)} e ${str(self.sender_reward)} respectivamente.'
        else:    
            msg = f'💪 O aventureiro <@{str(self.user_id)}> completou e entregou a quest *{flavor1}**{obra} ({self.type})**{flavor2}* criada por <@{str(self.sender_id)}>! A recompensa distribuída foi de ${str(self.buyer_reward)} e ${str(self.sender_reward)} respectivamente.'

        if str(self.user_id) != str(334509476428251137):
            await generate_guild_log(msg)   
        

@guilda.command(name='aceitar_quest', description='Este comando permite aceitar quests disponíveis no quadro')
async def guilda_aceitar_quest_command(
    ctx: discord.ApplicationContext,
    order: discord.Option(str, autocomplete=get_quests_options, name='quests')
):
    
    user_id = ctx.author.id

    real_name, _type = order.split(' (')
    
    _type = _type.strip(')')

    print(real_name)
    print(_type)

    sender_id = dbservice.select('quests', ['sender'], '', {'item_name': real_name, 'item_type': _type})
    
    if user_id == int(sender_id):
        
        await ctx.response.send_message("Você não pode aceitar uma quest que você mesmo enviou.", ephemeral=True)
        
    else:

        value = dbservice.select('quests', ['value'], '', {'item_name': real_name, 'item_type': _type})
                                                        
        time_passed = int(datetime.datetime.now().timestamp()) - int(dbservice.select('quests', ['date_inserted'], '', {'item_name': real_name, 'item_type': _type}))
    
        days = floor(time_passed / 86400)

        print('days: ' + str(days))

        buyer_slots = dbservice.select('quests', ['buyer'], '', {'buyer': user_id})

        if buyer_slots == str(user_id):
            buyer_slots = 1
        
        else:
            buyer_slots = len(buyer_slots)
    
        print('slots: ' + str(buyer_slots))

        if buyer_slots >= int(dbservice.select('user', ['quest_buying_slots'], '', {'id': user_id})):

            print(dbservice.select('user', ['quest_buying_slots'], '', {'id': user_id}))
        
            await ctx.response.send_message('Você não tem espaço para aceitar uma nova quest.', ephemeral=True)
    
        else:

            value = calculate_quest_reward(value, days)
            
            await ctx.response.send_message('Para formalizar a aquisição da quest, clique no botão abaixo.', ephemeral=True, view=AcquiringBtn(value, user_id, sender_id, real_name, _type))

def calculate_quest_reward(base_value, days_passed):
    
    print('days_passed')
    print(days_passed)
    
    value = base_value

    factor = 1.03

    for day in range(int(days_passed)):
        value = ceil(value * factor)
        print(value)

    return value 

async def get_user_received_quests(ctx: discord.AutocompleteContext):

    user_name = dbservice.select('user', ['name'], '', {'id': ctx.interaction.user.id})
    
    quests_options = dbservice.select('quests', ['item_name', 'item_type'], '', {'buyer': str(ctx.interaction.user.id)})
    
    print(quests_options)

    if not isinstance(quests_options, list):
        quests_options = [quests_options]
        print('test:')
        print(quests_options)

    names = []

    for name in quests_options:
        
        names.append(name[0] + ' (' + name[1] + ')')
            
    print(names)

    return [name for name in names if ctx.value.lower() in name.lower()]

@guilda.command(name='abandonar_quest', description='Este comando permite que você abandone uma quest')
async def guilda_abandonar_quest_command(
    ctx: discord.ApplicationContext,
    quest: discord.Option(str, name='quest', autocomplete=get_user_received_quests)
):
    user_id = str(ctx.author.id)
    
    real_name, _type = quest.split(' (')

    url = dbservice.select('quests', ['item_url'], '', {'item_name': real_name})
    
    type, anilist_id = get_type_and_id_from_anilist_link(url)
        
    exists = dbservice.check_existence('quests', {'buyer': user_id, 'id_anilist': anilist_id})
        
    if exists == 1:
            
        obra = dbservice.select('quests', ['item_name'], '', {'buyer': user_id, 'id_anilist': anilist_id})
        print(dbservice.select('quests', ['flavor_text'], '', {'buyer': user_id, 'id_anilist': anilist_id}))
        flavor1, flavor2 = dbservice.select('quests', ['flavor_text'], '', {'buyer': user_id, 'id_anilist': anilist_id}).split('*')
        dbservice.update('quests', ['buyer', 'is_available', 'abandoned'], ['', 'true', 'true'], {'buyer': user_id, 'id_anilist': anilist_id})
        
        if dbservice.select('user', ['sexo'], '', {'id': user_id}) == 'm':    
            msg = f'💀 A aventureira <@{str(user_id)}> morreu tentanto terminar a quest *{flavor1}**{obra} ({type})**{flavor2}* e a mesma foi devolvida ao quadro. Essa quest não conta para o limite de criação do criador.'
        else:
            msg = f'💀 O aventureiro <@{str(user_id)}> morreu tentanto terminar a quest *{flavor1}**{obra} ({type})**{flavor2}* e a mesma foi devolvida ao quadro. Essa quest não conta para o limite de criação do criador.'
        await generate_guild_log(msg)
            
        await ctx.response.send_message('Quest abandonada com sucesso.', ephemeral=True)
    else:

        await ctx.response.send_message('Você não é o dono dessa quest ou ela não existe.', ephemeral=True)

@guilda.command(name='entregar_quest', description='Este comando permite que se entregue uma quest')
async def guilda_entregar_quest_command(
    ctx: discord.ApplicationContext,
    quest: discord.Option(str, autocomplete=get_user_received_quests, name='quest')
):
    
    user = str(ctx.author.id)
    
    real_name, _type = quest.split(' (')
    
    _type = _type.strip(')')

    url = dbservice.select('quests', ['item_url'], '', {'item_name': real_name})
        
    type, anilist_id = get_type_and_id_from_anilist_link(url)
        
    exists = dbservice.check_existence('quests', {'buyer': user, 'id_anilist': anilist_id})
        
    if exists == 1:
            
        sender_id = dbservice.select('quests', ['sender'], '', {'id_anilist': anilist_id})

        time_passed = int(dbservice.select('quests', ['date_bought'], '', {'id_anilist': anilist_id})) - int(dbservice.select('quests', ['date_inserted'], '', {'item_name': real_name, 'item_type': _type}))
        print('time elapsed: ' + str(time_passed))
        
        days = floor(time_passed / 86400)
        print('days: ' + str(days))
    
        base_value = dbservice.select('quests', ['value'], '', {'item_name': real_name, 'item_type': _type})
        
        reward = calculate_quest_reward(base_value, days)
    
        buyer_reward = reward
    
        sender_reward = ceil(reward/2)
            
        print('rewards: ')
        print(buyer_reward)
        print(sender_reward)
        
        await ctx.response.send_message('Quest entregue com sucesso. Considere deixar um comentário ou até mesmo uma resenha sobre a obra. Você receberá um bônus de 5% da recompensa. É importante realizar um mínimo de esforço.', ephemeral=True, view=ReviewBtn(ctx, user, sender_id, real_name, type, buyer_reward, sender_reward, url))
            
    else:
        
        possible_group = dbservice.select('quests', ['party'], '', {'id_anilist': anilist_id})
        
        if ',' in possible_group:
            group = possible_group.split(',')
            if user == group[0]:
            
                sender_id = dbservice.select('quests', ['sender'], '', {'id_anilist': anilist_id})
                
                date_bought = dbservice.select('quests', ['date_bought'], '', {'id_anilist': anilist_id})

                time_passed = int(date_bought) - int(dbservice.select('quests', ['date_inserted'], '', {'item_name': real_name, 'item_type': _type}))
                print('time elapsed: ' + str(time_passed))
        
                days = floor(time_passed / 86400)
                print('days: ' + str(days))
    
                base_value = dbservice.select('quests', ['value'], '', {'item_name': real_name, 'item_type': _type})
        
                reward = calculate_quest_reward(base_value, days)
    
                buyer_reward = floor(reward/len(group))
    
                sender_reward = ceil(reward/2)
                
                obra = dbservice.select('quests', ['item_name'], '', {'item_name': real_name, 'item_type': _type})
                flavor1, flavor2 = dbservice.select('quests', ['flavor_text'], '', {'item_name': real_name, 'item_type': _type}).split('*')
        
                # dbservice.delete('quests', {'item_name': real_name, 'item_type': _type})
        
                msg = f'Os aventureiros ' 
                
                idx = 1
                    
                for member in group:
                    member_name = dbservice.select('user', ['name'], '', {'id': member})
                    if idx == len(group):
                        msg += f' e {member_name}'
                    else:
                        idx += 1
                        msg += f', {member_name}'
                        
                msg += f' completaram e entregaram a quest *{flavor1}**{real_name} ({_type})**{flavor2}* criada por <@{str(sender_id)}>! A recompensa distribuída foi de ${str(buyer_reward)} por aventureiro e ${str(sender_reward)} para o criador..'
            
                await generate_guild_log(msg)
                print(msg)

                await ctx.response.send_message('Quest entregue com sucesso. Quests em grupo não tem a opção de resenha, mas você pode enviá-la no privado do kaiser para que ela seja adicionada ao canal de resenhas.', ephemeral=True)
                

        await ctx.response.send_message('Você não é o dono dessa quest ou ela não existe.', ephemeral=True)

@guilda.command(name='quadro', description='Este comando permite visualizar as quests disponíveis')
async def classificados_command(
    ctx: discord.ApplicationContext,
    type: discord.Option(str, choices=['Anime', 'Manga'], name='tipo', required=False),
    disponibilidade: discord.Option(str, choices=['Quests aceitas'], name='disponibilidade', required=False)
):
    if disponibilidade != 'Quests aceitas':
        
        if type == 'Anime':
            data = dbservice.select('quests', ['item_url', 'item_name', 'item_type', 'value', 'date_inserted', 'flavor_text'], ' ORDER BY date_inserted', {'is_available':'true', 'item_type':'anime'})
    
        elif type == 'Manga':
            data = dbservice.select('quests', ['item_url', 'item_name', 'item_type', 'value', 'date_inserted', 'flavor_text'], ' ORDER BY date_inserted', {'is_available':'true', 'item_type':'manga'})
    
        else:
            data = dbservice.select('quests', ['item_url', 'item_name', 'item_type', 'value', 'date_inserted', 'flavor_text'], ' ORDER BY date_inserted', {'is_available':'true'})

    else:
        if type == 'Anime':
            data = dbservice.select('quests', ['item_url', 'item_name', 'item_type', 'value', 'date_inserted', 'flavor_text', 'buyer'], ' ORDER BY date_inserted', {'is_available':'false', 'item_type':'anime'})
    
        elif type == 'Manga':
            data = dbservice.select('quests', ['item_url', 'item_name', 'item_type', 'value', 'date_inserted', 'flavor_text', 'buyer'], ' ORDER BY date_inserted', {'is_available':'false', 'item_type':'manga'})
    
        else:
            data = dbservice.select('quests', ['item_url', 'item_name', 'item_type', 'value', 'date_inserted', 'flavor_text', 'buyer'], ' ORDER BY date_inserted', {'is_available':'false'})

        
    text = 'QUESTS \n\n'
    
    
    print('chegou aqui 1')
    print(data)
    if len(data) < 1:
        await ctx.response.send_message(text + 'Não existem quests disponíveis.', ephemeral=True)
        return
    print('chegou aqui 2')
    if not isinstance(data, list):
        data = [data]
        print('test:')
        print(data)
    
    # await ctx.respond(f'**QUESTS**')
    
    msg = await create_placeholder_message(ctx, ctx.interaction.channel.id)
    await ctx.response.send_message('OK', ephemeral=True)

    print('chegou aqui 3')

    await gerar_quest_board(msg, 1, 0, data)
                
async def gerar_quest_board(msg, page, last_page, data):
    
    print(data)
    print(len(data))
    
    if not isinstance(data, list):
        data = [data]
        print('test:')
        print(data)

    batch = 8

    indice = (page * batch) - (batch - 1)

    text = '# **QUESTS**\n\n'

    print('page')
    print(page)

    print('indice:')
    print(indice)

    last_page = ceil(len(data) / batch)

    for obra in data[batch*(page-1):batch*page]:

        print(indice)

        print('obra')
        print(obra)

        for i in obra:
            print(i)
        
        print(obra[4])
        
        time_passed = int(datetime.datetime.now().timestamp()) - int(obra[4])
        print('time elapsed: ' + str(time_passed))
        
        days = floor(time_passed / 86400)
        print('days: ' + str(days))
        
        value = calculate_quest_reward(obra[3], days)
        
        flavor1, flavor2 = obra[5].split('*')
        
        text += flavor1 + '**' + obra[1] + '**' + flavor2 + '\n'
            
        text += '<' + obra[0] + '>\nTipo: ' + obra[2].capitalize() + ' \nRecompensa: $' + str(value) + '\n'
        
        print('len of obra')
        print(str(len(obra)))
        

        if len(obra) == 7:
            aventureiro = dbservice.select('user', ['name'], '', {'id': obra[6]})
            if dbservice.select('user', ['sexo'], '', {'id': obra[6]}) == 'm':
                text += f'Aventureira: {aventureiro}\n'
            else:
                text += f'Aventureiro: {aventureiro}\n'
        
        text += '\n'
    
    if page <= last_page:

        await msg.edit(text, view=QuestBoardPagination(msg, page, last_page, data))

@guilda.command(name='flavor', description='Este comando permite a criação de "flavor texts" que enfeitarão as quests no quadro')
async def flavor_command(
    ctx: discord.ApplicationContext,
    flavor_text: discord.Option(str, name='texto', description='Insira um asterisco * onde ficará o nome da obra. Ex: Conquiste o * para vencer!')
):
    
    user_id = str(ctx.author.id)
    
    dbservice.insert('quest_flavors', ['flavor', 'creator'], [flavor_text, user_id])

    await ctx.response.send_message('Flavor adicionado!', ephemeral=True)


@guilda.command(name='inventario', description='Este comando permite visualizar seu dinheiro, espaço e quests aceitas')
async def inventario_command(
    ctx: discord.ApplicationContext,
    user: discord.Option(str, name='usuario', autocomplete=get_members_names2, required=False)
):
    if user == None:   
        user_id = ctx.author.id
    else:
        user_id = dbservice.select('user', ['id'], '', {'name':user})

    seller_slots = dbservice.select('quests', ['sender'], '', {'sender': user_id, 'is_available': 'true'})

    if seller_slots == str(user_id):
        seller_slots = 1
        
    else:
        seller_slots = len(seller_slots)
        
    buyer_slots = dbservice.select('quests', ['buyer'], '', {'buyer': user_id})

    if buyer_slots == str(user_id):
        buyer_slots = 1
        
    else:
        buyer_slots = len(buyer_slots)
        
    seller_total_slots = dbservice.select('user', ['quest_selling_slots'], '', {'id': user_id})
    buyer_total_slots = dbservice.select('user', ['quest_buying_slots'], '', {'id': user_id})
    
    data = dbservice.select('quests', ['item_url', 'item_name', 'item_type', 'value', 'date_inserted', 'flavor_text', 'date_bought'], '', {'buyer': str(user_id)})
    
    grana = dbservice.select('user', ['zakoleta'], '', {'id': user_id})
    
    # await send_message(ctx, f'MEU INVENTÁRIO')
    text = ''
    if user != None:
        text += f'**Inventário de {user} **\n\n'
      
    if user == None:
        
        text += '**$' + str(grana) + '**\n\n'
        if dbservice.select('user', ['quest_cancel_due_date'], '', {'id': user_id}) != None:
            due_date = int(dbservice.select('user', ['quest_cancel_due_date'], '', {'id': user_id})) - 10800
            data_cd = datetime.datetime.utcfromtimestamp(due_date).strftime('%d-%m-%Y %H:%M:%S')
            text += 'Data do próximo cancelamento de quest: ' + data_cd + '\n\n'
        text += '**Quests à venda: **' + str(seller_slots) + '/' + str(seller_total_slots) + ' \n\n'
        selling_quests = dbservice.select('quests', ['item_url', 'item_name', 'item_type', 'value', 'date_inserted', 'flavor_text'], '', {'sender': user_id, 'is_available': 'true'})
        
        if not isinstance(selling_quests, list):
            selling_quests = [selling_quests]
            
        for quest in selling_quests:
            time_passed = int(datetime.datetime.now().timestamp()) - int(quest[4])
            print('time_passed')
            print(time_passed)
        
            days = floor(time_passed / 86400)
            print('days')
            print(days)
        
            value = calculate_quest_reward(quest[3], days)
        
            flavor1, flavor2 = quest[5].split('*')
        
            text += flavor1 + '**' + quest[1] + '**' + flavor2 + '\n'
            
            text += '<' + quest[0] + '>\nTipo: ' + quest[2].capitalize() + ' \nRecompensa: $' + str(value) + '\n\n'
            
        text += '\n**Quests Aceitas **\n\nSolo: ' + str(buyer_slots) + '/' + str(buyer_total_slots)
        text += '\n\n'
        
    print('length of data')
    print(len(data))
    if len(data) < 1:
        await ctx.response.send_message(text + 'Você não tem nenhuma quest aceita.', ephemeral=True)
        return
    
    page = 1
    last_page = 0

    print('data info:')
    print(data)
    print(len(data))
        
    
    if not isinstance(data, list):
        data = [data]
        print('test:')
        print(data)

    batch = 10

    indice = (page * batch) - (batch - 1)

    print('page')
    print(page)

    print('indice:')
    print(indice)

    last_page = ceil(len(data) / batch)

    for obra in data[batch*(page-1):batch*page]:

        print(indice)

        print('obra')
        print(obra)

        for i in obra:
            print(i)
        
        if obra[6] != None:
            time_passed = int(obra[6]) - int(obra[4])
        else:
            time_passed = int(obra[6]) - int(obra[4])
            
        print('time_passed')
        print(time_passed)
        
        days = floor(time_passed / 86400)
        print('days')
        print(days)
        
        value = calculate_quest_reward(obra[3], days)
        
        flavor1, flavor2 = obra[5].split('*')
        
        text += flavor1 + '**' + obra[1] + '**' + flavor2 + '\n'
            
        text += '<' + obra[0] + '>\nTipo: ' + obra[2].capitalize() + ' \nRecompensa: $' + str(value) + '\n\n'

    taken_quests = dbservice.select('quests', ['party', 'id_anilist'], '', {'is_available': 'false'})
    print('taken_quests')
    print(taken_quests)
    
    if not isinstance(taken_quests, list):
        taken_quests = [taken_quests]
    
    quest_data = None
    
    for quest in taken_quests:
        print('party')
        print(quest)
        if quest[0] != None:
            members = from_list_of_tuples_to_list(quest[0])
            print('party')
            print(str(quest[1]))
            # members = party.split(',')
            # print('members')
            # print(members)
            if user_id in members:
                quest_data = dbservice.select('quests', ['item_url', 'item_name', 'item_type', 'value', 'date_inserted', 'flavor_text', 'date_bought'], '', {'id_anilist': str(quest[1])})
                break
          
    if quest_data != None:
        text += f'Party: 1/1'
    else:
        text += f'Party: 0/1'
        
    print('quest_data')
    print(quest_data)
        
    if quest_data[6] != None:
        time_passed = int(quest_data[6]) - int(quest_data[4])
            
    print('time_passed')
    print(time_passed)
        
    days = floor(time_passed / 86400)
    print('days')
    print(days)
        
    value = calculate_quest_reward(quest_data[3], days)
        
    flavor1, flavor2 = quest_data[5].split('*')
    text += f'\n\n*{flavor1}**{quest_data[1]}**{flavor2}\nTipo: {quest_data[2]}\nRecompensa: ${str(value)}\n\n'
    
    await ctx.response.send_message(text, ephemeral=True)


#channel == 1193144846945353749

async def generate_guild_log(msg):
    
    await send_message2(msg, 1193144846945353749, True)
    
async def get_user_created_quests(ctx: discord.AutocompleteContext):

    user_name = dbservice.select('user', ['name'], '', {'id': ctx.interaction.user.id})
    
    quests_options = dbservice.select('quests', ['item_name', 'item_type'], '', {'sender': str(ctx.interaction.user.id), 'is_available': 'true'})
    
    print(quests_options)

    if not isinstance(quests_options, list):
        quests_options = [quests_options]
        print('test:')
        print(quests_options)

    names = []

    for name in quests_options:
        
        names.append(name[0] + ' (' + name[1] + ')')
            
    print(names)

    return [name for name in names if ctx.value.lower() in name.lower()]

@guilda.command(name='cancelar_quest', description='Este comando permite que você cancele uma quest criada por você que ainda não foi aceita')
async def cancelar_quest_command(
    ctx: discord.ApplicationContext,
    quest: discord.Option(str, autocomplete=get_user_created_quests, name='quest')
):
    user = ctx.author.id
    
    real_name, _type = quest.split(' (')
    
    _type = _type.strip(')')
    
    anilist_id = dbservice.select('quests', ['id_anilist'], '', {'sender': user, 'item_name': real_name})
    
    print('anilist_id')
    print(anilist_id)

    ts = int(datetime.datetime.now().timestamp() + 259200)
    
    due_date = dbservice.select('user', ['quest_cancel_due_date'], '', {'id': user})
    
    print('due date')
    print(str(due_date))
    
    print('now')
    print(ts)
    
    if due_date == None or datetime.datetime.now().timestamp() >= due_date:
        data_cd = datetime.datetime.utcfromtimestamp(ts).strftime('%d-%m-%Y %H:%M:%S')
        
        flavor1, flavor2 = dbservice.select('quests', ['flavor_text'], '', {'sender': user, 'id_anilist': anilist_id}).split('*')
        
        msg = f'❌ A quest *{flavor1}**{real_name} ({_type})**{flavor2}* foi deletada pelo criador.'
        
        await generate_guild_log(msg)
    
        dbservice.delete('quests', {'sender': user, 'id_anilist': anilist_id})
        dbservice.update('user', ['quest_cancel_due_date'], [ts], {'id': user})
    
        await ctx.response.send_message(f'Quest cancelada com sucesso. Você poderá cancelar outra quest em {data_cd}.', ephemeral=True)

    
    else:
        
        data_cd = datetime.datetime.utcfromtimestamp(due_date - 10800).strftime('%d-%m-%Y %H:%M:%S')
        
        await ctx.response.send_message(f'Não foi possível cancelar a quest. Você só poderá cancelar outra quest em {data_cd}.', ephemeral=True)
   
@guilda.command(name='formar_grupo')
async def formar_grupo_command(
    ctx: discord.ApplicationContext,
    quest: discord.Option(str, autocomplete=get_quests_options, name='quests', required=True),
    membro1: discord.Option(str, autocomplete=get_members_names2, name='primeiro_membro', required=True),
    membro2: discord.Option(str, autocomplete=get_members_names2, name='segundo_membro', required=False),
    membro3: discord.Option(str, autocomplete=get_members_names2, name='terceiro_membro', required=False),
    membro4: discord.Option(str, autocomplete=get_members_names2, name='quarto_membro', required=False)
):
    _possible = [membro1, membro2, membro3, membro4]

    leader = dbservice.select('user', ['name'], '', {'id': ctx.author.id})    
    
    group = []
    
    for member in _possible:
        if member != None:
            group.append(member)

    taken_quests = dbservice.select('quests', ['party'], '', {'is_available': 'false'})
    print('taken_quests')
    print(taken_quests)
    
    if not isinstance(taken_quests, list):
        taken_quests = [taken_quests]
    
    for party in taken_quests:
        print('party')
        print(party)
        if party[0] != None:
            members = party.split(',')
            if bool(set(members).intersection(group)) == True:
                 await ctx.response.send_message(f'Um ou mais aventureiros do grupo não podem participar da quest.', ephemeral=True)
                 return
        
    quest_name, type = quest.split(' (')
    tipo = type.strip(')')
    
    party_text = ''
    for member in group:
        member_id = dbservice.select('user', ['id'], '', {'name': member})
        if member_id == dbservice.select('quests', ['sender'], '', {'item_name': quest_name, 'item_type': tipo}):
            await ctx.response.send_message(f'Um ou mais aventureiros do grupo não podem participar da quest.', ephemeral=True)
            
        party_text += str(member_id) + ','
        
    party_text = party_text.rstrip(',')
    
    dbservice.update('quests', ['party', 'is_available', 'date_bought'], [party_text, 'false', int(datetime.datetime.now().timestamp())], {'item_name': quest_name, 'item_type': tipo})
    
    flavor1, flavor2 = dbservice.select('quests', ['flavor_text'], '', {'item_name': quest_name, 'item_type': tipo}).split('*')

    msg = f'Um grupo de aventureiros foi formado para cuidar da quest *{flavor1}**{quest}**{flavor2}*. Seus membros são {leader}'
    
    idx = 1
    
    for member in group:
        if member == leader:
            pass
        if idx == len(group):
            msg += f' e {member}'
        else:
            idx += 1
            msg += f', {member}'
    
    await ctx.response.send_message('Grupo criado com sucesso!', ephemeral=True)
        
    time_passed = int(datetime.datetime.now().timestamp()) - int(dbservice.select('quests', ['date_inserted'], '', {'item_name': quest_name, 'item_type': tipo}))
    print('time elapsed: ' + str(time_passed))
        
    days = floor(time_passed / 86400)
    print('days: ' + str(days))
    
    base_value = dbservice.select('quests', ['value'], '', {'item_name': quest_name, 'item_type': tipo})
        
    reward = calculate_quest_reward(base_value, days)
    
    buyer_reward = floor(reward/len(group))
    
    sender_reward = ceil(reward/2)
        
    msg = msg.rstrip(',') + f'. Cada aventureiro receberá ${str(buyer_reward)} e o criador receberá ${str(sender_reward)} na finalização da quest, que deverá ser entregue pelo líder {leader}.'
    
    await generate_guild_log(msg)
    
# THRESHOLD:
#
# NEEDS TO SAVE PREVIOUSLY THRESHOLD SO IT WON'T SPAM THE LOG

# @tasks.loop(seconds=60)
# async def check_quests():
    
#     thresholds = [10, 25, 50, 75, 100, 250, 500, 750, 1000, 1500, 2000, 3000, 4000, 5000, 10000, 25000, 50000]
    
#     quests = dbservice.select('quests', ['id_anilist', 'item_name', 'item_type', 'value', 'date_inserted', 'flavor_text'], '', {'is_available': 'true'})
    
#     for quest in quests:
#         time_passed = int(datetime.datetime.now().timestamp()) - int(quest[4])
#         days = floor(time_passed / 86400)
#         reward = calculate_quest_reward(quest[3], days)
        
#         flavor1, flavor2 = quest[5].split('*')
        
#         last_threshold = 0
        
#         for threshold in thresholds:
#             if reward >= threshold:
#                 last_threshold = threshold
#             else:
#                 msg = f'📈 A quest *{flavor1}**{quest[1]} ({quest[2]})**{flavor2}* valorizou e ultrapassou o valor de ${str(last_threshold)}, chegando a ${str(reward)}.'
        

# to do

# criar canal que mantém o quadro sempre exposto e atualizado ao vivo
# sistema de log por threshold atingido na recompensa das quests
# pensar no sistema de upvote e downvote do nico
# pensar em sistema de raid
# sistema de waifus a la ab + amq

##############################
#
# IDEIA
#
# Desafios cooperativos
#
# o bot ou algo do tipo escolherá um grupo de obras a serem terminadas
#
# após terminar uma quantidade mínima das obras, outro pacote de desafios é liberado

# Auxiliar command
@bot.command(name='aux')
async def aux_command(ctx):

    if ctx.author.id in admins:
        type_factor = 0.004
        total_duration = 5025
        duration_factor = 1 + (total_duration * type_factor)
                
        hours = floor(total_duration / 60)
                
        size_factor = 1 + ((hours - 1)/20)
        print('size factor')
        print(str(size_factor))
            
        reward = ceil(((100 * duration_factor) - 100) * size_factor)

        print(get_timestamp() + ': Done')

config = configparser.RawConfigParser()
config.read('app.properties')
token = config.get('Discord', 'token')
bot.run(token)