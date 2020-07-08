import os

from fileutils import process_file
from storage import Storage


def traverse(dir: str, db_name):
    if not os.path.isdir(dir):
        raise ValueError("invalid dir")
    # root traversal is a predictable depth_first
    with Storage(db_name, drop=True) as storage:
        # init root (create entry)
        # storage.create_directory(os.path.abspath(dir))
        for current_dir, dirs, files in os.walk(os.path.abspath(dir)):
            print(f"current_dir {current_dir}")
            cur_dir_id = storage.create_directory(current_dir)
            # sub dirs
            # sub files. filename-id
            old_files = storage.old_files(current_dir)
            # save root to db
            for f in files:
                file_path = os.path.join(current_dir, f)
                sha256, permissions = process_file(file_path)
                print(f"file: {f}, perms: {permissions}, sha: {sha256[-6:]}")
                storage.save_file(os.path.join(current_dir, f), cur_dir_id,
                                  permissions,
                                  sha256)
                old_files.pop(os.path.join(current_dir, f), None)
            storage.drop_files(list(old_files.values()))

            # dirname - id
            old_dirs = storage.old_dirs(cur_dir_id)
            for d in dirs:
                storage.create_directory(os.path.join(current_dir, d),
                                         cur_dir_id)
                print(f"dir: {d}")
                old_dirs.pop(os.path.join(current_dir, d), None)
            storage.drop_dirs(list(old_dirs.values()))
