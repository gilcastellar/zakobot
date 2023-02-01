from pickle import FALSE
import random
import json
from xml.etree.ElementPath import find

roulette_members = []

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
        fully_compatible, roulette, pairs = compatibility_check(members, previous_roulette)

    return roulette, members, pairs

def compatibility_check(members, previous_roulette):
    roulette = ''
    pairs = []
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
            if (str(d['id']) + ',' + str(n['id'])) in file:
                return 'not',''

        roulette = roulette + ' ' + d['nome'] + ' -> ' + n['nome'] + '\n'
        pairs.append(d['nome'] + ' -> ' + n['nome'])

        index += 1

    return 'yes', roulette, pairs


def find_member(id):

    with open('roulette_members.json','r') as file:
                    
        roulette_members = json.load(file)
        for d in roulette_members:
            if d['id'] == id:
                return d
            
