'''
this file is used to read excel file consists of 'CDSCode', 'County', 'District', 'School' Columns
output will be separate county, district and school json file with their parent reference

set file_path variable where your excel file exist

run "python excel_to_cds.py" command to run the file
'''

import pandas as pd
import os
import sys
import json

# Load the xlsx file
file_path = 'Jenzabar-CDS_Codes-CA_Public_School_List.xlsx'
excel_data = pd.read_excel(file_path)
# Read the values of the file in the dataframe
data = pd.DataFrame(excel_data, columns=['CDSCode', 'County', 'District', 'School'])
list_data = list(data.iloc)

county = []
district = []
school = []

county_value = []
district_value = {}
school_value = {}

for item in list_data:
    if not item['County'] in county_value:
        county_value.append(item['County'])
        district_value[item['County']] = [item['District']]
        school_value[item['District']] = [item['CDSCode']]

        county.append(
            {
                'label': item['County'],
                'value': item['County'],
                'parent': ''
            }
        )
        district.append(
            {
                'label': item['District'],
                'value': item['District'],
                'parent': item['County']
            }
        )
        school.append(
            {
                'label': item['School'],
                'value': str(item['CDSCode']),
                'parent': item['District']
            }
        )
    else:
        if not item['District'] in district_value[item['County']]:
            district_value[item['County']] = [item['District']]
            school_value[item['District']] = [item['CDSCode']]

            district.append(
                {
                    'label': item['District'],
                    'value': item['District'],
                    'parent': item['County']
                }
            )
            school.append(
                {
                    'label': item['School'],
                    'value': str(item['CDSCode']),
                    'parent': item['District']
                }
            )
        else:
            school_value[item['District']] = [item['CDSCode']]
            school.append(
                {
                    'label': item['School'],
                    'value': str(item['CDSCode']),
                    'parent': item['District']
                }
            )


# json_county = {
#     county
# }
# json_district = {
#     district
# }
# json_school = {
#     school
# }

with open('county.json', 'w', encoding='utf-8') as f:
    json.dump(county, f, ensure_ascii=False, indent=4)

with open('district.json', 'w', encoding='utf-8') as f:
    json.dump(district, f, ensure_ascii=False, indent=4)

with open('school.json', 'w', encoding='utf-8') as f:
    json.dump(school, f, ensure_ascii=False, indent=4)
