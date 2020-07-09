import sqlite3
from datetime import datetime
from typing import Sequence

import queries


class Storage:
    def __init__(self, db_file, drop=False):
        self.db_file = db_file
        self.drop = drop

    def __enter__(self):
        conn = sqlite3.connect(self.db_file,
                               isolation_level=None,
                               detect_types=sqlite3.PARSE_DECLTYPES |
                                            sqlite3.PARSE_COLNAMES)
        conn.execute(queries.ENABLE_FK)
        conn.row_factory = sqlite3.Row
        self.conn = conn
        if self.drop:
            self.conn.executescript(queries.DROP_TABLES)
        self.conn.executescript(queries.MAKE_TABLES)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            print("ex")
            # log exceptions
            pass
        self.conn.close()
        return False

    def save_file(self, filename, parent_dir, permissions, sha256):
        file_record = self.conn.execute(
            "SELECT * from file where dir_id = ? and filename = ?",
            (parent_dir, filename)).fetchone()
        if not file_record:
            # insert
            self.conn.execute(queries.INSERT_FILE, (
                parent_dir, filename, datetime.now(), permissions, sha256))
        else:
            self.conn.execute(
                "UPDATE file set last_modified = ?, permissions = ?, sha256 = ?"
                " where id = ?",
                (datetime.now(), permissions, sha256, file_record['id']))

    def save_dir(self, dir_path, parent_dir):
        return self.conn.execute(queries.INSERT_DIR, (parent_dir, dir_path))

    def fetch_subdirs(self, dir_id):
        # select all dirs
        dir_cache = {}
        result = self.conn.execute(
            "SELECT id, parent_dir_id, dir_path from directory "
            "where parent_dir_id = ?", (dir_id,))

        for dir_id, parent_dir_id, dir_path in result:
            dir_cache[dir_path] = dir_id
        return dir_cache

    def fetch_files(self, dir_path):
        result = self.conn.execute(
            "SELECT file.filename,file.id from file join directory "
            "on dir_id=directory.id "
            "where directory.dir_path = ?", (dir_path,))
        file_cache = {}
        for filename, file_id in result:
            file_cache[filename] = file_id
        return file_cache

    def drop_files(self, file_ids: Sequence):
        if file_ids and len(file_ids) != 0:
            self.conn.execute(f"DELETE FROM file where id in ("
                              f"{self._plug_params(file_ids)})", file_ids)

    def _plug_params(self, values: Sequence) -> str:
        return ','.join(['?'] * len(values))

    def drop_dirs(self, dir_ids: Sequence):
        if dir_ids and len(dir_ids) != 0:
            self.conn.execute(f"DELETE FROM directory where id in ("
                              f"{self._plug_params(dir_ids)})", dir_ids)

    def create_directory(self, dir_path, parent_dir_id=None):
        directory = self.conn.execute(
            "select id from directory where dir_path=?",
            (dir_path,)).fetchone()

        if not directory:
            parent_id = parent_dir_id or self.get_parent_dir(dir_path)
            row = self.save_dir(dir_path, parent_id)
            return row.lastrowid
        return directory['id']

    def get_parent_dir(self, dir_path):
        parent_path = dir_path[:-dir_path.rfind('/')]

        return self.conn.execute(
            "SELECT id from directory where dir_path = ?",
            (parent_path,)).fetchone()
