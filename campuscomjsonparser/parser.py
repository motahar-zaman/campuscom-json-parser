import sys
from pathlib import Path
import click
from serializers import ProductSerializer
import json
from mysql_connector import add_row, update_row, check_exists, delete_children
from logger import logger
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn, SpinnerColumn, TimeRemainingColumn, TimeElapsedColumn, MofNCompleteColumn

progress = Progress(
    SpinnerColumn(),
    MofNCompleteColumn(),
    BarColumn(bar_width=None),
    TaskProgressColumn(),
    TimeElapsedColumn(),
    transient=True
)


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
@click.option('--insert_new_only', is_flag=True, help="Insert new items, skip the rest.")
def main(datafile, mapping, config, insert_new_only):
    """Simple script that parses a JSON file and stores the data into a database."""

    data_map, config, data = config_reader(mapping, config, datafile)
    datafile = Path(datafile)

    processed = 0
    failed = 0
    skipped = 0
    updated = 0
    created = 0

    with open(data) as f:
        logger(f'Reading file: {datafile}')
        lines = [line for line in f.readlines() if line.strip() != '']
        logger(f'Number of records found: {len(lines)}')

        with progress:
            for line in progress.track(lines):
                serializer = ProductSerializer(data_map, data=line)
                product = serializer.serialize()
                modules = product.pop('modules', [])
                topics = product.pop('topics', [])
                skills = product.pop('skills', [])

                # check if exists. we will either skip or update depending on user input.
                product_exists = check_exists(config, data_map['product_table_name'], 'product_id', product)
                if insert_new_only and product_exists:
                    # skip skip
                    skipped = skipped + 1
                    continue

                # if the product is not skipped, we delete everything if it exists (except the product itself, which we update)

                if product_exists:
                    # update product.
                    product_id = update_row(config, data_map['product_table_name'], product, product_exists)
                    # update does not return product id sometimes. so
                    product_id = product_exists
                    updated = updated + 1
                    # delete children.
                    delete_children(data_map, product_exists)

                else:
                    # otherwise, just create records normally
                    product_id = add_row(config, data_map['product_table_name'], product)
                    if not product_id:
                        failed = failed + 1
                        continue
                    else:
                        created = created + 1

                for topic in topics:
                    topic_id = add_row(config, data_map['topic_table_name'], topic)
                    add_row(config, data_map['product_topic_join_table_name'], {'product_id': product_id, 'topic_id': topic_id})

                for module in modules:
                    lessons = module.pop('lessons', [])
                    module['product_id'] = product_id
                    module_id = add_row(config, data_map['module_table_name'], module)

                    for lesson in lessons:
                        lesson['module_id'] = module_id
                        add_row(config, data_map['lesson_table_name'], lesson)

                for skill in skills:
                    skill_id = add_row(config, 'skills', skill)
                    add_row(config, data_map['product_skill_join_table'], {'product_id': product_id, 'skill_id': skill_id})

                processed = processed + 1
        logger(f'Created: {created}')
        logger(f'Updated: {updated}')
        logger(f'Skipped: {skipped}')
        logger(f'Failed: {failed}')
        logger(f'Number of records processed: {processed}')

    logger('\n')

if __name__ == '__main__':
    logger('#################### SUMMARY ####################')
    main()
