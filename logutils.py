import logging
import sys


def configure_logging(log_file: str, verbose: bool):
    handlers = [logging.FileHandler(filename=log_file, mode='a')]
    if verbose:
        handlers.append(logging.StreamHandler(sys.stdout))
        # noinspection PyArgumentList
        logging.basicConfig(handlers=handlers, level=logging.INFO,
                            format='%(asctime)s %(levelname)-5s %(message)s')
