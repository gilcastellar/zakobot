import database

def update(table, columns, values, where):

    query = "SELECT COUNT(1) FROM " + str(table) + " WHERE "

    print(where)

    for i in where:

        query += i + '="' + str(where[i]) + '" AND '

    query = query.rstrip(' AND ')

    exists = database.check_existence(query)

    print('exists')
    print(exists)

    if exists == 1:

        query = "UPDATE " + str(table) + " SET "

        idx = 0

        for column in columns:

            if idx != 0:

                query += ", "

            query += str(column) + "='" + str(values[idx]) + "'"
            idx += 1

        query += " WHERE "

        for i in where:

            query += i + "='" + str(where[i]) + "' AND "

        query = query.rstrip(" AND ")

        print(query)
    
        database.update(query)

    return exists

def update_zakoleta(table, quantity, log, user_id, operation):

    if operation == 'add':

        query = 'UPDATE ' + table + ' SET zakoleta=zakoleta+' + str(quantity) + ', zakoleta_log=concat(zakoleta_log, "' + log + '") WHERE id="' + str(user_id) + '"'

    if operation == 'sub':
        
        query = 'UPDATE ' + table + ' SET zakoleta=zakoleta-' + str(quantity) + ', zakoleta_log=concat(zakoleta_log, "' + log + '") WHERE id="' + str(user_id) + '"'
        
    print(query)

    database.update(query)

def insert(table, columns, val, ignore=False):

    if ignore:
        query = 'INSERT IGNORE INTO ' + table + ' ('

    else:
        query = 'INSERT INTO ' + table + ' ('

    _val = '('

    for column in columns:

        query += str(column) + ','

        _val += '%s,'

    query = query.rstrip(',')

    _val = _val.rstrip(',') + ')'

    query += ') VALUES ' + _val

    #print(query)
    #print(val)

    return database.insert(query, val)

def select(table, columns, extra, where=''):

    query = 'SELECT '

    if columns == []:

        query += '*'

    else:

        for column in columns:

            query += str(column) + ','

        query = query.strip(',')

    query += ' FROM ' + table

    if where != '':

        query += ' WHERE '

        for i in where:

            query += i + '="' + str(where[i]) + '" AND '

        query = query.rstrip(' AND ')


    if extra != '':

        query += ' ' + extra

    #print(query)

    response = database.select(query)

    if len(response) == 1:

        if len(response[0]) == 1:

            return response[0][0]

        else:

            return response[0]

    else:
        
        return response

def check_existence(table, where):

    query = 'SELECT COUNT(1) FROM ' + str(table) + ' WHERE '

    for i in where:

        query += i + '="' + str(where[i]) + '" AND '

    query = query.rstrip(' AND ')

    print(query)

    return database.check_existence(query)

def drop(table):

    sql = 'DROP TABLE ' + table

    database.execute(sql)

def create(table, extra):

    sql = 'CREATE TABLE IF NOT EXISTS ' + table + extra
    
    database.execute(sql)

def truncate(table):

    sql = 'TRUNCATE TABLE ' + table 

    database.execute(sql)

def delete(table, where):

    query = 'DELETE FROM ' + table + ' WHERE '

    for i in where:

        query += i + '="' + str(where[i]) + '" AND '
        
    query = query.rstrip(' AND ')

    print(query)

    database.execute(query)