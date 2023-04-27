'''
This script is for importing data from mysql DB to mongodb of affiliate products(courses) which is from imported json files data.

set correct credentials of mysql and mongoDbB database into mongo_connect() and MySqlDatabase config variable
then run "python import_data_from_mysql_to_mongodb.py"

Working Procedure:
1. takes data from mysql DB which credentials are given
2. create required objects (product, vendor, skills, modules, topic, provider) accordingly
3. insert data into mongodb
'''


import mysql.connector
from pymongo import MongoClient
from models.product.product import Product
from models.product.topic import Provider, Vendor, Subject
from models.product.embeded_doc import Module
from models.history.import_history import ImportHistoryData
from mongoengine import connect, disconnect


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance


@singleton
class MySqlDatabase(object):
    # mysql database credentials
    config = {
        "host": "127.0.0.1",
        "port": 3306,
        "user": "zaman",
        "password": "Zaman@95",
        "database": "scrapped_courses_data",
        "use_unicode": True,
        "raise_on_warnings": True
    }
    def __init__(self):
        try:
            conn = mysql.connector.connect(**self.config)
        except mysql.connector.Error as e:
            logger(e, level=40)
            sys.exit('Could not connect to database')

        self.connection = conn

    def connect(self):
        return self.connection


def mongo_connect():
    #dev
    mongodb_host = 'ec2-18-188-170-233.us-east-2.compute.amazonaws.com'
    mongodb_database = 'campus'
    mongodb_port = 27017
    mongodb_username = 'cc-dev-admin-api'
    mongodb_password = 'FWPCIvc7McXRhg'
    mongodb_auth_database = 'admin'

    '''mongodb://zaman:zaman%4095@localhost:27017/?authSource=admin&readPreference=primary&appname=MongoDB%20Compass&ssl=false'''
    '''mongodb://cc-dev-admin-api:FWPCIvc7McXRhg@ec2-18-188-170-233.us-east-2.compute.amazonaws.com:27017/?authSource=admin&readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false'''
    # # local
    # mongodb_host = 'localhost'
    # mongodb_database = 'campus'
    # mongodb_port = 27017
    # mongodb_username = 'zaman'
    # mongodb_password = 'zaman@4095'
    # mongodb_auth_database = 'admin'

    disconnect()
    connect(mongodb_database, host=mongodb_host, port=int(mongodb_port), username=mongodb_username,
            password=mongodb_password, authentication_source=mongodb_auth_database)


def insert_mongo_from_mysql():
    mongo_connect()

    # my_sql connection
    my_sql_db = MySqlDatabase()
    connection = my_sql_db.connect()
    cursor = connection.cursor()

    # get time_to_complete column values by vendor
    # sql = f"SELECT * from updated_products"

    sql = f"SELECT * from updated_products WHERE vendor='Udemy'"
    cursor.execute(sql)
    products = cursor.fetchall()

    for idx, product in enumerate(products):
        # if idx < 15001: # 5th script
        # if idx < 9001: # 4th script
        # if idx < 6001: # 3rd script
        # if idx < 3004: # 2nd script
        #     continue

        # UPDATE product from mysql to mongo

        try:
            vendor = Vendor.objects.get(name='Udemy')
        except Vendor.DoesNotExist:
           continue

        try:
            product_obj = Product.objects.get(name=product[1], vendor=vendor)
        except Product.DoesNotExist:
            continue
        else:
            product_obj.url['affiliate_url'] = product[17]
            product_obj.save()
            print(product_obj.id, idx + 1, ' of ', len(products))
            continue
            

        # INSERT from mysql to mongodb
        # TODO => insert Lesson from lesson table for each module

        module_sql = f"SELECT * FROM modules WHERE product_id = {product[0]}"
        cursor.execute(module_sql)
        modules = cursor.fetchall()

        module_list = []
        for module in modules:
            module_obj = Module(
                name=module[1],
                short_desc=module[2],
                long_desc=module[3],
                time=module[4],
                lessons=module[5]
            )
            module_list.append(module_obj)

        # if product[12] == 'Coursera' or product[12] == 'Datacamp' or product[12] == 'Edureka':
        #     continue

        skill_sql = f"SELECT s.skill_id, s.name from skills as s INNER JOIN jn_product_skills as j ON j.skill_id = s.skill_id WHERE j.product_id = {product[0]}"
        cursor.execute(skill_sql)
        skills = cursor.fetchall()

        skill_list = []
        for skill in skills:
            skill_list.append(skill[1])

        topic_sql = f"SELECT t.topic_id, t.name, t.short_desc, t.long_desc, t.length from topics as t INNER JOIN jn_product_topics as j ON j.topic_id = t.topic_id WHERE j.product_id = {product[0]}"
        cursor.execute(topic_sql)
        topics = cursor.fetchall()

        topic_list = []
        for topic in topics:
            try:
                topic = Topic.objects.get(name=topic[1], short_desc=topic[2], long_desc=topic[3], length=topic[4])
            except Topic.DoesNotExist:
                topic = Topic.objects.create(name=topic[1], short_desc=topic[2], long_desc=topic[3], length=topic[4])

            topic_list.append(topic.id)

        try:
            provider = Provider.objects.get(name=product[7])
        except Provider.DoesNotExist:
            provider = Provider.objects.create(name=product[7])

        try:
            vendor = Vendor.objects.get(name=product[12])
        except Vendor.DoesNotExist:
            vendor = Vendor.objects.create(name=product[12])

        price = product[19]
        converted_price = 0
        if not price or price == 'Free':
            pass
        else:
            converted_price = product[19].split('$')[1]

        product_obj = Product(
            name=product[1],
            image={
                'original': product[18],
                'cover': product[18],
                'thumbnail': product[18]
            },
            url={
                'product_url': product[15],
                'affiliate_url': product[17]
            },
            price=converted_price,
            level=product[20],
            short_desc=product[2],
            long_desc=product[3],
            user_rating=product[5],
            user_rating_count=product[6],
            provided_by=provider,
            type=product[8],
            language=product[16],
            total_enrolled=product[9],
            time_to_complete=int(product[10]),
            vendor=vendor,
            related_job_titles=[],
            keywords=product[21].split() if product[21] else [],
            skills=skill_list,
            modules=module_list,
            topics=topic_list,
            top_20=0
        )
        product_obj.save()
        print(product_obj.id, idx + 1, ' of ', len(products))
        # import ipdb; ipdb.set_trace()
        # if idx >= 15000:
        #     break



if __name__ == '__main__':
    insert_mongo_from_mysql()
