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

def remove_roulette_member(list, members):
    members = members.split(',')
    for member in members:
        if member in list:
            list.remove(member)
    return list


def shuffle_roulette(r,z):
    compatible = 'not'

    while compatible != 'yes':
        random.shuffle(r)
        compatible, new_roulette = compability_check(r,z)

    return r, new_roulette

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



