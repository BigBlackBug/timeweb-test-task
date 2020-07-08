import os

import hashutils


def process_file(root, filename):
    abs_path = os.path.join(root, filename)
    sha256 = hashutils.calculate_hash(abs_path)
    # update_time = datetime.utcnow()
    permissions = oct(os.stat(abs_path).st_mode)[-3:]
    return sha256, permissions


def traverse(dir: str):
    if not os.path.isdir(dir):
        raise ValueError("invalid dir")

    for root, dirs, files in os.walk(os.path.abspath(dir)):
        print(f"root {root}")
        # save root to db
        for f in files:
            sha256, permissions = process_file(root, f)
            print(f"file: {f}, perms: {permissions}, sha: {sha256[-6:]}")
        for d in dirs:
            print(f"dir: {d}")
        print("---------------")
