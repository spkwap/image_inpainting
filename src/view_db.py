import sqlite3

# Połącz się z bazą danych (utworzy plik, jeśli nie istnieje)
conn = sqlite3.connect('instance/site.db')

# Utwórz kursor do wykonywania zapytań SQL
cursor = conn.cursor()

# Wyświetl listę tabel w bazie danych
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tabele w bazie danych:", tables)

# Jeśli chcesz zobaczyć dane w konkretnej tabeli, np. 'User':
try:
    table_name = 'User'  # Zmień na nazwę tabeli, którą chcesz wyświetlić
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    print(f"\nZawartość tabeli {table_name}:")
    for row in rows:
        print(row)
except sqlite3.Error as e:
    print(f"Błąd podczas odczytu tabeli: {e}")


try:
    table_name = 'images'
    cursor.execute(f"SELECT * FROM {table_name}")
    cursor.execute(f"PRAGMA table_info({table_name});")
    rows = cursor.fetchall()
    print(f"\nZawartość tabeli {table_name}:")
    for row in rows:
        print(row)
except sqlite3.Error as e:
    print(f"Błąd podczas odczytu tabeli: {e}")

# Zamknij połączenie
conn.close()
