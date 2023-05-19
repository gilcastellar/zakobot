import database

def update(table, columns, values, where_col, where_val):

    sql = 'UPDATE ' + str(table) + ' SET '

    idx = 0

    for column in columns:

        if idx != 0:

            sql += ', '

        sql += str(column) + '="' + str(values[idx]) + '"'
        idx += 1

    sql += ' WHERE ' + str(where_col) + '="' + str(where_val) + '"'

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

            sql += i + '="' + where[i] + '",'

        sql = sql.strip(',')

    print(sql)

    ...

