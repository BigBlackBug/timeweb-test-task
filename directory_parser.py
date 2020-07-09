import logging
import os

from fileutils import process_file
from storage import Storage

logger = logging.getLogger(__name__)


def traverse(dir: str, db_name: str):
    if not os.path.isdir(dir):
        raise ValueError(f"{dir} is not a valid directory")
    # root traversal is a predictable depth_first
    with Storage(db_name, drop=True) as storage:
        for current_dir, dirs, files in os.walk(os.path.abspath(dir)):
            logger.info(f"Processing directory: '{current_dir}'")
            cur_dir_id = storage.create_directory(current_dir)
            # filename - id
            existing_files = storage.fetch_files(current_dir)
            for filename in files:
                logger.info(f"Found file {filename}")

                file_path = os.path.join(current_dir, filename)
                sha256, permissions = process_file(file_path)
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
