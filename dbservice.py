import database

def update(table, columns, values, where):

    sql = 'UPDATE ' + str(table) + ' SET '

    idx = 0

    for column in columns:

        if idx != 0:

            sql += ', '

        sql += str(column) + '="' + str(values[idx]) + '"'
        idx += 1

    for i in where:

        sql += i + '="' + str(where[i]) + '",'

    sql = sql.strip(',')

    print(sql)
    
    database.update(sql)

def insert(table, columns, val):

    sql = 'INSERT INTO ' + table + ' ('

    _val = '('

    for column in columns:

        sql += str(column) + ','

        _val += '%s,'

    sql = sql.strip(',')

    _val = _val.strip(',') + ')'

    sql += ') VALUES ' + _val

    print(sql)
    print(val)

    database.insert(sql,val)


def select(table, columns, where=''):

    sql = 'SELECT '

    for column in columns:

        sql += str(column) + ','

    sql = sql.strip(',')

    sql += ' FROM ' + table

    if where != '':

        sql += ' WHERE '

        for i in where:

            sql += i + '="' + str(where[i]) + '",'

        sql = sql.strip(',')

    print(sql)

    response = database.select_t(sql)

    if len(response) == 1:

        if len(response[0]) == 1:

            return response[0][0]

        else:

            return response[0]

    else:
        
        return response

