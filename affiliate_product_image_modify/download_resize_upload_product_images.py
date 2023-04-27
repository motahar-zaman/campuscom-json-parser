'''
this file is used to download affiliate product images, resize and upload to s3 bucket and update product image field

set mongodb credentials in mongo_connect() to connect with mongo database

set your directory to store images locally into img_path variable and resize_img_path variable to store modified images

set aws storage bucket credentials by AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME variables

run "python download_resize_upload_product_images.py" command to run the file
'''

from pymongo import MongoClient
from models.product.product import Product
from models.product.topic import Provider, Vendor, TopSkill
from models.product.embeded_doc import Module
from mongoengine import connect, disconnect
from models.occupation.occupation import Occupation
from models.occupation.occupational_employment_statistics import OccupationalEmploymentStatistics
import requests
from PIL import Image
import os
import boto3
import glob
from pathlib import Path
import json
import mimetypes


def mongo_connect():
    # dev
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


# function to download images from the products image url into a directory
def download_product_images():
    mongo_connect()
    count = 0

    # # for linkedin product url from products (dictionary key will be product_id, value will be url)
    # # then scrap image_url from the product by product_url using python scrapy and store in a json file
    # # then access the json file and download images from the image_url

    # try:
    #     vendor = Vendor.objects.get(name='Linkedin')
    # except Vendor.DoesNotExist:
    #     print("vendor not found")
    #     return false
    # else:
    #     products = Product.objects.filter(vendor=vendor)
    #     count = 0
    #     product_urls = {}
    #     for data in products:
    #         count += 1
    #         product_urls[str(data.id)] = data.url['product_url']
    #
    #     json_file_name = '/home/zaman/Documents/products_as_courses/linkedin_product_urls.json'
    #     with open(json_file_name, 'w', encoding='utf-8') as data:
    #         json.dump(product_urls, data, ensure_ascii=False, indent=4)
    #
    #     print('got url ', count)


    # # Scrapper code inside Scrappy project named repos/data_scrapper

    # import scrapy
    # import json
    #
    # class DataSpider(scrapy.Spider):
    #     name = 'data_scraping'
    #
    #     # for linkedin image download link scraping from linkedin product url
    #     start_urls = []
    #     with open('/home/zaman/Documents/products_as_courses/linkedin_product_urls.json') as f:
    #         # start_urls = ['https://www.linkedin.com/learning/teamwork-foundations-2020']
    #         datas = json.load(f)
    #         for key, value in datas.items():
    #             start_urls.append(value)
    #
    #     def parse(self, response, **kwargs):
    #         with open('/home/zaman/Documents/products_as_courses/linkedin_product_urls.json') as f:
    #             datas = json.load(f)
    #
    #         image_urls = {}
    #         r_url = response.request.url
    #         json_file_name = '/home/zaman/Documents/products_as_courses/linkedin_product_image_urls.json'
    #         for data in response.css('img.top-card__image').extract():
    #             image = data.split('data-delayed-url=')
    #             image_url = image[-1].strip('">')
    #
    #             for key, value in datas.items():
    #                 if value == r_url:
    #                     image_urls[key] = image_url.replace('amp;', '')
    #                     break
    #
    #         with open(json_file_name) as fp:
    #             datas = json.load(fp)
    #             datas.update(image_urls)
    #
    #         with open(json_file_name, 'w', encoding='utf-8') as d:
    #             json.dump(datas, d, ensure_ascii=False, indent=4)
    #
    #         print('--------------------------------')
    #         print("done")
    #         print('---------------------------------')
    #
    # # end of scrapper code


    # # download the images from image_url stored in a json file mapping with product_id
    # img_path = "/home/zaman/repos/Scripts/linkedin_product_images/"
    # with open('/home/zaman/Documents/products_as_courses/linkedin_product_image_urls2.json') as f:
    #     datas = json.load(f)
    #
    # for key, value in datas.items():
    #     image_url = value
    #     if image_url:
    #         try:
    #             response = requests.get(image_url)
    #             img_ext = mimetypes.guess_extension(response.headers.get('content-type', '').split(';')[0])
    #             image_name = img_path + key + img_ext
    #
    #             with open(image_name, "wb") as f:
    #                 f.write(response.content)
    #
    #         except Exception as e:
    #             print("-----------------------------------------------------")
    #             print(e)
    #             print("-----------------------------------------------------")
    #         else:
    #             count += 1
    # print('-----------------------------------')
    # print(count)
    # print('-----------------------------------')
    #
    # return True

    # download images from the image_url getting from products image field
    products = Product.objects.all()

    length = products.count()
    count = 0
    success = 0
    error = 0
    for data in products:
        count += 1
        # if count <= 4400:
        #     continue

        image_url = data.image.get("original", None)
        if image_url:
            try:
                image_name = img_path + str(data.id) + "." + image_url.split(".")[-1]
                response = requests.get(image_url)
                with open(image_name, "wb") as f:
                    f.write(response.content)
                    success += 1
            except Exception as e:
                error += 1
                print("-----------------------------------------------------")
                print(e)
                print("-----------------------------------------------------")

        print("total " + str(count) + ", success " + str(success) + " of " + str(length))
        # if count >= 5000:
        #     break
    return True


# function to resize images and make original, cover and thumbnail images into a directory
def resize_images():
    # directory of the image files
    img_path = "/home/zaman/repos/Scripts/linkedin_product_images/"
    resize_img_path = "/home/zaman/repos/Scripts/resize_linkedin_product_images/"
    card_img_width = 600
    thumbnail_img_width = 300

    dir_list = os.listdir(img_path)
    length = len(dir_list)
    count = 0
    errors = {}

    for file in dir_list:
        # if count < 1840:
        #     count += 1
        #     continue

        file_name = list(os.path.splitext(file))  # get root and extension of the file

        try:
            img_data = Image.open(
                img_path + file_name[0] + file_name[1])  # My image is a 200x374 jpeg that is 102kb large
        except Exception as e:
            errors[file] = e
            print(e)
            continue
        image_size = img_data.size

        card_ration = card_img_width / image_size[0]
        thumbnail_ration = thumbnail_img_width / image_size[0]

        # downsize the image with an ANTIALIAS filter (gives the highest quality)
        original_img = img_data
        card_img = img_data.resize((card_img_width, int(image_size[1] * card_ration)), Image.ANTIALIAS)
        thumbnail_img = img_data.resize((thumbnail_img_width, int(image_size[1] * thumbnail_ration)), Image.ANTIALIAS)

        try:
            if img_data.mode == 'RGBA' and file_name[1].lower() != '.png':
                file_name[1] = '.png'
            original_img.save(resize_img_path + file_name[0] + "_original" + file_name[1])
            card_img.save(resize_img_path + file_name[0] + "_cover" + file_name[1], optimize=True, quality=80)
            thumbnail_img.save(resize_img_path + file_name[0] + "_thumbnail" + file_name[1], optimize=True, quality=80)
        except Exception as e:
            errors[file] = e
            print(e)

        count += 1
        print("convert ", count, "of ", length)

    return True


# function to upload resize images into s3 bucket and update products image field accordingly
def upload_images_to_s3():
    # directory of the image files
    img_path = "/home/zaman/repos/Scripts/linkedin_product_images/"
    resize_img_path = "/home/zaman/repos/Scripts/resize_linkedin_product_images/"
    dir_list = os.listdir(img_path)
    mongo_connect()

    length = len(dir_list)
    count = 0
    errors = {}
    upload = 0
    update = 0

    # AWS S3 credentials and connection
    AWS_ACCESS_KEY_ID = 'AKIA2OCLDIYHVHKGGEPP'
    AWS_SECRET_ACCESS_KEY = '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'
    AWS_STORAGE_BUCKET_NAME = 'cc.dev.marketplace.resources.public'
    s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    for file in dir_list:
        count += 1
        # if count < 8000:
        #     continue
        file_name = os.path.basename(file)
        file_names = file_name.split('.')
        product_id = file_names[0]

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            continue
        else:
            re_image = resize_img_path + product_id + "*"
            re_image_path = glob.glob(re_image)

            for image in re_image_path:
                file_name = os.path.basename(image)
                file_names = file_name.split('_')
                image_type = file_names[-1].split('.')[-2]
                image_ext = file_names[-1].split('.')[-1]

                with open(image, 'rb') as f:
                    image_file = f.read()

                destination = 'assets/learning_products/'

                if image_type == 'original':
                    destination = destination + 'hero/' + str(product_id) + '.' + image_ext
                    product.image['original'] = destination

                elif image_type == 'cover' or image_type == 'card':
                    destination = destination + 'card/' + str(product_id) + '.' + image_ext
                    product.image['cover'] = destination

                elif image_type == 'thumbnail':
                    destination = destination + 'square/' + str(product_id) + '.' + image_ext
                    product.image['thumbnail'] = destination

                try:
                    response = s3_client.put_object(Bucket=AWS_STORAGE_BUCKET_NAME, Key=destination, Body=image_file)
                except Exception as e:
                    print(e)
                    errors[image] = e
                    continue
                else:
                    upload += 1
                    product.save()
                    update += 1
                    print("upload ", upload, "product_id ", product.id, update, count, " of ", length)

        # if count > 8000:
        #     break

    print(count, errors)
    return True


if __name__ == '__main__':
    download_product_images()
    resize_images()
    upload_images_to_s3()
