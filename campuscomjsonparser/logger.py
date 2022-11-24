import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        # logging.StreamHandler(sys.stdout)
    ]
)


def logger(msg, level=20):
    logging.log(level, msg)
