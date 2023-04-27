'''
This script is for tagging oes_national data with occupation(career) when only national data is updated from imported excel file.
remove the previous collection and insert updated data.
so the relation with occupation is destroyed. that's why we have to create the relation(tagging)
Working Procedure:
1. get all occupations
2. create occupation_code using soc_code
3. using the occupation_code, find out the according oes_national data
4. then tag the data, and update to mongodb
'''


from pymongo import MongoClient
from models.product.product import Product
from models.product.topic import Provider, Vendor, TopSkill
from models.product.embeded_doc import Module
from mongoengine import connect, disconnect
from models.occupation.occupation import Occupation
from models.occupation.occupational_employment_statistics import OccupationalEmploymentStatistics


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


def tag_national_with_occupation():
    mongo_connect()
    occupations = Occupation.objects.all()
    length = occupations.count()
    count = 0
    success = 0
    for data in occupations:
        count += 1
        if count <=200:
            continue
        soc_codes = data.soc_code.split(".")
        if soc_codes[0] is not None:
            occupation_code = soc_codes[0]
        else:
            print("Soc Code Error ", data.id)
            continue
        try:
            occ_emp_stats = OccupationalEmploymentStatistics.objects.filter(occupation_code=occupation_code).first()
        except Exception as e:
            print(e)
            print(" Occupation Error ", data.id, occupation_code)
            continue
        else:
            data.oes_national = occ_emp_stats
            data.save()
            success += 1

        print("total " + str(count) + ", success " + str(success) + " of " + str(length))
        # if count >= 200:
        #     break

if __name__ == '__main__':
    tag_national_with_occupation()
