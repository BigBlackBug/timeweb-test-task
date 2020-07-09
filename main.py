import argparse
import logging
import sys

import directory_parser

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Saves the directory structure '
                    'to the supplied database file. \n '
                    'All paths in arguments can be relative or absolute')
    parser.add_argument("-d", "--directory", required=True, type=str,
                        help="path to the directory to be scanned")
    parser.add_argument("-b", "--database", required=True, type=str,
                        help="path to the database file")
    parser.add_argument("-l", "--log", required=True, type=str,
                        help="path to the logfile")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="if set, prints logging messages to stdout")

    args = parser.parse_args()

    handlers = [logging.FileHandler(filename=args.log, mode='a')]
    if args.verbose:
        handlers.append(logging.StreamHandler(sys.stdout))
        # noinspection PyArgumentList
        logging.basicConfig(handlers=handlers, level=logging.INFO,
                            format='%(asctime)s %(levelname)-5s %(message)s')

    # TODO parse args errors
    # validate directory, database, log
    logger.info(f"Directory parser started for "
                f"directory: '{args.directory}' "
                f"database: '{args.database}' "
                f"logfile: '{args.log}' "
                f"verbose: '{args.verbose}' ")
    try:
        directory_parser.traverse(args.directory, args.database)
    except Exception as e:
        logger.error(f"{str(e.__class__.__name__)} - {str(e)}")
    logger.info(f"Directory parser DONE")
