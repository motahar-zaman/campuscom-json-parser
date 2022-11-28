# campuscom-json-parser

Parses provided data and stores them into mysql database

Installation instructions
-------------------------

To install this package first clone this repository. Then step into the directory:

```
cd campuscom-json-parser
```

After that, run the following command to install required dependencies:
```
pip install -r requirements.txt
```

Once installed, invoke the script with ``--help`` param to see how to pass data and configurations needed to properly run the script.
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

A sample of mapper file and config file is included with this project. Please modify them as neccessary and then use them.
