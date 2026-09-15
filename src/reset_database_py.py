"""
Skrypt do resetowania bazy danych.
Usuwa starą bazę i tworzy nową z poprawną strukturą.
"""

import os
from database import JobDatabase

def main():
    print("\n" + "="*70)
    print("  RESET BAZY DANYCH")
    print("="*70 + "\n")
    
    db_path = 'jobs.db'
    
    # Sprawdzamy czy baza istnieje
    if os.path.exists(db_path):
        print(f"Znaleziono bazę danych: {db_path}")
        confirm = input("Czy na pewno chcesz usunąć bazę danych? (t/n): ")
        
        if confirm.lower() == 't':
            try:
                os.remove(db_path)
                print(f"✓ Baza danych usunięta: {db_path}")
            except Exception as e:
                print(f"✗ Błąd przy usuwaniu bazy: {e}")
                return
        else:
            print("Anulowano.")
            return
    else:
        print("Baza danych nie istnieje, zostanie utworzona nowa.")
    
    # Tworzymy nową bazę z poprawną strukturą
    print("\nTworzenie nowej bazy danych...")
    db = JobDatabase(db_path)
    print("✓ Nowa baza danych utworzona z poprawną strukturą!\n")
    
    print("="*70)
    print("Teraz możesz uruchomić: python scraper.py")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()