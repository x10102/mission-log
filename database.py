import sqlite3
import typing as t
from os import remove
from os.path import exists

from users import User, UserRole
from entries import Entry

from datetime import datetime
from collections import namedtuple

from markup import remove_tags

fp_entry = namedtuple('FrontpageEntry', 'id date text private')

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

CREATE TABLE IF NOT EXISTS Entry (
id          INTEGER     NOT NULL PRIMARY KEY AUTOINCREMENT,
timestamp   DATETIME    NOT NULL,
text        TEXT        NOT NULL,
private     BOOLEAN     NOT NULL DEFAULT 0,
iduser      INTEGER     NOT NULL,
FOREIGN KEY (iduser) REFERENCES User(id)
    ON DELETE RESTRICT
)
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

    def create_default_user(self, u: User) -> None:
        query = "SELECT id FROM User WHERE username=?"
        if not self._tryexec(query, (u.login,)).fetchone():
            query = "INSERT INTO User (username, password, idrole) VALUES (?, ?, ?);"
            data = (u.login, u.password, u.role.value)
            self._tryexec(query, data)
    
    def get_frontpage(self, page: int = 0, private=False):
        def text_preview(text):
            line = text.split('<br>')[0]
            stripped = remove_tags(line)
            if len(stripped) > 120:
                return stripped[:120]+'...'
            else:
                return stripped
        if not private:
            query = "SELECT id, timestamp, text, private FROM Entry WHERE private=0 ORDER BY id DESC LIMIT 20 OFFSET ?"
        else:
            query = "SELECT id, timestamp, text, private FROM Entry ORDER BY id DESC LIMIT 20 OFFSET ?"
        data = (page * 20,)
        rows = self._tryexec(query, data).fetchall()
        entries = [fp_entry(row[0], datetime.strptime(row[1], "%d-%m-%Y %H:%M:%S"), text_preview(row[2]), row[3]) for row in rows]
        return entries
    
    def get_user(self, uid: int) -> t.Optional[User]:
        query = "SELECT id, username, password, idrole FROM User WHERE id=?"
        row = self._tryexec(query, (uid,)).fetchone()
        if not row:
            return None
        else:
            return User(row[1], row[2], UserRole(row[3]), row[0])
        
    def get_username(self, username: str) -> t.Optional[User]:
        query = "SELECT id, username, password, idrole FROM User WHERE username=?"
        row = self._tryexec(query, (username,)).fetchone()
        if not row:
            return None
        else:
            return User(row[1], row[2], UserRole(row[3]), row[0])

    def create_entry(self, e: Entry):
        query = "INSERT INTO Entry (text, timestamp, iduser, private) VALUES (?, ?, ?, ?)"
        data = (e.text, e.timestamp.strftime("%d-%m-%Y %H:%M:%S"), e.author.get_id(), e.private)
        cur = self._tryexec(query, data)
        return cur.lastrowid

    def get_entry(self, eid: int) -> t.Optional[Entry]:
        query = "SELECT id, timestamp, text, iduser, private FROM Entry WHERE id=?"
        row = self._tryexec(query, (eid,)).fetchone()
        if not row:
            return None
        else:
            return Entry(row[2], self.get_user(row[3]), row[4], datetime.strptime(row[1], "%d-%m-%Y %H:%M:%S"), row[0])
        
    def delete_entry(self, eid: int) -> None:
        query = "DELETE FROM Entry WHERE id=?"
        self._tryexec(query, (eid,))