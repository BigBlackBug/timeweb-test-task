MAKE_TABLES = """ 
CREATE TABLE if not exists directory(
    id integer PRIMARY KEY, 
    parent_dir_id integer  REFERENCES directory(id),
    dir_path text NOT NULL
);
CREATE TABLE if not exists file(
    id integer PRIMARY KEY, 
    dir_id integer REFERENCES directory(id) ON DELETE CASCADE,
    filename text NOT NULL,
    last_modified timestamp NOT NULL,
    permissions integer NOT NULL,
    sha256 char(64) NOT NULL
);"""

DROP_TABLES = "DROP table if exists file; DROP table if exists directory"

INSERT_FILE = """
    INSERT into file (dir_id, filename, last_modified, permissions, sha256) 
    VALUES (?,?,?,?,?) 
"""

INSERT_DIR = "INSERT into directory (parent_dir_id,dir_path) VALUES (?,?)"

ENABLE_FK = "PRAGMA foreign_keys = ON;"
