import sqlite3

conn = sqlite3.connect('instance/site.db')

cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tabele w bazie danych:", tables)

try:
    table_name = 'User'
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

conn.close()
