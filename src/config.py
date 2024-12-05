# src/config.py
import os

class Config:
    SECRET_KEY = os.urandom(24)

    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = 'uploads'
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_DURATION = 3600
