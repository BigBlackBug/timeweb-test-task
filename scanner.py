import argparse
import logging

from dir_scanner import scanner
from utils import logutils

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Saves the directory structure '
                    'to the supplied database file. '
                    'All paths specified by arguments '
                    'can be relative or absolute')
    parser.add_argument("-d", "--directory", required=True, type=str,
                        help="path to the directory to be scanned")
    parser.add_argument("-b", "--database", required=True, type=str,
                        help="path to the database file")
    parser.add_argument("-l", "--log", required=True, type=str,
                        help="path to the logfile")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="if set, prints logging messages to stdout")

    args = parser.parse_args()

    logutils.configure_logging(args.log, args.verbose)

    logger.info(f"Directory scanner started for "
                f"directory: '{args.directory}' "
                f"database: '{args.database}' "
                f"logfile: '{args.log}' "
                f"verbose: '{args.verbose}' ")
    try:
        scanner.scan_directory(args.directory, args.database)
    except Exception as e:
        logger.error(f"{str(e.__class__.__name__)} - {str(e)}")
    logger.info(f"Directory scanner DONE")
