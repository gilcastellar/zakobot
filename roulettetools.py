from pickle import FALSE
import random

def create_roulette():
    return []

def add_roulette_member(list, members):
    members = members.split(',')
    for member in members:
        if member not in list:
            list.append(member)
    return list

def shuffle_roulette(r):
    compatible = False

    while compatible == False:
        random.shuffle(r)
        if compability_check(r) == True:
            compatible = True

    return r

def compability_check(r):
    
    # + sends anime
    # - sends manga
    # ~ only receives anime
    # . only receives manga
    symbols = ["+","-","~","."]

    index = 0

    for member in r:
        if symbols[0] not in member: # checks if member can't send anime
            if index != len(r) - 1: # checks for last member
                if symbols[2] in r[index + 1]: # checks if next member only accepts anime
                    return False
            else:
                if symbols[2] in r[0]: # checks if next member only accepts anime
                    return False
                
        if symbols[1] not in member: # checks if member can't send manga
            if index != len(r) - 1: # checks for last member
                if symbols[3] in r[index + 1]: # checks if next member only accepts manga
                    return False
            else:
                if symbols[3] in r[0]: # checks if next member only accepts manga
                    return False
        index += 1

    return True

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



