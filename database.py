# database.py

import sqlite3
from typing import List, Tuple

class Database:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        # Table for subjects
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')
        # Table for words
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER,
                uzbek TEXT NOT NULL,
                english TEXT NOT NULL,
                FOREIGN KEY(subject_id) REFERENCES subjects(id)
            )
        ''')
        self.conn.commit()

    # Admin Functions
    def create_subject(self, name: str) -> bool:
        cursor = self.conn.cursor()
        try:
            cursor.execute('INSERT INTO subjects (name) VALUES (?)', (name,))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Subject already exists

    def delete_subject(self, name: str) -> bool:
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM subjects WHERE name = ?', (name,))
        result = cursor.fetchone()
        if result:
            subject_id = result[0]
            cursor.execute('DELETE FROM words WHERE subject_id = ?', (subject_id,))
            cursor.execute('DELETE FROM subjects WHERE id = ?', (subject_id,))
            self.conn.commit()
            return True
        return False

    def add_word(self, subject: str, uzbek: str, english: str) -> bool:
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM subjects WHERE name = ?', (subject,))
        result = cursor.fetchone()
        if result:
            subject_id = result[0]
            cursor.execute('INSERT INTO words (subject_id, uzbek, english) VALUES (?, ?, ?)',
                           (subject_id, uzbek, english))
            self.conn.commit()
            return True
        return False

    def delete_word(self, subject: str, word_id: int) -> bool:
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM subjects WHERE name = ?', (subject,))
        result = cursor.fetchone()
        if result:
            subject_id = result[0]
            cursor.execute('SELECT id FROM words WHERE id = ? AND subject_id = ?', (word_id, subject_id))
            word = cursor.fetchone()
            if word:
                cursor.execute('DELETE FROM words WHERE id = ?', (word_id,))
                self.conn.commit()
                return True
        return False

    # User Functions
    def get_subjects(self) -> List[str]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT name FROM subjects')
        subjects = cursor.fetchall()
        return [subject[0] for subject in subjects]

    def get_words_by_subject(self, subject: str) -> List[Tuple[int, str, str]]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM subjects WHERE name = ?', (subject,))
        result = cursor.fetchone()
        if result:
            subject_id = result[0]
            cursor.execute('SELECT id, uzbek, english FROM words WHERE subject_id = ?', (subject_id,))
            words = cursor.fetchall()
            return words
        return []

    def close(self):
        self.conn.close()
