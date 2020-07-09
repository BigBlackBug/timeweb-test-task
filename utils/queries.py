CREATE_TABLES = """ 
CREATE TABLE if not exists directory(
    id integer PRIMARY KEY, 
    parent_dir_id integer REFERENCES directory(id),
    dir_path text NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS directory_unique_path_index 
ON directory(dir_path);
CREATE INDEX IF NOT EXISTS directory_parent_id_index 
ON directory(parent_dir_id);
CREATE TABLE if not exists file(
    id integer PRIMARY KEY, 
    dir_id integer REFERENCES directory(id) ON DELETE CASCADE,
    filename text NOT NULL,
    last_modified timestamp NOT NULL,
    permissions integer NOT NULL,
    sha256 char(64) NOT NULL
);"""

DROP_TABLES = "DROP table if exists file; DROP table if exists directory"

ENABLE_FK = "PRAGMA foreign_keys = ON;"
