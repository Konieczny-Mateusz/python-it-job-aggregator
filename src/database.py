import sqlite3
import pandas as pd
from typing import List, Dict, Optional


class JobDatabase:
    """Klasa zarządzająca bazą danych ofert pracy."""

    def __init__(self, db_path: str = 'jobs.db'):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Inicjalizacja bazy danych i utworzenie tabeli."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Sprawdzamy czy tabela istnieje
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='job_offers'")
        table_exists = cursor.fetchone() is not None

        if table_exists:
            # Sprawdzamy czy kolumna category istnieje
            cursor.execute("PRAGMA table_info(job_offers)")
            columns = [column[1] for column in cursor.fetchall()]

            if 'category' not in columns:
                print("  Aktualizacja struktury bazy danych - dodawanie kolumny 'category'...")
                try:
                    cursor.execute('ALTER TABLE job_offers ADD COLUMN category TEXT')
                    conn.commit()
                    print("  ✓ Kolumna 'category' dodana pomyślnie")
                except Exception as e:
                    print(f"  ⚠ Błąd przy dodawaniu kolumny: {e}")
        else:
            # Tworzymy nową tabelę
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS job_offers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    company TEXT,
                    location TEXT,
                    salary TEXT,
                    employment_type TEXT,
                    experience_level TEXT,
                    category TEXT,
                    source TEXT NOT NULL,
                    url TEXT,
                    posted_date TEXT,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            print("  ✓ Tabela job_offers utworzona")

        conn.close()

    def save_jobs(self, df: pd.DataFrame):
        """Zapisuje oferty pracy z DataFrame do bazy danych."""
        conn = sqlite3.connect(self.db_path)
        df.to_sql('job_offers', conn, if_exists='append', index=False)
        conn.close()

    def get_all_jobs(self) -> pd.DataFrame:
        """Pobiera wszystkie oferty z bazy danych."""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query('SELECT * FROM job_offers', conn)
        conn.close()
        return df

    def filter_jobs(self,
                    keyword: Optional[str] = None,
                    location: Optional[str] = None,
                    source: Optional[str] = None,
                    experience_level: Optional[str] = None,
                    category: Optional[str] = None) -> pd.DataFrame:
        """Filtruje oferty pracy według podanych kryteriów."""
        conn = sqlite3.connect(self.db_path)

        query = 'SELECT * FROM job_offers WHERE 1=1'
        params = []

        if keyword:
            query += ' AND (title LIKE ? OR description LIKE ?)'
            params.extend([f'%{keyword}%', f'%{keyword}%'])

        if location:
            query += ' AND location LIKE ?'
            params.append(f'%{location}%')

        if source:
            query += ' AND source = ?'
            params.append(source)

        if experience_level:
            query += ' AND experience_level = ?'
            params.append(experience_level)

        if category:
            query += ' AND category = ?'
            params.append(category)

        query += ' ORDER BY created_at DESC'

        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df

    def get_statistics(self) -> Dict:
        """Generuje statystyki dotyczące ofert pracy."""
        conn = sqlite3.connect(self.db_path)

        stats = {}

        # Liczba ofert według źródła
        df = pd.read_sql_query(
            'SELECT source, COUNT(*) as count FROM job_offers GROUP BY source',
            conn
        )
        stats['by_source'] = df.to_dict('records')

        # Liczba ofert według lokalizacji (top 10)
        df = pd.read_sql_query(
            'SELECT location, COUNT(*) as count FROM job_offers GROUP BY location ORDER BY count DESC LIMIT 10',
            conn
        )
        stats['by_location'] = df.to_dict('records')

        # Liczba ofert według poziomu doświadczenia
        df = pd.read_sql_query(
            'SELECT experience_level, COUNT(*) as count FROM job_offers GROUP BY experience_level',
            conn
        )
        stats['by_experience'] = df.to_dict('records')

        # Liczba ofert według typu zatrudnienia
        df = pd.read_sql_query(
            'SELECT employment_type, COUNT(*) as count FROM job_offers GROUP BY employment_type',
            conn
        )
        stats['by_employment_type'] = df.to_dict('records')

        # Liczba ofert według kategorii stanowiska
        df = pd.read_sql_query(
            'SELECT category, COUNT(*) as count FROM job_offers WHERE category IS NOT NULL GROUP BY category ORDER BY count DESC',
            conn
        )
        stats['by_category'] = df.to_dict('records')

        # Całkowita liczba ofert
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM job_offers')
        stats['total_jobs'] = cursor.fetchone()[0]

        conn.close()
        return stats

    def clear_database(self):
        """Usuwa wszystkie oferty z bazy danych."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM job_offers')
        conn.commit()
        conn.close()