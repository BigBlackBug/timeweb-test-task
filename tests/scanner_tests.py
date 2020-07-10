import os
import sqlite3
import tempfile
import unittest
from datetime import datetime

from dir_scanner import scanner
from utils import queries


class ScannerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        tempdir = tempfile.gettempdir()
        self.db_path = os.path.join(tempdir, 'temp.db')
        self.conn = sqlite3.connect(self.db_path,
                                    isolation_level=None,
                                    detect_types=sqlite3.PARSE_DECLTYPES |
                                                 sqlite3.PARSE_COLNAMES)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(queries.CREATE_TABLES)

    def tearDown(self) -> None:
        self.conn.close()
        os.remove(self.db_path)

    def test_files_created_empty_db(self):
        folder = tempfile.mkdtemp()
        tempfile.mkstemp(dir=folder)
        tempfile.mkstemp(dir=folder)
        scanner.scan_directory(folder, self.db_path)

        dirs = self.conn.execute("SELECT * from directory").fetchall()
        self.assertEqual(len(dirs), 1)
        directory = dirs[0]
        self.assertEqual(directory['parent_dir_id'], None)
        self.assertEqual(directory['dir_path'], folder)

        files = self.conn.execute("SELECT * from file").fetchall()
        self.assertEqual(len(files), 2)
        self.assertEqual(files[0]['dir_id'], directory['id'])
        self.assertEqual(files[1]['dir_id'], directory['id'])

    def test_dirs_deleted(self):
        # this is stored in db
        # dir1
        #   file1
        #   dir2
        #     file2

        # this is what's really on the fs
        # dir1
        #   file1
        folder = tempfile.mkdtemp()
        _, file1 = tempfile.mkstemp(dir=folder)
        subdir = os.path.join(folder, 'subdir')
        dir_id = 1
        sub_dir_id = 2
        self.conn.execute(
            "INSERT into directory(id,parent_dir_id,dir_path)values(?,?,?)",
            (dir_id, None, folder))
        self.conn.execute(
            "INSERT into directory(id,parent_dir_id,dir_path)values(?,?,?)",
            (sub_dir_id, dir_id, subdir))
        old_modification_time = datetime.now()

        self.conn.execute(
            "INSERT into file (dir_id, filename, last_modified, "
            "permissions, sha256) VALUES (?,?,?,?,?)",
            (dir_id, file1, old_modification_time,
             '777', 'msha256'))

        self.conn.execute(
            "INSERT into file (dir_id, filename, last_modified, "
            "permissions, sha256) VALUES (?,?,?,?,?)",
            (sub_dir_id, 'file2', old_modification_time,
             '777', 'msha256'))

        scanner.scan_directory(folder, self.db_path)

        dirs = self.conn.execute("SELECT * from directory").fetchall()
        self.assertEqual(len(dirs), 1)
        directory = dirs[0]
        self.assertEqual(directory['parent_dir_id'], None)
        self.assertEqual(directory['dir_path'], folder)

        files = self.conn.execute("SELECT * from file").fetchall()
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0]['dir_id'], dir_id)
        self.assertEqual(files[0]['filename'], file1)

    def test_files_deleted(self):
        # this is stored in db
        # dir1
        #   file1
        #   whateverfile

        # this is what's really on the fs
        # dir1
        #   file1
        #   file2
        folder = tempfile.mkdtemp()
        _, file1 = tempfile.mkstemp(dir=folder)
        _, file2 = tempfile.mkstemp(dir=folder)
        dir_id = 1
        self.conn.execute(
            "INSERT into directory(id,parent_dir_id,dir_path)values(?,?,?)",
            (dir_id, None, folder))

        old_modification_time = datetime.now()
        self.conn.execute(
            "INSERT into file (dir_id, filename, last_modified, "
            "permissions, sha256) VALUES (?,?,?,?,?)",
            (dir_id, file1, old_modification_time,
             '777', 'msha256'))

        # after scan this file should be gone
        self.conn.execute(
            "INSERT into file (dir_id, filename, last_modified, "
            "permissions, sha256) VALUES (?,?,?,?,?)",
            (dir_id, 'whateverfile', old_modification_time,
             '777', 'msha256'))

        scanner.scan_directory(folder, self.db_path)

        dirs = self.conn.execute("SELECT * from directory").fetchall()
        self.assertEqual(len(dirs), 1)
        directory = dirs[0]
        self.assertEqual(directory['parent_dir_id'], None)
        self.assertEqual(directory['dir_path'], folder)

        files = self.conn.execute("SELECT * from file").fetchall()
        self.assertEqual(len(files), 2)
        self.assertEqual(files[0]['dir_id'], dir_id)
        self.assertEqual(files[0]['filename'], file1)

        self.assertEqual(files[1]['dir_id'], dir_id)
        self.assertEqual(files[1]['filename'], file2)
