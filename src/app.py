from flask import Flask, jsonify
import os
import subprocess
from PIL import Image
import numpy as np
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from forms import RegistrationForm, LoginForm
from models import db, User, UserImage
from app import db
from flask import send_file
import base64
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash
from io import BytesIO
from scipy.ndimage import rank_filter
import time
import cv2

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
UPLOAD_FOLDER = 'data/uploads'
RESULTS_FOLDER = 'results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)


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
@login_required
def gallery():
    images = UserImage.query.filter(UserImage.user_id == current_user.id).all()
    image_data_list = [
        {'id': image.id, 'filename': image.filename, 'data': base64.b64encode(image.image_data).decode('utf-8')}
        for image in images
    ]
    return render_template('gallery.html', images=image_data_list)


@app.route('/delete_all_images', methods=['POST'])
@login_required
def delete_all_images():
    try:
        images = UserImage.query.filter_by(user_id=current_user.id).all()

        if not images:
            flash('No images to delete.', 'warning')
            return redirect(url_for('gallery'))

        for image in images:
            db.session.delete(image)

        db.session.commit()
        flash('All images deleted successfully!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting images: {e}', 'danger')

    return redirect(url_for('gallery'))

@app.route('/edit_image/<int:image_id>', methods=['GET', 'POST'])
@login_required
def edit_image(image_id):
    image = UserImage.query.filter_by(id=image_id, user_id=current_user.id).first()

    if not image:
        flash('Image not found or you do not have permission to edit it.', 'danger')
        return redirect(url_for('gallery'))

    if request.method == 'GET':
        image_data = base64.b64encode(image.image_data).decode('utf-8')
        return render_template('edit_image.html', image_id=image.id, image_data=image_data)

    if request.method == 'POST':
        try:
            new_image_data = request.files.get('edited_image').read()

            image.image_data = new_image_data
            db.session.commit()

            return jsonify({"success": True})
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "error": str(e)})


@app.route('/delete_image/<int:image_id>', methods=['POST'])
@login_required
def delete_image(image_id):
    image = UserImage.query.filter_by(id=image_id, user_id=current_user.id).first()
    if not image:
        flash('Image not found or you do not have permission to delete it.', 'danger')
        return redirect(url_for('gallery'))

    db.session.delete(image)
    db.session.commit()
    flash('Image deleted successfully!', 'success')
    return redirect(url_for('gallery'))

@app.route('/download_image/<int:image_id>', methods=['POST'])
def download_image(image_id):
    image = UserImage.query.get(image_id)

    if image is None:
        return "Image not found", 404

    image_data = image.image_data
    image_io = BytesIO(image_data)

    return send_file(image_io, mimetype='image/png', as_attachment=True, download_name=f"{image.filename}.png")


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    image_count = UserImage.query.filter_by(user_id=current_user.id).count()

    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')

        if check_password_hash(current_user.password, current_password):
            current_user.password = generate_password_hash(new_password)
            db.session.commit()
            flash('Password is changed!', 'success')
        else:
            flash('Old password is incorrect!', 'danger')

    return render_template('profile.html', user=current_user, image_count=image_count)


@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    try:
        user = current_user

        images = UserImage.query.filter_by(user_id=user.id).all()
        for image in images:
            db.session.delete(image)

        db.session.delete(user)
        db.session.commit()

        logout_user()

        flash('Your account has been deleted successfully.', 'success')
        return redirect(url_for('login'))

    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting account: {e}', 'danger')
        return redirect(url_for('profile'))


@app.route('/upload_image', methods=['POST'])
def upload_image():
    image_file = request.files.get('image')
    if not image_file:
        return jsonify({'error': 'No image provided'}), 400

    image_extension = "png"

    image_path = os.path.join(UPLOAD_FOLDER, f'original_image.{image_extension}')
    try:
        image_file.save(image_path)
        return jsonify({'message': 'Image uploaded successfully', 'path': image_path}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to save image: {e}'}), 500


@app.route('/inpaint', methods=['POST'])
def inpaint():
    image_file = request.files['image']
    model_name = request.form.get('model')
    detection_mode = request.form.get('detection_mode')

    if not model_name or model_name not in ['places2.pth', 'celeba.pth', 'psv.pth']:
        return jsonify({'error': 'Invalid model selected.'}), 400

    image_extension = "png"

    image_path = os.path.join(UPLOAD_FOLDER, f'input_image.{image_extension}')
    image_file.save(image_path)


    try:
        image = Image.open(image_path).convert("RGB")
        original_size = image.size
        image.save(image_path)
    except Exception as e:
        return jsonify({'error': f'Failed to process the uploaded image: {e}'}), 500
    print(detection_mode)
    image_np = np.array(image)
    if detection_mode == 'manual':
        try:
            mask = (~np.all(image_np == [255, 255, 255], axis=-1)).astype(np.uint8) * 255
            mask_image = Image.fromarray(mask, mode='L')

        except Exception as e:
            return jsonify({'error': f'Failed to generate or save the mask: {e}'}), 500
    elif detection_mode == 'auto':
        try:
            print("Starting automatic detection with detect_noise_pixels...")

            # Wywołanie funkcji detect_noise_pixels
            start_time = time.time()
            mask_np = detect_noise_pixels(image_np, threshold=50)  # Użyj funkcji detect_noise_pixels

            # Zapisanie maski do pliku
            mask_image = Image.fromarray(mask_np, mode='L')
            mask_debug_path = os.path.join(UPLOAD_FOLDER, 'debug_auto_mask.png')
            mask_image.save(mask_debug_path)
            print(f"Automatic mask saved at {mask_debug_path}")

            # Oczekiwanie na zakończenie (sprawdzanie poprawności danych)
            timeout = 5  # maksymalny czas oczekiwania
            while mask_np is None or mask_np.sum() == 0:  # Jeśli maska jest pusta, czekamy
                if time.time() - start_time > timeout:
                    raise TimeoutError(f"Automatic mask generation took too long (>{timeout} seconds).")
                time.sleep(0.1)  # małe opóźnienie
            print("Automatic detection completed successfully.")

        except TimeoutError as e:
            return jsonify({'error': f'Automatic detection timeout: {e}'}), 500
        except Exception as e:
            return jsonify({'error': f'Failed to perform automatic detection: {e}'}), 500

    else:
        return jsonify({'error': 'Invalid detection mode.'}), 400

    mask_path = os.path.join(UPLOAD_FOLDER, f'input_mask.{image_extension}')
    mask_image.save(mask_path)

    list_file_path = 'places2_example_list'
    try:
        with open(list_file_path, 'w') as f:
            original_image_path = f"data/uploads/original_image.{image_extension}"
            mask_path = mask_path.replace("\\", "/")
            f.write(f"{original_image_path}\t{mask_path}\n")
    except Exception as e:
        return jsonify({'error': f'Failed to prepare the example list file: {e}'}), 500

    try:
        result = subprocess.run(
            ['python', 'src/test.py', '--list_file', list_file_path, '--snapshot', f'data/{model_name}'],
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
        'results', f'original_image.{image_extension}'
    )

    try:
        with Image.open(result_path) as result_image:
            resized_image = result_image.resize(original_size, Image.LANCZOS)
            resized_image.save(result_path)
    except FileNotFoundError:
        return jsonify({'error': 'Result file not found'}), 404

    try:
        with open(result_path, 'rb') as f:
            image_data = f.read()

        current_time = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        new_filename = f"Photo saved {current_time}"

        if current_user.is_authenticated:
            user_instance = User.query.get(current_user.id)
            new_image = UserImage(filename=new_filename, image_data=image_data, user=user_instance)
        else:
            return "User not authenticated", 401

        db.session.add(new_image)
        db.session.commit()
    except Exception as e:
        return jsonify({'error': f'Failed to save the result: {e}'}), 500

    return send_file(result_path, mimetype=f'image/{image_extension}')


def detect_noise_pixels(image, threshold=20):

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    smoothed_image = cv2.medianBlur(gray_image, 5)

    diff = cv2.absdiff(gray_image, smoothed_image)

    _, noise_mask = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)

    noise_mask = cv2.bitwise_not(noise_mask)

    return noise_mask

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
