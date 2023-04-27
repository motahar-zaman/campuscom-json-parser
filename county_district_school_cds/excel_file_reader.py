'''
this file is used to read excel file consists of 'CDSCode', 'County', 'District', 'School' Columns
output as a json file in this file directory

set file_path variable where your excel file exist

run "python excel_file_reader.py" command to run the file
'''

import pandas as pd
import os
import sys
import json


file_path = 'Jenzabar-CDS_Codes-CA_Public_School_List.xlsx'
excel_data = pd.read_excel(file_path)
# Read the values of the file in the dataframe
data = pd.DataFrame(excel_data, columns=['CDSCode', 'County', 'District', 'School'])
list_data = list(data.iloc)

county = []
county_value = []
district_value = {}
school_value = {}
for item in list_data:
    if item['County'] in county_value:
        for cty_indx, cty in enumerate(county):
            if cty['value'] == item['County']:
                if item['District'] in district_value[item['County']]:
                    for indx, dist in enumerate(cty['district']):
                        if dist['value'] == item['District']:
                            school_value[item['District']].append(item['CDSCode'])
                            dist['school'].append({
                                'label': item['School'],
                                'value': str(item['CDSCode'])
                            })
                            county[cty_indx]['district'][indx]=dist

                else:
                    district_value[item['County']].append(item['District'])
                    school_value[item['District']]=[item['CDSCode']]
                    cty['district'].append(
                        {
                            'label': item['District'],
                            'value': item['District'],
                            'school': [
                                {
                                    'label': item['School'],
                                    'value': str(item['CDSCode'])
                                }
                            ]
                        }
                    )
    else:
        county_value.append(item['County'])
        district_value[item['County']] = [item['District']]
        school_value[item['District']] = [item['CDSCode']]
        county.append(
            {
                'label': item['County'],
                'value': item['County'],
                'district': [
                    {
                        'label': item['District'],
                        'value': item['District'],
                        'school': [
                            {
                                'label': item['School'],
                                'value': str(item['CDSCode'])
                            }
                        ]
                    }
                ]
            }
        )

json_county = {
    'county': county
}

with open('cds_code.json', 'w', encoding='utf-8') as f:
    json.dump(json_county, f, ensure_ascii=False, indent=4)
