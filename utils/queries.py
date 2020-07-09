CREATE_TABLES = """ 
CREATE TABLE IF NOT EXISTS directory(
    id INTEGER PRIMARY KEY, 
    parent_dir_id INTEGER REFERENCES directory(id),
    dir_path TEXT NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS directory_unique_path_index 
ON directory(dir_path);
CREATE INDEX IF NOT EXISTS directory_parent_id_index 
ON directory(parent_dir_id);
CREATE TABLE IF NOT EXISTS file(
    id INTEGER PRIMARY KEY, 
    dir_id INTEGER REFERENCES directory(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    last_modified TIMESTAMP NOT NULL,
    permissions INTEGER NOT NULL,
    sha256 char(64) NOT NULL
);"""

DROP_TABLES = "DROP TABLE IF EXISTS file;" \
              "DROP TABLE IF EXISTS directory;" \
              "DROP INDEX IF EXISTS directory_unique_path_index;" \
              "DROP INDEX IF EXISTS directory_parent_id_index;"

ENABLE_FK = "PRAGMA foreign_keys = ON;"
