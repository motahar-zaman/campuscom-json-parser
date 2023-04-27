'''
this file is used to convert all the jsonlines files from a directory to json files

set your directory to path variable where all the jsonlines files are located
run "python jsonlines_to_json.py" command to run the file
'''


import pandas as pd
import os
import sys
import json
import jsonlines
import pathlib

# the directory of jsonlines files
path = "/home/zaman/Documents/Scrap/Full Scrapes"
dir_list = os.listdir(path)


for file in dir_list:
    json_array = []
    file_name = os.path.splitext(file)[0]
    with jsonlines.open(path+'/'+file) as f:
        for line in f.iter():
            json_array.append(line)

        json_file_name = path+'/'+file_name+'.json'
        with open(json_file_name, 'w', encoding='utf-8') as data:
            json.dump(json_array, data, ensure_ascii=False, indent=4)

        with open(json_file_name) as data:
            try:
                json.load(data)  # put JSON-data to a variable
            except Exception as err:
                print("Invalid JSON")  # in case json is invalid
                print(err)
                print(json_file_name)
            else:
                print("Valid JSON")  # in case json is valid
