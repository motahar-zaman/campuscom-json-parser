import mysql.connector

def add_row(config, tablename, rowdict):
    conn = mysql.connector.connect(
        host=config['host'],
        user=config['username'],
        password=config['password'],
        port=config['port'],
        database=config['database']
    )

    cursor = conn.cursor()
    # filter out keys that are not column names
    cursor.execute("describe %s" % tablename)
    allowed_keys = set(row[0] for row in cursor.fetchall())
    keys = allowed_keys.intersection(rowdict)

    if len(rowdict) > len(keys):
        unknown_keys = set(rowdict) - allowed_keys
        print('unknown keys: ', unknown_keys)

    columns = ", ".join(keys)
    values_template = ", ".join(["%s"] * len(keys))

    sql = "insert into %s (%s) values (%s)" % (
        tablename, columns, values_template)
    values = tuple(rowdict[key] for key in keys)

    # print('sql: ', sql)
    # print('values: ', values)
    # return ''

    cursor.execute(sql, values)
    return cursor.insert_id()
