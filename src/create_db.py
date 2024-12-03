from app import app, db
from models import User#, Image

with app.app_context():
    db.create_all()  # Tworzy wszystkie tabele na podstawie modeli
    print("Baza danych i tabele zostały utworzone.")

    # Dodanie testowych użytkowników
    admin = User(username='admin', email='admin@example.com')
    admin.set_password('adminpassword')

    guest = User(username='guest', email='guest@example.com')
    guest.set_password('guestpassword')

    db.session.add(admin)
    db.session.add(guest)
    db.session.commit()
    print("Testowi użytkownicy zostali dodani.")
