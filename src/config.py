# src/config.py
import os

class Config:
    # Tajny klucz do sesji, tokenów itp.
    SECRET_KEY = os.urandom(24)

    # Ustawienie bazy danych (w tym przypadku SQLite)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'  # Ścieżka do pliku bazy danych
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Wyłącza zbędne śledzenie zmian w bazie danych

    # Możliwe dodatkowe ustawienia
    # Folder do przechowywania plików uploadowanych przez użytkowników
    UPLOAD_FOLDER = 'uploads'
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    # Rozszerzenia dozwolone w uploadzie plików (np. obrazy)
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


    # Ustawienia dotyczące logowania (np. czas trwania sesji)
    SESSION_COOKIE_SECURE = False  # Ustaw na True, gdy aplikacja działa przez HTTPS
    REMEMBER_COOKIE_DURATION = 3600  # Czas trwania "zapamiętywania" użytkownika (1 godzina)
