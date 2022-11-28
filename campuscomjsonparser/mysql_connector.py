import sys
import mysql.connector
from logger import logger


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance


@singleton
class Database(object):
    def __init__(self, config):
        config.update({"raise_on_warnings": True})
        try:
            conn = mysql.connector.connect(**config)
        except mysql.connector.Error as e:
            logger(e, level=40)
            sys.exit('Could not connect to database')

        self.connection = conn

    def connect(self):
        return self.connection


def check_exists(config, tablename, id_field, product):
    database = Database(config)
    connection = database.connect()
    cursor = connection.cursor()
    sql = f"SELECT {id_field}, COUNT(*) FROM {tablename} WHERE provided_by = %s AND name = %s GROUP BY {id_field}"

    cursor.execute(sql, (product['provided_by'], product['name']))
    # execute statement same as above  
    msg = cursor.fetchone()
    # check if it is empty and print error
    if msg:
        print('existense: ', msg)
        return msg[0]
    return None


def add_row(config, tablename, rowdict):
    database = Database(config)
    connection = database.connect()
    cursor = connection.cursor()

    cursor.execute("describe %s" % tablename)
    allowed_keys = set(row[0] for row in cursor.fetchall())
    keys = allowed_keys.intersection(rowdict)

    if len(rowdict) > len(keys):
        sys.exit(f'column name mistach in table {tablename}')

    columns = ", ".join(keys)
    values_template = ", ".join(["%s"] * len(keys))

    sql = "insert into %s (%s) values (%s)" % (
        tablename, columns, values_template)
    values = tuple(rowdict[key] for key in keys)

    try:
        cursor.execute(sql, values)
        row_id = cursor.lastrowid
        connection.commit()
    except mysql.connector.Error as e:
        logger(e, level=40)
    return row_id


def update_row(config, tablename, rowdict, row_id):
    database = Database(config)
    connection = database.connect()
    cursor = connection.cursor()

    cursor.execute("describe %s" % tablename)
    allowed_keys = set(row[0] for row in cursor.fetchall())
    keys = allowed_keys.intersection(rowdict)

    if len(rowdict) > len(keys):
        sys.exit(f'column name mistach in table {tablename}')

    columns = "=%s, ".join(keys)

    sql = f"UPDATE {tablename} SET {columns} WHERE product_id = {row_id}"
    values = tuple(rowdict[key] for key in keys)
    import ipdb; ipdb.set_trace()
    try:
        cursor.execute(sql, values)
        row_id = cursor.lastrowid
        connection.commit()
    except mysql.connector.Error as e:
        logger(e, level=40)
    return row_id
