from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# db jest już zainicjalizowane w app.py, więc tutaj go używamy
db = SQLAlchemy()  # To musi być importowane z głównej aplikacji w momencie inicjalizacji

# Model użytkownika
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Id użytkownika
    username = db.Column(db.String(150), unique=True, nullable=False)  # Nazwa użytkownika
    email = db.Column(db.String(120), unique=True, nullable=False)  # Adres e-mail
    password = db.Column(db.String(150), nullable=False)  # Hasło użytkownika

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

    # Ustawianie hasła (wygenerowanie hash'a)
    def set_password(self, password):
        self.password = generate_password_hash(password)

    # Sprawdzanie hasła (porównanie z zapisanym hash'em)
    def check_password(self, password):
        return check_password_hash(self.password, password)
