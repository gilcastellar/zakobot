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
    ...