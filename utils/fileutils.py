import hashlib
import os

BUFFER_SIZE = 65536


def calculate_hash(path):
    hasher = hashlib.sha256()

    with open(path, 'rb') as file:
        while True:
            data = file.read(BUFFER_SIZE)
            if not data:
                break
            hasher.update(data)
    return hasher.hexdigest()


def process_file(abs_path):
    """
    :param abs_path: path to a file
    :return: tuple (sha256 hash of the file, permissions in XXX format)
    """
    sha256 = calculate_hash(abs_path)
    permissions = oct(os.stat(abs_path).st_mode)[-3:]
    return sha256, permissions
