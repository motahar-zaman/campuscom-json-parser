# campuscom-json-parser

Parses provided data and stores them into mysql database

Preparations
------------

This script requires a mapping file. It must be a valid JSON file containing key value pairs corresponding to table and column names. A sample mapping file is included in this repo. The file looks like this:

```
{
    "product": {
        "name": "Learning Product Name",
        "topics": "Topics",
        "modules": "Modules",
        "skills": "Skills"
    },

    "topic": {
        "name": "Topic Name"
    },

    "module": {
        "name": "Module Name"
    }
}

```

The top level keys are for the types of data we are going to parse e.g. `product`, `topic`, `skill`, `module`, `lesson` etc. And inside each item, they keys denote the column names in the table, and their values represent the names in the data file. So, the keys `name`, `topics` and others are the column names in the table for product. And their values (`Learning Product Name`, `Topics` etc.) must be the labels in the data file. Please note, these items are all case sensitive.

A configuration file containing database credentials must be supplied as well. That file is fairly self-explanatory:
```
{
    "host": "127.0.0.1",
    "port": 3306,
    "user": "",
    "password": "",
    "database": "",
    "use_unicode": true
}

```

This file must be valid JSON. In future, it may contain more configuration options as the project grows. A sample is provided with this repo.

How to run this script
----------------------

To run this package first clone this repository. Then step into the directory:

```
cd campuscom-json-parser
```

After that, run the following command to install required dependencies:
```
pip install -r requirements.txt
```

Once dependencies are taken care off, invoke the script with ``--help`` param to see how to pass data and configurations files needed to properly run the script.
```
python campuscomjsonparser/parser.py --help
```

Output:
```
Usage: parser.py [OPTIONS]

  Simple script that parses a JSON file and stores the data into a database.

Options:
  --mapping TEXT   File containing mapping of data file and db schema
                   [required]
  --config TEXT    File containing configuration options  [required]
  --datafile TEXT  Path of the JSON file  [required]
  --help           Show this message and exit.
```

A sample of mapping file and config file is included with this project. Please modify them as neccessary before using them.

Finally, run the script like this:

```
python campuscomjsonparser/parser.py --datafile /path/to/courses.jsonlines --mapping /path/to/mapping.json --config /path/to/config.json
```

Troubleshooting
---------------

Please make sure to use python 3 to run the script.
The script will write logs in a file called `debug.log`. Please consult that file in case of trouble.
