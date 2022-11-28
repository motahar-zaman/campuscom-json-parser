import json
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
        conn = mysql.connector.connect(**config)

        self.connection = conn

    def connect(self):
        return self.connection


def check_exists(config, tablename, id_field, provided_by, name):
    database = Database(config)
    connection = database.connect()
    cursor = connection.cursor()
    sql = f"SELECT {id_field}, COUNT(*) FROM {tablename} WHERE provided_by = %s AND name = %s GROUP BY {id_field}"

    cursor.execute(sql, (provided_by, name))
    # execute statement same as above  
    msg = cursor.fetchone()
    # check if it is empty and print error
    if msg:
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
        unknown_keys = set(rowdict) - allowed_keys
        print(tablename)
        print('unknown keys: ', unknown_keys)

    columns = ", ".join(keys)
    values_template = ", ".join(["%s"] * len(keys))

    sql = "insert into %s (%s) values (%s)" % (
        tablename, columns, values_template)
    values = tuple(rowdict[key] for key in keys)

    cursor.execute(sql, values)
    row_id = cursor.lastrowid
    connection.commit()
    return row_id


def update_row(config, tablename, rowdict, row_id):
    database = Database(config)
    connection = database.connect()
    cursor = connection.cursor()
    cursor.execute("describe %s" % tablename)
    allowed_keys = set(row[0] for row in cursor.fetchall())
    keys = allowed_keys.intersection(rowdict)

    if len(rowdict) > len(keys):
        unknown_keys = set(rowdict) - allowed_keys
        print(tablename)
        print('unknown keys: ', unknown_keys)

    columns = ", ".join(keys)
    values_template = ", ".join(["%s"] * len(keys))

    sql = "UPDATE %s SET (%s) values (%s) WHERE id = (%s)" % (
        tablename, columns, values_template, row_id)
    values = tuple(rowdict[key] for key in keys)

    cursor.execute(sql, values)
    row_id = cursor.lastrowid
    connection.commit()
    return row_id
