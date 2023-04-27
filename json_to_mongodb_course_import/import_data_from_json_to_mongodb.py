'''
    This script is for updating mongodb affiliate product(course) data from imported json files data.

    set the file_path variable with your file location and name,
    set correct credentials for mongoDbB database into mongo_connect()
    then run "python import_data_from_json_to_mongodb.py"

    Working Procedure:
    1. takes data from the given path of a json file
    2. find out the product object by title(name) and vendor
    3. update the fields which required
    4. update the object to mongodb
'''

import mysql.connector
from pymongo import MongoClient
from models.product.product import Product
from models.product.topic import Provider, Vendor, Subject
from models.product.embeded_doc import Module, Lesson
from mongoengine import connect, disconnect
import json


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


def update_mongo_from_json():
    mongo_connect()

    file_path = '/home/zaman/Documents/Scrap/Full Scrapes/linkedin_final.json'
    with open(file_path) as f:
        datas = json.load(f)
        length = len(datas)
        errors = {}
        count = 0
        for idx, data in enumerate(datas):
            if idx < 4400:
                continue
            try:
                vendor = Vendor.objects.get(name=data['Vendor'])
            except Vendor.DoesNotExist:
                vendor = Vendor.objects.create(name=data['Vendor'])

            try:
                product = Product.objects.get(name=data['Learning Product Name'], vendor=vendor)
            except Product.DoesNotExist:
                count += 1
                errors[idx] = {
                    'product_name': data['Learning Product Name'],
                    'vendor': data['Vendor'],
                    'error': 'product not found in mongodb'
                }
                print(idx, "product not found with title '" + data['Learning Product Name'] + "'")
                continue
            else:

                # update user_rating data
                # product.user_rating = data['UserRating']
                # product.save()


                # update modules and Lessons data
                product_modules = product.modules
                json_modules = data['Modules']
                modules = []

                for json_module in json_modules:
                    find = False
                    for product_module in product_modules:
                        if json_module['Module Name'] and product_module['name'] == json_module['Module Name']:
                            find = True
                            break
                        else:
                            if product_module['name'] == '' and json_module['Module Name'] == '' and len(json_modules) == 1:
                                find = True
                                break
                    if not find:
                        json_lessons = json_module['Lesson']
                        lesson_list = []
                        for json_lesson in json_lessons:
                            lesson_obj = Lesson(
                                name=str(json_lesson['Lesson Name']),
                                long_desc=json_lesson['Lesson Description'],
                                type=json_lesson['Type']
                            )
                            lesson_list.append(lesson_obj)

                        modules.append(
                            Module(
                                name=json_module['Module Name'],
                                short_desc=None,
                                long_desc=json_module['Module Description'],
                                time=json_module['Time'],
                                lessons=lesson_list
                            )
                        )
                product.modules = product_modules + modules
                product.save()


                # update subjects data
                # subject_list = []
                # subjects = data['Learning Product Category']
                # for subject in subjects.split(','):
                #     subject = subject.strip()
                #     try:
                #         subject_obj = Subject.objects.get(name=subject)
                #     except Subject.DoesNotExist:
                #         subject_obj = Subject.objects.create(name=subject)
                #     subject_list.append(subject_obj.id)

                # update topics data
                # try:
                #     product.topics = [topic['Topic Name'] for topic in data['Topics']]
                # except Exception as e:
                #     product.topics = [topic for topic in data['Topics']]
                # product.subjects = subject_list
                # product.save()
                print(product.id, idx + 1, ' of ', length)
            # if idx >= 4400:
            #     break



if __name__ == '__main__':
    update_mongo_from_json()
