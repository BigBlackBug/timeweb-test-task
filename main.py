import argparse
import os

from fileutils import process_file
from storage import Storage


def traverse(dir: str, db_name):
    if not os.path.isdir(dir):
        raise ValueError("invalid dir")
    # root traversal is a predictable depth_first
    with Storage(db_name, drop=False) as storage:
        # init root (create entry)
        # storage.create_directory(os.path.abspath(dir))
        for current_dir, dirs, files in os.walk(os.path.abspath(dir)):
            print(f"current_dir {current_dir}")
            cur_dir_id = storage.create_directory(current_dir)
            # filename - id
            old_files = storage.fetch_files(current_dir)
            for filename in files:
                logger.info(f"Processing file {filename}")

                file_path = os.path.join(current_dir, filename)
                sha256, permissions = process_file(file_path)
                storage.save_file(file_path, cur_dir_id, permissions, sha256)
                old_files.pop(file_path, None)
            storage.drop_files(list(old_files.values()))

            # dirname - id
            old_dirs = storage.fetch_subdirs(cur_dir_id)
            for dirname in dirs:
                logger.info(f"Processing sub directory {dirname}")

                dir_path = os.path.join(current_dir, dirname)
                storage.create_directory(dir_path, parent_dir_id=cur_dir_id)
                old_dirs.pop(dir_path, None)
            storage.drop_dirs(list(old_dirs.values()))
