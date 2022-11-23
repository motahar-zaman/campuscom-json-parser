import sys
from pathlib import Path
import click
from campuscomjsonparser.serializers import ProductSerializer
from rich import print
import json
import logging
from campuscomjsonparser.mysql_connector import add_row

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)


def config_reader(mappingfile, configfile, datafile):
    """
    Reads all the configurations from specified files and returns a tuple containing the
    values in python friendly format
    """
    mapping = Path(mappingfile)
    configuration = Path(configfile)
    data = Path(datafile)

    if mapping.exists():
        with open(mapping) as f:
            try:
                data_map = json.loads(f.read())
            except json.JSONDecodeError as e:
                logging.error(e)
                sys.exit('Can not continue. Please consult logs for further information.')
    else:
        logging.error('Provided mapping file does not exist')
        sys.exit('Can not continue. Please consult logs for further information.')

    if configuration.exists():
        with open(configuration) as f:
            try:
                config = json.loads(f.read())
            except json.JSONDecodeError as e:
                logging.error(e)
                sys.exit('Can not continue. Please consult logs for further information.')
    else:
        logging.error('Provided configuration file does not exist')
        sys.exit('Can not continue. Please consult logs for further information.')

    if not data.exists():
        logging.error('Provided data file does not exist')
        sys.exit('Can not continue. Please consult logs for further information.')

    return (data_map, config, data)


@click.command()
@click.option("--mapping", default='.', help="File containing mapping of data file and db schema")
@click.option("--config", default='.', help="File containing configuration options")
@click.option("--datafile", default='.', help="Path of the JSON file")
def main(datafile, mapping, config):
    """Simple script that parses a JSON file and stores the data into a database."""

    data_map, config, data = config_reader(mapping, config, datafile)
    datafile = Path(datafile)

    with open(data) as f:
        for line in f:
            serializer = ProductSerializer(data_map, data=line)
            product = serializer.serialize()
            moduels = product.pop('modules', [])
            topics = product.pop('topics', [])
            del product['prerequisites']

            product_id = add_row(config, 'product', product)

            # save moduels and others here



if __name__ == '__main__':
    main()
