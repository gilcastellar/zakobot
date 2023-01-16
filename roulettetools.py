import random

def create_roulette():
    return []

def add_roulette_member(list,members):
    members = members.split(',')
    for member in members:
        if member not in list:
            list.append(member)
    return list

def shuffle_roulette(r):
    random.shuffle(r)
    return r

def format(r):
    index = 0
    result = ''
    for member in r:
        if index != len(r) - 1:
            result += member + ' -> ' + r[index + 1] + '\n'
        else:
            result += member + ' -> ' + r[0] + '\n'
        index += 1
    return result

def roulette_members():
    return roulette_list