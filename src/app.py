from flask import Flask, request, render_template, jsonify, send_file, redirect, url_for, flash
import os
import subprocess
from PIL import Image
import numpy as np
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from forms import RegistrationForm, LoginForm
from models import db, User, UserImage
from flask import request
from app import db
from werkzeug.utils import secure_filename
from flask import send_file
from io import BytesIO
from PIL import Image as PILImage
import base64
from werkzeug.utils import secure_filename
from datetime import datetime


# Inicjalizacja aplikacji
app = Flask(__name__)
app.config.from_object(Config)  # Ładowanie konfiguracji z pliku config.py

# Inicjalizacja bazy danych i logowania
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Strona logowania
UPLOAD_FOLDER = 'data/uploads'
RESULTS_FOLDER = 'results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)


# Definicja funkcji ładowania użytkownika
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    return redirect(url_for('home')) if current_user.is_authenticated else redirect(url_for('login'))

@app.route('/home')
@login_required
def home():
    return render_template('upload.html', username=current_user.username)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Registered successfully, you can now login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('home'))
        flash('Invalid username or password.', 'danger')

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout.', 'info')
    return redirect(url_for('login'))

@app.route('/gallery')
def gallery():

    images = UserImage.query.filter(UserImage.user_id == current_user.id).all()

    image_data_list = []
    for image in images:
        # Jeśli obraz jest zapisany w formacie binarnym
        img_data_binary = base64.b64encode(image.image_data).decode('utf-8')
        image_data_list.append({'filename': image.filename, 'data': img_data_binary})

    return render_template('gallery.html', images=image_data_list)


def ensure_binary_mask(mask_np):
    """
    Zamienia piksele na czne (0) lub białe (255) w masce.
    """

    mask_np[mask_np <= 20] = 0

    mask_np[mask_np > 20] = 255
    return mask_np




@app.route('/inpaint', methods=['POST'])
def inpaint():

    image_file = request.files['image']
    image_extension = image_file.filename.split('.')[-1].lower()

    if image_extension not in ['jpg', 'jpeg', 'png']:
        return jsonify({'error': 'Only jpg, jpeg, or png images are allowed.'}), 400


    image_path = os.path.join(UPLOAD_FOLDER, f'input_image.{image_extension}')
    image_file.save(image_path)

    try:

        image = Image.open(image_path).convert("RGB")
        image.save(image_path)
    except Exception as e:
        return jsonify({'error': f'Failed to process the uploaded image: {e}'}), 500


    try:
        image_np = np.array(image)

        mask = (~np.all(image_np == [255, 255, 255], axis=-1)).astype(np.uint8) * 255
        mask_image = Image.fromarray(mask, mode='L')


        mask_path = os.path.join(UPLOAD_FOLDER, f'input_mask.{image_extension}')
        mask_image.save(mask_path)
    except Exception as e:
        return jsonify({'error': f'Failed to generate or save the mask: {e}'}), 500


    list_file_path = 'places2_example_list'
    try:
        with open(list_file_path, 'w') as f:
            image_path = image_path.replace("\\", "/")
            mask_path = mask_path.replace("\\", "/")
            f.write(f"{image_path}\t{mask_path}\n")
    except Exception as e:
        return jsonify({'error': f'Failed to prepare the example list file: {e}'}), 500


    try:
        result = subprocess.run(
            ['python', 'src/test.py', '--list_file', list_file_path, '--snapshot', 'data/places2.pth'],
            check=True, capture_output=True, text=True
        )
        print("stdout:", result.stdout)
        print("stderr:", result.stderr)
    except subprocess.CalledProcessError as e:
        return jsonify({
            'error': f"Inpainting script failed. Return code: {e.returncode}, "
                     f"stdout: {e.stdout}, stderr: {e.stderr}"
        }), 500


    result_path = os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),
        'results', f'input_image.{image_extension}'
    )

    #save_image_to_db(result_path, image_path, current_user.id)
    try:
        with open(result_path, 'rb') as f:
            image_data = f.read()

    except FileNotFoundError:
        return jsonify({'error': 'Result file not found'}), 404

    current_time = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
    new_filename = f"Photo saved on {current_time}"

    if current_user.is_authenticated:
        user_instance = User.query.get(current_user.id)
        new_image = UserImage(filename=new_filename, image_data=image_data, user=user_instance)
    else:
        # Handle the case when the user is not authenticated
        # You can return an error, redirect, or any other response
        return "User not authenticated", 401

    db.session.add(new_image)
    db.session.commit()

    return send_file(result_path, mimetype=f'image/{image_extension}')




with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
