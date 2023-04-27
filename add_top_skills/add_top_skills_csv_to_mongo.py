'''
This script is for adding top 20 courses(products) from csv file.
the file columns are as: 'Top_Skills', 'Course_Title', 'Vendor', 'Rank'

set the file_path variable with your file location and name
then run "python add_top_skills_csv_to_mongo.py"

Working Procedure:
1. find or create the top_skill object of TopSkill model(collection)
2. find the product(course) by title and vendor
3. then append the top_skills field with the top_skill object and rank accordingly
'''

import pandas as pd
import csv
from pymongo import MongoClient
from models.product.product import Product
from models.product.topic import Provider, Vendor, TopSkill
from models.product.embeded_doc import Module
from mongoengine import connect, disconnect


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


def insert_mongo_from_csv():
    mongo_connect()
    file_path = "recommended_courses_ordering_recommended_courses.csv"
    with open(file_path, 'r') as file:
        list_data = csv.reader(file)

        count = 0
        not_count = 0
        not_found = []
        for indx, item in enumerate(list_data):
            if indx < 1:
                continue

            try:
                top_skill_obj = TopSkill.objects.get(name=item[0])
            except TopSkill.DoesNotExist:
                top_skill_obj = TopSkill.objects.create(name=item[0])

            try:
                vendor = Vendor.objects.get(name=item[3])
            except Vendor.DoesNotExist:
                not_count += 1
                not_found.append({
                    'top_skill_id': str(top_skill_obj.id),
                    'vendor': item[3],
                    'product_name': item[2].strip('"'),
                    'rank': item[4]
                })
                print("Vendor not found", top_skill_obj.id, count)
                continue

            try:
                product_obj = Product.objects.get(name=item[2].strip('"'), vendor=vendor)
            except Product.DoesNotExist:
                not_count += 1
                not_found.append({
                    'top_skill_id': str(top_skill_obj.id),
                    'vendor': item[3],
                    'product_name': item[2].strip('"'),
                    'rank': item[4]
                })
                print("Product not found", top_skill_obj.id, count)
                continue
            else:
                product_obj.top_skills.append({'top_skill': top_skill_obj.id, 'rank': item[4]})
                product_obj.save()
                count += 1
                print(product_obj.id, top_skill_obj.id, count, not_count)
        print("found and add " + str(count) + ", not_found " + str(not_count))
        print("not_found items = ", not_found)

if __name__ == '__main__':
    insert_mongo_from_csv()
