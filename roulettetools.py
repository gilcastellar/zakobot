from pickle import FALSE
import random
import json
from xml.etree.ElementPath import find

roulette_members = []

def create_roulette():
    return []

#def add_roulette_member(list, members):
#    members = members.split(',')
#    for member in members:
#        if member not in list:
#            list.append(member)
#    return list

#def remove_roulette_member(list, members):
#    members = members.split(',')
#    for member in members:
#        if member in list:
#            list.remove(member)
#    return list

def shuffle_roulette(previous_roulette):
    members = []

    fully_compatible = 'not'
    
    with open('roulette_members.json', 'r') as file:
        roulette_members = json.load(file)

        for d in roulette_members:
            if d['ativo'].lower() == 'sim':
                members.append(d['id'])
    
    while fully_compatible != 'yes':
        random.shuffle(members)
        fully_compatible, roulette = compatibility_check(members, previous_roulette)

    return roulette, members

def compatibility_check(members, previous_roulette):
    roulette = ''
    index = 0

    for member in members:
        if index != len(members) - 1: # checks for last member
            n = find_member(members[index+1])
        else:
            n = find_member(members[0])
        d = find_member(member)
        if d['tipo'] == 'manga':
            if n['tipo'].lower() == 'anime':
                return 'not',''
        elif d['tipo'].lower() == 'anime':
            if n['tipo'].lower() == 'manga':
                return 'not',''

        # The below section creates a new string containing 
        # the new roulette while checking if no one is paired together again

        with open('original_roulette.txt') as file:
            file = file.read()
            print(file)
            print(str(d['id']) + ',' + str(n['id']))
            if (str(d['id']) + ',' + str(n['id'])) in file:
                return 'not',''

        roulette = roulette + ' ' + d['nome'] + ' -> ' + n['nome'] + '\n' 

        index += 1

    return 'yes', roulette


def find_member(id):

    with open('roulette_members.json','r') as file:
                    
        roulette_members = json.load(file)
        for d in roulette_members:
            if d['id'] == id:
                return d


def compability_check(r,z):
    
    # + sends anime
    # - sends manga
    # ~ only receives anime
    # . only receives manga
    symbols = ["+","-","~","."]

    # invokes new_roulette
    new_roulette = ''

    index = 0

    for member in r:
        if symbols[0] not in member: # checks if member can't send anime
            if index != len(r) - 1: # checks for last member
                if symbols[2] in r[index + 1]: # checks if next member only accepts anime
                    return 'not', ''
            else:
                if symbols[2] in r[0]: # checks if next member only accepts anime
                    return 'not', ''
                
        if symbols[1] not in member: # checks if member can't send manga
            if index != len(r) - 1: # checks for last member
                if symbols[3] in r[index + 1]: # checks if next member only accepts manga
                    return 'not', ''
            else:
                if symbols[3] in r[0]: # checks if next member only accepts manga
                    return 'not', ''
        
        # The below section creates a new string containing 
        # the new roulette while checking if no one is paired together again

        if index == len(r) - 1:
            new_roulette = new_roulette + ' ' + member.strip('+-.~') + ' ' + r[0].strip('+-.~') #
        
        elif r[index].strip('+-.~') + ' ' + r[index+1].strip('+-.~') in z: # 
            return 'not', ''
        else:
            new_roulette = new_roulette + ' ' + member.strip('+-.~')

        index += 1

    return 'yes', new_roulette
def format(r):
    result = ''

    index = 0
    
    for member in r:
        if index != len(r) - 1: # checks for last member
            result += member.strip('+-.~') + ' -> ' + r[index + 1].strip('+-.~') + '\n'
        else:
            result += member.strip('+-.~') + ' -> ' + r[0].strip('+-.~') + '\n'
        index += 1

    return result



