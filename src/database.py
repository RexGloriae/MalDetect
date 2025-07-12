import sqlite3
from log import logging

class Database:
    def __init__(self):
        self.db_name = "malware.db"
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''
        CREATE TABLE IF NOT EXISTS malware (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_hash TEXT UNIQUE
            )
        ''')
        conn.commit()
        conn.close()

    def exists(self, hash):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("SELECT 1 FROM malware WHERE file_hash = ?", (hash,))
        exists = c.fetchone() is not None
        conn.commit()
        conn.close()
        return exists

    def save(self, hash):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        try:
            c.execute('''
                INSERT INTO malware (file_hash)
                VALUES (?)
            ''', (
                hash,
            ))
            conn.commit()
        except sqlite3.IntegrityError:
            logging.warning(f'A try to insert an existing hash has failed...')
            return
        finally:
            conn.close()

    def get_all_hashes(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT * FROM malware')
        rows = c.fetchall()
        conn.close()
        return set(row[0] for row in rows)