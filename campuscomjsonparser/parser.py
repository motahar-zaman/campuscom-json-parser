import sys
from pathlib import Path
import click
from serializers import ProductSerializer
import json
from mysql_connector import add_row, update_row, check_exists
from logger import logger


def terminate(msg='Can not continue. Please consult logs for details'):
    sys.exit(msg)


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
                logger(e, level=40)
                terminate()
    else:
        logger('Provided mapping file does not exist', level=40)
        terminate()

    if configuration.exists():
        with open(configuration) as f:
            try:
                config = json.loads(f.read())
            except json.JSONDecodeError as e:
                logger(e, level=40)
                terminate()
    else:
        logger('Provided configuration file does not exist', level=40)
        terminate()

    if not data.exists():
        logger('Provided data file does not exist', level=40)
        terminate()

    return (data_map, config, data)


@click.command()
@click.option("--mapping", required=True, help="File containing mapping of data file and db schema")
@click.option("--config", required=True, help="File containing configuration options")
@click.option("--datafile", required=True, help="Path of the JSON file")
def main(datafile, mapping, config):
    """Simple script that parses a JSON file and stores the data into a database."""

    data_map, config, data = config_reader(mapping, config, datafile)
    datafile = Path(datafile)

    with open(data) as f:
        for line in f:
            serializer = ProductSerializer(data_map, data=line)
            product = serializer.serialize()
            modules = product.pop('modules', [])
            topics = product.pop('topics', [])
            skills = product.pop('skills', [])
            product_where = f"provided_by = '{product['provided_by']}' AND name = '{product['name']}'"
            product_exists = check_exists(config, 'product', 'product_id', product_where)
            if product_exists:
                # or update
                # update_row(config, 'product', product, product_exists)
                # logger(f'inserted product: {product_exists}')
                logger(f'skipping product: {product_exists}')
                continue
            else:
                product_id = add_row(config, 'product', product)

                for topic in topics:
                    topic_id = add_row(config, 'topics', topic)
                    jn_product_topics_id = add_row(config, 'jn_product_topics', {'product_id': product_id, 'topic_id': topic_id})

                for module in modules:
                    lessons = module.pop('lessons', [])
                    module_id = add_row(config, 'modules', module)

                    for lesson in lessons:
                        lesson_id = add_row(config, 'lessons', lesson)

                for skill in skills:
                    skill_id = add_row(config, 'skills', skill)
                    jn_product_skills_id = add_row(config, 'jn_product_skills', {'product_id': product_id, 'skill_id': skill_id})

                logger(f'inserted product: {product_id}')


if __name__ == '__main__':
    main()
