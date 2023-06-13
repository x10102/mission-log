import sqlite3
import typing as t
from os import remove
from os.path import exists

from users import User

DB_CREATE_SCRIPT = """
CREATE TABLE IF NOT EXISTS User_Role (
id          INTEGER     NOT NULL PRIMARY KEY,
name        TEXT        NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS User (
id          INTEGER     NOT NULL PRIMARY KEY AUTOINCREMENT,
username    TEXT        NOT NULL UNIQUE,
password    BLOB        NOT NULL       ,
profile     TEXT        ,
idrole      INT         NOT NULL,
FOREIGN KEY (idrole) REFERENCES User_Role(id)
    ON DELETE RESTRICT
);
"""
DB_POPULATE_TYPES_SCRIPT = """
INSERT INTO User_Role (id, name) VALUES (1, "Owner"), (2, "User");
"""
class Database:

    def __init__(self, filepath: str = 'data/diary.db', drop: bool = False, output_queries = False) -> None:
        if exists(filepath) and drop:
            remove(filepath)
        
        self.connection = sqlite3.connect(filepath, check_same_thread=False)
        if output_queries:
            self.connection.set_trace_callback(print)

        self._tryexec(DB_CREATE_SCRIPT, script=True)
        if drop:
            self._tryexec(DB_POPULATE_TYPES_SCRIPT, script=True)
        
    def close(self) -> None:
        self.connection.close()
    
    def _tryexec(self, query: str, data: t.Tuple = (), script: bool = False) -> sqlite3.Cursor:
        try:
            with self.connection as con:
                cur = con.cursor()
                if script:
                    cur.executescript(query)
                else:
                    cur.execute(query, data)
                return cur
        except sqlite3.Error as e:
            raise RuntimeError(f'Database query aborted with error: {str(e)}') from e

    def create_user(self, u: User) -> None:
        query = "INSERT INTO User (username, password, idrole) VALUES (?, ?, ?);"
        data = (u.login, u.password, u.role.value)
        self._tryexec(query, data)
    
    def get_frontpage(self, page: int = 0):
        return None