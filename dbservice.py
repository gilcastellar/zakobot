import database

def update(table, columns, values, where_col, where_val):

    sql = 'UPDATE ' + table + ' SET '

    idx = 0

    for column in columns:

        if idx != 0:

            sql += ', '

        sql += column + '="' + values[idx] + '"'
        idx += 1

    sql += ' WHERE ' + where_col + '="' + where_val + '"'

    print(sql)
    
    database.update(sql)

def insert(table, columns, values):

    sql = 'INSERT INTO ' + table + ' ('

    val = '('

    _val = '('

    for column in columns:

        sql += column + ','

        _val += '%s,'

    for value in values:

        val += '"' + value + '",'

    _val = _val.strip(',') + ')'
    
    val = val.strip(',') + ')'

    sql += ') VALUES ' + _val

    print(sql)
    print(val)
