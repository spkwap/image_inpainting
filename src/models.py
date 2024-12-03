from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):  # Dodanie UserMixin
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    images = db.relationship('UserImage', back_populates='user', lazy=True)  # Relacja do obrazów

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

    def set_password(self, password):
        """Generuje hash hasła."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Sprawdza poprawność hasła."""
        return check_password_hash(self.password, password)


class UserImage(db.Model):
    __tablename__ = 'images'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    image_data = db.Column(db.LargeBinary, nullable=False)  # Kolumna do przechowywania danych obrazu
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key dla użytkownika
    user = db.relationship('User', back_populates='images')  # Relacja z użytkownikiem

    def __init__(self, filename, image_data, user):
        """Konstruktor do tworzenia instancji obrazu."""
        self.filename = filename
        self.image_data = image_data
        self.user = user  # Przypisanie użytkownika do obrazu
