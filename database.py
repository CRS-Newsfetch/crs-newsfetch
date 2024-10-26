import sqlite3

class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect('scholar_data.db')
        self.cursor = self.conn.cursor()
        self.create_tables()

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
            citations INTEGER,
            year TEXT,
            form_submitted INTEGER DEFAULT 0,  
            FOREIGN KEY (author_id) REFERENCES authors (id)
        )
        ''')

        self.conn.commit()

    #try catch to insert author table
    def insert_author(self, author_name):
        try:
            self.cursor.execute('INSERT OR IGNORE INTO authors (name) VALUES (?)', (author_name,))
            self.conn.commit()
            self.cursor.execute('SELECT id FROM authors WHERE name = ?', (author_name,))
            return self.cursor.fetchone()[0]
        except Exception as e:
            print(f"Error inserting author!!! {e}")
            return None

    # try catch to insert publication table
    def insert_publication(self, author_id, title, citations, year, form_submitted=0):
        try:
            self.cursor.execute('''
            INSERT INTO publications (author_id, title, citations, year, form_submitted)
            VALUES (?, ?, ?, ?, ?)
            ''', (author_id, title, citations, year, form_submitted))
            self.conn.commit()
        except Exception as e:
            print(f"Error inserting publication!!! {e}")
            return None

    def close_connection(self):
        self.conn.close()
    
    # note to code reviwers-- you can check strucuture easily by running an sql script
    # i.e. "SELECT * FROM authors;" and "SELECT * FROM publications;" 
    # make sure to populate database using scraper. get scraper code. write author names in a txt file called names.txt
    # hopefully saves time

    def get_all_authors(self):
        self.cursor.execute('SELECT * FROM authors')
        authors = self.cursor.fetchall()
        print("Authors:")
        for author in authors:
            print(author)

    def get_all_publications(self):
        # retrives assosiated authors and publications using unique author id as a foreign key
        self.cursor.execute('''
            SELECT publications.id, authors.name, publications.title, publications.citations, publications.year, publications.form_submitted
            FROM publications
            JOIN authors ON publications.author_id = authors.id
        ''')
        publications = self.cursor.fetchall()
        print("Publications:")
        for publication in publications:
            print(publication)