import hashlib
import os

BUF_SIZE = 65536


def calculate_hash(file):
    hasher = hashlib.sha256()

    with open(file, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            hasher.update(data)
    return hasher.hexdigest()


def process_file(abs_path):
    sha256 = calculate_hash(abs_path)
    permissions = oct(os.stat(abs_path).st_mode)[-3:]
    return sha256, permissions
