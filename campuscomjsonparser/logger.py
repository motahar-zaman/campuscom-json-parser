import sys
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler('{:%Y-%m-%d_output}.log'.format(datetime.now())),
        # logging.StreamHandler(sys.stdout)
    ]
)


def logger(msg, level=20):
    logging.log(level, msg)
