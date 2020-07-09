import argparse
import logging
import multiprocessing
import signal
import sys
import time

from dir_scanner import scanner
from utils import yaml, logutils

logger = logging.getLogger(__name__)


def scanner_daemon(dir, db_name, interval_sec=5):
    try:
        while True:
            scanner.scan_directory(dir, db_name)
            time.sleep(interval_sec)
    except BaseException as e:
        logger.error(f"{str(e.__class__.__name__)} - {str(e)}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Runs a directory scanner script')
    parser.add_argument("-c", "--config", required=True, type=str,
                        help="path to a config file", )
    args = parser.parse_args()
    try:
        config = yaml.from_file(args.config)
    except BaseException as e:
        logger.error(f"{str(e.__class__.__name__)} - {str(e)}")
    else:
        logutils.configure_logging(config['log'], True)
        traversal = multiprocessing.Process(target=scanner_daemon,
                                            args=(
                                                config['directory'],
                                                config['database']),
                                            daemon=True)
        traversal.start()

        # waiting for an interrupt
        signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))
        signal.pause()
