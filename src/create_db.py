from app import app, db
from models import User, UserImage

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

    # Dodanie testowego zdjęcia
    try:
        with open('src/results/case1_input.png', 'rb') as f:
            image_data = f.read()
    except FileNotFoundError:
        print("Plik wynikowy nie został znaleziony.")
        image_data = None

    if image_data:
        # Dodanie zdjęć do bazy danych
        image1 = UserImage(filename='image1.jpg', image_data=image_data, user=admin)
        image2 = UserImage(filename='image2.jpg', image_data=image_data, user=guest)

        db.session.add(image1)
        db.session.add(image2)
        db.session.commit()
        print("Testowe zdjęcia zostały dodane.")
    else:
        print("Nie można dodać zdjęć, ponieważ brakuje danych obrazu.")
