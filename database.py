﻿import mysql.connector
import json
import configparser




config = configparser.RawConfigParser()
config.read('app.properties')
user = config.get('Database', 'user')
password = config.get('Database', 'password')
host = config.get('Database', 'host')
port = config.get('Database', 'port')
database = config.get('Database', 'database')


id_guild = '1059298932825538661'

#with open('roulette_members.json', 'r') as file:
#    roulette_members = json.load(file)
#    for member in roulette_members:
#        id = member['id']
#        name = member['nome']
#        points = member['pontos']

#        sql = "INSERT INTO member (id_discord, id_guild, name, points) VALUES (%s, %s, %s, %s)"
#        val = (id,id_guild,name,points)
#        print(val)
#        cur.execute(sql, val)
#        db.commit()



#cur.execute('SELECT * FROM users WHERE id_discord="129635640122933248"')

#myresult = cur.fetchall()
#print(myresult)

#if len(myresult) < 1:
#    sql = "INSERT INTO users (id_discord, id_guild, name) VALUES (%s, %s, %s)"
#    val = ('129635640122933248','1059298932825538661','juan')
#    cur.execute(sql, val)
#    db.commit()

#for result in myresult:
#    print(result)


#sql = 'DELETE FROM members WHERE name = "kaiser"'

#cur.execute(sql)

#db.commit()

def connect_db():
    _user = config.get('Database', 'user')
    _password = config.get('Database', 'password')
    _host = config.get('Database', 'host')
    _port = config.get('Database', 'port')
    _database = config.get('Database', 'database')
    return mysql.connector.connect(user=_user,
                password=_password,
                host=_host,
                port=_port,
                database=_database)

    
def query_user_id(user_id):
    db = connect_db()

    cur = db.cursor()
    cur.execute('SELECT id FROM user WHERE id_discord="' + str(user_id) + '"')
    return cur.fetchall()

def profile_query(user_id):
    db = connect_db()

    cur = db.cursor()
    id = query_user_id(user_id)
    cur.execute('SELECT * FROM member_has_roleta JOIN member ON member_has_roleta.member_id=member.id JOIN roleta ON member_has_roleta.roleta_id=roleta.id AND member.id="' + str(id[0][0]) + '"')

    desc = cur.description
    column_names = [col[0] for col in desc]
    return [dict(zip(column_names, row))  
        for row in cur.fetchall()][0]

def temp_update_profile():
    db = connect_db()

    cur = db.cursor()
    with open('roulette_members.json', 'r') as file:
        roulette_members = json.load(file)
        for member in roulette_members:
            print(member['id'])
            id = query_user_id(member['id'])[0][0]
            print(id)
            obs = member['obs']
            ativo = member['ativo']
            tipo = member['tipo']

            #cur.execute("SELECT member_id FROM member_has_roleta")

            #ids = cur.fetchall()

            #for i in range(len(ids)):
            #    if id not in ids[i]:
            sql = "INSERT INTO member_has_roleta (member_id, roleta_id, obs, ativo, tipo) VALUES (%s, %s, %s, %s, %s)"
            val = (id,1,obs,ativo,tipo)
            print(val)
            cur.execute(sql, val)
            db.commit()

#def select(sql):
#    db = connect_db()

#    cur = db.cursor()
#    cur.execute(sql)

#    return cur.fetchone()[0]

def select(sql):
    db = connect_db()

    cur = db.cursor()
    cur.execute(sql)

    return cur.fetchall()

def execute(sql):
    db = connect_db()

    cur = db.cursor()
    cur.execute(sql)
    
    db.commit()

def check_existence(query):
    db = connect_db()

    cur = db.cursor()
    cur.execute(query)

    return cur.fetchone()[0]

def check_if_exists_two(item1, item2, column1, column2, table):
    db = connect_db()

    cur = db.cursor()
    cur.execute('SELECT COUNT(1) FROM ' + table + ' WHERE ' + column1 + '=' + item1 + ' AND ' + column2 + '=' + item2)

    return cur.fetchone()[0]

def selectall(sql, fix=False):
    db = connect_db()

    cur = db.cursor()
    cur.execute(sql)

    if fix:
        fixed = []

        for i in cur.fetchall():
            fixed.append(i[0])

        return fixed
    else:

        return cur.fetchall()
    #return cur.description

def insert(sql, val):
    db = connect_db()

    cur = db.cursor()
    cur.execute(sql,val)
    db.commit()

    return cur.lastrowid

def update(sql):
    db = connect_db()

    cur = db.cursor()
    #sql = 'INSERT INTO ' + table + ' (' + column + ') VALUES ("' + text + '") WHERE member_id=' + user_id
    #print(sql)
    cur.execute(sql)
    db.commit()

#temp_update_profile()