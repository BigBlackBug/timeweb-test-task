import logging
import os
from datetime import datetime

from utils import fileutils
from .storage import Storage

logger = logging.getLogger(__name__)


def scan_directory(dir: str, db_name: str):
    """
    Recursively goes through the directory and saves its structure
    to the sqlite database file
    :param dir: relative or absolute path to a directory to parse
    :param db_name: name for a database file
    """
    if not os.path.isdir(dir):
        raise ValueError(f"{dir} is not a valid directory")
    # root traversal is a predictable depth_first
    with Storage(db_name) as storage:
        abspath = os.path.abspath(dir)
        logger.info(f"Started scanning '{abspath}'")

        for current_dir, dirs, files in os.walk(abspath):
            logger.info(f"Processing directory: '{current_dir}'")
            cur_dir_id = storage.create_directory(current_dir)

            modification_date = datetime.now()
            for filename in files:
                logger.info(f"Found file '{filename}'")

                file_path = os.path.join(current_dir, filename)
                try:
                    sha256, permissions = fileutils.process_file(file_path)
                except Exception as e:
                    logger.error(f"Error parsing file: str{e}")
                else:
                    storage.save_file(filename=file_path,
                                      modification_date=modification_date,
                                      parent_dir_id=cur_dir_id,
                                      permissions=permissions,
                                      sha256=sha256)
            # drop files that were deleted from the file system
            storage.drop_old_files(cur_dir_id, modification_date)
            # dir_path - id
            existing_dirs = storage.fetch_subdirs(cur_dir_id)
            for dirname in dirs:
                logger.info(f"Found sub directory '{dirname}'")

                dir_path = os.path.join(current_dir, dirname)
                storage.create_directory(dir_path, parent_dir_id=cur_dir_id)
                existing_dirs.pop(dir_path, None)
            # drop deleted directory entries
            storage.drop_dirs(list(existing_dirs.values()))
