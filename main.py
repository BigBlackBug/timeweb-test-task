import logging
import os
import sys

from fileutils import process_file
from storage import Storage

logger = logging.getLogger(__name__)


def traverse(dir: str, db_name: str):
    if not os.path.isdir(dir):
        raise ValueError(f"{dir} is not a valid directory")
    # root traversal is a predictable depth_first
    with Storage(db_name, drop=False) as storage:
        for current_dir, dirs, files in os.walk(os.path.abspath(dir)):
            logger.info(f"Current directory: '{current_dir}'")
            cur_dir_id = storage.create_directory(current_dir)
            # filename - id
            existing_files = storage.fetch_files(current_dir)
            for filename in files:
                logger.info(f"Processing file {filename}")

                file_path = os.path.join(current_dir, filename)
                sha256, permissions = process_file(file_path)
                storage.save_file(file_path, cur_dir_id, permissions, sha256)
                existing_files.pop(file_path, None)
            storage.drop_files(list(existing_files.values()))

            # dirname - id
            existing_dirs = storage.fetch_subdirs(cur_dir_id)
            for dirname in dirs:
                logger.info(f"Processing sub directory {dirname}")

                dir_path = os.path.join(current_dir, dirname)
                storage.create_directory(dir_path, parent_dir_id=cur_dir_id)
                existing_dirs.pop(dir_path, None)
            storage.drop_dirs(list(existing_dirs.values()))


if __name__ == '__main__':
    directory = sys.argv[1]
    db_name = sys.argv[2]
    logfile = sys.argv[3]

    logging.basicConfig(filename=logfile, level=logging.INFO,
                        format='%(asctime)s %(levelname)-5s %(message)s')

    # TODO log arguments + parsing errors
    logger.info(f"Directory parser started for '{directory}'")
    try:
        traverse(directory, db_name)
    except Exception as e:
        logger.error(f"{str(e.__class__.__name__)} - {str(e)}")
    logger.info(f"Directory parser DONE")
