import sqlite3
from typing import Sequence

import utils.queries as Q


def _plug_in_params(values: Sequence) -> str:
    return ','.join(['?'] * len(values))


class Storage:
    def __init__(self, db_file, drop=False):
        self.db_file = db_file
        self.drop = drop

    def __enter__(self):
        conn = sqlite3.connect(self.db_file,
                               isolation_level=None,
                               detect_types=sqlite3.PARSE_DECLTYPES |
                                            sqlite3.PARSE_COLNAMES)
        conn.execute(Q.ENABLE_FK)
        conn.row_factory = sqlite3.Row
        self.conn = conn
        if self.drop:
            self.conn.executescript(Q.DROP_TABLES)
        self.conn.executescript(Q.CREATE_TABLES)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
        # not consuming the exception here
        return False

    def save_file(self, filename, modification_date,
                  parent_dir_id, permissions, sha256):
        """
        Updates a file entry that corresponds to the filename and parent_dir_id.
        Or saves an entry in case it doesn't exist

        :param filename:
        :param modification_date:
        :param parent_dir_id:
        :param permissions:
        :param sha256:
        """
        file_record = self.conn.execute(
            "SELECT * from file where dir_id = ? and filename = ?",
            (parent_dir_id, filename)).fetchone()
        if not file_record:
            # insert
            self.conn.execute(
                "INSERT into file (dir_id, filename, last_modified, "
                "permissions, sha256) VALUES (?,?,?,?,?)",
                (parent_dir_id, filename, modification_date,
                 permissions, sha256))
        else:
            self.conn.execute(
                "UPDATE file set last_modified = ?, "
                "permissions = ?, sha256 = ? where id = ?",
                (modification_date, permissions, sha256, file_record['id']))

    def _save_directory(self, dir_path, parent_dir):
        return self.conn.execute(
            "INSERT INTO directory (parent_dir_id,dir_path)"
            "VALUES (?,?)", (parent_dir, dir_path))

    def fetch_subdirs(self, dir_id):
        """
        Returns all directory entries inside the dir_id
        :param dir_id:
        :return: dict {directory path -> directory id}
        """
        dir_cache = {}
        result = self.conn.execute(
            "SELECT id, parent_dir_id, dir_path from directory "
            "where parent_dir_id = ?", (dir_id,))

        for dir_id, parent_dir_id, dir_path in result:
            dir_cache[dir_path] = dir_id
        return dir_cache

    def drop_old_files(self, dir_id, modification_date):
        """
        Drops all file entries that belong in the directory
        with id=dir_id which haven't changed since modification_date
        :param dir_id:
        :param modification_date:
        :return:
        """
        self.conn.execute(f"DELETE FROM file where dir_id = ?"
                          f" and last_modified < ?",
                          (dir_id, modification_date))

    def drop_dirs(self, dir_ids: Sequence):
        """
        Deletes directory entries with ids from dir_ids.
        Also deletes all file entries related to the each directory.
        :param dir_ids:
        """
        if dir_ids and len(dir_ids) != 0:
            self.conn.execute(f"DELETE FROM directory where id in ("
                              f"{_plug_in_params(dir_ids)})", dir_ids)

    def create_directory(self, dir_path, parent_dir_id=None):
        """
        Returns the directory id, corresponding to the provided
        directory path.
        If it doesn't exist, creates the directory entry.
        :param dir_path:
        :param parent_dir_id:
        :return: directory id
        """
        # indexed query
        directory = self.conn.execute(
            "select id from directory where dir_path=?",
            (dir_path,)).fetchone()

        if not directory:
            # TODO a potential bug
            parent_id = parent_dir_id or self.get_parent_dir(dir_path)
            row = self._save_directory(dir_path, parent_id)
            return row.lastrowid
        return directory['id']

    def get_parent_dir(self, dir_path):
        """
        Returns a directory entry which is a parent to dir_path
        :param dir_path:
        """
        parent_path = dir_path[:-dir_path.rfind('/')]

        # indexed query
        return self.conn.execute(
            "SELECT id from directory where dir_path = ?",
            (parent_path,)).fetchone()
