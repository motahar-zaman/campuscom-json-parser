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
    cursor = connection.cursor(buffered=True)
    sql = f"SELECT {id_field}, COUNT(*) FROM {tablename} WHERE vendor = %s AND name = %s GROUP BY {id_field}"

    cursor.execute(sql, (product['vendor'], product['name']))
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
        return row_id
    except mysql.connector.Error as e:
        logger(f"Could not create item in table {tablename}", level=40)
        logger(f"Name: {rowdict.get('name', '')}", level=40)
        logger(e, level=40)
    return None


def update_row(config, tablename, rowdict, row_id):
    database = Database(config)
    connection = database.connect()
    cursor = connection.cursor()

    cursor.execute("describe %s" % tablename)
    allowed_keys = set(row[0] for row in cursor.fetchall())
    keys = allowed_keys.intersection(rowdict)

    if len(rowdict) > len(keys):
        sys.exit(f'column name mistach in table {tablename}')

    columns = ", ".join([key + '=%s' for key in keys])

    sql = f"UPDATE {tablename} SET {columns} WHERE product_id = {row_id}"
    values = tuple(rowdict[key] for key in keys)

    try:
        cursor.execute(sql, values)
        row_id = cursor.lastrowid
        connection.commit()

        return row_id
    except mysql.connector.Error as e:
        logger(f'Could not update row {row_id} in table {tablename}', level=40)
        logger(f"Name: {rowdict.get('name', '')}", level=40)
        logger(e, level=40)

    return None


def delete_children(data_map, product_id):
    database = Database(data_map)
    connection = database.connect()
    cursor = connection.cursor()

    # topics
    sql = f"SELECT topic_id from {data_map['product_topic_join_table_name']} WHERE product_id = {product_id}"
    cursor.execute(sql)
    topic_ids = cursor.fetchall()

    if len(topic_ids):
        # delete topics
        topic_list = [item[0] for item in topic_ids]
        sql = f"DELETE FROM {data_map['topic_table_name']} WHERE topic_id IN (" + ",".join(["%s"] * len(topic_ids)) + ')'
        cursor.execute(sql, topic_list)
        connection.commit()

        # delete from joint table
        sql = f"DELETE FROM {data_map['product_topic_join_table_name']} WHERE product_id = {product_id}"
        cursor.execute(sql)
        connection.commit()

    # skills
    sql = f"SELECT skill_id from {data_map['product_skill_join_table']} WHERE product_id = {product_id}"
    cursor.execute(sql)
    skill_ids = cursor.fetchall()

    if len(skill_ids):
        # delete skills
        skill_list = [item[0] for item in skill_ids]
        sql = f"DELETE FROM {data_map['skill_table_name']} WHERE skill_id IN (" + ",".join(["%s"] * len(skill_ids)) + ')'
        cursor.execute(sql, skill_list)
        connection.commit()

        # delete from joint table
        sql = f"DELETE FROM {data_map['product_skill_join_table']} WHERE product_id = {product_id}"
        cursor.execute(sql)
        connection.commit()

    # modules
    sql = f"DELETE FROM {data_map['module_table_name']} WHERE product_id = {product_id}"
    cursor.execute(sql)
    connection.commit()

    # this should also delete lessons

    return None
