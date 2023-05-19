async def update(table, columns, values):

    sql = 'UPDATE ' + table + ' SET '

    idx = 0

    for column in columns:
        if idx != 0:
            sql += ', '
        sql += column + '="' + values[idx] + '"'
        idx += 1

    print(sql)
    ...