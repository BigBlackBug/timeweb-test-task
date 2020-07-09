import logging
import os

from utils import fileutils
from .storage import Storage

logger = logging.getLogger(__name__)


def scan_directory(dir: str, db_name: str):
    """
    Recursively goes through the directory and stores its structure
    to the sqlite database file
    :param dir: relative or absolute path to a directory to parse
    :param db_name: name for a database file
    """
    if not os.path.isdir(dir):
        raise ValueError(f"{dir} is not a valid directory")
    # root traversal is a predictable depth_first
    with Storage(db_name) as storage:
        abspath = os.path.abspath(dir)
        logger.info(f"Started traversal for '{abspath}'")

        for current_dir, dirs, files in os.walk(abspath):
            logger.info(f"Processing directory: '{current_dir}'")
            cur_dir_id = storage.create_directory(current_dir)
            # filename - id
            existing_files = storage.fetch_files(current_dir)
            for filename in files:
                logger.info(f"Found file {filename}")

                file_path = os.path.join(current_dir, filename)
                sha256, permissions = fileutils.process_file(file_path)
                storage.save_file(file_path, cur_dir_id, permissions, sha256)
                existing_files.pop(file_path, None)
            storage.drop_files(list(existing_files.values()))

            # dirname - id
            existing_dirs = storage.fetch_subdirs(cur_dir_id)
            for dirname in dirs:
                logger.info(f"Found sub directory {dirname}")

                dir_path = os.path.join(current_dir, dirname)
                storage.create_directory(dir_path, parent_dir_id=cur_dir_id)
                existing_dirs.pop(dir_path, None)
            storage.drop_dirs(list(existing_dirs.values()))
