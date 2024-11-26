import sqlite3

from scholar_result import ScholarResult

class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect('scholar_data.db')
        self.cursor = self.conn.cursor()
        self.create_tables()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_connection()

    def create_tables(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS authors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
        ''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS publications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author_id INTEGER,
            title TEXT NOT NULL,
            year INTEGER,
            url TEXT,
            form_submitted INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_published INTEGER DEFAULT 0,
            is_hidden INTEGER DEFAULT 0,
            FOREIGN KEY (author_id) REFERENCES authors (id)
        )
        ''')
        self.conn.commit()

    def hide_result(self, result: ScholarResult):
        self.cursor.execute("UPDATE publications SET is_hidden = 1 WHERE id = ?",
                            (result.id,))
        self.conn.commit()

    def unhide_result(self, result: ScholarResult):
        self.cursor.execute("UPDATE publications SET is_hidden = 0 WHERE id = ?", 
                             (result.id,))
        self.conn.commit()

    def insert_author(self, author_name) -> int | None:
        try:
            self.cursor.execute('INSERT OR IGNORE INTO authors (name) VALUES (?)', (author_name,))
            self.conn.commit()
            return self._last_insert_rowid()
        except Exception as e:
            print(f"Error inserting author!!! {e}")
            return None

    def insert_publication(self, author_id, title, year, url, form_submitted=0, is_published=0, is_hidden=0):
        try:
            self.cursor.execute('''
            INSERT INTO publications (author_id, title, year, url, form_submitted, is_published, is_hidden)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (author_id, title, year, url, form_submitted, is_published, is_hidden))
            self.conn.commit()
            return self._last_insert_rowid()
        except Exception as e:
            print(f"Error inserting publication!!! {e}")
            return None

    def get_all_authors(self):
        self.cursor.execute('SELECT * FROM authors')
        authors = self.cursor.fetchall()
        print("Authors:")
        for author in authors:
            print(author)

    def get_all_publications(self):
        self.cursor.execute('''
            SELECT publications.id, authors.name, publications.title, publications.year, 
                   publications.url, publications.form_submitted, publications.timestamp, 
                   publications.is_published, publications.is_hidden
            FROM publications
            JOIN authors ON publications.author_id = authors.id
        ''')
        publications = self.cursor.fetchall()
        print("Publications:")
        for publication in publications:
            print(publication)

    def close_connection(self):
        if self.conn:
            self.conn.close()

    def _last_insert_rowid(self) -> int:
        self.cursor.execute("SELECT last_insert_rowid()")
        return self.cursor.fetchone()[0]

# note to code reviwers-- you can check strucuture easily by running an sql script
    # i.e. "SELECT * FROM authors;" and "SELECT * FROM publications;" 
    # make sure to populate database using scraper. get scraper code. write author names in a txt file called names.txt
    # hopefully saves time
