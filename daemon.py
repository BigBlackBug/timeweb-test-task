import argparse
import logging
import multiprocessing
import signal
import sys
import time

import directory_parser
import logutils
import yaml

logger = logging.getLogger(__name__)


def traversal_daemon(dir, db_name, interval_sec=5):
    try:
        while True:
            directory_parser.traverse(dir, db_name)
            time.sleep(interval_sec)
    except BaseException as e:
        logger.error(f"{str(e.__class__.__name__)} - {str(e)}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Runs a directory traversal script')
    parser.add_argument("-c", "--config", required=True, type=str,
                        help="path to a config file", )
    args = parser.parse_args()
    try:
        config = yaml.from_file(args.config)
    except BaseException as e:
        logger.error(f"{str(e.__class__.__name__)} - {str(e)}")
    else:
        logutils.configure_logging(config['log'], True)
        traversal = multiprocessing.Process(target=traversal_daemon,
                                            args=(
                                                config['directory'],
                                                config['database']),
                                            daemon=True)
        traversal.start()

        # waiting for an interrupt
        signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))
        signal.pause()
